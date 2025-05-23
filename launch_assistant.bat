@echo off
REM --- Define a literal quote character 'q' ---
set q="

REM Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"
REM Ensure SCRIPT_DIR ends with a backslash for reliable path concatenation
if "%SCRIPT_DIR:~-1%" NEQ "\" set "SCRIPT_DIR=%SCRIPT_DIR%\"

REM Change to the script's directory
cd "%SCRIPT_DIR%"

REM Determine Python executable path (including virtual environment)
if exist "%SCRIPT_DIR%.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
    set "PYTHON_EXECUTABLE_PATH=%SCRIPT_DIR%.venv\Scripts\python.exe"
    if not exist "%PYTHON_EXECUTABLE_PATH%" (
        echo [ERROR] python.exe not found at "%PYTHON_EXECUTABLE_PATH%" even though activate.bat exists.
        echo [ERROR] Falling back to system Python.
        set "PYTHON_EXECUTABLE_PATH=python.exe"
    )
) else (
    echo.
    echo [WARNING] Virtual environment '.venv' or its activate.bat was not found in this directory.
    echo [WARNING] Please ensure you have created it (python -m venv .venv) and installed dependencies.
    echo [WARNING] You can install dependencies manually by running:
    echo [WARNING]     .\.venv\Scripts\activate
    echo [WARNING]     pip install -r requirements.txt
    echo [WARNING] Attempting to use system Python, which may lack necessary libraries.
    echo.
    set "PYTHON_EXECUTABLE_PATH=python.exe"
)

REM Construct the command string that cmd.exe will execute inside the new Windows Terminal tab.
REM This needs to be a single string for 'cmd.exe /k', and then that whole string
REM needs to be a single argument for wt.exe.
REM Using the 'q' variable to correctly embed quotes around paths that might contain spaces.
set "WT_INNER_CMD=cmd.exe /k %q%%PYTHON_EXECUTABLE_PATH%%q% %q%%SCRIPT_DIR%main_script.py%q%"

REM Construct the full PowerShell command string.
REM PowerShell requires single quotes for its string literals.
REM The %WT_INNER_CMD% will expand into the single-quoted string here.
set "POWERSHELL_CMD_STRING=Start-Process -FilePath 'wt.exe' -ArgumentList '--new-tab', '%WT_INNER_CMD%'"

REM Execute the PowerShell command. The outer quotes are for the batch 'powershell.exe -Command ""'
powershell.exe -NoProfile -Command "%POWERSHELL_CMD_STRING%"

pause
exit