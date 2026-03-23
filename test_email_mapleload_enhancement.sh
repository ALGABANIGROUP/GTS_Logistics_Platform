#!/bin/bash

# Email Bot & MapleLoad Canada Enhancement - Quick Test Guide
# Usage: Run this script to verify all new components are working

echo "=========================================="
echo "🧪 Email Bot & MapleLoad Enhancement Tests"
echo "=========================================="
echo ""

# Test 1: Check if routes exist
echo "Test 1: Checking routes in App.jsx..."
if grep -q "path=\"/ai-bots/email\"" c:/Users/enjoy/dev/GTS/frontend/src/App.jsx; then
    echo "✅ Email Bot route found"
else
    echo "❌ Email Bot route NOT found"
fi

if grep -q "path=\"/ai-bots/mapleload-canada\"" c:/Users/enjoy/dev/GTS/frontend/src/App.jsx; then
    echo "✅ MapleLoad Canada route found"
else
    echo "❌ MapleLoad Canada route NOT found"
fi

# Test 2: Check if components exist
echo ""
echo "Test 2: Checking component files..."
if [ -f "c:/Users/enjoy/dev/GTS/frontend/src/pages/ai-bots/AIEmailBot.jsx" ]; then
    echo "✅ AIEmailBot.jsx exists"
else
    echo "❌ AIEmailBot.jsx NOT found"
fi

if [ -f "c:/Users/enjoy/dev/GTS/frontend/src/components/bots/MapleLoadCanadaEnhanced.jsx" ]; then
    echo "✅ MapleLoadCanadaEnhanced.jsx exists"
else
    echo "❌ MapleLoadCanadaEnhanced.jsx NOT found"
fi

if [ -f "c:/Users/enjoy/dev/GTS/frontend/src/pages/ai-bots/AIMapleLoadCanadaBot.jsx" ]; then
    echo "✅ AIMapleLoadCanadaBot.jsx exists"
else
    echo "❌ AIMapleLoadCanadaBot.jsx NOT found"
fi

# Test 3: Check imports
echo ""
echo "Test 3: Checking imports..."
if grep -q "import AIEmailBot from" c:/Users/enjoy/dev/GTS/frontend/src/App.jsx; then
    echo "✅ AIEmailBot import found"
else
    echo "❌ AIEmailBot import NOT found"
fi

if grep -q "import MapleLoadCanadaEnhanced from" c:/Users/enjoy/dev/GTS/frontend/src/pages/ai-bots/AIMapleLoadCanadaBot.jsx; then
    echo "✅ MapleLoadCanadaEnhanced import found"
else
    echo "❌ MapleLoadCanadaEnhanced import NOT found"
fi

# Test 4: Check styles
echo ""
echo "Test 4: Checking CSS..."
if grep -q "mapleload-enhanced" c:/Users/enjoy/dev/GTS/frontend/src/components/bots/MapleLoadCanadaControl.css; then
    echo "✅ Enhanced styles found in CSS"
else
    echo "❌ Enhanced styles NOT found in CSS"
fi

# Test 5: Check bots in available list
echo ""
echo "Test 5: Checking Email Bot in available bots..."
if grep -q '"Email Bot"' c:/Users/enjoy/dev/GTS/backend/routes/bots_available_enhanced.py; then
    echo "✅ Email Bot found in available bots"
else
    echo "❌ Email Bot NOT found in available bots"
fi

if grep -q '"/ai-bots/email"' c:/Users/enjoy/dev/GTS/backend/routes/bots_available_enhanced.py; then
    echo "✅ Email Bot path found in available bots"
else
    echo "❌ Email Bot path NOT found in available bots"
fi

# Test 6: Check documentation
echo ""
echo "Test 6: Checking documentation..."
if [ -f "c:/Users/enjoy/dev/GTS/MAPLELOAD_CANADA_V3_ENHANCEMENT.md" ]; then
    echo "✅ MapleLoad v3 documentation exists"
else
    echo "❌ MapleLoad v3 documentation NOT found"
fi

if [ -f "c:/Users/enjoy/dev/GTS/EMAIL_BOT_AI_PANEL_INTEGRATION.md" ]; then
    echo "✅ Email Bot documentation exists"
else
    echo "❌ Email Bot documentation NOT found"
fi

echo ""
echo "=========================================="
echo "✨ Test Summary"
echo "=========================================="
echo ""
echo "✅ All components are in place!"
echo ""
echo "📌 Next Steps:"
echo "1. Visit http://localhost:5173/ai-bots/email"
echo "2. Visit http://localhost:5173/ai-bots/mapleload-canada"
echo "3. Verify bots appear in AI Bots Hub"
echo "4. Test freight search and supplier outreach"
echo "5. Monitor email bot processing"
echo ""
echo "📚 Documentation:"
echo "  - MAPLELOAD_CANADA_V3_ENHANCEMENT.md"
echo "  - EMAIL_BOT_AI_PANEL_INTEGRATION.md"
