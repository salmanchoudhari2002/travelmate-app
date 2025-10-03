# Restart uvicorn and run simulator v2
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine -like '*uvicorn*' -and $_.CommandLine -like '*travel_app*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1
Start-Process -NoNewWindow -FilePath .\.venv\Scripts\python.exe -ArgumentList '-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000','--app-dir',(Get-Location).Path -WorkingDirectory (Get-Location).Path -PassThru | Out-Null
Start-Sleep -Seconds 3
Write-Host "Uvicorn started, running frontend_simulator2.py now..."
.\.venv\Scripts\python.exe frontend_simulator2.py
