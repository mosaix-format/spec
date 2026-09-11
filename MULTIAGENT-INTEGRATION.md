# Multi-Agent Integration Guide

**Mosaix Format v1.2.0 — Non-normative**

This document describes how AI agents and multi-agent systems interact with Mosaix vaults through the MCP server interface. It is non-normative: nothing here adds to or modifies the specification. It records patterns observed in production deployments and codifies the conventions that make those patterns work reliably.

---

## 1. Architectural position

A Mosaix vault is persistent working memory for agents. It sits between the volatile, session-scoped context window and the slow, batch-oriented external knowledge base, filling a role that neither can:

**In-context memory** (system prompt, conversation history, scratchpad) is fast and fully available to the model, but it vanishes when the session ends and is bounded by the context window. An agent cannot build knowledge that outlasts a single conversation.

**Vector stores and retrieval databases** hold long-lived knowledge, but they are optimised for similarity search over embeddings, not for structured, self-describing records with typed entities, declared relations, and revision tracking. A vector store retrieves passages; it does not know what a note claims, who wrote it, when the fact was true, or whether the note contradicts another.

**A Mosaix vault** is the middle layer. Every note is an atomic, self-describing unit with a stable identity (`id`), a revision hash (`rev`), typed entities and relations, a reliability marker, and a summary written for a reader — human or machine — who has not opened the note. Notes survive sessions, carry provenance (`origin`, `as_of`), and resolve contradictions explicitly (R6) rather than silently overwriting. The vault is readable by any Markdown tool, hostable in Obsidian, versionable in Git, and composable into longer documents (§6) without duplicating content.

The **MCP server** is the sole programmatic access point. Agents do not read or write vault files directly. The server enforces conformance (§10) on every write, resolves aliases (§3.1), handles ULID id-first link resolution (§3.1), and presents notes in a form optimised for LLM consumption — with housekeeping metadata stripped from the output to avoid polluting the context window.

This separation — vault as persistent structured memory, MCP server as gatekeeper — means that an agent can be swapped, upgraded, or run in parallel without risking vault integrity. The vault's rules are enforced at the boundary, not inside the agent.

---

## 2. The MCP tool surface

The reference MCP server exposes six tools over JSON-RPC 2.0. These tools are the complete interface for agent interaction with a vault. No direct filesystem access is required or recommended.

| Tool | Input | Output | Purpose |
|------|-------|--------|---------|
| `read_note` | `path` (string) | Note body with frontmatter, **stripped** of `id`, `rev`, `status`, `updated`, and `mosaix` keys | Read a single note, ready for LLM injection |
| `search` | `query` (string), optional `limit` (int) | Ranked list of `{path, summary, score}` | Full-text search across the vault |
| `list_notes` | Optional `folder` (string), optional `tag` (string) | Array of `{path, title, updated, tags}` | Enumerate notes, optionally filtered |
| `write_note` | `path` (string), `frontmatter` (object), `body` (string) | `{path, rev, created}` | Create or update a note; validates against §10 before persisting |
| `move_note` | `from` (string), `to` (string) | `{from, to, updated_refs}` | Move a note, updating all incoming wikilinks |
| `delete_note` | `path` (string) | `{path, deleted}` | Remove a note; warns if incoming links exist |

### Stratification rule

When `read_note` returns a note, it **strips** five keys from the frontmatter before returning:

- **`id`** — the ULID is an internal stable identifier; it is never useful to the model as content.
- **`rev`** — the revision hash is a staleness-detection mechanism, not information.
- **`status`** — reliability markers are vault-internal bookkeeping.
- **`updated`** — the last-edit date is metadata about the note, not about the subject.
- **`mosaix`** — the format marker itself.

What remains — `title`, `tags`, `question`, `summary`, `keywords`, `entities`, `relations`, `links`, `origin`, `as_of` — is the semantic content of the note: what it says, what it connects to, and where the knowledge comes from. This is what belongs in a prompt. The stripped keys are still available through `list_notes` for orchestration and staleness checks; they are excluded from `read_note` because injecting them into an LLM context wastes tokens on information the model cannot act on and may hallucinate about.

---

## 3. Multi-vault orchestration patterns

Production deployments commonly maintain separate vaults for separate knowledge domains — one for product documentation, one for market intelligence, one for internal processes. Three patterns have emerged for orchestrating agents across multiple vaults.

### Pattern A: Router + Vault Workers

A **router agent** receives the user's request, determines which vault(s) are relevant, and dispatches to **vault worker agents**, each connected to a single vault via its own MCP server instance. The router merges results and resolves cross-vault references.

```
User → Router Agent → Vault Worker A (product vault)
                    → Vault Worker B (market vault)
                    → Vault Worker C (process vault)
       ← merged response ←
```

**When to use:** The domains are clearly separable. A question almost always maps to one vault, with occasional cross-vault joins. The router is lightweight — it classifies the query and fans out.

**Trade-off:** The router must know the scope of each vault. If vault boundaries shift, the router's classification logic must be updated. Cross-vault entity resolution (Pattern C) is the router's responsibility.

### Pattern B: Vault Federation

A single **federation server** exposes one unified MCP interface backed by multiple vaults. The server resolves `search` queries across all vaults, prefixes paths with vault identifiers, and enforces per-vault write permissions. The agent sees one logical vault.

```
User → Agent → Federation Server → Vault A
                                  → Vault B
                                  → Vault C
```

**When to use:** The agent should not need to know which vault a note lives in. The federation server handles routing transparently. Useful when vaults share entity types and the same taxonomy, or when a single agent needs to read broadly and write narrowly.

**Trade-off:** The federation server is more complex. It must handle path collisions (two vaults may have a note with the same filename), merged search rankings, and per-vault conformance rules.

### Pattern C: Cross-Vault Entity Resolution

When the same entity (a company, a product, a person) appears in multiple vaults, a **resolver agent** maintains a cross-vault entity index. It maps entity names and aliases to their canonical forms across vaults and can answer "what do we know about Entity X?" by gathering notes from all vaults where that entity appears.

```
User → "What do we know about Acme Corp?"
     → Resolver Agent → search(vault=product, entity="Acme Corp")
                       → search(vault=market, entity="Acme Corp")
                       → search(vault=process, entity="Acme Corp")
     ← consolidated entity profile ←
```

**When to use:** In combination with Pattern A or B, when entities span vault boundaries and the user expects a unified answer. The resolver uses `entities` from the frontmatter — it does not need to read note bodies to find mentions.

**Trade-off:** Requires a maintained cross-vault entity index. The `entity_registry` (§5.4.1) in each vault's meta note provides aliases that the resolver can use for fuzzy matching, but the registry is per-vault; the resolver must reconcile across registries.

---

## 4. Context injection best practices

Mosaix notes are designed for LLM consumption. The average note in production vaults runs approximately 600 tokens. This is not a prescribed limit — it is an observed average that informs context-budget planning.

### Injection order

When injecting a note into a prompt, present the fields in this order:

1. **`summary`** — always first. A well-written summary (120–240 characters) lets the model decide whether the full note is relevant before consuming more tokens.
2. **`keywords`** — six to eight terms that anchor the note's topic.
3. **`entities`** and **`relations`** — typed, structured facts. These are the highest-value-per-token fields for reasoning tasks.
4. **`body`** — the full text. Include only when the summary and entities are insufficient for the task.

### Budget guidelines

| Scenario | Recommended budget |
|---|---|
| Deep analysis of a focused topic | 5–8 complete notes (~3,000–5,000 tokens) |
| Broad survey or cross-cutting question | 15–20 summary+entities snippets (~1,500–2,000 tokens) |
| Entity lookup or fact check | 1–3 notes, entities only (~200–400 tokens) |

These are guidelines, not limits. The key principle is: **inject summaries first, then entities, then bodies** — and stop as soon as the model has enough context to answer. The stratification rule (§2) ensures that the tokens you do inject are semantic content, not housekeeping metadata.

### Injection anti-patterns

- **Injecting `id`, `rev`, `status`, or `updated`** — these waste tokens and invite hallucination. The model may fabricate ULIDs or revision hashes in its output. The stratification rule exists to prevent this.
- **Injecting all notes from a search** — search results are ranked; inject the top N, not the full list. If the model needs more, it can call `search` again with a refined query.
- **Injecting notes without `question` or `summary`** — a note without a summary forces the model to read the entire body to determine relevance. Ensure every note has a summary before using it in a multi-agent pipeline.

---

## 5. Mosaix Certified Client checklist

The following checklists define the minimum requirements for a tool or agent to present itself as a Mosaix-compatible client or enricher. These are non-normative recommendations — they do not affect vault conformance, but they establish a baseline for interoperability.

### Client requirements (5 criteria)

A Mosaix-certified client MUST:

1. **Implement all six MCP tools.** A client that only reads (`read_note`, `search`, `list_notes`) is a viewer, not a client. A client supports the full lifecycle: read, write, move, delete.

2. **Apply the stratification rule.** When injecting note content into an LLM prompt, the client MUST strip `id`, `rev`, `status`, `updated`, and `mosaix` from the frontmatter. If the client uses the MCP server's `read_note`, this is handled automatically. If the client reads files directly (not recommended), it must strip these keys itself.

3. **Run `mosaix check` before publishing.** Before any write that will be visible to other agents or users, the client MUST validate the vault (or the affected notes) against the conformance checks in §10. A write that introduces an error (exit code 1) MUST be rejected or flagged.

4. **Use PR-mediated writes in shared environments.** In any vault shared by more than one agent or user, writes MUST go through a branch-and-review workflow (R8 recommendation). The client writes to a branch, opens a pull request (or equivalent staging mechanism), and a human reviews before merge. Direct writes to the main line are acceptable only in single-user, single-agent vaults.

5. **Display the conformance badge accurately.** If the client surfaces a conformance badge, it MUST reflect the actual result of the most recent `mosaix check` run. A badge shown without a passing check is misleading.

### Enricher requirements (3 criteria)

A Mosaix-certified enricher — an agent or pipeline that generates or completes CORE frontmatter — MUST:

1. **Produce all six required CORE keys automatically.** An enricher that generates `summary` but not `keywords`, or `entities` but not `relations`, is incomplete. The enricher MUST produce: `updated`, `tags`, `summary`, `keywords`, `entities`, `rev`. Optional keys (`id`, `question`, `origin`, `as_of`, `relations`, `links`) SHOULD be produced when the information is available.

2. **Respect the vault's `entity_registry`.** When the meta note declares an `entity_registry` (§5.4.1), the enricher MUST use canonical entity type names or their declared aliases. An enricher that invents entity types not in the registry produces notes that fail E005.

3. **Publish accuracy benchmarks.** The enricher MUST document, for each key it generates, the accuracy measured against a human-reviewed gold set. At minimum: summary faithfulness (does the summary accurately reflect the body?), entity extraction precision and recall, and keyword relevance. These benchmarks are published alongside the enricher, not in the vault.

---

## References

- Mosaix Format Specification v1.2.0: [Mosaix-Format-v1.2.en.md](Mosaix-Format-v1.2.en.md)
- MCP Tool Surface (formal definitions): [MCP-TOOL-SURFACE.md](MCP-TOOL-SURFACE.md)
- Reference MCP server: [mosaix_mcp/](mosaix_mcp/)
- Machine-readable spec: [spec.yaml](spec.yaml)
