# 🧪 Manual Testing Guide - Email Bot & MapleLoad Canada v3

## Quick Manual Tests

### Test 1: Page Loading
**Email Bot**:
1. Open browser to `http://localhost:5173/ai-bots/email`
2. ✅ Page loads without errors
3. ✅ Header displays "Email Bot Processing System"
4. ✅ 4 stat cards visible (green, blue, yellow, red)
5. ✅ Tab navigation visible (Overview, Mappings, History, Performance)

**MapleLoad Canada**:
1. Open browser to `http://localhost:5173/ai-bots/mapleload-canada`
2. ✅ Page loads without errors
3. ✅ Header displays "MapleLoad Canada - Freight Search & Supplier Outreach"
4. ✅ 5 tabs visible (Freight Search, Supplier Outreach, Smart Matching, Analytics, History)
5. ✅ Search form visible in Freight Search tab

---

### Test 2: Email Bot Functionality

#### Overview Tab
- [ ] Stats cards display:
  - Total Processed: numeric value
  - Successful: numeric value with green
  - Pending: numeric value with yellow
  - Failed: numeric value with red
- [ ] Charts visible and render correctly
- [ ] Connection status shows "Live" with green indicator

#### Mappings Tab
- [ ] Table header shows: Email Pattern | Bot Name | Workflow | Status
- [ ] At least one mapping visible
- [ ] Status badge shows "Active"

#### History Tab
- [ ] History items display as cards
- [ ] Each card shows:
  - From email address
  - Subject line
  - Bot name
  - Status color (green/yellow/red)
  - Timestamp
- [ ] Clicking card shows detail modal
- [ ] Modal has close button (×)

#### Performance Tab
- [ ] Bar chart displays processing data
- [ ] Chart has 3 data series (Processed, Successful, Failed)
- [ ] Legend shows correctly

---

### Test 3: MapleLoad Canada Functionality

#### Freight Search Tab
**Search Form**:
- [ ] 6 input fields visible:
  1. Origin City (text)
  2. Destination City (text)
  3. Weight (number)
  4. Commodity Type (text)
  5. Pickup Date (date)
  6. Max Rate (number)
- [ ] Search button clickable
- [ ] All fields accept input

**Search Results**:
- [ ] After clicking search, 8 loads display
- [ ] Each load card shows:
  - Load ID (e.g., LOAD-001)
  - Rate in green
  - Origin → Destination with icon
  - Weight, commodity, dates
  - Posted by information
- [ ] Loads are selectable via checkbox
- [ ] Selection count updates

#### Supplier Outreach Tab
**Precondition**: Must select at least 1 load in Freight Search tab
- [ ] Message textarea visible for custom message
- [ ] 5 supplier cards display:
  1. TransCanada Logistics
  2. Maple Freight Solutions
  3. Northern Dispatch
  4. Canadian Carriers Network
  5. Express Logistics Canada
- [ ] Each supplier shows:
  - Name
  - Email address
  - Rate range (e.g., $1.50-$2.50/mile)
  - Capacity (trucks)
- [ ] Suppliers are selectable via checkbox
- [ ] Selection count updates
- [ ] "Send" button enabled when selections made

#### Smart Matching Tab
- [ ] 4 info cards visible:
  - 🎯 Accuracy (95% match accuracy)
  - ⚡ Speed (Real-time matching in seconds)
  - 💰 Optimization (Maximize profit margins)
  - 📈 Learning (Improves with every transaction)
- [ ] "Go to Supplier Outreach" button visible

#### Analytics Tab
- [ ] 4 stat cards visible:
  - Total Loads Searched
  - Average Match Score (92.5%)
  - Avg Rate Per Load ($1,844)
  - Delivery Success Rate (98.7%)

#### History Tab
- [ ] 3 history items display as cards
- [ ] Each card shows:
  - Icon (Clock/Send/CheckCircle)
  - Title
  - Description
  - Timestamp (e.g., "2 hours ago")

---

### Test 4: Responsive Design

#### Desktop (1920px)
- [ ] Multi-column grids visible
- [ ] All content fits without horizontal scroll
- [ ] Padding/margins look balanced

#### Tablet (768px)
- [ ] Grid adjusts to 2-3 columns
- [ ] Tab buttons wrap correctly
- [ ] Form fields stack reasonably

#### Mobile (375px)
- [ ] Single column layout
- [ ] Form fields full width
- [ ] Tab buttons horizontal scroll
- [ ] All text readable
- [ ] Touch targets large enough (44px+)

---

### Test 5: Interaction Testing

#### Email Bot
- [ ] Tab switching works smoothly
- [ ] Modal opens and closes correctly
- [ ] Hover effects visible on cards

#### MapleLoad Canada
- [ ] Checkboxes toggle selection state
- [ ] Checkboxes update count summary
- [ ] Tab switching smooth
- [ ] Form inputs accept text/numbers
- [ ] Buttons have hover effects
- [ ] Buttons are disabled when appropriate

---

### Test 6: Visual Design

#### Color Scheme
- [ ] Dark navy background (#0f1419)
- [ ] Pink/purple accents (#ec4899, #d946ef)
- [ ] Green for success indicators
- [ ] Red for failure indicators
- [ ] Blue for info elements
- [ ] Yellow for pending states

#### Typography
- [ ] Headers are larger/bolder
- [ ] Body text readable (14-16px)
- [ ] Good contrast ratio (white on dark)
- [ ] Font stack appropriate

#### Spacing
- [ ] Consistent padding around elements
- [ ] Good whitespace between sections
- [ ] Grid gaps visible and balanced

#### Icons
- [ ] Lucide icons visible and sized correctly
- [ ] Icons have appropriate colors
- [ ] Icons align with text properly

---

### Test 7: Error Handling

#### Search with Empty Fields
- [ ] Alert displayed if required fields missing
- [ ] Message is clear: "Please enter origin and destination"

#### Modal Detail View
- [ ] Modal displays without layout issues
- [ ] Content readable and complete
- [ ] Close button works (×)
- [ ] Click outside doesn't close (if applicable)

---

### Test 8: Browser Compatibility

Test on multiple browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Edge

Check for:
- [ ] No console errors
- [ ] Styling renders correctly
- [ ] Animations smooth
- [ ] Forms work properly

---

### Test 9: Performance

**Network Tab** (DevTools):
- [ ] Components load in <1 second
- [ ] No large unoptimized images
- [ ] CSS properly bundled

**Console** (DevTools):
- [ ] No JavaScript errors
- [ ] No warnings about missing dependencies
- [ ] No React warnings

**Performance** (DevTools):
- [ ] 60fps animations
- [ ] <100ms input response time
- [ ] No memory leaks (check overtime)

---

## Automated Test Script

```bash
#!/bin/bash
# Quick verification script

echo "Testing Email Bot component..."
grep -q "AIEmailBot" frontend/src/App.jsx && echo "✅ Import exists" || echo "❌ Import missing"
grep -q "/ai-bots/email" frontend/src/App.jsx && echo "✅ Route exists" || echo "❌ Route missing"
test -f "frontend/src/pages/ai-bots/AIEmailBot.jsx" && echo "✅ Component file exists" || echo "❌ File missing"

echo ""
echo "Testing MapleLoad Canada component..."
grep -q "MapleLoadCanadaEnhanced" frontend/src/pages/ai-bots/AIMapleLoadCanadaBot.jsx && echo "✅ Import updated" || echo "❌ Import not updated"
test -f "frontend/src/components/bots/MapleLoadCanadaEnhanced.jsx" && echo "✅ Component file exists" || echo "❌ File missing"

echo ""
echo "Testing CSS..."
grep -q "mapleload-enhanced" frontend/src/components/bots/MapleLoadCanadaControl.css && echo "✅ Styles added" || echo "❌ Styles missing"

echo ""
echo "Testing documentation..."
test -f "MAPLELOAD_CANADA_V3_ENHANCEMENT.md" && echo "✅ MapleLoad docs exist" || echo "❌ Docs missing"
test -f "EMAIL_BOT_AI_PANEL_INTEGRATION.md" && echo "✅ Email bot docs exist" || echo "❌ Docs missing"

echo ""
echo "✨ Verification complete!"
```

---

## Troubleshooting

### Issue: Page Won't Load
**Solution**:
1. Check browser console (F12) for errors
2. Verify `http://localhost:5173` is running
3. Try hard refresh (Ctrl+Shift+R)
4. Check network tab for failed requests

### Issue: Components Look Wrong
**Solution**:
1. Clear browser cache
2. Check DevTools - zoom at 100%
3. Verify CSS file loaded (Network tab)
4. Check window width (responsive test)

### Issue: Features Not Working
**Solution**:
1. Check browser console for JavaScript errors
2. Verify no typos in input values
3. Check if API endpoints would be called (Network tab)
4. Verify form validation messages

---

## Pass Criteria

All tests pass when:
- ✅ All components load without errors
- ✅ All interactive elements work
- ✅ Responsive design works at all breakpoints
- ✅ Visual design matches specification
- ✅ No console errors or warnings
- ✅ Performance is acceptable
- ✅ Accessibility is good (keyboard nav, contrast)

---

**Test Date**: ____________  
**Tested By**: ____________  
**Pass/Fail**: ____________  

---

## Next Steps After Testing
1. Document any issues found
2. Create bug reports for any failures
3. Verify backend API readiness
4. Schedule deployment planning meeting
5. Prepare user training materials
6. Set up monitoring/alerting
7. Plan phased rollout strategy
