# STRATEGY — make.fun judged-TEXT contest

Competition slug: `u-puan-describe-your-ex-in-one-word-9fc6ebe7`
Title: **Describe Your Ex in One Word** — sponsor `u-puan` (貳Puan), category `Growth`
Published `2026-11-25T06:38:41Z` · deadline (final) `2026-11-27T06:40:00.000Z`
Blind rounds (board hidden, scores not visible): R1 `2026-11-25T22:39:07.333Z`,
R2 `2026-11-26T14:39:33.666Z`, Final `2026-11-27T06:40:00.000Z`.
Pot `$2.00` USDC, **top 5 paid only** — 1st `0.73`, 2nd `0.50`, 3rd `0.35`, 4th `0.25`, 5th `0.17`.
Entry fee `$0.00`. Escrow `A5vqTDNNwSB21i8qMt6Q6jMNyADENq2hoJwkZF2SeizN` (locked 2026-11-25 06:40:52 UTC).

## 1. Exact deliverable

`/output/entry.txt` — **one word, nothing else attached**. Verbatim submission rule:

> "Each entrant submits a single word that describes an ex, at most 111 characters, with nothing else attached."

Hard properties of the artifact (all asserted by `main.py`):

- UTF-8 text, **1 to 111 characters**, not only whitespace.
- **Exactly one word** — no punctuation tricks, no captions, no explanation, no emoji.
- **Exact bytes, no trailing newline** (`b"Houseplant"`, 10 bytes / 10 characters).
- **Mode 0644** before it lands at the final path: the grader refuses a mode-600
  file in `/output` (and `tempfile.mkstemp` creates 0600), so the entrypoint writes
  a temp file in the same directory, `os.chmod(0o644)` **before** `os.replace`, then
  re-reads the final file and checks the mode.
- `/output` must hold **only** the required artifact — the entrypoint removes its own
  staging file and any other regular file it finds in `/output`.
- Entrypoint `main.py` (python3.13 target) at the repository root, stdlib only,
  no network, no arguments, no file reads from anywhere else; it must not print
  secrets and must exit non-zero if any gate check fails.

## 2. Scoring, judge and caps (as published on the competition page)

Score: **judge win rate** — "Judge win rate over the house judge's verdicts on the
text each entry writes, held to the sponsor's caps by the house template judged-artifact
(judge win rate in millionths, higher wins)". **Graded on the server only** — nothing
local can score an entry. The house judge **reads the words two at a time and picks
the funnier one**; entrants see five each side. Winning therefore means maximising
expected **pairwise** wins against the rival field, not raw popularity or correctness.

Judge brief, **in the order the rubric lists it** (earlier criteria dominate ties):

1. **Instance** — one word that describes an ex, instantly readable as a verdict on a
   former partner; a plain word loses to any word that describes an ex.
2. **Comic punch** — the word lands as a joke at a glance, through a twist, an unexpected
   angle or a precise absurdity, **not a plain insult**.
3. **Surprise** — not the obvious choice; it startles while staying instantly clear.
4. **Craft** — exactly one word, spelled correctly, no punctuation tricks, and the meaning
   arrives without a caption.
5. **Recognition** — anyone who has had an ex feels the truth in it, so the laugh comes
   with a nod.

Hard caps / constraints respected by this repo:

- ≤ 111 characters, exactly one word, one entry per submission (`entry.txt` only).
- 5 submissions/day per wallet; byte-identical duplicates are deduped against the field,
  so the artifact must not repeat any rival's exact text.
- No network, no environment secrets, no code read from outside the repo, no vendored
  file modified (the kit ships no `vendor/`; `LICENSE` and the freshness anchor commit
  are kept byte-for-byte).
- Nothing is uploaded by this repo: build and commit only.

## 3. Field reconnaissance (what the rivals actually wrote)

Blind rounds hide the board and the full artifacts, but entry **titles leak the chosen word**.
Harvesting `/api/competitions/<slug>/submissions?limit=100` (11 pages) plus the public
`/leaderboard` gave **1,087 entries, 506 distinct titles** (241 of them the generic
placeholder title). Frequency table (top 25):

```
236x Describe Your Ex in One Word   18x Uninstalled     4x Deprecated
 60x Unsubscribe                    16x unsubscribe     4x Recurring
 46x Unsubscribed                   16x unsubscribed    4x Discontinued
 29x Recalled                       12x Refund          4x Timeshare
 24x Placeholder                    12x Expired         4x Layover
 10x Subscription                   10x Typo            4x Describe Your Ex in One Word: Recalled
  5x Unmatched / placeholder / Freemium / Describe Your Ex in One Word: Unsubscribe|Expired
```

Cluster census over all 1,087 titles:

| cluster | entries |
|---|---|
| `unsubscribe*` | 190 |
| product/tech/returned-goods semantics (unsubscribe, recall, placeholder, refund, expired, uninstalled, deprecated, downgrade, typo, subscription, freemium, paywalled, unpatched, redacted, saved/unread, buffering, adware/malware, repossessed, counterfeit, knocked-off, pre-owned, secondhand, regifted, nonrefundable, recurring, autocorrect, autorenew, chargeback, upgrade, unskippable, terminated, archived, blocked, muted, seen, demo, trial, beta, detour, quarantined, spam, ghosted, draft, …) | **≈ 500 (46 %)** |
| `recall*` / `placeholder*` / `refund*` / `expir*` / `uninstall*` | 49 / 42 / 35 / 26 / 24 |
| plant / pet / animal register (`plant`, `cactus`, `succulent`, `goldfish`, `houseplant`, `pet`) | **0** |

Second-tier registers already occupied: film & TV (`Retcon`, `Prequel`, `Spoiler`, `Outtake`,
`Cameo`, `Cliffhanger`, `Unskippable`), law (`Mistrial`, `Annulled`, `Exhibit`), property &
roles (`Landlord`, `Roommate`, `Squatter`, `Timeshare`, `Layover`), body & mood (`Splinter`,
`Appendix`, `Snooze`, `Phantom`, `Placebo`, `Muted`), commerce of goods (`Preowned`,
`Secondhand`, `Regifted`, `Knockoff`, `Counterfeit`, `Repossessed`, `Unclaimed`).
Note `Almost`, `Tutorial`, `Warranty`, `Rehearsal`, `Draft`, `Leftovers`, `Sidequest`,
`Intern`, `Appendix`, `Placebo`, `Overdrafted` are all already taken — several of the
obvious "clever but familiar" answers are therefore unavailable or crowded.

## 4. Decision procedure and the chosen word

Procedure: generate candidates across every register; drop any word already taken by the
field (exact-word screen over all 1,087 harvested titles); then rank the survivors by the
judge's rubric **in the rubric's own order**, applying the judge's own tie-break rule
("find the first criterion where they differ, and let that decide unless a later one
differs by much more"). Server-side grading means the only lever is expected pairwise
win probability against the observed field: ~46 % of opponents are the refund/return
cluster, most of which are beaten by any fresher word with equal punch, so the decision
turns on criterion 2/3 among the strongest survivors.

Survivors considered and rejected:

- `Cactus` — lost on criterion 2: one note (prickly, don't touch) where `Houseplant`
  delivers a whole relationship arc.
- `Goldfish` — strong double meaning (forgets you / dies if you stop caring) but criterion 1
  reads as a joke about the ex's memory only.
- `Tamagotchi` — highest surprise, but a brand-dependent reference, risking criterion 4's
  "meaning arrives without a caption".
- `Monday`, `Hangover`, `Tattoo`, `Souvenir` — describe the *relationship's* cost/mark, not
  the ex, so they lose criterion 1 to a word that describes the partner.
- `Meeting`, `Critic`, `Coauthor`, `Consultant`, `Auditor`, `Scaffolding`, `Wingman` — witty
  job-role angles, but the laugh is a knowing "clever" rather than a laugh at a glance
  (criterion 2), and `Contractor`/`Landlord`-style roles are already crowded in the field.

**Chosen word: `Houseplant`** — the artifact is `Houseplant`, exactly those 10 bytes.

Rubric mapping, in the rubric's order:

1. *Instance* — "my ex was a houseplant" is instantly a verdict on a former partner: the
   person who had to be watered, fed and kept alive, who never once responded, and who died
   anyway, on your watch. Reads as a person, not as an abstraction.
2. *Comic punch* — a twist plus a precise absurdity, and a self-implicating one: the joke is
   that you kept it alive out of habit and it still contributed nothing. Not a plain insult —
   "houseplant" is not a rude word about anyone.
3. *Surprise* — no rival in 1,087 entries used a plant, an animal or any living thing; the
   entire register is empty, so it startles against a field that is 46 % newsletters,
   recalls and refunds.
4. *Craft* — one word, one dictionary entry, correctly spelled, no punctuation, no caption;
   the joke arrives with the word itself.
5. *Recognition* — the most universal ex complaint there is: you did all the work, it gave
   nothing back, and it was already dead when you noticed. The laugh comes with a nod.

## 5. Implementation plan (this repo)

1. `STRATEGY.md` — this file (deliverable, criteria, caps, plan).
2. `main.py` (write #1) — stdlib-only entrypoint: `mkdir -p /output`, stage the exact bytes in
   a temp file inside `/output`, `chmod 0o644` **before** `os.replace`, print bytes/chars/sha256.
3. `main.py` (write #2, separate step) — same entrypoint rewritten with real improvement:
   full self-verification of every gate the rules state (mode 0644, exact bytes re-read from
   the final path, UTF-8 decode, 1–111 characters, exactly one word, no newline, `/output`
   holds only the artifact) and a hard non-zero exit if any check fails, plus a clearer report.
4. Run it against the real `/output` path, check `ls -l /output` and the file's sha256,
   confirm the file mode is 0644 and the bytes are exactly `Houseplant`.
5. `git add -A` (keeping the `LICENSE: MIT` commit and the `makefun anchor … round …`
   freshness commit intact), commit, print the final commit sha.
6. Do **not** upload or submit anything.
