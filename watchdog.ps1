# Watchdog whisper-key : relance automatiquement si crash
param(
    [int]$RestartDelay = 5
)

$timestamp = { "[$(Get-Date -Format 'HH:mm:ss')]" }

while ($true) {
    Write-Host "$(& $timestamp) Demarrage whisper-key..." -ForegroundColor Green

    $process = Start-Process -FilePath "whisper-key" -PassThru -NoNewWindow
    $process.WaitForExit()

    $exitCode = $process.ExitCode

    if ($exitCode -eq 0) {
        Write-Host "$(& $timestamp) whisper-key arrete proprement (exit 0)." -ForegroundColor Yellow
        break
    } else {
        Write-Host "$(& $timestamp) whisper-key crashe (exit $exitCode) -> relance dans ${RestartDelay}s..." -ForegroundColor Red
        Start-Sleep -Seconds $RestartDelay
    }
}
