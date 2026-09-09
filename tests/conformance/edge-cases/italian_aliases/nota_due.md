---
titolo: Nota Due — Alias Italiani
aggiornato: 2026-09-09
tags: [test, conformance, italian]
stato: ok
riassunto: "Seconda nota con frontmatter completamente in italiano: verifica mcp_entita con tipi azienda, documento ed evento, mcp_relazioni con alias da e a, e mcp_collegamenti verso nota_uno e Home."
parole_chiave: [alias, italiano, frontmatter, nota, collegamento, mosaix, conformance, test]
mcp_entita:
  - {nome: Meridian Industries, tipo: azienda}
  - {nome: Specifica Mosaix, tipo: documento}
  - {nome: Lancio v1.1, tipo: evento}
mcp_relazioni:
  - {da: Meridian Industries, tipo: collega, a: Andrea Fiorino}
mcp_collegamenti: [nota_uno, Home]
mcp_rev: 000000000000
---

# Nota Due

Seconda nota di test con frontmatter in italiano — verifica alias item e value. ✅

Vedi [[nota_uno]] e [[Home]].
