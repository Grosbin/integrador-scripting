# Script para verificar usuarios creados en Windows 11
# Uso: .\verificar_usuarios.ps1

param(
    [string]$CsvFile = "datos\empleados.csv",
    [switch]$ShowAll = $false
)

# Función para logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp [$Level] $Message"
    Write-Host $logMessage
}

# Función para verificar usuarios desde CSV
function Verify-UsersFromCsv {
    param([string]$CsvPath)
    
    if (-not (Test-Path $CsvPath)) {
        Write-Log "Archivo CSV no encontrado: $CsvPath" "ERROR"
        return
    }
    
    Write-Log "=== VERIFICACIÓN DESDE ARCHIVO CSV ===" "INFO"
    
    try {
        $employees = Import-Csv $CsvPath -Encoding UTF8
        
        foreach ($employee in $employees) {
            $username = ($employee.correo -split '@')[0]
            $username = $username -replace '[^a-zA-Z0-9]', ''
            if ($username.Length -gt 20) {
                $username = $username.Substring(0, 20)
            }
            
            try {
                $user = Get-LocalUser -Name $username -ErrorAction Stop
                Write-Log "Usuario encontrado: $username ($($employee.nombre_completo))" "SUCCESS"
                Write-Log "   - Departamento: $($employee.departamento)" "INFO"
                Write-Log "   - Descripción: $($user.Description)" "INFO"
                Write-Log "   - Último acceso: $($user.LastLogon)" "INFO"
                Write-Log "   - Cuenta habilitada: $($user.Enabled)" "INFO"
            } catch [Microsoft.PowerShell.Commands.UserNotFoundException] {
                Write-Log "Usuario NO encontrado: $username ($($employee.nombre_completo))" "ERROR"
            }
            Write-Log ""
        }
    } catch {
        Write-Log "Error leyendo CSV: $($_.Exception.Message)" "ERROR"
    }
}

# Función para listar todos los usuarios temporales
function Show-TemporaryUsers {
    Write-Log "=== USUARIOS TEMPORALES EN EL SISTEMA ===" "INFO"
    
    try {
        $tempUsers = Get-LocalUser | Where-Object { $_.Description -like "*Empleado temporal*" }
        
        if ($tempUsers.Count -gt 0) {
            Write-Log "Total de usuarios temporales encontrados: $($tempUsers.Count)" "INFO"
            Write-Log ""
            
            foreach ($user in $tempUsers) {
                Write-Log "Usuario: $($user.Name)" "INFO"
                Write-Log "   - Nombre completo: $($user.FullName)" "INFO"
                Write-Log "   - Descripción: $($user.Description)" "INFO"
                Write-Log "   - Último acceso: $($user.LastLogon)" "INFO"
                Write-Log "   - Cuenta habilitada: $($user.Enabled)" "INFO"
                Write-Log "   - Contraseña nunca expira: $($user.PasswordNeverExpires)" "INFO"
                Write-Log ""
            }
        } else {
            Write-Log "No se encontraron usuarios temporales" "WARNING"
        }
    } catch {
        Write-Log "Error listando usuarios: $($_.Exception.Message)" "ERROR"
    }
}

# Función para verificar grupos de usuarios
function Show-UserGroups {
    Write-Log "=== VERIFICACIÓN DE GRUPOS ===" "INFO"
    
    try {
        $tempUsers = Get-LocalUser | Where-Object { $_.Description -like "*Empleado temporal*" }
        
        foreach ($user in $tempUsers) {
            Write-Log "Usuario: $($user.Name)" "INFO"
            
            # Verificar grupo Administradores
            $isAdmin = Get-LocalGroupMember -Group "Administradores" -ErrorAction SilentlyContinue | 
                      Where-Object { $_.Name -like "*\$($user.Name)" }
            if ($isAdmin) {
                Write-Log "   Está en grupo Administradores" "SUCCESS"
            } else {
                Write-Log "   NO está en grupo Administradores" "INFO"
            }
            
            # Verificar grupo Usuarios
            $isUser = Get-LocalGroupMember -Group "Usuarios" -ErrorAction SilentlyContinue | 
                     Where-Object { $_.Name -like "*\$($user.Name)" }
            if ($isUser) {
                Write-Log "   Está en grupo Usuarios" "SUCCESS"
            } else {
                Write-Log "   NO está en grupo Usuarios" "WARNING"
            }
            Write-Log ""
        }
    } catch {
        Write-Log "Error verificando grupos: $($_.Exception.Message)" "ERROR"
    }
}

# Función para mostrar todos los usuarios locales
function Show-AllLocalUsers {
    Write-Log "=== TODOS LOS USUARIOS LOCALES ===" "INFO"
    
    try {
        $allUsers = Get-LocalUser | Sort-Object Name
        
        Write-Log "Total de usuarios locales: $($allUsers.Count)" "INFO"
        Write-Log ""
        
        foreach ($user in $allUsers) {
            $isTemp = $user.Description -like "*Empleado temporal*"
            $status = if ($isTemp) { "TEMPORAL" } else { "REGULAR" }
            
            Write-Log "$status $($user.Name) - $($user.FullName)" "INFO"
            Write-Log "   - Descripción: $($user.Description)" "INFO"
            Write-Log "   - Habilitado: $($user.Enabled)" "INFO"
            Write-Log ""
        }
    } catch {
        Write-Log "Error listando todos los usuarios: $($_.Exception.Message)" "ERROR"
    }
}

# Función para verificar reporte generado
function Show-GeneratedReport {
    Write-Log "=== BUSCANDO REPORTES GENERADOS ===" "INFO"
    
    try {
        $reports = Get-ChildItem -Path "." -Filter "reporte_usuarios_*.csv" | Sort-Object LastWriteTime -Descending
        
        if ($reports.Count -gt 0) {
            Write-Log "Reportes encontrados:" "INFO"
            foreach ($report in $reports) {
                Write-Log "   - $($report.Name) (Creado: $($report.LastWriteTime))" "INFO"
            }
            
            # Mostrar contenido del reporte más reciente
            $latestReport = $reports[0]
            Write-Log ""
            Write-Log "Contenido del reporte más reciente ($($latestReport.Name)):" "INFO"
            
            $reportData = Import-Csv $latestReport.FullName -Encoding UTF8
            foreach ($row in $reportData) {
                $statusIcon = if ($row.Estado -eq "Creado") { "OK" } else { "ERROR" }
                Write-Log "$statusIcon $($row.NombreCompleto) - $($row.Usuario) - $($row.Estado)" "INFO"
            }
        } else {
            Write-Log "No se encontraron reportes generados" "WARNING"
        }
    } catch {
        Write-Log "Error buscando reportes: $($_.Exception.Message)" "ERROR"
    }
}

# Función principal
function Main {
    Write-Log "INICIANDO VERIFICACIÓN DE USUARIOS" "INFO"
    Write-Log "=====================================" "INFO"
    
    # Verificar permisos de administrador
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Log "Este script funciona mejor con privilegios de administrador" "WARNING"
    }
    
    # Verificar usuarios desde CSV
    Verify-UsersFromCsv -CsvPath $CsvFile
    
    Write-Log ""
    
    # Mostrar usuarios temporales
    Show-TemporaryUsers
    
    Write-Log ""
    
    # Verificar grupos
    Show-UserGroups
    
    Write-Log ""
    
    # Mostrar reportes generados
    Show-GeneratedReport
    
    Write-Log ""
    
    # Mostrar todos los usuarios si se solicita
    if ($ShowAll) {
        Show-AllLocalUsers
    }
    
    Write-Log "Verificación completada" "SUCCESS"
}

# Ejecutar función principal
Main 