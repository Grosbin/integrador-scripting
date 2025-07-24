# Verificación rápida de usuarios creados
# Ejecutar como administrador: .\verificar_rapido.ps1

Write-Host "VERIFICACIÓN RÁPIDA DE USUARIOS" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# 1. Verificar usuarios temporales
Write-Host "`nUSUARIOS TEMPORALES:" -ForegroundColor Yellow
$tempUsers = Get-LocalUser | Where-Object { $_.Description -like "*Empleado temporal*" }
if ($tempUsers.Count -gt 0) {
    Write-Host "Encontrados $($tempUsers.Count) usuarios temporales:" -ForegroundColor Green
    $tempUsers | Format-Table Name, FullName, Description, Enabled -AutoSize
} else {
    Write-Host "No se encontraron usuarios temporales" -ForegroundColor Red
}

# 2. Verificar desde CSV
Write-Host "`nVERIFICACIÓN DESDE CSV:" -ForegroundColor Yellow
if (Test-Path "datos\empleados.csv") {
    $employees = Import-Csv "datos\empleados.csv" -Encoding UTF8
    foreach ($emp in $employees) {
        $username = ($emp.correo -split '@')[0] -replace '[^a-zA-Z0-9]', ''
        if ($username.Length -gt 20) { $username = $username.Substring(0, 20) }
        
        try {
            $user = Get-LocalUser -Name $username -ErrorAction Stop
            Write-Host "$username ($($emp.nombre_completo)) - CREADO" -ForegroundColor Green
        } catch {
            Write-Host "$username ($($emp.nombre_completo)) - NO ENCONTRADO" -ForegroundColor Red
        }
    }
} else {
    Write-Host "Archivo datos\empleados.csv no encontrado" -ForegroundColor Red
}

# 3. Verificar reportes
Write-Host "`nREPORTES GENERADOS:" -ForegroundColor Yellow
$reports = Get-ChildItem -Filter "reporte_usuarios_*.csv" | Sort-Object LastWriteTime -Descending
if ($reports.Count -gt 0) {
    Write-Host "Reporte más reciente: $($reports[0].Name)" -ForegroundColor Green
    Write-Host "Creado: $($reports[0].LastWriteTime)" -ForegroundColor Gray
} else {
    Write-Host "No se encontraron reportes" -ForegroundColor Red
}

# 4. Comandos adicionales para verificar manualmente
Write-Host "`nCOMANDOS PARA VERIFICACIÓN MANUAL:" -ForegroundColor Yellow
Write-Host "Get-LocalUser | Where-Object { `$_.Description -like '*Empleado temporal*' }" -ForegroundColor Gray
Write-Host "Get-LocalGroupMember -Group 'Usuarios'" -ForegroundColor Gray
Write-Host "Get-LocalGroupMember -Group 'Administradores'" -ForegroundColor Gray

Write-Host "`nVerificación completada" -ForegroundColor Green 