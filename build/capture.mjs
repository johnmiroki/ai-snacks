// Snapshot what the browser makes of the page sources.
//
//   node build/capture.mjs
//
// The command index builds its cards with JavaScript. Crawlers that feed AI
// answers do not run JavaScript, so the cards are rendered here once and baked
// into the published file by build.py. This also renders the OG images.
//
// Only needed when a page source or an OG template changes. Set CHROMIUM_PATH
// to use a browser Playwright did not install itself.

import { chromium } from "playwright";
import { readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BUILD = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(BUILD);
const CS_SRC = join(BUILD, "claude-code-cheatsheet");
const CS_OUT = join(ROOT, "claude-code-cheatsheet");
const SK_SRC = join(BUILD, "claude-code-built-in-skills");
const SK_OUT = join(ROOT, "claude-code-built-in-skills");

const EXPECTED_COMMANDS = 143;
const EXPECTED_FLAGS = 57;

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
const page = await browser.newPage();

// ---------------------------------------------------------------- the page data

await page.setContent(await readFile(join(CS_SRC, "claude-code-commands.html"), "utf8"), {
  waitUntil: "load",
});

const captured = await page.evaluate(() => {
  const t = (el) => (el ? el.textContent.trim() : null);

  const sections = [...document.querySelectorAll("#sections section")].map((s) => ({
    id: s.id,
    title: t(s.querySelector("h2")),
    blurb: t(s.querySelector(".sec-head p")),
    commands: [...s.querySelectorAll(".cmd")].map((c) => {
      const link = c.querySelector("a.cmd-name");
      const tags = [...c.querySelectorAll(".tags .tag")];
      return {
        id: c.id,
        name: c.dataset.name,
        family: c.dataset.fam,
        description: t(c.querySelector(".cmd-desc")),
        argument: t(c.querySelector(".cmd-arg")),
        aliases: tags
          .filter((x) => x.classList.contains("alias") || !x.className.replace("tag", "").trim())
          .map((x) => t(x)),
        conditional: tags.some((x) => x.classList.contains("gate")),
        registeredInCli: c.dataset.unreg !== "1",
        unregisteredReason:
          c.dataset.unreg === "1" ? (c.querySelector(".tag.unreg") || {}).title || null : null,
        docs: link ? link.href : null,
      };
    }),
  }));

  const flags = [...document.querySelectorAll("#flagbody tr")].map((r) => ({
    flag: t(r.querySelector(".f")),
    description: t(r.querySelector(".d")),
  }));

  return {
    extract: {
      sections,
      flags,
      totals: { commands: document.querySelectorAll(".cmd").length, flags: flags.length },
    },
    prerender: {
      sections: document.getElementById("sections").innerHTML,
      flagbody: document.getElementById("flagbody").innerHTML,
      flagcount: document.getElementById("flagcount").textContent,
      stats: Object.fromEntries(
        ["native", "skill", "cli", "hidden", "flags", "linked", "unreg"].map((k) => [
          k,
          document.getElementById("s-" + k).textContent,
        ])
      ),
      cardCount: document.querySelectorAll(".cmd").length,
      hiddenCount: [...document.querySelectorAll(".cmd")].filter(
        (c) => c.style.display === "none"
      ).length,
    },
    ids: [...document.querySelectorAll(".cmd")].map((c) => c.id),
  };
});

const { extract, prerender, ids } = captured;

if (extract.totals.commands !== EXPECTED_COMMANDS || extract.totals.flags !== EXPECTED_FLAGS) {
  throw new Error(
    `expected ${EXPECTED_COMMANDS} commands and ${EXPECTED_FLAGS} flags, ` +
      `got ${extract.totals.commands} and ${extract.totals.flags}`
  );
}
if (new Set(ids).size !== ids.length) {
  throw new Error("duplicate command anchors: " + ids.filter((v, i) => ids.indexOf(v) !== i));
}

await writeFile(join(CS_SRC, "extract.json"), JSON.stringify(extract, null, 2));
await writeFile(join(CS_SRC, "prerender.json"), JSON.stringify(prerender, null, 2));

// ---------------------------------------------------------------- the OG images

await page.setViewportSize({ width: 1200, height: 630 });

for (const [template, out] of [
  [join(BUILD, "og-hub.html"), join(ROOT, "og.png")],
  [join(CS_SRC, "og.html"), join(CS_OUT, "og.png")],
  [join(SK_SRC, "og.html"), join(SK_OUT, "og.png")],
]) {
  await page.setContent(await readFile(template, "utf8"), { waitUntil: "load" });
  await page.screenshot({ path: out, type: "png" });
}

await browser.close();

console.log(`  ${extract.totals.commands} commands, ${extract.totals.flags} flags, ` +
  `${prerender.hiddenCount} hidden by the default filter`);
console.log("  wrote extract.json, prerender.json, og.png, claude-code-cheatsheet/og.png, " +
  "claude-code-built-in-skills/og.png");
console.log("\nnow run: python3 build/build.py");
