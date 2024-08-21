@echo off
REM Set the path to your python.exe
REM Update the following line with the correct path to your python.exe
set PYTHON_EXECUTABLE=python.exe

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
