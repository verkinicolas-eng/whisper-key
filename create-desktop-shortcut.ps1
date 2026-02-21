# create-desktop-shortcut.ps1
# Crée un raccourci desktop pour ouvrir Claude Code dans whisper-key-local en mode dangerously

$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\whisper-key Dev.lnk"
$projectPath = "C:\Users\nicol\Dev\whisper-key-local"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "C:\Windows\System32\cmd.exe"
$Shortcut.Arguments = "/k cd /d `"$projectPath`" && claude --dangerously-skip-permissions"
$Shortcut.WorkingDirectory = $projectPath
$Shortcut.Description = "whisper-key Dev - Claude Code (dangerously)"
$Shortcut.IconLocation = "C:\Windows\System32\cmd.exe,0"
$Shortcut.Save()

Write-Host "Raccourci cree : $shortcutPath" -ForegroundColor Green
Write-Host "  Dossier : $projectPath" -ForegroundColor Cyan
Write-Host "  Commande : claude --dangerously-skip-permissions" -ForegroundColor Cyan
