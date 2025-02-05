@echo off
:: Check for administrative privileges
:: Try to create a folder in a restricted location to verify if the script has admin rights
mkdir "%SystemRoot%\System32\TempFolder" >nul 2>&1
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    :: Re-run the script with administrative privileges
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Clean up the temporary folder if created
rmdir "%SystemRoot%\System32\TempFolder" >nul 2>&1

:: Set the path to python.exe relative to the batch file location
set "PYTHON_EXECUTABLE=%~dp0python.exe"

REM Define the Python command to execute
set PYTHON_COMMAND=from seabreeze import os_setup;os_setup.main()

REM Print the path to the python executable and current directory (for debugging purposes)
echo Python executable: %PYTHON_EXECUTABLE%
echo Current directory: %cd%

REM Run the Python command in a new command window
start cmd /k %PYTHON_EXECUTABLE% -c "%PYTHON_COMMAND%"

REM Store the setup flag (optional, replace with actual logic if needed)
REM If you need to store the setup flag, you can add additional logic here
REM Example:
REM echo Setup completed > setup_flag.txt

echo SeaBreeze setup script has been executed.
pause
