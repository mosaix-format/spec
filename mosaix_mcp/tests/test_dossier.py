"""Dossier (§6.1): il server legge la mappa `dossier` in stile blocco e in stile flow con gli alias italiani
(come la scrive vault-mcp), risolve le note come `members` + `added` - `excluded`, e il controllo segnala un
dossier senza criterio, un'esclusione violata e un dossier vecchio.

Usa i vault di prova della suite di conformita' (`tests/conformance/edge-cases/dossier_*`).
Eseguibile diretto (`python test_dossier.py`) o con pytest.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from mosaix_mcp.vault import VaultIndex  # noqa: E402

EDGE = ROOT / "tests" / "conformance" / "edge-cases"


def test_dossier_valido():
    v = VaultIndex(EDGE / "dossier_valid")
    ds = {d["title"]: d for d in v.list_dossiers()}
    assert set(ds) == {"Fragments by criterion", "Frammenti per criterio"}
    it = ds["Frammenti per criterio"]
    assert it["kind"] == "tema" and it["origin"] == "model"
    assert "virgole, punti: e parentesi" in it["criterion"]
    en = v.read_dossier("Fragments by criterion")
    # frag2 e' escluso a mano: resta fuori anche se il criterio lo raccoglie
    assert [n["stem"] for n in en["notes"]] == ["frag1", "frag3"] and en["excluded"] == ["frag2"]
    assert not en["stale"]
    assert v.compose("Fragments by criterion")["fragments"] == ["frag1.md", "frag3.md"]
    r = v.check()
    assert r["errors"] == [] and r["warnings"] == [], r


def test_dossier_rotto():
    v = VaultIndex(EDGE / "dossier_broken")
    r = v.check()
    assert sorted({e["id"] for e in r["errors"]}) == ["E016", "E017"], r
    assert sorted({w["id"] for w in r["warnings"]}) == ["W010", "W011"], r


if __name__ == "__main__":
    test_dossier_valido()
    test_dossier_rotto()
    print("ok")
