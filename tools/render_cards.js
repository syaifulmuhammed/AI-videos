// Renders each card in tools/cards.html to a PNG frame sequence.
// Usage: node tools/render_cards.js <reel_dir>
// Output: <reel_dir>/build/cards/<id>/0001.png ... and <reel_dir>/stills/<id>.png
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

async function main() {
  const reelDir = path.resolve(process.argv[2] || ".");
  const data = JSON.parse(fs.readFileSync(path.join(reelDir, "data.json"), "utf8"));
  const timeline = JSON.parse(fs.readFileSync(path.join(reelDir, "timeline.json"), "utf8"));
  const fps = timeline.fps;
  const cardIds = [...new Set(timeline.beats.map(b => b.card).filter(Boolean))];

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: timeline.width, height: timeline.height } });
  await page.goto("file://" + path.join(__dirname, "cards.html"));
  await page.evaluate(() => document.fonts.ready);

  const manifest = {};
  fs.mkdirSync(path.join(reelDir, "stills"), { recursive: true });
  for (const id of cardIds) {
    const outDir = path.join(reelDir, "build", "cards", id);
    fs.rmSync(outDir, { recursive: true, force: true });
    fs.mkdirSync(outDir, { recursive: true });
    const info = await page.evaluate(([id, d]) => window.setupCard(id, d), [id, data]);
    const frames = Math.ceil(info.animEnd * fps) + 1;
    for (let f = 0; f < frames; f++) {
      await page.evaluate(t => window.renderAt(t), f / fps);
      await page.screenshot({
        path: path.join(outDir, String(f + 1).padStart(4, "0") + ".png"),
        omitBackground: info.layout === "overlay",
      });
    }
    fs.copyFileSync(path.join(outDir, String(frames).padStart(4, "0") + ".png"), path.join(reelDir, "stills", id + ".png"));
    manifest[id] = { layout: info.layout, frames };
    console.log(`${id}: ${frames} frames (${info.layout})`);
  }
  fs.writeFileSync(path.join(reelDir, "build", "cards", "manifest.json"), JSON.stringify(manifest, null, 2));
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
