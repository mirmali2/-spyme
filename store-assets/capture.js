/**
 * Automated screenshot capture for App Store / Play Store.
 *
 * Renders /store-assets/screenshots.html via headless Chromium and saves
 * each .shot block as a PNG at full resolution.
 *
 * Usage:
 *   cd store-assets
 *   npm install puppeteer
 *   node capture.js
 *
 * Output:
 *   store-assets/output/01-live-view.png       (1290 x 2796)
 *   store-assets/output/02-multi-camera.png    (1290 x 2796)
 *   ... etc
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const SHOTS = [
  '01-live-view',
  '02-multi-camera',
  '03-fire-alarm',
  '04-theft-detection',
  '05-privacy',
];

(async () => {
  const outDir = path.join(__dirname, 'output');
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--font-render-hinting=none'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 3000, deviceScaleFactor: 1 });

  const url = 'file://' + path.resolve(__dirname, 'screenshots.html');
  console.log('Loading', url);
  await page.goto(url, { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 1500));  // let iframes settle

  const elements = await page.$$('.shot');
  console.log(`Found ${elements.length} screenshots to capture.`);

  for (let i = 0; i < elements.length; i++) {
    const out = path.join(outDir, `${SHOTS[i] || 'shot-' + (i+1)}.png`);
    await elements[i].screenshot({ path: out, omitBackground: false });
    console.log(`  ✓ ${out}`);
  }

  await browser.close();
  console.log('\nDone. Upload these to App Store Connect / Play Console.');
  console.log('  iPhone 6.7"   → 1290 × 2796 ✓');
  console.log('  Google Play    → any of these works ✓');
})();
