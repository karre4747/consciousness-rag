# Frontend Guide

_Last updated: December 2025_

Goal: deliver a rich, modern portal UI while keeping the stack simple (vanilla HTML/CSS/JS) and security strong (CSP-friendly, no eval). This guide lays out the staged refactor path and expectations for future frontend work.

## 1) Current state
- Single-page UI at `backend/static/index.html`.
- Large inline `<script>` handling upload, tagging, documents, query, analysis, and spending.
- CSP currently permissive (`'unsafe-inline' 'unsafe-eval'`); intended to tighten after JS is externalized.

## 2) Staged refactor plan

### Stage 1 — Externalize & modularize
- Move all inline JS into `backend/static/js/app.js` (loaded with `defer`).
- Split responsibilities into modules/namespaces:
  - `Upload` (file handling, progress)
  - `Docs` (list, search, delete)
  - `Tagging` (verify, retag)
  - `Analysis` (estimate/run)
  - `Research` (query, render answers/sources)
  - `Spending` (dashboard, history, cap updates)
  - `UIHelpers` (modals, toasts, formatting, escapeHtml)
- Replace inline handlers with `addEventListener`.
- Remove any string-based timers; use function callbacks.

### Stage 2 — Tighten CSP
- Target CSP: scripts from `'self'`, no `'unsafe-eval'`; remove `'unsafe-inline'` once all inline JS is gone.
- If temporary inline snippets remain, use nonces; prefer zero inline script in final state.
- Align with `CSP_BEST_PRACTICES.md` and the web.dev CSP guidance.

### Stage 3 — UX polish & accessibility
- Standardize design tokens (colors, spacing, typography) via CSS variables.
- Ensure clear loading/error/success states for upload, query, analysis, spending actions.
- Accessibility: semantic headings, focus management for modals, keyboard navigation, ARIA labels where needed.
- Responsive layout: test on mobile/tablet/desktop breakpoints.

### Stage 4 — Framework-ready (optional future)
- Keep modules “component-like” (state + render helpers) to ease migration to React/Vite or SvelteKit if complexity grows.
- Keep API calls decoupled from DOM updates to simplify future adoption of a framework.

## 3) Coding standards
- No `eval`, no string-based `setTimeout`/`setInterval`, no inline event handlers.
- Keep DOM queries scoped and cached when practical.
- Centralize fetch wrappers for consistent headers, error handling, and JSON parsing.
- Keep UI state minimal and explicit; prefer pure functions for rendering blocks.
- Escape untrusted text when injecting into the DOM (use `escapeHtml` helper).

## 4) File layout (proposed)
- `backend/static/index.html` — HTML skeleton only; references CSS/JS.
- `backend/static/css/app.css` — shared styles and tokens (can be extracted from existing `<style>`).
- `backend/static/js/app.js` — main entry; imports or contains modules.
- Optional: split modules if size grows (e.g., `upload.js`, `docs.js`, `tagging.js`, `analysis.js`, `research.js`, `spending.js`, `ui-helpers.js`), but keep import count small and paths simple.

## 5) Testing expectations
- Smoke tests: upload a file, verify duplicate check, delete a doc, run query, verify tagging, view spending dashboard and modal.
- Browser console: no CSP violations, no uncaught errors.
- Layout: basic responsiveness and visible loading/error states.

## 6) CSP checklist for completion
- All scripts loaded via `<script src="/static/js/app.js" defer></script>`.
- No inline event handlers; no `unsafe-eval`.
- CSP header tightened in `backend/main.py` after refactor:
  - `script-src 'self'` (plus nonce if interim inline code remains).
  - `style-src 'self' 'unsafe-inline'` acceptable until CSS is externalized.
- Verify in DevTools that no CSP errors appear during normal flows.

## 7) References
- `CSP_BEST_PRACTICES.md`
- `EVOLVE_ENGINEERING_GUIDE.md`
- `API_REFERENCE.md` (for endpoints used by the UI)
- `TESTING_GUIDE.md` (for manual UI flows)


