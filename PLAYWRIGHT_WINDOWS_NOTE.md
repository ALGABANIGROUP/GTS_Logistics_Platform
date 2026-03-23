# Playwright Windows Permissions Note

**Important for Windows users:**

To run Playwright-based frontend integration tests (such as `test_frontend_integration.py`), you must launch your terminal as **Administrator**. This is required so Playwright can create the necessary named pipes and browser helper processes.

## Steps
1. **Open PowerShell or CMD as Administrator:**
   - Right-click on the Start menu > Windows PowerShell (Admin) or Command Prompt (Admin).
2. **Navigate to your project directory:**
   ```
   cd C:\Users\enjoy\dev\GTS
   ```
3. **Activate your virtual environment (if needed):**
   ```
   .\.venv\Scripts\activate
   ```
4. **Run the test:**
   ```
   python -m pytest backend/tests/test_frontend_integration.py
   ```

If you see `PermissionError [WinError 5]` or Playwright cannot create named pipes, make sure you are running as Administrator.

---
For more details, see the Playwright documentation: https://playwright.dev/python/docs/intro
