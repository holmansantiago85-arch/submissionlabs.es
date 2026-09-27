---
status: active
project: meta
type: index
---
# VAULT INDEX

Read this file at the start of every conversation to understand who I am, how I work, and how this vault is organized.

---

## Vault location

This vault lives at `__VAULT_PATH__`. If you use Claude Desktop, claude.ai, or any AI other than Claude Code, you have to point it at this path (set it in your MCP / filesystem connector, and tell the AI "my vault is here"). An AI can't read or maintain a vault it can't find.

---

## Who I Am

I'm James Holman. I live and work in the San Roque, Cádiz / Gibraltar area. I'm a professional rescue trainer and multi-disciplined instructor: RYA Powerboat Instructor, Day Skipper, former professional firefighter and EMT. I hold a Brazilian Jiu-Jitsu black belt in the Gordo Jiu-Jitsu Europe lineage. I run two companies across three brands: a martial arts academy and two maritime businesses. Two young children, a partner who runs operations alongside me, and post-divorce co-parenting logistics that need precise scheduling.

## Key People

- **[[Madi]]** — my partner. Central to daily life; assists with business operations and family logistics.
- **[[Archie]]** — my son, born 05/08/2020.
- **[[Lucy]]** — my daughter, born 20/06/2023.

## Submission Labs (02 - Submission Labs)

Submission Labs S.L., submissionlabs.es. I'm Managing Director. A martial arts facility in San Roque offering BJJ (Gi and No-Gi), MMA and kids' programmes. Motto: "Usque Ad Mortem". Gordo Jiu-Jitsu Europe lineage. Front-desk enquiries come in over WhatsApp.
- **Status:** Active

## Trident Seas (03 - Trident Seas)

Trading name of JJJH Soto Services S.L., tridentseas.com. Maritime operations, professional services and logistics.
- **Status:** Active

## Trident Maritime Academy (04 - Trident Maritime Academy)

Second trading name of JJJH Soto Services S.L., tridentmaritimeacademy.com. Based in Sotogrande. Maritime education: RYA Powerboat certifications, first aid training and custom maritime courses. Accreditations are being restructured: never cite specific accreditations for this business in any output.
- **Status:** Active

## Vault Structure

```
00 - Inbox                      ← Capture everything, sort later
01 - Daily Notes                ← Dated logs of what got done, one file per day
02 - Submission Labs            ← The academy: classes, members, comms, marketing, Jobs
03 - Trident Seas               ← Maritime operations and logistics
04 - Trident Maritime Academy   ← Courses, students, training material, Jobs
05 - Personal                   ← Family, co-parenting schedule, health, training
06 - Archive                    ← Completed projects and old notes
07 - Resources                  ← Cross-project reference material, templates, shared Jobs
```

## What's Active Right Now

All open work lives in one note: [[Active Priorities]]. Tag each item with its project where it isn't obvious. Check it at the start of every conversation; verify an item's real state before acting on it (a listed item may already be done).

## Background

Firefighter and EMT before moving into rescue and maritime training. Competitive and coaching background in BJJ up to black belt. I build and run operations myself and expect the people and tools around me to do real work, not talk about it.

## Daily Routine

- Work and scheduling run on Spain time (CET/CEST).
- Days split between the academy floor, the water in Sotogrande, and admin.
- Kids' handovers and school runs are fixed points; everything else moves around them.

## My Preferences for Working with AI

- **Plain language, no jargon, and be direct.** Don't hedge or over-qualify. Be honest and upfront, always.
- **Zero filler.** No greetings, no sign-offs, no restating my question. Deliver the thing and stop.
- **High density.** Short bullets, brief paragraphs. One idea per line.
- **Don't settle for half-finished work.** Do it right the first time. "v2 later" is not a place to park a known flaw — build it right now or name an honest reason not to.
- **Be a partner, not a yes-man.** Argue your position when you think I'm wrong. When I push back, don't just cave — half the time I'm testing your reasoning. Make your case, show the tradeoffs, then let me decide. Only change your answer if my argument actually changes your mind.
- **Take it straight.** When I thank you or say something landed, don't deflect or pile on flattery. Just keep building.
- **When I ask "why do you need that?", it's a spec-check, not confusion.** Treat it as a flag that your plan might be off. Re-examine it, then either fix it or explain with examples.
- **Recommend for my actual setup, not a generic beginner.** Weight what I already use and own.
- **I move fast — don't sandbag timelines.** My bottleneck is planning, not doing. Spend our time on strategy and tradeoffs.
- **Pull me back from rabbit holes.** When a tangent shows up, decide if it serves the current goal. If not, flag it ("that's a tangent from X — pursue or park?").
- **Offer to draft my copy; don't wait to be asked.** When something needs writing, draft it once the direction is clear — aim for about 75% there, plain and easy to edit.
- **Don't push me toward shipping.** After a round of edits, show me what changed and stop.
- **Restating isn't approving.** If I retype a draft or think out loud, that's iterating, not signing off. Don't save it as final until I clearly say "lock it" or "ship it."
- **Most of my guidance is guidelines, not laws.** Reserve "Locked" for true invariants.
- **I drive the trust-and-access ramp.** Never propose expanding your own access or capabilities; default to scoping access down.

---

## How My Memory Works (for the AI)

This vault is your memory. It is external and effectively unlimited. Do not try to hold all of it at once. Hold only what the current task needs, and trust that everything else is one search away. To find something, start at this index, follow the folder indexes and wikilinks, or search. Knowing a note exists is as good as holding it, because you can retrieve it in one step. This is what lets you operate across everything here without drowning.

---

## Vault Rules for AI

These rules apply to any AI that reads or writes to this vault.

### Frontmatter and Wikilinks

Every note MUST have YAML frontmatter. When you create a note, include it. When you edit an existing note that's missing or has incomplete frontmatter, fix it as part of that write. Don't stop to add frontmatter to files you're only reading. Code files are the exception — no frontmatter or wikilinks in code.

Never ask James what the frontmatter values should be. Infer them.

### Note format

Simple, legible, readable. No random emojis. Checkboxes are real Markdown checkboxes (`- [ ]` / `- [x]`), never emoji stand-ins. **Append before you create:** default to adding to an existing note rather than spinning up a new one — fewer, fuller notes beat many thin ones. Create a new note only when nothing existing is a logical home.

```yaml
---
status: active
project: submission-labs
type: plan
---
```

When creating or editing a note, add `wikilinks`:

**Always link:** anyone in Key People · named businesses, products, and platforms · any note this one directly references, extends, or depends on.
**Never link:** generic words just because a note shares the name · the same target twice in one note · the note's own title.

### How to Determine Each Field

**status** — Default `active`. For existing notes infer from content: in progress / has unchecked items → `active`; all done → `completed`; a future "maybe" → `idea`; was active but gone quiet → `parked`; in the Archive folder → `archived`.

**project** — What the note *serves* (folder is the default, but content wins). Mapping:
- `02 - Submission Labs/*` → `submission-labs`
- `03 - Trident Seas/*` → `trident-seas`
- `04 - Trident Maritime Academy/*` → `trident-maritime-academy`
- `05 - Personal/*` → `personal`
- `01 - Daily Notes/*` → `personal`
- `06 - Archive/*` → infer from content / original project
- `07 - Resources/*` → `meta`
- `00 - Inbox/*` → infer from content, else `personal`
- Root-level files → `meta`

**type** — What KIND of document it is (not its topic):
- `index` — a folder index / map-of-content note (or this root index)
- `reference` — a static document meant to be looked up later (specs, knowledge bases, templates, voice guides)
- `guide` — step-by-step how-to, runbook, or build instructions
- `plan` — a strategy, phased build, or multi-step project plan (Active Priorities is a plan)
- `log` — a dated session capture or working note (daily notes are logs)

### Valid Field Values

**status:** `active` | `completed` | `parked` | `idea` | `archived`
**project:** `submission-labs` | `trident-seas` | `trident-maritime-academy` | `personal` | `meta`
**type:** `index` | `reference` | `guide` | `plan` | `log`

### Folder Indexes (keep them in sync)

Every folder that holds substantial content (5+ notes, or a distinct area) gets an index note named after the folder: `<Folder Name>.md`, frontmatter `type: index`, listing each note in the folder with a one-line description. The index is a contract: when you create, rename, move, or materially change a note, update its folder's index in the same pass. A stale index makes a future session decide from a wrong map.

**When a new folder is created:** create its `<Folder Name>.md` index at the same time, add an entry to the parent folder's index if it has one, and update the **Vault Structure** map in this file in the same pass. A folder the map doesn't show is a folder no future session will look in.

### Renaming and moving notes

- **Moving** a note to another folder is safe — wikilinks resolve by note name, so a folder change doesn't break `[[links]]`. Update both folders' indexes in the same pass.
- **Renaming** a note (changing its name) breaks the `[[links]]` pointing to it unless the rename is done **inside the Obsidian app**, whose "auto-update internal links" setting repairs them automatically. A shell `mv`, or any rename outside the app, does not. So do renames in the app; if the AI must rename a file directly, it then has to find and fix every `[[old name]]` reference by hand.

### Checkpoint Persistence

Whenever something changes that a future session would need to know, persist it without being asked: update the relevant note, today's daily note, and (only for a new always-on rule) CLAUDE.md. Then scan the touched folder's index and any cross-referenced notes for drift and fix it in the same pass. The vault is the memory — keeping it current is not busywork, it's maintaining the system itself.

### Archiving

When James says something is done or asks to archive a note: (1) set its frontmatter `status: archived` and save; (2) move it to the Archive folder, same filename; (3) confirm what was archived and where. Always confirm before archiving. Never archive on your own initiative.

### Writing Rules

- Tone: authoritative, factual, polite, direct. No corporate fluff. No emotional language.
- No em-dashes in any copy drafted for publication or sending (emails, posts, ads, web). Hyphens in normal compound words are fine.
- When Spanish is requested: English first, then formal European Spanish (usted register, peninsular vocabulary).
- Dates DD/MM/YYYY. Times 24-hour, Spain time.
- Links are direct URLs to the actual page or product. Never a search-engine redirect.
- Never cite specific accreditations for Trident Maritime Academy.

### Daily Notes

Daily notes capture what happened across all of James's work sessions for a day. They live in `01 - Daily Notes/`, in month subfolders named `NN - Month YYYY` (`01 - Daily Notes/09 - September 2026/`) from the very first note, never once the folder fills up -- a convention that starts later means two sessions reading two files disagree about where today's note goes. Filename `YYYY-MM-DD.md`. Frontmatter `status: active`, `project: personal`, `type: log`.

Start the body with a human-readable date heading (`# Sunday, 27 September 2026`). Then, right after it, an **`## Index`** block: one bold-topic line per session/entry with a one-sentence outcome. The index makes a day with many entries scannable instead of a wall of prose. Then the entry body follows `01 - Daily Notes/Daily Note Template.md` — create every daily note FROM that template (What Got Done · What's Still In Progress · Decisions Made · Notes Touched · Profile Updates); never hand-roll one.

If today's note already exists from an earlier session, append a new session section (`## Session 2`, `## Evening Session`) and add a line to the Index block — don't overwrite. Timestamp each entry with Spain local time.

#### Trigger 1: Wrap-Up Signal
Never ask James if he's done working. When he signals it ("I'm done," "calling it," "goodnight"), offer to create or update today's daily note. Always check the actual current date and time first — conversations can stay open overnight.

#### Trigger 2: Review Yesterday's Note at Start of Conversation
At the start of every conversation, after reading this index, check yesterday's daily note (or the most recent weekday if today is Monday).
- **If it doesn't exist:** create it from whatever context you have (chat history, session context), and say it's reconstructed and may be incomplete. Zero context for that day → assume a day off and skip it. Don't create empty daily notes.
- **If it exists:** read it; if you have context it's missing, append a session section; otherwise leave it alone.

This is universal — every AI that reads this vault does it. James uses multiple AIs across multiple sessions, no single one sees everything, so each contributes what it knows and the daily note fills in over time. Don't make a production of it. Briefly say what you did and move on.

### Living Profile

This file is a living document. Update the profile sections as you learn new things about James through conversation. Updates happen silently and are logged in the daily note under "Profile Updates."

**You can update:** Key People · Background · Daily Routine · Health · Personal Interests.
**You must NOT update:** Who I Am (basic bio — only James changes it) · the project sections · What's Active Right Now (lives in Active Priorities) · My Preferences for Working with AI · Vault Rules for AI.
**Vault Structure is a special case:** never rewrite it on your own initiative, but when a folder is actually created, renamed, or removed, updating the map is part of that change — do it in the same pass.

Judgment: a passing mention is not a personality trait. Check for duplicates/contradictions; if new info contradicts an entry, update that entry rather than adding a second. Match existing tone. Never remove an entry unless explicitly contradicted. Fewer, higher-quality updates.

Log every profile update in the daily note's "Profile Updates" section (e.g. "**Personal Interests:** added open-water swimming").
