"""Regressione: l'indice e' chiaviato per path, non per stem.

`README` esiste in decine di cartelle. Indicizzando per stem, `_notes` teneva
solo l'ultimo file letto: le altre note sparivano da search/list_notes e un
path completo ne restituiva un'altra, in silenzio.

Eseguibile diretto (`python test_vault_index.py`) o con pytest.
"""
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mosaix_mcp.vault import VaultIndex  # noqa: E402


def _fm(title: str, extra: str = "") -> str:
    """Frontmatter conforme a §10: summary 120-240 char, 6-8 keyword, rev presente."""
    summary = (f"{title} e' una nota di prova usata dal test di regressione "
               f"sull'indice del vault Mosaix, abbastanza lunga da rispettare il "
               f"vincolo di lunghezza imposto dal controllo di conformita.")
    assert 120 <= len(summary) <= 240, len(summary)
    return (
        "---\n"
        f"title: {title}\n"
        "updated: 2026-09-12\n"
        "tags: [prova, indice]\n"
        f"summary: {summary}\n"
        "keywords: [prova, indice, vault, stem, path, regressione]\n"
        "rev: 1\n"
        + extra +
        "---\n"
    )


def _build(root: Path) -> None:
    files = {
        "a/README.md": "readme di A",
        "b/README.md": "readme di B",
        "c/README.md": "readme di C",
        "a/Home.md": "# Home\n\nmappa",
        "note/linker.md": "vedi [[target]] per i dettagli",
        "note/target.md": "il bersaglio",
        "note/doc.md": "documento composto",
        "_meta/Conventions.md": "convenzioni",
        "Open questions.md": "domande aperte",
    }
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        extra = ""
        if rel == "note/doc.md":
            extra = "type: document\nfragments: [frag_uno, frag_due]\n"
        p.write_text(_fm(Path(rel).stem, extra) + "\n" + body + "\n",
                     encoding="utf-8")
    for frag in ("frag_uno", "frag_due"):
        p = root / "note" / f"{frag}.md"
        p.write_text(_fm(frag) + f"\ncontenuto {frag}\n", encoding="utf-8")


def _check(name: str, cond: bool, detail: str = "") -> bool:
    print(f"  {'OK ' if cond else 'KO '} {name}" + (f"  — {detail}" if detail else ""))
    return cond


def test_index_is_keyed_by_path() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="mosaix-idx-"))
    try:
        _build(tmp)
        idx = VaultIndex(tmp)
        on_disk = len([p for p in tmp.rglob("*.md")])
        esiti = []

        esiti.append(_check(
            "ogni file e' una riga dell'indice",
            len(idx) == on_disk, f"{len(idx)} indicizzate / {on_disk} su disco"))

        a = idx.read_note("a/README.md")
        b = idx.read_note("b/README.md")
        c = idx.read_note("c/README.md")
        esiti.append(_check("read 'a/README.md' -> A", "readme di A" in a["body"]))
        esiti.append(_check("read 'b/README.md' -> B", "readme di B" in b["body"]))
        esiti.append(_check("read 'c/README.md' -> C", "readme di C" in c["body"]))

        try:
            idx.read_note("README")
            ambiguo = False
        except KeyError as exc:
            ambiguo = "Ambiguous" in str(exc)
        esiti.append(_check("stem ambiguo -> errore esplicito, non scelta a caso", ambiguo))

        percorsi = {r["path"] for r in idx.list_notes()}
        esiti.append(_check(
            "list_notes vede tutti e tre i README",
            {"a/README.md", "b/README.md", "c/README.md"} <= percorsi,
            f"{len(percorsi)} note listate"))

        esiti.append(_check(
            "search trova il corpo di c/README.md",
            any(r["path"] == "c/README.md"
                for r in idx.search("readme di C", field="body"))))

        comp = idx.compose("note/doc")
        esiti.append(_check("compose risolve i frammenti",
                            "contenuto frag_uno" in comp["composed_text"]))

        hist = idx.history("note/target")
        esiti.append(_check("history parte dalla nota giusta",
                            hist["path"] == "note/target.md"))

        mv = idx.move_note("note/target", "archivio/target")
        esiti.append(_check("move sposta il file",
                            (tmp / "archivio" / "target.md").exists()
                            and not (tmp / "note" / "target.md").exists(),
                            str(mv)))
        esiti.append(_check("move riscrive il wikilink entrante",
                            "[[target]]" in idx.read_note("note/linker.md")["body"]))
        esiti.append(_check("move lascia la vecchia chiave fuori indice",
                            idx._resolve_ref("archivio/target") is not None
                            and idx._resolve_ref("note/target") is None))

        rifiutato = False
        try:
            idx.delete_note("archivio/target")   # linker.md lo linka con [[target]]
        except ValueError as exc:
            rifiutato = "PERMISSION_DENIED" in str(exc)
        esiti.append(_check("delete con link entranti viene rifiutato", rifiutato))

        idx.delete_note("c/README.md", force=True)
        esiti.append(_check("delete force rimuove dal disco e dall'indice",
                            not (tmp / "c" / "README.md").exists()
                            and idx._resolve_ref("c/README.md") is None))
        esiti.append(_check("delete non tocca gli altri README",
                            "readme di A" in idx.read_note("a/README.md")["body"]))

        idx.write_note("nuova/nota.md", {
            "title": "Nuova", "updated": "2026-09-12", "tags": ["prova"],
            "summary": _fm("Nuova").split("summary: ")[1].split("\n")[0],
            "keywords": ["a", "b", "c", "d", "e", "f"], "rev": 1,
        }, "corpo uno\n")
        idx.write_note("nuova/nota.md", {
            "title": "Nuova", "updated": "2026-09-13", "tags": ["prova"],
            "summary": _fm("Nuova").split("summary: ")[1].split("\n")[0],
            "keywords": ["a", "b", "c", "d", "e", "f"], "rev": 2,
        }, "corpo due\n")
        catena = idx.history("nuova/nota")
        esiti.append(_check("write_note + supersede -> history con 2 versioni",
                            catena["chain_length"] == 2,
                            f"chain_length={catena['chain_length']}"))

        print(f"\n{sum(esiti)}/{len(esiti)} controlli passati")
        assert all(esiti), "regressione sull'indice"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    test_index_is_keyed_by_path()
