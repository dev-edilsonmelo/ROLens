# Script para executar GUI como Administrador
$pythonPath = "python"
$scriptPath = Join-Path $PSScriptRoot "gui.py"

# Verifica se já está rodando como admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    # Já é admin, executa diretamente
    Write-Host "Executando como Administrador..." -ForegroundColor Green
    & $pythonPath $scriptPath
} else {
    # Não é admin, solicita elevação
    Write-Host "Solicitando privilégios de Administrador..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python gui.py"
}
