@echo off
REM Environment Configuration Test Script for Windows
REM Tests all critical environment variables for GTS Logistics

echo 🔧 Testing GTS Environment Configuration
echo ========================================
echo.

REM Colors (Windows CMD doesn't support ANSI colors well, using symbols)
set "RED=[ERROR]"
set "GREEN=[OK]"
set "YELLOW=[WARN]"

REM Function to check environment variable
:check_env_var
setlocal enabledelayedexpansion
set "var_name=%~1"
set "var_value=%~2"
set "description=%~3"

if "%var_value%"=="" (
    echo %RED% %var_name%: NOT SET - %description%
    goto :eof
)

echo %var_value% | findstr /C:"your" >nul
if %errorlevel%==0 (
    echo %YELLOW% %var_name%: PLACEHOLDER VALUE - %description%
    goto :eof
)

echo %var_value% | findstr /C:"YOUR" >nul
if %errorlevel%==0 (
    echo %YELLOW% %var_name%: PLACEHOLDER VALUE - %description%
    goto :eof
)

echo %GREEN% %var_name%: CONFIGURED
goto :eof

REM Load environment variables from .env file
if exist ".env" (
    for /f "tokens=*" %%a in (.env) do (
        set %%a 2>nul
    )
    echo 📄 Environment file loaded successfully
) else (
    echo [ERROR] .env file not found
    exit /b 1
)

echo.
echo 🔍 Checking Database Configuration:
call :check_env_var "DATABASE_URL" "%DATABASE_URL%" "PostgreSQL connection string"
call :check_env_var "DB_HOSTNAME" "%DB_HOSTNAME%" "Database hostname"
call :check_env_var "DB_NAME" "%DB_NAME%" "Database name"

echo.
echo 📧 Checking Email Configuration:
call :check_env_var "SMTP_HOST" "%SMTP_HOST%" "SMTP server hostname"
call :check_env_var "SMTP_USER" "%SMTP_USER%" "SMTP username"
call :check_env_var "SMTP_PASSWORD" "%SMTP_PASSWORD%" "SMTP password"

echo.
echo 🚨 Checking Incident Response System:
call :check_env_var "LOG_PATH" "%LOG_PATH%" "Log file path"
call :check_env_var "ALERT_EMAIL" "%ALERT_EMAIL%" "Alert notification email"
call :check_env_var "INCIDENT_RETENTION_DAYS" "%INCIDENT_RETENTION_DAYS%" "Incident data retention"

echo.
echo 🔑 Checking API Keys:
call :check_env_var "OPENWEATHER_API_KEY" "%OPENWEATHER_API_KEY%" "Weather service API key"
call :check_env_var "ALPHA_VANTAGE_KEY" "%ALPHA_VANTAGE_KEY%" "Market data API key"
call :check_env_var "MARKETAUX_KEY" "%MARKETAUX_KEY%" "News service API key"

echo.
echo 📱 Checking Optional Services:
call :check_env_var "SLACK_WEBHOOK_URL" "%SLACK_WEBHOOK_URL%" "Slack notifications webhook"

echo.
echo 📊 Configuration Summary:
echo ========================

REM Count configured vs not configured
set /a total_vars=0
set /a configured_vars=0
set /a placeholder_vars=0

REM Check critical variables
set "critical_vars=DATABASE_URL SMTP_HOST LOG_PATH ALERT_EMAIL"
for %%v in (%critical_vars%) do (
    set /a total_vars+=1
    call set "value=%%!%%v!%%"
    if defined value (
        echo !value! | findstr /C:"your" >nul
        if !errorlevel!==1 (
            echo !value! | findstr /C:"YOUR" >nul
            if !errorlevel!==1 (
                set /a configured_vars+=1
            ) else (
                set /a placeholder_vars+=1
            )
        ) else (
            set /a placeholder_vars+=1
        )
    )
)

echo Total Critical Variables: %total_vars%
echo Properly Configured: %configured_vars%
echo Placeholder Values: %placeholder_vars%

if %configured_vars%==%total_vars% (
    echo [SUCCESS] All critical variables are configured!
) else if %placeholder_vars% gtr 0 (
    echo [WARNING] Some variables have placeholder values that need to be replaced
) else (
    echo [ERROR] Some critical variables are not set
)

echo.
echo 📖 Next Steps:
echo 1. Review any [ERROR] or [WARN] items above
echo 2. Update placeholder values with real credentials
echo 3. Run: .\start_incident_system.bat
echo 4. Monitor logs: Get-Content logs\app.log -Tail 10

echo.
echo 📚 For detailed setup instructions, see: API_KEYS_SETUP_GUIDE.md

pause