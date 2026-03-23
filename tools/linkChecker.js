// linkChecker.js
const puppeteer = require('puppeteer');

const pagesToCheck = [
  'http://localhost:5173/',                   // Home
  'http://localhost:5173/dashboard',          // Freight Dashboard
  'http://localhost:5173/ai-bots',            // Bots List
  'http://localhost:5173/ai-bots/freight',    // AI Freight Broker
  'http://localhost:5173/emails',             // Emails Page
  'http://localhost:5173/shipments',          // Shipments Page
  'http://localhost:5173/expenses',           // Expenses Page
  'http://localhost:5173/platform-expenses',  // Platform Expenses
  'http://localhost:5173/map?shipment_id=1',  // Map Page for Shipment #1
];

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  for (const url of pagesToCheck) {
    try {
      const response = await page.goto(url, { waitUntil: 'networkidle2', timeout: 10000 });
      const status = response.status();
      const pageTitle = await page.title();
      console.log(`✅ ${status} - ${url} - Title: ${pageTitle}`);
    } catch (error) {
      console.error(`❌ Error accessing ${url}:`, error.message);
    }
  }

  await browser.close();
})();
