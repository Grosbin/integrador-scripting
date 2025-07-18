# Sistema de Gestión de Usuarios Temporales
# Crea cuentas de usuario locales desde archivo CSV para temporadas altas

param(
    [string]$CsvFile = "datos\empleados.csv",
    [string]$LogFile = "usuarios_creados.log",
    [switch]$DryRun = $false
)

# Configuración
$ErrorActionPreference = "Stop"
$LogPath = Join-Path $PWD $LogFile

# Función para logging con timestamp
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp [$Level] $Message"
    
    Write-Host $logMessage
    Add-Content -Path $LogPath -Value $logMessage -Encoding UTF8
}

# Función para generar contraseña segura
function New-SecurePassword {
    param([int]$Length = 12)
    
    # Caracteres permitidos para contraseña
    $lowercase = "abcdefghijklmnopqrstuvwxyz"
    $uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    $numbers = "0123456789"
    $symbols = "!@#$%^&*"
    
    # Asegurar que la contraseña tenga al menos un carácter de cada tipo
    $password = ""
    $password += ($lowercase.ToCharArray() | Get-Random)
    $password += ($uppercase.ToCharArray() | Get-Random)
    $password += ($numbers.ToCharArray() | Get-Random)
    $password += ($symbols.ToCharArray() | Get-Random)
    
    # Completar longitud restante
    $allChars = $lowercase + $uppercase + $numbers + $symbols
    for ($i = 4; $i -lt $Length; $i++) {
        $password += ($allChars.ToCharArray() | Get-Random)
    }
    
    # Mezclar caracteres
    $passwordArray = $password.ToCharArray()
    $shuffled = $passwordArray | Sort-Object {Get-Random}
    
    return -join $shuffled
}

# Función para validar formato de email
function Test-EmailFormat {
    param([string]$Email)
    
    $emailRegex = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return $Email -match $emailRegex
}

# Función para crear usuario local
function New-LocalEmployee {
    param(
        [string]$FullName,
        [string]$Email,
        [string]$Department,
        [string]$Password,
        [bool]$IsAdmin = $false
    )
    
    try {
        # Generar nombre de usuario desde email
        $username = ($Email -split '@')[0]
        
        # Limpiar caracteres especiales del nombre de usuario
        $username = $username -replace '[^a-zA-Z0-9]', ''
        
        # Limitar longitud del nombre de usuario
        if ($username.Length -gt 20) {
            $username = $username.Substring(0, 20)
        }
        
        Write-Log "Creando usuario: $username ($FullName)"
        
        if ($DryRun) {
            Write-Log "DRY RUN: Usuario $username sería creado" "INFO"
            return @{
                Success = $true
                Username = $username
                Password = $Password
            }
        }
        
        # Verificar si el usuario ya existe
        try {
            $existingUser = Get-LocalUser -Name $username -ErrorAction Stop
            Write-Log "Usuario $username ya existe, actualizando..." "WARNING"
            
            # Actualizar contraseña
            $securePassword = ConvertTo-SecureString $Password -AsPlainText -Force
            Set-LocalUser -Name $username -Password $securePassword -FullName $FullName
            
        } catch [Microsoft.PowerShell.Commands.UserNotFoundException] {
            # Usuario no existe, crear nuevo
            $securePassword = ConvertTo-SecureString $Password -AsPlainText -Force
            
            New-LocalUser -Name $username `
                         -Password $securePassword `
                         -FullName $FullName `
                         -Description "Empleado temporal - $Department" `
                         -PasswordNeverExpires:$true `
                         -UserMayNotChangePassword:$false
        }
        
        # Agregar a grupos apropiados
        if ($IsAdmin) {
            try {
                Add-LocalGroupMember -Group "Administradores" -Member $username -ErrorAction SilentlyContinue
                Write-Log "Usuario $username agregado al grupo Administradores"
            } catch {
                Write-Log "No se pudo agregar $username a Administradores: $($_.Exception.Message)" "WARNING"
            }
        }
        
        # Agregar a grupo de usuarios
        try {
            Add-LocalGroupMember -Group "Usuarios" -Member $username -ErrorAction SilentlyContinue
        } catch {
            # Usuario probablemente ya está en el grupo
        }
        
        Write-Log "✅ Usuario $username creado exitosamente"
        
        return @{
            Success = $true
            Username = $username
            Password = $Password
        }
        
    } catch {
        Write-Log "❌ Error creando usuario $username : $($_.Exception.Message)" "ERROR"
        return @{
            Success = $false
            Username = $username
            Error = $_.Exception.Message
        }
    }
}

# Función para procesar archivo CSV
function Process-EmployeeCsv {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Log "❌ Archivo CSV no encontrado: $FilePath" "ERROR"
        return $false
    }
    
    try {
        $employees = Import-Csv $FilePath -Encoding UTF8
        
        if ($employees.Count -eq 0) {
            Write-Log "⚠️  Archivo CSV está vacío" "WARNING"
            return $true
        }
        
        Write-Log "📄 Procesando $($employees.Count) empleados desde $FilePath"
        
        $successCount = 0
        $errorCount = 0
        $results = @()
        
        foreach ($employee in $employees) {
            # Validar campos requeridos
            if (-not $employee.nombre_completo -or -not $employee.correo) {
                Write-Log "❌ Empleado con campos faltantes: $($employee | ConvertTo-Json -Compress)" "ERROR"
                $errorCount++
                continue
            }
            
            # Validar formato de email
            if (-not (Test-EmailFormat $employee.correo)) {
                Write-Log "❌ Email inválido para $($employee.nombre_completo): $($employee.correo)" "ERROR"
                $errorCount++
                continue
            }
            
            # Generar contraseña
            $password = New-SecurePassword
            
            # Determinar si necesita privilegios administrativos
            $isAdmin = $employee.departamento -eq "TI" -or $employee.departamento -eq "Administración"
            
            # Crear usuario
            $result = New-LocalEmployee -FullName $employee.nombre_completo `
                                       -Email $employee.correo `
                                       -Department $employee.departamento `
                                       -Password $password `
                                       -IsAdmin $isAdmin
            
            if ($result.Success) {
                $successCount++
                
                # Agregar resultado para reporte
                $results += [PSCustomObject]@{
                    NombreCompleto = $employee.nombre_completo
                    Usuario = $result.Username
                    Email = $employee.correo
                    Departamento = $employee.departamento
                    Contraseña = $result.Password
                    EsAdmin = $isAdmin
                    Estado = "Creado"
                }
            } else {
                $errorCount++
                
                $results += [PSCustomObject]@{
                    NombreCompleto = $employee.nombre_completo
                    Usuario = $result.Username
                    Email = $employee.correo
                    Departamento = $employee.departamento
                    Contraseña = ""
                    EsAdmin = $isAdmin
                    Estado = "Error: $($result.Error)"
                }
            }
        }
        
        # Generar reporte de usuarios creados
        $reportFile = "reporte_usuarios_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
        $results | Export-Csv -Path $reportFile -NoTypeInformation -Encoding UTF8
        
        Write-Log "📊 Reporte generado: $reportFile"
        Write-Log "=== RESUMEN ==="
        Write-Log "✅ Usuarios creados exitosamente: $successCount"
        Write-Log "❌ Errores: $errorCount"
        Write-Log "📁 Total procesados: $($successCount + $errorCount)"
        
        return $errorCount -eq 0
        
    } catch {
        Write-Log "❌ Error procesando archivo CSV: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Función para mostrar usuarios existentes
function Show-ExistingUsers {
    try {
        $localUsers = Get-LocalUser | Where-Object { $_.Description -like "*Empleado temporal*" }
        
        if ($localUsers.Count -gt 0) {
            Write-Log "👥 Usuarios temporales existentes:"
            foreach ($user in $localUsers) {
                Write-Log "   - $($user.Name) ($($user.FullName))"
            }
        } else {
            Write-Log "ℹ️  No hay usuarios temporales existentes"
        }
    } catch {
        Write-Log "⚠️  No se pudieron listar usuarios existentes: $($_.Exception.Message)" "WARNING"
    }
}

# Función para limpiar usuarios temporales antiguos
function Remove-OldTemporaryUsers {
    param([int]$DaysOld = 30)
    
    try {
        $cutoffDate = (Get-Date).AddDays(-$DaysOld)
        $tempUsers = Get-LocalUser | Where-Object { 
            $_.Description -like "*Empleado temporal*" -and 
            $_.LastLogon -lt $cutoffDate 
        }
        
        if ($tempUsers.Count -gt 0) {
            Write-Log "🧹 Eliminando $($tempUsers.Count) usuarios temporales antiguos..."
            
            foreach ($user in $tempUsers) {
                if (-not $DryRun) {
                    Remove-LocalUser -Name $user.Name -Confirm:$false
                }
                Write-Log "🗑️  Usuario eliminado: $($user.Name)"
            }
        } else {
            Write-Log "ℹ️  No hay usuarios temporales antiguos para eliminar"
        }
    } catch {
        Write-Log "⚠️  Error eliminando usuarios antiguos: $($_.Exception.Message)" "WARNING"
    }
}

# Función principal
function Main {
    Write-Log "=== INICIO DE GESTIÓN DE USUARIOS TEMPORALES ==="
    
    # Verificar permisos de administrador
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Log "❌ Este script requiere privilegios de administrador" "ERROR"
        exit 1
    }
    
    if ($DryRun) {
        Write-Log "🔍 Ejecutando en modo DRY RUN (no se realizarán cambios)" "INFO"
    }
    
    # Mostrar usuarios existentes
    Show-ExistingUsers
    
    # Procesar archivo CSV
    $success = Process-EmployeeCsv -FilePath $CsvFile
    
    # Limpiar usuarios antiguos
    Remove-OldTemporaryUsers -DaysOld 30
    
    Write-Log "=== FIN DE GESTIÓN DE USUARIOS TEMPORALES ==="
    
    if ($success) {
        Write-Log "✅ Proceso completado exitosamente"
        exit 0
    } else {
        Write-Log "❌ Proceso completado con errores"
        exit 1
    }
}

# Manejo de errores globales
trap {
    Write-Log "❌ Error fatal: $($_.Exception.Message)" "ERROR"
    exit 1
}

# Ejecutar función principal
Main