import fs from "node:fs";
import vm from "node:vm";
import assert from "node:assert/strict";

const root = "site";
const records = JSON.parse(fs.readFileSync(root + "/data/launches.json", "utf8"));
assert.ok(Array.isArray(records.records) && records.records.length >= 65, "original menu records missing");
assert.equal(new Set(records.records.map(r => r.id)).size, records.records.length, "duplicate menu IDs");
const validImage = /^assets\/uploads\/[a-zA-Z0-9_-]+\.(?:webp|png|jpe?g)$/;
for (const rec of records.records) {
  assert.ok(rec.id && rec.product && rec.country && rec.brand, "missing required record fields");
  assert.ok(!rec.image || validImage.test(rec.image), "unsafe local image path: " + rec.image);
}
for (const filename of ["index.html","admin.html"]) {
  const html=fs.readFileSync(root + "/" + filename,"utf8");
  const blocks=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script\s*>/g)];
  assert.ok(blocks.length, "missing JavaScript: "+filename);
  for (let i=0;i<blocks.length;i++) {
    new vm.Script(blocks[i][1],{filename:filename+"#script"+i});
  }
  console.log("JS syntax valid:",filename,blocks.length,"scripts");
}
const index=fs.readFileSync(root+"/index.html","utf8");
assert.ok(index.includes("data/launches.json"), "Homepage must load editable data");
assert.ok(index.includes("admin.html"), "Admin link not found");
assert.ok(!/(?<!\$)\$\(['"][^'"]+['"]\)\.forEach\(/.test(index), "querySelector result cannot be iterated; use $ (querySelectorAll)");
assert.ok(!/(?<!\$)\$\(['"][^'"]+['"]\)\.map\(/.test(index), "querySelector result cannot use map; use $ (querySelectorAll)");
assert.ok(index.includes("id=\"view-monitoring\""), "Workbook monitoring view missing");
assert.ok(index.includes("function renderMonitoring()"), "Workbook cards renderer missing");

const admin=fs.readFileSync(root+"/admin.html","utf8");
assert.ok(admin.includes("https://api.github.com") && admin.includes("site/data/launches.json"),"Admin editor not wired to GitHub");
assert.ok(!/localStorage\s*\.|sessionStorage\s*\./.test(admin),"Admin must not persist credentials");
console.log("PASS", records.records.length,"menu records; admin photo editor present");
