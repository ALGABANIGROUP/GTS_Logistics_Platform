#!/bin/bash
# Environment Configuration Test Script
# Tests all critical environment variables for GTS Logistics

echo "🔧 Testing GTS Environment Configuration"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check environment variable
check_env_var() {
    local var_name=$1
    local var_value=$2
    local description=$3

    if [ -z "$var_value" ]; then
        echo -e "${RED}❌ $var_name: NOT SET - $description${NC}"
        return 1
    elif [[ "$var_value" == *"your"* ]] || [[ "$var_value" == *"YOUR"* ]]; then
        echo -e "${YELLOW}⚠️  $var_name: PLACEHOLDER VALUE - $description${NC}"
        return 2
    else
        echo -e "${GREEN}✅ $var_name: CONFIGURED${NC}"
        return 0
    fi
}

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs 2>/dev/null)
    echo "📄 Environment file loaded successfully"
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

echo ""
echo "🔍 Checking Database Configuration:"
check_env_var "DATABASE_URL" "$DATABASE_URL" "PostgreSQL connection string"
check_env_var "DB_HOSTNAME" "$DB_HOSTNAME" "Database hostname"
check_env_var "DB_NAME" "$DB_NAME" "Database name"

echo ""
echo "📧 Checking Email Configuration:"
check_env_var "SMTP_HOST" "$SMTP_HOST" "SMTP server hostname"
check_env_var "SMTP_USER" "$SMTP_USER" "SMTP username"
check_env_var "SMTP_PASSWORD" "$SMTP_PASSWORD" "SMTP password"

echo ""
echo "🚨 Checking Incident Response System:"
check_env_var "LOG_PATH" "$LOG_PATH" "Log file path"
check_env_var "ALERT_EMAIL" "$ALERT_EMAIL" "Alert notification email"
check_env_var "INCIDENT_RETENTION_DAYS" "$INCIDENT_RETENTION_DAYS" "Incident data retention"

echo ""
echo "🔑 Checking API Keys:"
check_env_var "OPENWEATHER_API_KEY" "$OPENWEATHER_API_KEY" "Weather service API key"
check_env_var "ALPHA_VANTAGE_KEY" "$ALPHA_VANTAGE_KEY" "Market data API key"
check_env_var "MARKETAUX_KEY" "$MARKETAUX_KEY" "News service API key"

echo ""
echo "📱 Checking Optional Services:"
check_env_var "SLACK_WEBHOOK_URL" "$SLACK_WEBHOOK_URL" "Slack notifications webhook"

echo ""
echo "📊 Configuration Summary:"
echo "========================"

# Count configured vs not configured
total_vars=0
configured_vars=0
placeholder_vars=0

# Check critical variables
critical_vars=("DATABASE_URL" "SMTP_HOST" "LOG_PATH" "ALERT_EMAIL")
for var in "${critical_vars[@]}"; do
    value=$(eval echo \$$var)
    ((total_vars++))
    if [ -n "$value" ] && [[ "$value" != *"your"* ]] && [[ "$value" != *"YOUR"* ]]; then
        ((configured_vars++))
    elif [ -n "$value" ]; then
        ((placeholder_vars++))
    fi
done

echo "Total Critical Variables: $total_vars"
echo "Properly Configured: $configured_vars"
echo "Placeholder Values: $placeholder_vars"

if [ $configured_vars -eq $total_vars ]; then
    echo -e "${GREEN}🎉 All critical variables are configured!${NC}"
elif [ $placeholder_vars -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Some variables have placeholder values that need to be replaced${NC}"
else
    echo -e "${RED}❌ Some critical variables are not set${NC}"
fi

echo ""
echo "📖 Next Steps:"
echo "1. Review any ❌ or ⚠️ items above"
echo "2. Update placeholder values with real credentials"
echo "3. Run: ./start_incident_system.sh"
echo "4. Monitor logs: tail -f /var/log/gts/monitor.log"

echo ""
echo "📚 For detailed setup instructions, see: API_KEYS_SETUP_GUIDE.md"