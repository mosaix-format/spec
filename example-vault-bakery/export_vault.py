#!/usr/bin/env python3
"""
export_vault.py — writes the Forno Vialetto example vault (.md files) from vault-data.js,
then runs the reference checker on it.

    python export_vault.py            # writes ./vault/ and mosaix-bakery-vault.zip next to this file
    python export_vault.py out_dir    # writes elsewhere (no zip)

vault-data.js is the single source of truth.
Standard library only.
"""
import json, re, sys, subprocess, zipfile, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "vault-data.js"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "vault"


def load_notes():
    text = SRC.read_text(encoding="utf-8")
    start = text.index("[", text.index("window.MOSAIX_VAULT"))
    end = text.rindex("]") + 1
    js = text[start:end]
    # strip JS comments, quote bare keys, remove trailing commas → JSON
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    js = re.sub(r"(?m)^\s*//.*$", "", js)
    strings = []
    def _stash(m):
        strings.append(m.group(0))
        return f"\x00{len(strings) - 1}\x00"
    js = re.sub(r'"(?:[^"\\]|\\.)*"', _stash, js)
    js = re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', js)
    js = re.sub(r",\s*([}\]])", r"\1", js)
    js = re.sub(r"\x00(\d+)\x00", lambda m: strings[int(m.group(1))], js)
    return json.loads(js)


def yaml_list(items):
    if not items:
        return "[]"
    def q(x):
        return f'"{x}"' if any(c in x for c in ",:#") else x
    return "[" + ", ".join(q(i) for i in items) + "]"


def frontmatter(n):
    lines = ["---", f"title: {n['title']}", f"type: {n['type']}", f"updated: {n['updated']}",
             f"tags: {yaml_list(n['tags'])}", f"status: {n['status']}",
             f'summary: "{n["summary"]}"', f"keywords: {yaml_list(n['keywords'])}"]
    if n.get("entities"):
        lines.append("entities:")
        lines += [f"  - {{name: {e['name']}, type: {e['type']}}}" for e in n["entities"]]
    else:
        lines.append("entities: []")
    if n.get("relations"):
        lines.append("relations:")
        lines += [f"  - {{from: {r['from']}, type: {r['type']}, to: {r['to']}}}" for r in n["relations"]]
    else:
        lines.append("relations: []")
    lines.append(f"links: {yaml_list(n['links'])}")
    if n.get("fragments"):
        lines.append(f"fragments: {yaml_list(n['fragments'])}")
    if n.get("pool"):
        lines.append(f"pool: {yaml_list(n['pool'])}")
    if n.get("layout"):
        lay = n["layout"]
        lines.append("layout:")
        if "cover" in lay:
            c = lay["cover"]
            lines.append(f"  cover: {{title: {c['title']}, subtitle: {c['subtitle']}, date: {c['date']}}}")
        if "page" in lay:
            lines.append(f"  page: {lay['page']}")
        if "sections" in lay:
            lines.append("  sections:")
            for sec in lay["sections"]:
                lines.append(f"    - {{title: {sec['title']}, fragments: {yaml_list(sec['fragments'])}}}")
        if "show" in lay:
            lines.append(f"  show: {yaml_list(lay['show'])}")
    if n["path"].startswith("_meta/Conventions"):
        lines.append('mosaix: "1.0"')
        lines.append("folders: {01-People: who the partners are, 02-Products: what the bakery sells, 03-Suppliers: who provides ingredients, 04-Market: where they sell and who competes, 05-Operations: how the bakery runs, 06-Decisions: choices that shape the business}")
        lines.append("reliability: {key: status, values: [sourced, to-confirm, superseded]}")
        lines.append("domain_keys: {season: [spring, summer, autumn, winter], channel: [shop, market, wholesale]}")
        lines.append("entity_types: [recipe]")
        lines.append("relation_types: [supplies, owns, sells at, competes with, depends on]")
        lines.append("maintainers:")
        lines.append("  - {name: E. Nordgren, area: products}")
        lines.append("  - {name: M. Trevisan, area: operations}")
    lines.append(f"rev: {n['rev']}")
    lines.append("---")
    return "\n".join(lines)


def main():
    notes = load_notes()
    OUT.mkdir(parents=True, exist_ok=True)
    for n in notes:
        p = OUT / n["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        body = n["body"].replace("\\n", "\n")
        p.write_text(frontmatter(n) + "\n\n# " + n["title"] + "\n\n" + body + "\n", encoding="utf-8")
    print(f"wrote {len(notes)} notes to {OUT}")
    checker = HERE.parent / "audit_reference.py"
    rc = 0
    if checker.exists():
        rc = subprocess.run([sys.executable, str(checker), str(OUT), "--verbose"]).returncode
    if len(sys.argv) == 1 and rc == 0:
        zpath = HERE / "mosaix-bakery-vault.zip"

        def hexcolor(h):
            return {"a": 1, "rgb": int(h.lstrip("#"), 16)}

        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(OUT.rglob("*.md")):
                z.write(p, "mosaix-bakery-vault/" + p.relative_to(OUT).as_posix())
            readme = ("Mosaix example vault — Forno Vialetto, a fictional artisan bakery.\n"
                      "Open the folder in Obsidian or any Markdown editor; start from Home.md.\n"
                      "Check it: python audit_reference.py mosaix-bakery-vault\n"
                      "Everything in this vault is invented. CC BY-SA 4.0.\n"
                      "https://mosaixformat.org\n")
            z.writestr("mosaix-bakery-vault/README.txt", readme)

            obsidian = "mosaix-bakery-vault/.obsidian/"
            z.writestr(obsidian + "app.json", json.dumps({
                "readableLineLength": True,
                "showFrontmatter": True,
                "newFileLocation": "current",
                "useMarkdownLinks": False,
                "attachmentFolderPath": "assets",
            }, indent=2))
            z.writestr(obsidian + "appearance.json", json.dumps({
                "baseFontSize": 16,
            }, indent=2))
            z.writestr(obsidian + "core-plugins.json", json.dumps({
                "file-explorer": True, "global-search": True, "switcher": True, "graph": True,
                "backlink": True, "outgoing-link": True, "tag-pane": True, "properties": True,
                "page-preview": True, "outline": True, "word-count": True,
                "file-recovery": True,
            }, indent=2))
            z.writestr(obsidian + "graph.json", json.dumps({
                "colorGroups": [
                    {"query": '["type":moc]', "color": hexcolor("#c9a227")},
                    {"query": '["type":document]', "color": hexcolor("#14130f")},
                    {"query": '["type":synthesis]', "color": hexcolor("#7d786c")},
                    {"query": "path:_meta", "color": hexcolor("#9b3b2a")},
                ],
                "showTags": False,
                "showAttachments": False,
                "showOrphans": True,
            }, indent=2))
        print(f"zipped -> {zpath} ({zpath.stat().st_size} bytes)")
        site = HERE.parent / "site"
        if site.is_dir():
            shutil.copy2(zpath, site / zpath.name)
            print(f"copied {zpath.name} to site/")
    elif len(sys.argv) == 1:
        print("not zipped: vault is not conformant")


if __name__ == "__main__":
    main()
