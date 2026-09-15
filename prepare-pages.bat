@echo off
setlocal
if exist upstream rmdir /s /q upstream
if exist public rmdir /s /q public
git clone --depth 1 https://github.com/Lolendor/reVCDOS.git upstream
if errorlevel 1 exit /b 1
py build_pages.py upstream public
if errorlevel 1 python build_pages.py upstream public
if errorlevel 1 exit /b 1
echo.
echo Ready: .\public
echo For a quick local test: py -m http.server 8000 --directory public
endlocal
