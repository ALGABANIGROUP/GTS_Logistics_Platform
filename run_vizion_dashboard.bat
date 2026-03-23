@echo off
setlocal
set PY=%~dp0\.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
set VIZION_EYE_PATH=F:\ASUS ROG Strix G614JV\GTS Logistics\TheVIZION
pushd "%VIZION_EYE_PATH%"
%PY% -m vizion_eye.cli dashboard
popd
endlocal
