@echo off

where ab >nul 2>&1
if errorlevel 1 (
  echo O ab nao foi encontrado. Coloque a pasta Apache24\bin no PATH.
  exit /b 1
)

curl.exe -s http://127.0.0.1:9002/health >nul 2>&1
if errorlevel 1 (
  echo O app2 esta fora do ar. Suba com: python app.py 9002
  exit /b 1
)

echo === 30000 requisicoes, 50 simultaneas, Round Robin ===
curl.exe -s http://127.0.0.1:8080/algorithm/round_robin
echo.
echo O app2 sera derrubado daqui a 2 segundos...

start /b powershell -NoProfile -Command "Start-Sleep 2; Stop-Process -Id (Get-NetTCPConnection -LocalPort 9002 -State Listen).OwningProcess -Force"

ab -n 30000 -c 50 http://127.0.0.1:8080/ | findstr /C:"Requests per second" /C:"Time per request" /C:"Failed requests" /C:"Non-2xx"

echo.
curl.exe -s http://127.0.0.1:8080/status | findstr "http total alive"
echo.
echo Para religar o app2: python app.py 9002
