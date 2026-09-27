---
status: active
project: meta
type: plan
---
# Integrations Plan

How Jared runs his Jarvis (Substack, "Six Weeks With Jarvis", 07/2026): a dedicated Mac on 24/7, its own email address and phone number, wired into more than a dozen services he already pays for. It watches his membership platform, manages four inboxes with a different policy each, auto-unsubscribes newsletters, and answers one phone line in a British butler voice. The pattern: one agent, one memory, many connectors, each with a written policy note.

James's equivalent, in priority order. Each one becomes a Job note once wired.

## Phase 1: read-only, low risk
- [ ] **Google Calendar** via Claude Code MCP. Family handovers, classes, courses. Read first; write only after the calendar names are confirmed.
- [ ] **Gmail** via Claude Code MCP. Triage and drafts only, no sending. Policy per inbox: academy enquiries, maritime clients, personal.
- [ ] **Dropbox / Google Drive** for course packs and academy documents.

## Phase 2: act, with ask-first permissions
- [ ] **WhatsApp front desk** for the academy (see [[Jobs/WhatsApp Front Desk]]). Needs WhatsApp Web or Business API access on the Mac mini.
- [ ] **Metricool** scheduling (see [[Jobs/Social Content]]). Send for review, never auto-publish.
- [ ] **Supabase / website** health check for submissionlabs.es. Read-only monitoring first.

## Phase 3: always-on
- [ ] Morning brief at a fixed time: calendar, inbox summary, open priorities, handovers today. Spoken through the voice line or written to the daily note.
- [ ] Inbox policies written as notes the agent reads before acting, one per inbox, as Jared does.

## Rules
- Every connector gets a note here stating what it may read, what it may change, and what always needs James's yes.
- Permission mode stays "ask" until a connector has run clean for two weeks.
- Secrets live in the macOS Keychain. Never in a note.
