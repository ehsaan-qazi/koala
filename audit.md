
# Koala Phase 2 — Completion Audit

> Scope: This audit compares the **current state of the repository** against the
> **Phase 2 requirements** defined in `implementation_plan.md`
> (Section 7.2 — "Phase 2: Document Upload & Roadmap Extraction (4 weeks)").
>
> Date: 2026-07-20

---

## 0. Headline Finding

**Phase 2 is NOT complete.** The central deliverable — *AI extraction of a
**roadmap** (assessment items: assignments, exams, quizzes, projects…) that the
user reviews and confirms* — **does not exist in the codebase.**

What *is* implemented in its place is **topic extraction** (which is actually a
**Phase 3** feature), and it is gated behind the **Pro plan**, which **inverts
the plan's pricing model** (the plan makes *roadmap* AI free and *topic* AI Pro).

In short: the wrong phase was built, on the wrong provider, with the wrong
pricing gate. The roadmap model and table exist and are ready, but nothing
populates them and there is no UI for them.

**Exit criteria not met:** *"User uploads a syllabus, AI extracts a roadmap,
user confirms it."* → The "roadmap" part and the "confirm" part are both missing.

---

## 0.5 Approved Mid-Project Deviations (NOT issues)

Two plan deviations were **consciously approved** and must no longer be treated
as defects:

- **LLM provider = Groq** (plan said Gemini/OpenAI/Anthropic adapter). Rationale:
  Groq's generous free tier; the `groq_router.py` circuit-breaker is solid.
  → Keep Groq. See §2.3 (re-classified as approved).
- **Object storage = Cloudflare R2** (plan said Supabase Storage). Rationale: R2
  gives **10 GB free** vs Supabase's **500 MB**. → Keep R2. See §2.1 (re-classified
  as approved). Note: the plan's *signed-URL direct upload* flow was also dropped
  in favour of server-side upload via the API; this is a minor accepted deviation.

## 0.6 Known Defect (fixed 2026-07-20): "Create Course" button

**Symptom:** Clicking "+ New Course" / "Add Course" appeared to do nothing.

**Root cause:** The New Course modal is rendered with
`<div className="modal-overlay">`, but the CSS
(`.modal-overlay { opacity:0; pointer-events:none }`) only reveals it when an
`.open` class is present — which the React code never adds. The modal mounted
invisibly and was non-interactive. (CSS was ported from a vanilla-HTML design that
toggled `.open` via JS.)

**Fix (Milestone M0):** Made `.modal-overlay` visible by default in
`web/src/styles/index.css`, and added the `open` class in
`web/src/pages/DashboardPage.jsx` for the intended slide-in animation.

---

## 1. Requirement-by-Requirement Status

| # | Phase 2 Task (from plan) | Priority | Status | Notes |
|---|---|---|---|---|
| 1 | Course CRUD — REST API + React pages | Must | ✅ Done | `routes/courses.py` + `pages/CoursePage.jsx`. Functional. |
| 2 | Document upload endpoint (Signed URL → Supabase Storage → DB) | Must | ✅ Approved deviation | Upload works via **Cloudflare R2** (approved over Supabase for 10 GB free) + **server-side upload** (signed-URL flow dropped). See §2.1 / §0.5. |
| 3 | PDF text extraction (PyMuPDF + pdfplumber) | Must | ❌ Diverged | Uses **PyPDF2** only. No pdfplumber/PyMuPDF. See §2.2. |
| 4 | LLM adapter pattern (Gemini / OpenAI / Anthropic) | Must | ✅ Approved deviation | **Groq** chosen over Gemini (approved). `groq_router.py` circuit-breaker is the implementation. See §2.3 / §0.5. |
| 5 | **Roadmap extraction** (structured JSON → insert `roadmap_nodes`) | Must | ❌ Missing | **No roadmap extraction code, no `roadmap_nodes` route, no service.** This is the headline gap. See §2.4. |
| 6 | Extraction status polling (GET status + React polling/SSE) | Must | ❌ Missing | No `GET /documents/{id}/extraction-status` endpoint. `processing_status` column exists but is not exposed. Extraction runs inline/synchronously. See §2.5. |
| 7 | **Confirm-before-lock UI** (edit/confirm/delete + visual state) | Must | ❌ Missing | No roadmap review UI at all. Even topic extraction has no confirm/edit step. See §2.6. |
| 8 | Multi-document merge (lightweight RAG) | Should | ❌ Missing | Not implemented. |
| 9 | Placeholder handling (visual distinction + nudges) | Must | ❌ Missing | N/A until roadmap nodes exist; no UI nudges. See §2.7. |

Supporting gaps: **No Phase 2 tests**, **stub-note auto-creation missing**,
**wrong tier gate on extraction** (see below).

---

## 2. Detailed Issues & Remaining Work

### 2.1 Document upload — Cloudflare R2 (APPROVED deviation)
- **Plan:** Client requests a *signed upload URL*, uploads the PDF **directly to
  Supabase Storage**; the server only stores the path.
- **Reality:** `web/src/api/client.js` + `routes/documents.py` send the raw file
  bytes to the backend via multipart; `storage_service.py` uploads to
  **Cloudflare R2** using a server-side boto3 `put_object`.
- **Status:** **Approved deviation** (see §0.5). R2 chosen for 10 GB free vs
  Supabase's 500 MB; the signed-URL direct-upload flow was dropped in favour of
  server-side upload. Keep as-is. (`supabase_*` config vars in `config.py` are now
  vestigial but harmless — used only for Supabase Auth JWT verification.)
- **Impact:** Higher server bandwidth/compute than the plan's design, but
  acceptable for the ~50-user target.

### 2.2 PDF text extraction — wrong library
- **Plan:** PyMuPDF (`fitz`) for text, `pdfplumber` for tables.
- **Reality:** `extraction_service.extract_text_from_pdf` uses **PyPDF2 only**.
- **Impact:** Lower-quality text/table extraction; structured field extraction
  (deadlines, weights) will be less reliable.

### 2.3 LLM adapter — Groq (APPROVED deviation)
- **Plan:** Adapter pattern supporting **Gemini (default), OpenAI, Anthropic**,
  key loaded server-side from env via `LLM_PROVIDER`.
- **Reality:** `groq_router.py` is a Groq-only circuit-breaker router.
  `config.llm_provider` defaults to `"groq"`. No Gemini/OpenAI/Anthropic clients.
- **Status:** **Approved deviation** (see §0.5). Groq's free tier was chosen over
  Gemini. Keep as-is. No further action required.

### 2.4 Roadmap extraction — entirely missing (CRITICAL)
- There is **no** `routes/roadmap_nodes.py`, **no** `services/roadmap_extraction`,
  and **no** prompt that produces roadmap structure.
- The only extraction (`/documents/{id}/extract`) calls
  `extract_topics_for_document`, which inserts **`topics`** (Phase 3 entity)
  with a flat `title` list only.
- The `roadmap_nodes` table and `RoadmapNode` model **are fully defined**
  (with `node_type`, `deadline`, `weight_percent`, `is_placeholder`,
  `is_confirmed`, `extraction_confidence`) but are **never written to**.
- **What must be built:** a roadmap extraction pipeline that
  1. downloads the PDF, extracts text (§2.2),
  2. calls the LLM with the **structured roadmap prompt** from the plan
     (returns `{nodes:[{title, node_type, deadline, weight_percent, confidence}], warnings}`),
  3. inserts `roadmap_nodes` with `is_confirmed=False`, `is_placeholder` set per
     null fields, `extraction_confidence` per node,
  4. (Phase 4) auto-creates a stub note per node.

### 2.5 Extraction runs synchronously — no job/status/polling
- **Plan:** `POST /extract` returns `202 Accepted {job_id}`; a background task
  does the work; client polls `GET /extraction-status`.
- **Reality:** `trigger_extraction` awaits extraction **inline** and returns only
  after completion. There is **no** status endpoint and **no** `BackgroundTasks`
  usage.
- **Correctness bug:** `extraction_service.extract_topics_for_document` is `async`
  but calls **blocking** libraries (`boto3`, `PyPDF2`, `groq`) directly inside the
  event loop → **blocks the entire FastAPI event loop** during extraction.
- **Frontend:** `CoursePage.handleExtract` does a blocking `await`, then refreshes
  and switches to the Topics tab. No spinner tied to `processing_status`, no
  polling, no error display from `error_message`.

### 2.6 Confirm-before-lock UI — missing (CRITICAL)
- **Plan:** A review table of extracted nodes with inline **edit / confirm /
  delete** and visual state indicators (pending / confirmed / placeholder).
- **Reality:** No such UI exists. `App.jsx` has **no ExtractionReviewPage** (it is
  listed in the plan's structure but not created). `CoursePage` has only
  *Overview / Documents / Topics* tabs — **no Roadmap tab**.
- **Remaining:** Build the roadmap review page (route `/courses/:id/roadmap` or a
  dedicated review step), with per-node edit, confirm, delete, placeholder
  badges, and a "confirm all" action.

### 2.7 Placeholder handling — missing
- The model supports `is_placeholder` and `extraction_confidence`, but there is no
  UI that visually distinguishes placeholders (null deadline/weight) or nudges the
  user to fill them. Must ship with the confirm-before-lock UI (§2.6).

### 2.8 Tier gate inversion (pricing bug)
- **Plan:** *Roadmap AI = Free tier* (3 docs/course); *Topic AI = Pro*.
- **Reality:** `require_pro(current_user)` is called at the top of
  `trigger_extraction`, so **all** AI extraction (currently only topics) requires
  Pro. Free users cannot run the Phase 2 core flow.
- **Fix:** Roadmap extraction must be allowed for Free (subject to the 3-doc
  limit). Topic extraction (Phase 3) should keep the Pro gate. Re-point the gate
  accordingly once roadmap extraction exists.

### 2.9 Stub-note auto-creation — missing
- The plan's extraction sequence includes *"Auto-create stub notes for each node."*
  Not implemented (deferred to Phase 4, but the pipeline hook is absent).

### 2.10 Testing — Phase 2 has zero coverage
- **Plan (§10):** Unit + API tests for extraction; happy path + validation.
- **Reality:** only `backend/tests/test_main.py`. No tests for upload, limits,
  extraction, or status. CI (GitHub Actions) may exist but covers nothing Phase-2.
- **Remaining:** Add tests for upload limits, doc_type gating, extraction
  success/failure, and (once built) roadmap node insertion + confirm flow.

### 2.11 Authentication provider (Phase 1 drift, but relevant)
- The plan specified self-issued JWT (`app_secret_key`). The implementation uses
  **Supabase Auth** JWTs, validated in `middleware/auth.py`, with auto-provisioned
  users keyed by `supabase_uid`.
- This is internally consistent (frontend sends Supabase token, backend verifies
  it), so Phase 2 *auth* works — but it is a deviation from the plan that should be
  acknowledged. No action required for Phase 2 completion, flagged for record.

---

## 3. What IS Working (credit where due)
- Course CRUD (API + UI) ✅
- Document upload + delete + dedup (SHA-256) + upload-limit enforcement ✅
- `doc_type` Pro-only gating (`instructor_notes`, `slides`) ✅
- File-size limits per tier ✅
- `RoadmapNode` model + migration table fully defined and ready ✅
- Groq circuit-breaker router (solid engineering, just wrong vendor per plan) ✅
- Tier gate + billing limits endpoint (`/billing/limits`) wired to UI ✅

---

## 4. Recommended Remediation Order

1. **Decide the provider/storage question** (Groq vs Gemini; R2 vs Supabase). If
   keeping the plan's design, swap to Gemini adapter + Supabase signed-URL upload.
   If keeping current choices, update the plan to reflect them. *(Blocker for
   everything else being "to spec.")*
2. **Build roadmap extraction** (`services/roadmap_extraction.py` + prompt +
   `routes/roadmap_nodes.py`: list / confirm / update / delete). Insert
   `roadmap_nodes` with placeholder + confidence flags. *(Core gap.)*
3. **Move extraction to a background task** with `202 + job_id` and a
   `GET /documents/{id}/extraction-status` endpoint; offload blocking calls with
   `run_in_threadpool` so the event loop isn't blocked.
4. **Fix the tier gate**: roadmap extraction = Free (within 3-doc limit); topic
   extraction = Pro.
5. **Build the Confirm-before-lock UI** (roadmap review page) with edit/confirm/
   delete + placeholder visuals + nudges. Add a Roadmap tab to `CoursePage`.
6. **Wire frontend polling** to `processing_status` with proper loading/error
   states using `error_message`.
7. **(Should)** Add multi-document merge (syllabus + academic calendar RAG).
8. **Add Phase 2 tests** (upload limits, extraction, status, confirm flow) + CI.
9. **(Phase 4 hook)** Auto-create stub notes per confirmed node.

---

## 5. Summary Verdict

| Dimension | Verdict |
|---|---|
| Phase 2 exit criteria met? | ❌ No |
| Core roadmap extraction | ❌ Not implemented |
| Confirm-before-lock UI | ❌ Not implemented |
| Status/polling | ❌ Not implemented |
| Storage/LLM per plan | ⚠️ Diverged (R2 + Groq) |
| Wrong-phase work shipped | ⚠️ Topic extraction (Phase 3) built early & mis-priced |
| Tests | ❌ None for Phase 2 |
| Foundation (Course/Document CRUD, limits) | ✅ Solid |

**Bottom line:** Build the roadmap extraction pipeline, the confirm-before-lock
review UI, and the async status flow. Re-point the Pro gate so roadmap extraction
is Free (topics stay Pro). Groq + R2 are **approved deviations** — no
reconciliation needed.

---

## 6. Phase 2 Remediation Milestones (granular)

Each milestone is independently shippable and leaves the app in a working state,
so partial progress survives an interrupted session. Status legend: ⬜ pending ·
🟡 in progress · ✅ done.

| ID | Milestone | What it delivers | Depends on |
|----|-----------|------------------|------------|
| **M0** | Fix "Create Course" modal | Modal visible/clickable (CSS + `open` class) | — |
| **M1** | Roadmap extraction service | `services/roadmap_extraction.py`: structured prompt → parse → insert `roadmap_nodes` (placeholder + confidence flags) | — |
| **M2** | Roadmap nodes API + extract endpoint | `routes/roadmap_nodes.py` (list/get/update/confirm/delete); `POST /documents/{id}/extract-roadmap` (FREE); register router | M1 |
| **M3** | Async extraction + status polling | `BackgroundTasks` + 202; `GET /documents/{id}/extraction-status`; offload blocking calls (`run_in_threadpool`) | M1, M2 |
| **M4** | Frontend Roadmap tab + Confirm-before-lock UI | Roadmap tab in `CoursePage`; review/edit/confirm/delete; placeholder badges; poll `processing_status` | M2, M3 |
| **M5** | Tier gate correction | Roadmap extraction Free (within 3-doc limit); topic extraction stays Pro | M2 |
| **M6** | Phase 2 tests | pytest: upload limit, roadmap insert, status, confirm flow | M1–M3 |

### Out of scope (Phase 3+)
- Multi-document merge (RAG) — plan "Should"
- Stub-note auto-creation — plan Phase 4 hook
- Topic extraction review UI — Phase 3 (current `/extract` topic flow remains Pro-gated)

### Progress

| ID | Status | Notes |
|----|--------|-------|
| M0 | ✅ done | CSS + React `open` class fixed 2026-07-20 |
| M1 | ✅ done | `services/roadmap_extraction.py` — structured prompt → parse → insert `roadmap_nodes` |
| M2 | ✅ done | `routes/roadmap_nodes.py` (list/create/update/confirm/delete) + `POST /documents/{id}/extract-roadmap` (FREE) + router registered |
| M3 | ✅ done | `BackgroundTasks` + 202 + `GET /documents/{id}/extraction-status`; blocking calls offloaded via `run_in_threadpool` (also fixed in topic extraction) |
| M4 | ✅ done | `CoursePage.jsx` Roadmap tab + confirm-before-lock UI (edit/confirm/delete, placeholder badges, confidence) + poll on `processing_status`; roadmap CSS added |
| M5 | ✅ done | `extract-roadmap` is Free (within 3-doc limit); `extract` (topics) stays `require_pro` |
| M6 | ✅ done | Infra-free unit tests for roadmap parsing (9 passing). Full DB/API integration tests deferred (need a test DB + Groq/R2) |
