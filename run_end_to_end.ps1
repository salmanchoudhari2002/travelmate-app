Set-Location "C:\Users\91960\travel_app"
Write-Host "Stopping python processes..."
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1
Write-Host "Starting uvicorn..."
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList '-m','uvicorn','backend.app.main:app','--host','127.0.0.1','--port','8000','--app-dir',(Get-Location).Path -WorkingDirectory (Get-Location).Path -NoNewWindow -PassThru | Out-Null
Start-Sleep -Seconds 4
Write-Host "Running simulator..."
& ".\.venv\Scripts\python.exe" "frontend_simulator2.py"
Write-Host "Querying /map/search..."
try {
    $res = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/map/search?query=Taj%20Mahal&limit=1' -Method GET -TimeoutSec 30 -ErrorAction Stop
    Write-Host "map/search status: 200"
    $res | ConvertTo-Json -Depth 10
    if ($res.results -and $res.results.Count -gt 0) {
        $thumb = $res.results[0].thumbnail
        Write-Host "thumbnail field: $thumb"
        if ($thumb -and $thumb -like '/static/*') {
            $url = 'http://127.0.0.1:8000' + $thumb
            Write-Host "Thumbnail URL: $url"
            try {
                $h = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -ErrorAction Stop
                Write-Host "Thumbnail headers:"
                $h.Headers.GetEnumerator() | ForEach-Object { Write-Host "$($($_.Name)): $($_.Value)" }
            } catch {
                Write-Host "Failed HEAD: $($_.Exception.Message)"
            }
        }
    }
} catch {
    Write-Host "map/search failed: $($_.Exception.Message)"
}
Write-Host "Done."