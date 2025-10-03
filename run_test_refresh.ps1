# Restart uvicorn and run simulator
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine -like '*uvicorn*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1
Start-Process -FilePath .\.venv\Scripts\python.exe -ArgumentList '-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000','--app-dir',(Get-Location).Path -WorkingDirectory (Get-Location).Path -NoNewWindow -PassThru | Out-Null
Start-Sleep -Seconds 3
Write-Host 'Server started; running simulator...'
.\.venv\Scripts\python.exe frontend_simulator2.py
