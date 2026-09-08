param(
  [ValidateRange(1, 65535)]
  [int]$Port = 8080
)

$ErrorActionPreference = "Stop"

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pythonLauncher) {
  $pythonCommand = "py"
  $pythonArguments = @("-3")
} else {
  $pythonLauncher = Get-Command python -ErrorAction SilentlyContinue
  if ($pythonLauncher) {
    $pythonCommand = "python"
    $pythonArguments = @()
  }
}

if (-not $pythonLauncher) {
  throw "No se encontró Python. Instálalo desde https://www.python.org/downloads/ o usa GitHub Codespaces."
}

if ($pythonLauncher.Source -like "*WindowsApps*") {
  throw "Solo se encontró el acceso directo de Microsoft Store, no Python. Instálalo desde https://www.python.org/downloads/ o usa GitHub Codespaces."
}

$null = & $pythonCommand @pythonArguments --version 2>$null
if ($LASTEXITCODE -ne 0) {
  throw "No se encontró una instalación funcional de Python. Instálala desde https://www.python.org/downloads/ o usa GitHub Codespaces."
}

Write-Host "Servidor disponible en http://localhost:$Port"
& $pythonCommand @pythonArguments -m http.server $Port
