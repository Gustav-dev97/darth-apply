// Quando a porta estiver ocupada executar:

Get-Process python -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -like "*darth-apply*" } |
    Stop-Process -Force
Write-Host "Backend encerrado."

// Para rodar o backend:

uv run python src/backends/main.py