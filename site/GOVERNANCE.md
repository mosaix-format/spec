# Governance — Mosaix Format

## 1. Versioning policy (SemVer)

- **MAJOR** (2.0, 3.0...): breaks backward compatibility. A vault conformant
  to the previous version may not be conformant to the new one. Examples:
  removing a CORE key, changing the semantics of a rule, making a previously
  optional key mandatory.

- **MINOR** (1.1, 1.2...): adds optional keys, new recommendations, or
  tooling. Never breaks the conformance of existing vaults. Examples: adding
  `question` as an optional CORE key, new entity types, new checker warnings.

- **PATCH** (1.1.1, 1.1.2...): typo fixes in the spec, textual clarifications,
  checker corrections with no semantic changes, documentation updates.

The current version number lives in `spec.yaml` (source of truth).

## 2. RFC process

Anyone can propose a change:

1. Open a GitHub Issue using the "RFC" template
2. The template requires:
   - **Problem**: what problem this proposal solves
   - **Proposal**: what changes in the spec (specific text, not vague)
   - **Backward compatibility**: does this change break existing vaults? How?
   - **Checker impact**: what changes in `audit_reference.py`
   - **Skill impact**: which skills need updating
   - **Conformance corpus impact**: which test cases need to be added/modified
3. Open discussion for 30 days (minimum)
4. Final decision by the maintainer, with written rationale in the Issue
5. If accepted: a PR that includes changes to ALL affected files
   (spec, `spec.yaml`, checker, skills, conformance corpus, `CHANGELOG.md`)

An RFC is never accepted without the complete PR — a spec-only change is not
enough.

## 3. Backward compatibility guarantee

- CORE keys are never removed in a MINOR
- Rules (R1–R7) do not change semantics in a MINOR
- New keys added in a MINOR are optional for at least one MINOR release
- The checker at version N must be able to validate vaults conformant to N-1
  with at most warnings (never new errors on previously conformant vaults)
- Recommendations (such as R8) can be added in a MINOR without backward
  compatibility constraints (they are non-normative)

## 4. Deprecation policy

- A deprecated feature generates WARNING for at least one MINOR release before
  becoming ERROR
- Documented in `CHANGELOG.md` with the date and planned removal version
- Example: `id` is a warning in v1.x → will become an error in v2.0

## 5. Version declaration

A note MAY declare `mosaix_version: 1.1` in its frontmatter. The checker
validates against the declared version. If not declared, it validates against
the latest version supported by the checker.

This allows vaults with notes at different versions during migration.

## 6. Maintainer

BDFL (Benevolent Dictator For Life): Andrea Fiorino
Contact: via GitHub Issues

The BDFL may delegate RFC review to trusted contributors, but the final
decision remains theirs. If the BDFL becomes inactive for 12+ months without
naming a successor, the contributor with the most accepted RFCs may assume
the role by opening a succession Issue.

## 7. Code of conduct

The project adopts the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
Unacceptable behaviour should be reported via private Issue or email.
