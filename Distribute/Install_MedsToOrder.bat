@echo off
setlocal

set "SRC_DIR=%~dp0"
set "TARGET_DIR=%USERPROFILE%\VAMEDS"

echo.
echo ================================================
echo   MedsToOrder Setup
echo ================================================
echo.

if not exist "%SRC_DIR%MedsToOrder.exe" (
    echo Could not find MedsToOrder.exe next to this installer.
    echo Please keep Install_MedsToOrder.bat in the same folder as
    echo MedsToOrder.exe and MedsToOrder_App_UserGuide.docx, then try again.
    echo.
    pause
    exit /b 1
)

if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
)

copy /Y "%SRC_DIR%MedsToOrder.exe" "%TARGET_DIR%\MedsToOrder.exe" >nul
copy /Y "%SRC_DIR%MedsToOrder_App_UserGuide.docx" "%TARGET_DIR%\MedsToOrder_App_UserGuide.docx" >nul

set "VBS=%TEMP%\_medstoorder_shortcut.vbs"
> "%VBS%" echo Set oWS = WScript.CreateObject("WScript.Shell")
>> "%VBS%" echo sLinkFile = "%USERPROFILE%\Desktop\MedsToOrder.lnk"
>> "%VBS%" echo Set oLink = oWS.CreateShortcut(sLinkFile)
>> "%VBS%" echo oLink.TargetPath = "%TARGET_DIR%\MedsToOrder.exe"
>> "%VBS%" echo oLink.WorkingDirectory = "%TARGET_DIR%"
>> "%VBS%" echo oLink.Description = "VA Medication Refill Identifier"
>> "%VBS%" echo oLink.Save
cscript //nologo "%VBS%" >nul 2>nul
del "%VBS%" >nul 2>nul

echo   MedsToOrder is ready to use.
echo.
echo   Installed to:
echo   %TARGET_DIR%
echo.
echo   A "MedsToOrder" shortcut was added to your Desktop.
echo   Double-click it any time to find medications you need
echo   to reorder.
echo.
echo ================================================
echo.
pause
