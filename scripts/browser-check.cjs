// Run with Playwright available in NODE_PATH. No browser code is shipped to the site.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const origin = process.env.BOXMELLO_QA_ORIGIN || 'http://127.0.0.1:8765';
const root = path.resolve(__dirname, '..');
const sitemap = fs.readFileSync(path.join(root, 'docs/sitemap.xml'), 'utf8');
const routes = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => new URL(m[1]).pathname);
const screenshotDir = path.join(root, 'artifacts/locales');
fs.mkdirSync(screenshotDir, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true, channel: process.env.BOXMELLO_QA_CHANNEL || 'chrome' });
  const failures = [], summaries = [];
  await Promise.all([320, 768, 1440].map(async width => {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    for (const route of routes) {
      const response = await page.goto(origin + route, { waitUntil: 'load' });
      const state = await page.evaluate(() => ({
        width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
        lang: document.documentElement.lang, dir: document.documentElement.dir,
        h1: document.querySelector('h1')?.textContent,
        images: [...document.images].every(i => i.complete && i.naturalWidth > 0),
        externalResources: performance.getEntriesByType('resource').filter(r => new URL(r.name).host !== location.host).map(r => r.name),
      }));
      if (response.status() !== 200 || state.scrollWidth > width || !state.h1 || !state.images || state.externalResources.length) failures.push({ route, width, status: response.status(), ...state });
      if (width === 320 && route.endsWith('/privacy/')) {
        await page.screenshot({ path: path.join(screenshotDir, state.lang + '-privacy-mobile.png') });
      }
      if (width === 768 && !route.match(/\/(privacy|terms|data-deletion|licenses)\/$/)) {
        await page.screenshot({ path: path.join(screenshotDir, state.lang + '-home-tablet.png') });
        await page.locator('.language-picker summary').click();
        const menu = await page.locator('.language-menu').boundingBox();
        if (!menu || menu.x < -1 || menu.x + menu.width > width + 1) failures.push({ route, width, languageMenu: menu });
        const current = page.locator('.language-menu a[aria-current="page"]');
        if (await current.count() !== 1) failures.push({ route, width, languageSelection: 'missing or duplicate' });
        await page.locator('.language-picker summary').click();
        const faq = page.locator('.faq-item').first();
        await faq.locator('summary').click();
        if (await faq.getAttribute('open') === null) failures.push({ route, width, faq: 'does not open' });
      }
    }
    summaries.push({ width, pages: routes.length });
    await page.close();
  }));
  await browser.close();
  const result = { origin, summaries, failures };
  fs.writeFileSync(path.join(root, 'artifacts/browser-check.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
  if (failures.length) process.exitCode = 1;
})().catch(error => { console.error(error); process.exitCode = 1; });
