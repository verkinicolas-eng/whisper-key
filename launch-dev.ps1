# Lancement dev whisper-key-local avec Claude Code
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$projectPath = "C:\Users\nicol\Dev\whisper-key-local"
Set-Location $projectPath

Write-Host "=== CLAUDE.md (contexte projet) ===" -ForegroundColor Cyan
Get-Content "CLAUDE.md" -Encoding UTF8 | Select-Object -First 30

Write-Host "`n=== JOURNAL.md (dernieres entrees) ===" -ForegroundColor Cyan
Get-Content "JOURNAL.md" -Encoding UTF8 | Select-Object -Last 20

Write-Host "`nLancement Claude Code..." -ForegroundColor Green
claude --dangerously-skip-permissions
