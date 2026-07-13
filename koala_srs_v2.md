**Koala**

Academic Roadmap, Notes & Progress Tracker

**Software Requirements Specification (SRS)**

Version 2.2

July 2026

| **Document Status** | Updated — Freemium/Pro Model Added (v2.2) |
| --- | --- |
| **Tech Stack** | Web: HTML/CSS/JS + Flask + PostgreSQL + REST API. Mobile: Native/cross-platform client consuming the same REST API. AI: Platform-managed LLM API keys; inference cost covered by subscription revenue |
| **Pricing Model** | Free tier (roadmap extraction, limited uploads) + Pro tier (AI topic extraction from notes/slides, higher limits) |
| **Target User** | Undergraduate / Postgraduate Students |
| **Prepared By** | Development Team |

# **Table of Contents**

# **1. Introduction**

## **1.1 Purpose**

This Software Requirements Specification (SRS) defines the complete functional and non-functional requirements for Koala v2.0 — a pivot from a manual academic self-tracking tool to an AI-assisted academic roadmap, note-taking, and progress-reflection application. This document supersedes Koala SRS v1.0 and is the single source of truth for all development decisions going forward.

## **1.2 Vision Statement**

Students start every semester with the same stack of syllabi and end it with nothing but a transcript of grades — no record of the effort, confusion, or growth in between. Koala closes that gap: it reads the documents a student already has, turns them into a living roadmap of the semester that fills itself in as the term unfolds, and lets every note, reflection, and self-assessment attach directly to the moment it belongs to. The result isn't another to-do list or another notes app — it's a single, evolving picture of how a student actually learns, so that by the end of a semester they understand not just what grade they got, but why.

## **1.3 Project Overview**

Koala v2.0 ingests a student's own course documents — syllabi, Course Learning Outcome (CLO) sheets, and instructor-provided notes/slides — and uses an AI extraction pipeline to build two things automatically:

1. A **semester roadmap** per course: assessments, deadlines, weights, and topics, with explicit placeholders for anything not yet announced, which the student progressively fills in and confirms.
2. A **topic checklist** per course: the list of topics actually covered in class, extracted from uploaded lecture notes/slides, which the student checks off as they complete each one — giving a running "X of Y topics done" view per course.

An Obsidian-style personal note-taking layer sits on top of both, so that notes, roadmap nodes, and topics are all part of the same linked graph rather than three disconnected tools. The self-assessment, goal-tracking, streak, and retrospective mechanics from v1.0 are retained, now attached to auto-generated roadmap nodes and topics instead of manually created ones.

## **1.4 Problem Statement**

| **Pain Point** | **Why existing tools (including Koala v1.0) fail here** |
| --- | --- |
| Cold-start setup fatigue | Manually re-creating every course, deadline, and weight from a syllabus PDF is grunt work on top of actual coursework — most students abandon the tool before it collects enough data to be useful. |
| Syllabi are incomplete on day one | Exam dates, rubrics, and topics are often announced mid-semester via email or LMS post, not in the original PDF. A one-time static import goes stale within weeks. |
| Notes live nowhere near the thing they're about | Lecture notes, deadlines, and reflections sit in three different apps with no link between them, so a student can't see whether thin notes on a topic actually predicted a weak grade. |
| No visibility into topic coverage | Students rarely have a clear, living view of "what have we actually covered so far, and what's left before the exam" — that picture exists only in scattered slide decks. |
| Students overestimate time and underestimate task complexity | Carried over from v1.0 — still unsolved by any generic task manager. |
| No personal record beyond the grade | After a semester ends, there is no record of how the student actually worked — only the final grade. |
| Goals set at the start of term are forgotten by week three | No accountability mechanism ties goals back to daily activity. |

## **1.5 Scope**

In scope for v2.2:

- **Free Tier**
  - Account creation and full course management (CRUD)
  - Document upload per course with enforced limits (see FR-00-05): syllabus and CLO files accepted
  - AI-assisted semester roadmap extraction from uploaded syllabus/CLO — powered by the platform's API key, no user key required
  - Confirm-and-edit step before any extracted data is treated as authoritative
  - Full manual roadmap/topic creation (no AI required)
  - Personal note-taking, bi-directional linking, backlinks, and graph view
  - Self-assessment logging, goal tracking, streaks, GPA calculator, profile, and retrospective

- **Pro Tier** (paid subscription)
  - Everything in Free, plus:
  - AI-assisted topic extraction from instructor notes/slides (PDF and PPT/PPTX) — the computationally heavier, per-file LLM call
  - Higher document upload limits (see FR-00-05)
  - Multi-document merge (syllabus + academic calendar) with RAG-based reconciliation
  - **GPA Calculator**: per-course grade tracking with credit hours, semester GPA, cumulative CGPA calculation, what-if scenario modelling, and integration with GPA-linked goals (available on both tiers)
  - Priority processing queue for extraction jobs

Out of scope for v2.2: LMS integration, real-time multi-user collaboration, automated grading, offline-first full-feature parity on mobile, notifications beyond streak/placeholder nudges, BYO API key support.

## **1.6 Definitions and Acronyms**

| **Term** | **Definition** |
| --- | --- |
| SRS | Software Requirements Specification |
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| CLO | Course Learning Outcomes — a document listing what a course is meant to teach |
| RAG | Retrieval-Augmented Generation — retrieving relevant text from documents before generating a structured answer; used when combining multiple/long source documents |
| LLM | Large Language Model — used for document extraction |
| Free Tier | The default account plan; includes roadmap extraction from syllabus with upload limits; no payment required |
| Pro Tier | The paid subscription plan; unlocks AI topic extraction from notes/slides and higher upload limits |
| Platform API Key | The LLM API key owned and managed by Koala; shared across all users; its cost is recovered through Pro subscriptions |
| Roadmap Node | A single extracted or manually created item on a course roadmap — an assignment, quiz, exam, project, or lab |
| Placeholder Node | A roadmap node whose details (date, weight, topic) are not yet known and must be filled in later |
| Topic | A single unit of course content extracted from instructor notes/slides, tracked as done/not-done |
| Topic Completion | A student's checked/unchecked status against a given topic |
| Confirm-before-lock | The mandatory review step where a student approves or edits AI-extracted data before it becomes authoritative |
| Note Graph | The bi-directional link structure connecting personal notes, roadmap nodes, and topics |
| Academic Profile | An auto-generated summary of patterns derived from a student's historical data |
| Retrospective | An end-of-semester summary report generated from all logged data |
| Upload Limit | The maximum number of documents a user may upload per course or per semester, enforced by their subscription tier |
| GPA | Grade Point Average — weighted average of grade points across courses in a semester |
| CGPA | Cumulative GPA — weighted average of grade points across all semesters |
| Grade Point | Numeric value assigned to a letter grade on a scale (4.0, 5.0, or 10-point) |
| Quality Points | Grade Points × Credit Hours for a single course; summed to compute GPA |
| Credit Hours | The unit-weight assigned to a course, reflecting contact hours per week |
| Grade Scale | The mapping of letter grades to numeric points (4.0 default; 5.0 and 10-point also supported) |
| What-If Scenario | A GPA simulation showing the required or predicted grade for a remaining course given a target or assumed grade |

# **2. System Overview**

## **2.1 System Architecture**

Koala v2.2 follows a three-tier architecture with an added AI extraction service, subscription gating, and two client types:

- **Web Frontend**: HTML, CSS, and JavaScript, communicating with the backend via REST API. Owns document upload, extraction review/confirmation, the notes graph view, retrospectives, and subscription/billing management.
- **Mobile Frontend**: Consumes the same REST API. Owns daily logging, topic check-offs, quick note capture, self-assessment prompts, and push notifications.
- **Backend**: Python/Flask exposing a RESTful API. Handles authentication, subscription tier enforcement, business logic, the extraction pipeline orchestration, and database access via SQLAlchemy ORM.
- **AI Extraction Service**: A backend module that calls the **platform-managed LLM API key** to produce structured roadmap and topic data. Free tier: roadmap extraction from syllabus only (rate-limited). Pro tier: topic extraction from notes/slides + multi-document RAG merge. The platform absorbs inference cost; Pro subscription revenue covers it.
- **Subscription & Billing**: A lightweight billing layer (e.g. Stripe or LemonSqueezy) that records the user's current plan and enforces tier gates on API routes.
- **Database**: PostgreSQL. Stores all user data, courses, documents, roadmap nodes, topics, notes, links, logs, goals, streaks, and subscription records.

## **2.2 User Roles**

| **Role** | **Description** |
| --- | --- |
| Free User | Uploads syllabi (within limit), gets AI roadmap extraction, uses all non-AI features. Cannot access topic extraction or multi-doc merge. |
| Pro User | All Free features plus AI topic extraction from notes/slides, higher upload limits, and priority extraction queue. |
| Admin (Future Scope) | Manages accounts, monitors AI cost dashboards, views aggregate anonymised platform statistics. Not implemented in v2.0. |

## **2.3 Platform Responsibility Split**

| **Activity** | **Web** | **Mobile** |
| --- | --- | --- |
| Document upload (syllabus, CLO, notes/slides) | Primary | Supported |
| Reviewing/confirming AI-extracted roadmap & topics | Primary (keyboard + screen space for corrections) | View-only recommended |
| Daily logging (status updates, confidence, quick notes) | Supported | Primary |
| Topic check-off | Supported | Primary |
| Deep note writing & linking, graph view | Primary | Quick-capture only, triaged later on web |
| Self-assessment prompts | Supported | Primary |
| Streak nudges / at-risk notifications | Not applicable | Primary |
| Semester retrospective | Primary | Summary view only |

## **2.4 High-Level User Journey**

1. Student registers (Free tier by default) and creates a semester with its courses.
2. **[Free]** Student uploads a syllabus and/or CLO file per course — upload count enforced against their tier limit.
3. **[Free]** AI extracts a draft roadmap (assessments, dates, weights) from the syllabus using the platform API key — no user key needed.
4. Student reviews, edits, and confirms the extracted roadmap before it goes live.
5. **[Pro only]** Student uploads instructor notes/slides; AI extracts a topic checklist per course.
6. **[Free — manual fallback]** Free-tier users can still create topics manually without AI extraction.
7. Through the semester (mobile-first): student fills in placeholders, checks off topics, logs confidence/effort/reflection, and captures quick notes.
8. Student writes and links fuller notes on web; backlinks and the graph view surface connections.
9. Dashboard surfaces real-time insight — overdue items, topic coverage, confidence trends, streaks.
10. At semester end, student generates a Retrospective Report.
11. Profile page reflects cumulative patterns across all semesters.
12. Free users see a contextual upgrade prompt when they hit a limit or attempt a Pro-only action.

# **3. Functional Requirements**

Each requirement is tagged with a unique ID, priority (Must Have / Should Have / Nice to Have), and rationale.

## **FR-00: Subscription & Tier Management**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-00-01 | Must Have | Every new account is provisioned on the Free tier automatically | No friction to start |
| FR-00-02 | Must Have | System records each user's current plan (free / pro) and plan expiry date in the database | Gate enforcement requires a reliable source of truth |
| FR-00-03 | Must Have | Backend enforces tier gates on all Pro-only routes — a Free user calling a Pro route receives a clear `403 Upgrade Required` response | Prevents abuse and drives upgrade conversion |
| FR-00-04 | Must Have | UI displays the user's current plan and remaining upload quota on the profile/settings page | Transparency |
| FR-00-05 | Must Have | Upload limits are enforced per user per semester: **Free tier — 3 documents total per course** (syllabus-type only); **Pro tier — 20 documents per course** (all types) | Controls platform AI inference cost |
| FR-00-06 | Must Have | When a Free user reaches their upload limit, the system blocks further uploads and shows a clear upgrade prompt — it does not silently discard the file | Good UX; never lose user data |
| FR-00-07 | Should Have | Payment and plan upgrade flow is handled via an external billing provider (Stripe or LemonSqueezy); the backend only records the resulting plan status via webhook | Keeps billing logic out of core app |
| FR-00-08 | Should Have | Pro subscription can be cancelled; on cancellation, the user reverts to Free tier at the end of the billing period — previously extracted Pro data (topics, etc.) remains visible but no new Pro-only extractions are permitted | Graceful downgrade |
| FR-00-09 | Nice to Have | Admin dashboard shows: total users, free vs pro ratio, AI token cost per day, upload volume per tier | Operational cost visibility |

## **FR-01: User Authentication & Account Management**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-01-01 | Must Have | User can register with email and password | Core access requirement |
| FR-01-02 | Must Have | Passwords hashed before storage (bcrypt) | Security baseline |
| FR-01-03 | Must Have | User can log in and receive a JWT token | Stateless auth across web and mobile clients |
| FR-01-04 | Must Have | JWT validated on all protected routes | Prevent unauthorised access |
| FR-01-05 | Must Have | User can log out on either client independently | Session management |
| FR-01-06 | Should Have | User can update profile (name, institution, semester) | Personalisation |
| FR-01-07 | Nice to Have | Password reset via email | User convenience |

## **FR-02: Course Management**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-02-01 | Must Have | User can create a course (name, code, semester, academic year) | Foundation of data model |
| FR-02-02 | Must Have | User can view all courses for the current semester | Core dashboard feature |
| FR-02-03 | Must Have | User can edit or delete course details | Data accuracy |
| FR-02-04 | Should Have | User can archive a course at semester end | Historical record and profile building |
| FR-02-05 | Should Have | User can view archived (past semester) courses | Long-term profile continuity |

## **FR-03: Document Upload & Roadmap Extraction** *(Free + Pro)*

The core differentiating feature of v2.2. Available on the **Free tier**; roadmap extraction from syllabus is included at no cost. Upload counts are enforced against tier limits (FR-00-05).

| **ID** | **Priority** | **Tier** | **Requirement** | **Rationale** |
| --- | --- | --- | --- | --- |
| FR-03-01 | Must Have | Free | User can upload syllabus and CLO files per course in PDF format, up to the tier upload limit | Core input for extraction |
| FR-03-02 | Must Have | Free | System extracts a draft roadmap per course using the platform API key: assessment title, type, date, weight percentage, where determinable | Removes manual data-entry friction; no user key required |
| FR-03-03 | Must Have | Free | Any field the source document does not specify is created as an explicit placeholder, not silently omitted | Matches the reality that syllabi are incomplete on day one |
| FR-03-04 | Must Have | Free | Extracted roadmap is shown to the student for review before being marked confirmed | Prevents silent extraction errors from being treated as fact |
| FR-03-05 | Must Have | Free | Student can edit any extracted field, add missing nodes, or delete incorrect ones during review | Trust and correctness |
| FR-03-06 | Must Have | Free | If user has reached their upload limit, the upload endpoint rejects the file with a `403` and an upgrade prompt — no file is stored | FR-00-06 enforcement |
| FR-03-07 | Should Have | Pro | System can re-process an updated/revised syllabus and merge changes into the existing roadmap without duplicating confirmed nodes | Supports mid-semester revisions |
| FR-03-08 | Should Have | Pro | System combines multiple documents (syllabus + academic calendar) into one coherent roadmap via RAG | Reduces manual reconciliation; heavier inference cost justifies Pro gate |
| FR-03-09 | Should Have | Free | Extraction pipeline surfaces a confidence indicator per extracted field | Helps the student know what to double-check |
| FR-03-10 | Nice to Have | Free | User can manually add a roadmap node without any source document | Flexibility for courses without a formal syllabus |

## **FR-04: Course Notes Material Upload & Topic Extraction** *(Pro only for AI; Free for manual)*

> [!IMPORTANT]
> AI-powered topic extraction from notes/slides is a **Pro-only** feature. Free-tier users can still create topics manually. The upload of notes/slides files counts against the per-course upload limit (FR-00-05).

| **ID** | **Priority** | **Tier** | **Requirement** | **Rationale** |
| --- | --- | --- | --- | --- |
| FR-04-01 | Must Have | Pro | Pro user can upload instructor-provided notes/slides (PDF or PPT/PPTX) per course, counted against their higher upload limit | Source material for AI topic extraction |
| FR-04-02 | Must Have | Free | Free user can manually create topics (title, order) without any document upload or AI call | Full usability without a subscription; manual fallback always works |
| FR-04-03 | Must Have | Pro | System extracts a topic list from uploaded materials using the platform API key (one topic per distinct concept/lecture section) | Gives Pro students an automatic course content picture |
| FR-04-04 | Must Have | Pro | Each AI-extracted topic is linked back to its source document | Traceability |
| FR-04-05 | Must Have | Free+Pro | Student can review, edit, reorder, merge, or delete topics (whether AI-extracted or manually created) before confirming the list | Extraction and manual entry both need correction capability |
| FR-04-06 | Should Have | Pro | System appends newly extracted topics when additional materials are uploaded later in the semester | Materials arrive week by week |
| FR-04-07 | Should Have | Free+Pro | Topics can optionally be linked to a specific roadmap node | Connects coverage to assessments |
| FR-04-08 | Must Have | Free | When a Free user attempts to trigger AI topic extraction, the system returns a `403 Upgrade Required` with a contextual upgrade prompt | Gate enforcement with clear messaging |

## **FR-05: Topic Progress Tracking**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-05-01 | Must Have | Student can mark a topic as done/not-done via a checkbox | Core progress-reflection mechanic |
| FR-05-02 | Must Have | Per-course view shows "X of Y topics completed" and which specific topics remain | Directly answers "what's left before the exam" |
| FR-05-03 | Should Have | Marking a topic done prompts an optional quick confidence rating on that topic | Feeds the profile's subject-strength insight |
| FR-05-04 | Should Have | Topic completion can be linked to a note written about that topic | Connects coverage tracking to the notes layer |
| FR-05-05 | Nice to Have | Dashboard surfaces topics nearing a linked assessment that are still incomplete | Proactive urgency signal |

## **FR-06: Personal Notes System**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-06-01 | Must Have | User can create markdown notes, freestanding or attached to a course, roadmap node, or topic | Central knowledge-capture feature |
| FR-06-02 | Must Have | A stub note is auto-created for each roadmap node and topic, ready to be written into | Removes blank-page setup friction, mirroring the roadmap's cold-start fix |
| FR-06-03 | Must Have | User can link notes to each other using [[wikilink]] syntax | Obsidian-style bi-directional linking |
| FR-06-04 | Must Have | Backlinks are shown automatically on any note that is linked to from elsewhere | Surfaces connections without manual upkeep |
| FR-06-05 | Should Have | A graph view visualises notes, roadmap nodes, and topics as a connected network, filterable by course | Reveals cross-course/topic connections a flat list would hide |
| FR-06-06 | Should Have | Quick-capture note entry on mobile (short text or voice-to-text), triaged and linked properly later on web | Supports fast in-class capture without requiring full editing on a phone |
| FR-06-07 | Nice to Have | Full-text search across all notes | Usability at scale as notes accumulate |

## **FR-07: Self-Assessment Logging**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-07-01 | Must Have | Student sets a confidence level (1-5) when a roadmap node is created or confirmed | Baseline for the confidence-gap metric |
| FR-07-02 | Must Have | Upon marking a roadmap node Submitted, student logs actual hours spent and a self-rated quality (1-5) | Core data collection for the profile |
| FR-07-03 | Must Have | System records the gap between estimated and actual hours, and between confidence and self-rated quality | Self-awareness metric, carried over from v1.0 |
| FR-07-04 | Should Have | Student can add a brief reflection note at submission | Qualitative profile data |
| FR-07-05 | Should Have | System records how far in advance or how late the node was submitted relative to its deadline | Procrastination fingerprint |
| FR-07-06 | Nice to Have | Mid-task check-in (updated confidence, hours remaining) | Richer tracking data |

## **FR-08: Goal Setting**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-08-01 | Must Have | Student can create semester goals (title, description, target date, category) | Intentionality feature |
| FR-08-02 | Must Have | Goals can be marked complete, in progress, or abandoned | Status tracking |
| FR-08-03 | Should Have | Goals can be linked to one or more courses | Context-aware tracking |
| FR-08-04 | Should Have | Goals from past semesters remain visible | Long-term profile building |

## **FR-09: Dashboard**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-09-01 | Must Have | Dashboard shows active roadmap nodes sorted by deadline | Core usability |
| FR-09-02 | Must Have | Dashboard highlights overdue nodes and unresolved placeholders | Urgency and gap awareness |
| FR-09-03 | Must Have | Dashboard shows per-course topic completion at a glance | Direct visibility into coverage |
| FR-09-04 | Should Have | Dashboard shows weekly workload summary (estimated hours due this week) | Time-management support |
| FR-09-05 | Should Have | Dashboard shows current goal progress and streak counts | Motivation |
| FR-09-06 | Nice to Have | Dashboard surfaces one profile-derived insight (e.g. "you tend to under-note before Chemistry assessments") | Key differentiator, ties notes to outcomes |

## **FR-10: Streak System**

| **Streak** | **Trigger** | **Breaks When** |
| --- | --- | --- |
| Activity Streak | Student logs a meaningful action on a given day (fills a placeholder, checks off a topic, writes/edits a note, completes a self-assessment) | No qualifying action logged for a full calendar day |
| On-Time Submission Streak | Student marks a roadmap node submitted on or before its deadline | A node is submitted late or missed entirely past its deadline |

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-10-01 | Must Have | System tracks both streaks as defined above | Core engagement loop tied to meaningful behaviour, not arbitrary taps |
| FR-10-02 | Must Have | Streaks reset to 0 on their break condition and are displayed prominently | Visibility drives motivation |
| FR-10-03 | Must Have | Longest streak ever achieved is stored per user | Personal-record motivator |
| FR-10-04 | Should Have | Visual streak heatmap (GitHub-style) over the past 12 weeks | Reinforces visual progress |
| FR-10-05 | Should Have | At-risk warning pushed on mobile late in the day if no action logged yet | Prevents accidental streak breaks |
| FR-10-06 | Nice to Have | Milestone celebration messages (7/30/50/100 days) | Variable reward schedule |

## **FR-11: Academic Profile & Insights**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-11-01 | Must Have | Profile shows total nodes logged, submitted, and completion rate | Baseline stats |
| FR-11-02 | Must Have | Profile shows average estimated vs actual hours per course | Planning accuracy insight |
| FR-11-03 | Must Have | Profile shows confidence trend per course over time | Subject-relationship awareness |
| FR-11-04 | Should Have | Profile shows topic completion rate per course over time | New coverage-based insight |
| FR-11-05 | Should Have | Profile correlates note density (notes/links written) against self-rated quality or grade per topic/node | The key new differentiator — connects note-taking behaviour to outcomes |
| FR-11-06 | Should Have | Profile shows procrastination fingerprint and strongest/weakest subjects | Carried over from v1.0 |
| FR-11-07 | Nice to Have | Semester-by-semester comparison of all above metrics | Growth trajectory |

## **FR-12: Semester Retrospective Report**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-12-01 | Must Have | User can trigger a Retrospective Report for any completed semester | Core differentiating feature |
| FR-12-02 | Must Have | Report includes completion rate, average grade (if entered), total hours logged, and final topic coverage per course | Summary stats |
| FR-12-03 | Should Have | Report shows planning accuracy, goals set vs achieved, and procrastination trend vs previous semester | Growth metric and accountability |
| FR-12-04 | Should Have | Report highlights note-density-vs-outcome patterns discovered that semester | Ties the notes layer into the narrative |
| FR-12-05 | Should Have | Retrospective includes final semester GPA and CGPA if GPA entries have been recorded (FR-13) | Unifies academic outcome data in one place |
| FR-12-06 | Nice to Have | Report exportable as PDF | Shareability |

## **FR-13: GPA Calculator**

A built-in GPA tool that works both as a **standalone calculator** (independent of any other Koala data) and as an **integrated feature** (reading grades from roadmap nodes, linking to GPA goals, and feeding the retrospective report). All calculation logic runs client-side (no server round-trip needed); persistence of grade entries uses the backend.

### **FR-13-A: Per-Course Grade Entry**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-13-01 | Must Have | User can record a letter grade and credit hours for each course in the current semester | Foundation of GPA computation |
| FR-13-02 | Must Have | System accepts letter grades (A+/A/A-/B+/B/B-/C+/C/C-/D/F) and maps them to grade points automatically | Removes manual lookup friction |
| FR-13-03 | Must Have | User can type a percentage mark; system auto-converts to the nearest letter grade and grade point | Supports institutions that report scores as percentages |
| FR-13-04 | Must Have | Credit hours per course are editable; defaults can be pre-populated from course creation data | Accommodates variable-credit courses |
| FR-13-05 | Should Have | Grade point scale is user-selectable: 4.0 (default), 5.0, or 10-point | Accommodates different institutional grading systems |
| FR-13-06 | Should Have | If a roadmap node with `status = 'Graded'` and a non-null `grade` field exists, that value is suggested as the pre-fill for the grade entry | Reduces double-entry between roadmap and GPA calculator |

### **FR-13-B: Semester GPA Calculation**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-13-07 | Must Have | System computes semester GPA as Σ(Quality Points) / Σ(Credit Hours) and displays it in real time as grades are entered or changed | Live feedback drives engagement |
| FR-13-08 | Must Have | Display shows: GPA value, equivalent letter grade, total credit hours, total quality points, and a visual progress bar relative to the scale maximum | Comprehensive at-a-glance summary |
| FR-13-09 | Must Have | User can add or remove courses from the semester GPA table dynamically | Supports mid-semester course drops/adds |
| FR-13-10 | Should Have | Per-course mini breakdown (letter grade + progress bar) is shown alongside the aggregate GPA | Helps identify the weakest course at a glance |

### **FR-13-C: Cumulative GPA (CGPA)**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-13-11 | Must Have | User can enter historical semester GPAs (GPA + credit hours per past semester) to compute a running CGPA | Enables multi-semester tracking |
| FR-13-12 | Must Have | The current semester's GPA (from FR-13-07) is automatically included in the CGPA calculation as a live row | No duplication of entry |
| FR-13-13 | Must Have | CGPA display mirrors the semester GPA panel: value, letter grade, totals, and a bar | Consistent UI |
| FR-13-14 | Should Have | A GPA trend chart plots semester GPA across all recorded semesters in chronological order | Visualises academic trajectory over time |
| FR-13-15 | Should Have | User can add or remove past semester rows from the CGPA table | Corrects historical data entry errors |

### **FR-13-D: What-If Calculator**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-13-16 | Must Have | Given current GPA, current credit hours graded, remaining course credits, and a target GPA — system computes the minimum grade needed in the remaining course | Answers "what do I need to score in this exam?" |
| FR-13-17 | Must Have | If the required grade exceeds the maximum (e.g. >4.0 on a 4.0 scale) system clearly states the target is not achievable with those inputs | Prevents false hope |
| FR-13-18 | Must Have | Given a hypothetical grade for a remaining course — system computes the predicted end-of-semester GPA | Answers "what happens to my GPA if I get a B?" |
| FR-13-19 | Should Have | A scenario comparison table shows all common letter grades for a given remaining course and the resulting GPA and goal status for each | Eliminates repetitive manual recalculation |

### **FR-13-E: Standalone Calculator Mode**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-13-20 | Must Have | A dedicated "Standalone" tab allows entry of arbitrary course names, credits, and grades without linking to any Koala course or semester | Users who just want a quick GPA check without setting up a full semester |
| FR-13-21 | Must Have | Standalone calculator output (GPA, letter grade, quality points) is computed entirely client-side with no data persisted | Privacy; no unintended record creation |
| FR-13-22 | Should Have | Standalone mode shows a grade-scale reference table (A → 4.0, B+ → 3.3, etc.) for the selected scale | Reduces lookups |

### **FR-13-F: Goal Integration**

| **ID** | **Priority** | **Requirement** | **Rationale** |
| --- | --- | --- | --- |
| FR-13-23 | Should Have | A goal can be flagged as a "GPA Goal" with a target GPA value (e.g. "Achieve ≥ 3.3 this semester") | Connects the goal system to the GPA calculator |
| FR-13-24 | Should Have | The GPA Calculator page displays all active GPA-linked goals with a live status indicator (Met / X away / Not achievable) that updates as grades are changed | Motivational feedback loop |
| FR-13-25 | Should Have | The Goal Status panel inside the GPA Calculator checks at minimum: target GPA met, Dean's List threshold (configurable), and academic probation risk (< 2.0) | Common milestone awareness |
| FR-13-26 | Nice to Have | Dashboard surfaces a GPA goal progress summary card when at least one GPA goal is active | Brings GPA tracking into the daily view |

# **4. Non-Functional Requirements**

## **NFR-01: Performance**

| **ID** | **Requirement** |
| --- | --- |
| NFR-01-01 | API endpoints respond within 500ms under normal single-user load |
| NFR-01-02 | Roadmap/topic extraction jobs run asynchronously and notify the client on completion rather than blocking the UI |
| NFR-01-03 | Dashboard loads all widgets within 2 seconds on standard broadband/mobile data |
| NFR-01-04 | Profile computation completes within 1 second for up to 1,000 roadmap nodes and notes combined |

## **NFR-02: Security & Privacy**

| **ID** | **Requirement** |
| --- | --- |
| NFR-02-01 | Passwords hashed with bcrypt (cost factor ≥ 12) |
| NFR-02-02 | JWT tokens expire after 24 hours and are validated on every protected endpoint |
| NFR-02-03 | User-supplied AI API keys are encrypted at rest and never exposed in logs or client-side code |
| NFR-02-04 | Uploaded documents (syllabi, instructor slides) are stored per-user and never shared across accounts |
| NFR-02-05 | User A must never be able to access, modify, or delete User B's data |
| NFR-02-06 | All API inputs validated and sanitised server-side |
| NFR-02-07 | HTTPS required in any deployed environment |

## **NFR-03: Usability**

| **ID** | **Requirement** |
| --- | --- |
| NFR-03-01 | Application usable without training or documentation |
| NFR-03-02 | Extracted roadmap/topic data is visually distinguished by state: confirmed, placeholder, or low-confidence — never presented as fact silently |
| NFR-03-03 | Web interface responsive from 1024px to 1440px+; mobile interface optimised for one-handed use |
| NFR-03-04 | Self-assessment and topic check-off interactions completable in under 30 seconds on mobile |
| NFR-03-05 | Error and extraction-failure states show human-readable messages with a manual-entry fallback |

## **NFR-04: Reliability & Maintainability**

| **ID** | **Requirement** |
| --- | --- |
| NFR-04-01 | No user data lost on server restart — all state persisted to the database |
| NFR-04-02 | Extraction failures fall back gracefully to an empty roadmap/topic list the student can build manually, never a blocked onboarding flow |
| NFR-04-03 | Codebase separates routes, models, services, and the extraction pipeline into distinct modules |
| NFR-04-04 | Schema changes managed through migrations only |

## **NFR-05: AI Extraction Quality**

| **ID** | **Requirement** |
| --- | --- |
| NFR-05-01 | No extracted field is written to the authoritative roadmap/topic list without passing through the confirm-before-lock review step |
| NFR-05-02 | Extraction pipeline must handle common syllabus formats (tabular, prose, scanned/OCR'd PDF) with a stated confidence score per field |
| NFR-05-03 | Re-extraction from an updated document must not duplicate already-confirmed nodes or topics |

## **NFR-06: Scalability (future consideration)**

| **ID** | **Requirement** |
| --- | --- |
| NFR-06-01 | Database schema supports multiple users without schema changes |
| NFR-06-02 | Extraction and profile computation logic abstracted into services for future caching/queueing |
| NFR-06-03 | REST API remains stateless to support horizontal scaling and multiple client types |

# **5. Database Schema**

All tables include created_at and updated_at timestamps. Foreign keys use ON DELETE CASCADE unless otherwise noted.

### **users**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| email | VARCHAR(255) UNIQUE NOT NULL | Login identifier |
| password_hash | VARCHAR(255) NOT NULL | bcrypt hashed |
| full_name | VARCHAR(255) | |
| institution | VARCHAR(255) | |
| ai_api_key_encrypted | TEXT | BYO key for extraction, encrypted at rest |

### **courses**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| user_id | INTEGER REFERENCES users(id) | Owner |
| name | VARCHAR(255) NOT NULL | |
| code | VARCHAR(50) | |
| semester | VARCHAR(50) NOT NULL | |
| academic_year | VARCHAR(20) | |
| is_archived | BOOLEAN DEFAULT FALSE | |
| credit_hours | DECIMAL(4,2) | Credit hours / units for this course; used by GPA calculator (FR-13-04) |
| grade_letter | VARCHAR(5) | Final letter grade (A+/A/A-/B+…F); nullable until graded; feeds GPA calculator (FR-13-06) |
| grade_scale | VARCHAR(10) DEFAULT '4.0' | Grade point scale used for this course: '4.0' \| '5.0' \| '10' (FR-13-05) |

### **documents**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| course_id | INTEGER REFERENCES courses(id) | |
| user_id | INTEGER REFERENCES users(id) | |
| doc_type | VARCHAR(50) | 'syllabus' \| 'clo' \| 'instructor_notes' \| 'slides' \| 'academic_calendar' |
| file_name | VARCHAR(255) | |
| storage_path | TEXT | |
| processing_status | VARCHAR(50) DEFAULT 'pending' | 'pending' \| 'processed' \| 'failed' |
| processed_at | TIMESTAMP | |

### **roadmap_nodes**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| course_id | INTEGER REFERENCES courses(id) | |
| user_id | INTEGER REFERENCES users(id) | Denormalised for query efficiency |
| source_document_id | INTEGER REFERENCES documents(id) NULLABLE | Null if manually created |
| title | VARCHAR(255) NOT NULL | |
| node_type | VARCHAR(100) | 'Assignment' \| 'Quiz' \| 'Exam' \| 'Project' \| 'Lab' \| 'Other' |
| deadline | TIMESTAMP NULLABLE | Null while a placeholder |
| weight_percent | DECIMAL(5,2) NULLABLE | |
| is_placeholder | BOOLEAN DEFAULT TRUE | Flips false once confirmed with real data |
| is_confirmed | BOOLEAN DEFAULT FALSE | Set true only after student review |
| estimated_hours | DECIMAL(5,2) | |
| actual_hours | DECIMAL(5,2) | |
| confidence_at_creation | SMALLINT CHECK (1-5) | |
| status | VARCHAR(50) DEFAULT 'Pending' | 'Pending' \| 'In Progress' \| 'Submitted' \| 'Graded' |
| grade | DECIMAL(5,2) | |
| submitted_at | TIMESTAMP | |

### **topics**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| course_id | INTEGER REFERENCES courses(id) | |
| source_document_id | INTEGER REFERENCES documents(id) NULLABLE | |
| linked_node_id | INTEGER REFERENCES roadmap_nodes(id) NULLABLE | Optional link to the assessment it feeds into |
| title | VARCHAR(255) NOT NULL | |
| order_index | INTEGER | Position in the course's topic sequence |
| is_confirmed | BOOLEAN DEFAULT FALSE | Set true after student review of extracted topics |

### **topic_completions**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| topic_id | INTEGER REFERENCES topics(id) | |
| user_id | INTEGER REFERENCES users(id) | |
| is_completed | BOOLEAN DEFAULT FALSE | |
| confidence_rating | SMALLINT CHECK (1-5) NULLABLE | Optional, logged on completion |
| completed_at | TIMESTAMP NULLABLE | |
| linked_note_id | INTEGER REFERENCES notes(id) NULLABLE | |

### **notes**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| user_id | INTEGER REFERENCES users(id) | |
| course_id | INTEGER REFERENCES courses(id) NULLABLE | |
| roadmap_node_id | INTEGER REFERENCES roadmap_nodes(id) NULLABLE | |
| topic_id | INTEGER REFERENCES topics(id) NULLABLE | |
| title | VARCHAR(255) | |
| content | TEXT | Markdown source |
| is_stub | BOOLEAN DEFAULT FALSE | True for auto-created empty stub notes |

### **note_links**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| source_note_id | INTEGER REFERENCES notes(id) | |
| target_note_id | INTEGER REFERENCES notes(id) | |

### **self_assessment_logs**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| roadmap_node_id | INTEGER REFERENCES roadmap_nodes(id) UNIQUE | |
| quality_self_rating | SMALLINT CHECK (1-5) | |
| mood_energy | SMALLINT CHECK (1-5) NULLABLE | |
| reflection_note | TEXT | |
| hours_before_deadline | DECIMAL(8,2) | Positive = early, negative = late |

### **goals**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| user_id | INTEGER REFERENCES users(id) | |
| title | VARCHAR(255) NOT NULL | |
| description | TEXT | |
| category | VARCHAR(100) | |
| semester | VARCHAR(50) | |
| target_date | DATE | |
| status | VARCHAR(50) DEFAULT 'Active' | 'Active' \| 'Complete' \| 'Abandoned' |
| is_gpa_goal | BOOLEAN DEFAULT FALSE | Marks this as a GPA-linked goal (FR-13-23) |
| gpa_target | DECIMAL(4,2) NULLABLE | Target GPA value for a GPA goal (e.g. 3.30) (FR-13-23) |

### **gpa_entries**

Stores user-persisted semester GPA history and current-semester per-course grade entries for the integrated GPA calculator. Standalone calculator data is **never persisted** (client-side only).

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| user_id | INTEGER REFERENCES users(id) ON DELETE CASCADE | Owner |
| semester | VARCHAR(50) NOT NULL | e.g. "Fall 2025" |
| academic_year | VARCHAR(20) | e.g. "2025-2026" |
| entry_type | VARCHAR(20) NOT NULL | 'course' (per-course entry) \| 'historical' (past-semester aggregate for CGPA) |
| course_id | INTEGER REFERENCES courses(id) ON DELETE SET NULL NULLABLE | Linked to a real course if entry_type = 'course' |
| course_label | VARCHAR(255) | Display name; copied from course or entered freely for historical rows |
| credit_hours | DECIMAL(4,2) NOT NULL | Credit hours for this entry |
| grade_letter | VARCHAR(5) | Letter grade for entry_type = 'course' rows |
| semester_gpa | DECIMAL(4,2) | Aggregate semester GPA for entry_type = 'historical' rows |
| grade_scale | VARCHAR(10) DEFAULT '4.0' | Grade point scale: '4.0' \| '5.0' \| '10' |
| created_at | TIMESTAMPTZ DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ DEFAULT NOW() | |

### **streaks**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| user_id | INTEGER PRIMARY KEY REFERENCES users(id) | |
| activity_streak_count | INTEGER DEFAULT 0 | |
| on_time_streak_count | INTEGER DEFAULT 0 | |
| longest_activity_streak | INTEGER DEFAULT 0 | |
| longest_on_time_streak | INTEGER DEFAULT 0 | |
| last_activity_date | DATE | |

### **streak_daily_log**

| **Column** | **Type / Constraint** | **Notes** |
| --- | --- | --- |
| id | SERIAL PRIMARY KEY | |
| user_id | INTEGER REFERENCES users(id) | |
| log_date | DATE NOT NULL | |
| action_count | INTEGER DEFAULT 0 | Used for the heatmap view |

# **6. REST API Specification**

Base URL: `/api/v1` — all protected endpoints require `Authorization: Bearer <token>`.

## **6.1 Authentication**

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| POST | /auth/register | Register new user |
| POST | /auth/login | Login — returns JWT |
| GET | /auth/me | Get current user profile |
| PUT | /auth/me | Update profile |
| PUT | /auth/ai-key | Store/update encrypted AI API key |

## **6.2 Courses**

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| GET | /courses | Get all courses for current user |
| POST | /courses | Create a course |
| GET | /courses/:id | Get single course with roadmap and topics |
| PUT | /courses/:id | Update course |
| DELETE | /courses/:id | Delete course (cascades) |
| PATCH | /courses/:id/archive | Toggle archive status |

## **6.3 Documents & Extraction**

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| POST | /courses/:id/documents | Upload a document (syllabus/CLO/notes/slides/calendar) |
| GET | /courses/:id/documents | List uploaded documents for a course |
| DELETE | /documents/:id | Delete an uploaded document |
| POST | /documents/:id/extract-roadmap | Trigger AI roadmap extraction (async) |
| POST | /documents/:id/extract-topics | Trigger AI topic extraction (async) |
| GET | /documents/:id/extraction-status | Poll extraction job status |

## **6.4 Roadmap Nodes**

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| GET | /roadmap-nodes | Get nodes (supports ?course_id=, ?status=, ?placeholder=) |
| POST | /roadmap-nodes | Create a node manually |
| PUT | /roadmap-nodes/:id | Update/edit a node (used during confirm-before-lock review) |
| POST | /roadmap-nodes/:id/confirm | Mark a reviewed node as confirmed |
| DELETE | /roadmap-nodes/:id | Delete a node |
| POST | /roadmap-nodes/:id/submit | Mark submitted — triggers self-assessment log creation |

## **6.5 Topics**

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| GET | /courses/:id/topics | Get topics for a course, with completion status |
| PUT | /topics/:id | Edit/reorder/merge a topic (review step) |
| POST | /topics/:id/confirm | Confirm an extracted topic |
| POST | /topics/:id/complete | Toggle completion, optional confidence rating |
| DELETE | /topics/:id | Delete a topic |

## **6.6 Notes**

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| GET | /notes | Get notes (supports ?course_id=, ?roadmap_node_id=, ?topic_id=) |
| POST | /notes | Create a note |
| PUT | /notes/:id | Update note content |
| DELETE | /notes/:id | Delete a note |
| GET | /notes/:id/backlinks | Get notes linking to this note |
| GET | /notes/graph | Get graph data (nodes + edges) for a course or globally |

## **6.7 Goals**

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| GET | /goals | Get all goals (supports ?semester=, ?is_gpa_goal=) |
| POST | /goals | Create goal (now accepts is_gpa_goal, gpa_target fields) |
| PUT | /goals/:id | Update goal |
| DELETE | /goals/:id | Delete goal |

## **6.8 Streaks**

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| GET | /streaks/me | Get current streaks and longest records |
| POST | /streaks/activity | Log a qualifying action |
| GET | /streaks/heatmap | Get daily activity log for past 84 days |

## **6.9 Profile \& Insights**

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| GET | /profile/summary | Aggregate stats: totals, completion rate, avg hours |
| GET | /profile/patterns | Procrastination fingerprint, strongest/weakest subjects |
| GET | /profile/confidence-trend | Confidence over time per course |
| GET | /profile/topic-coverage | Topic completion rate per course over time |
| GET | /profile/note-correlation | Note density vs. self-rated quality/grade correlation |
| GET | /profile/retrospective/:semester | Generate retrospective report for a given semester (now includes GPA if entries exist) |

## **6.10 GPA Calculator**

> All GPA *computation* is client-side. These endpoints only handle **persistence** of grade entries and fetching goal context. Standalone calculator data is never sent to the server.

| **Method** | **Endpoint** | **Description** |
| --- | --- | --- |
| GET | /gpa/entries | Get all GPA entries for the current user (supports ?semester=, ?entry_type=) |
| POST | /gpa/entries | Create a GPA entry (course grade or historical semester aggregate) |
| PUT | /gpa/entries/:id | Update a GPA entry (e.g. change grade after result release) |
| DELETE | /gpa/entries/:id | Delete a GPA entry |
| GET | /gpa/semester-summary | Returns pre-aggregated semester GPA + CGPA for all recorded semesters (server-computed for profile/retrospective integration) |
| GET | /gpa/goals | Returns all active GPA goals (is_gpa_goal=true) with their target_gpa and current tracking status |

# **7. AI Extraction Pipeline**

## **7.1 Approach**

- **Single document (e.g. one syllabus):** one structured-output LLM call (function calling / JSON schema) is sufficient — no retrieval step needed.
- **Multiple documents per course or semester (e.g. syllabus + academic calendar + a mid-semester addendum):** a lightweight retrieval step selects relevant passages from each document before the extraction call, so the roadmap can be updated incrementally without re-processing everything.
- **Instructor notes/slides for topic extraction:** each uploaded file is processed independently and appended to the course's topic list, since new materials typically arrive week by week rather than all at once.

## **7.2 Confirm-before-lock (mandatory)**

No extracted field — roadmap node or topic — is treated as authoritative until the student has reviewed it. Every extracted item is shown in one of three states: **Confirmed**, **Needs Review** (default state on first extraction), or **Placeholder** (field intentionally left blank because the source document didn't specify it). This step exists because syllabus formats are inconsistent (tables, prose, scanned/OCR'd PDFs) and extraction will sometimes misread a date or weight — the app must never let a wrong auto-extracted deadline masquerade as a real one.

## **7.3 Cost, Privacy & Tier Model**

### Platform API Key Architecture
- **Koala manages a single LLM API key** (recommended: Gemini API for cost-efficiency). All extraction calls are made server-side using this key — users never see, provide, or manage any AI credentials.
- **Free tier inference cost** is subsidised by the platform. Roadmap extraction from a typical syllabus costs ~$0.001–$0.003 per call (Gemini Flash pricing). With upload limits of 3 docs/course, worst-case cost per free user per semester is very small (~$0.01–0.03).
- **Pro tier inference cost** covers heavier topic extraction from slides/notes (more tokens, more calls). Pro subscription revenue is designed to cover this: even at $3–5/mo per Pro user with ~10 extraction calls/semester, the margin is comfortable.

### Tier Enforcement
| Action | Free | Pro |
| --- | --- | --- |
| Syllabus/CLO upload | ✅ Up to 3/course | ✅ Up to 20/course |
| Notes/slides upload | ❌ Blocked | ✅ Up to 20/course |
| Roadmap extraction (AI) | ✅ Included | ✅ Included |
| Topic extraction (AI) | ❌ `403 Upgrade Required` | ✅ Included |
| Multi-doc RAG merge | ❌ Blocked | ✅ Included |
| Manual topic creation | ✅ Unlimited | ✅ Unlimited |
| All non-AI features | ✅ Full access | ✅ Full access |

### Privacy
- Uploaded documents may contain instructor names and institution-specific policy text. This is disclosed clearly before the first upload.
- Documents are stored per-user and never shared across accounts or used to train models.
- Extraction failures fall back to an empty, manually-editable roadmap/topic list — onboarding is never blocked by an AI error.

### AI Cost Control Mechanisms
- **Rate limiting**: Free tier capped at 3 extraction calls per course per semester (enforced by upload limit).
- **File size limit**: Maximum 10 MB per uploaded file for Free; 25 MB for Pro — prevents runaway token usage.
- **Async queue**: All extraction jobs run asynchronously. A per-user concurrency limit (1 active job for Free, 3 for Pro) prevents abuse.
- **Token budget**: Extraction prompts are structured to request only the needed JSON schema, keeping token counts predictable.

# **8. Recommended Project Structure**

## **8.1 Backend (Flask)**

```
Koala-backend/
├── app/
│   ├── __init__.py            # App factory, register blueprints
│   ├── models/                # SQLAlchemy models
│   ├── routes/                # Blueprint route files
│   ├── services/
│   │   ├── extraction_service.py   # Roadmap & topic extraction orchestration
│   │   ├── profile_service.py
│   │   └── notes_service.py        # Link parsing, backlinks, graph data
│   ├── schemas/                # Marshmallow schemas
│   └── utils/                  # JWT helpers, error handlers, encryption
├── migrations/
├── tests/
├── config.py
├── requirements.txt
└── run.py
```

## **8.2 Web Frontend**

```
Koala-web/
├── index.html          # Dashboard
├── login.html
├── courses.html
├── document-review.html   # Confirm-before-lock review UI
├── roadmap.html
├── topics.html
├── notes.html           # Editor + graph view
├── profile.html
├── retrospective.html
├── css/
├── js/
│   ├── api.js
│   ├── extraction.js    # Polling extraction jobs, rendering review states
│   ├── notes-graph.js
│   └── ...
└── assets/
```

## **8.3 Mobile App**

```
Koala-mobile/
├── screens/
│   ├── Dashboard
│   ├── TopicChecklist
│   ├── QuickNoteCapture
│   ├── SelfAssessmentPrompt
│   └── RetrospectiveSummary   # Read-only summary view
├── services/
│   ├── api.ts
│   ├── sync.ts             # Offline quick-capture, sync-on-reconnect
│   └── notifications.ts    # Streak / placeholder nudges
└── ...
```

# **9. Implementation Phases**

| **Phase** | **Name** | **Deliverables** |
| --- | --- | --- |
| Phase 1 | Foundation | Auth, course CRUD (with credit_hours/grade_letter), db schema (gpa_entries), basic web shell |
| Phase 2 | Roadmap Extraction | Document upload, single-document extraction, confirm-before-lock review UI, placeholder handling |
| Phase 3 | Topic Extraction & Checklist | Instructor notes/slides upload, topic extraction, review UI, completion checkboxes, per-course coverage view |
| Phase 4 | Notes System | Markdown notes, stub auto-creation, wikilinks, backlinks, graph view |
| Phase 5 | Self-Assessment & Goals | Submission flow, confidence/quality gap tracking, goals CRUD (inc. GPA goal type) |
| Phase 5.5 | GPA Calculator | Semester GPA entry, live calculation, CGPA historical rows, what-if mode, goal integration |
| Phase 6 | Mobile App v1 | Daily logging, topic check-off, quick-capture, self-assessment, sync; GPA read-only view |
| Phase 7 | Profile, Streaks & Insights | Profile computation, note-density correlation, streak system, heatmap; GPA trend chart |
| Phase 8 | Retrospective & Polish | Retrospective report, mobile notifications, responsive polish, error handling |

# **10. Risks, Assumptions & Constraints**

## **10.1 Assumptions**

- A single developer is building this project initially.
- Application runs on free/low-cost hosting tiers at launch (~50 users).
- Free-tier inference cost (roadmap extraction) is low enough (~$0.01–0.03/user/semester) to absorb with zero initial revenue.
- A meaningful fraction of active users (target: 10–15%) will convert to Pro within 6 months.
- Data volume per user will not exceed roughly 1,000 roadmap nodes/notes combined.

## **10.2 Risks**

| **Risk** | **Likelihood** | **Mitigation** |
| --- | --- | --- |
| Extraction accuracy varies widely across syllabus formats | High | Mandatory confirm-before-lock step; never auto-apply unreviewed data; manual-entry fallback always available |
| Free-tier AI cost exceeds revenue at early scale | Medium | Upload limits cap worst-case spend; monitor cost dashboard (FR-00-09); can tighten limits without code changes |
| Low Pro conversion rate makes AI cost unsustainable | Medium | Keep Free tier genuinely useful (full manual mode + roadmap AI); position Pro on the high-value pain point (topic extraction = most time-saving feature) |
| LLM API pricing changes (platform key model) | Low-Medium | Abstract the LLM provider behind an adapter; can switch providers or tighten token budgets without changing product behaviour |
| Uploaded instructor materials raise copyright/privacy questions | Medium | Store per-user only, never shared or used to train models, disclosed clearly in privacy notice |
| Mobile/web sync conflicts (edits on both while offline) | Medium | Last-write-wins with a visible conflict flag on notes; keep mobile edits scoped to append-mostly actions |
| Scope creep across two clients and an AI pipeline | High | Strictly sequence phases; mobile v1 ships with a deliberately reduced feature set (see 2.3) |
| Note graph becomes noisy/unmanageable at scale | Low-Medium | Filter graph view by course by default; full-text search as a fallback discovery method |

## **10.3 Constraints**

- Backend/web tech stack: HTML/CSS/JS, Python/Flask, PostgreSQL, REST API.
- AI extraction uses a **platform-managed API key**; BYO key support is explicitly out of scope.
- Upload limits (3 docs/course Free, 20 docs/course Pro) are a hard constraint driven by AI cost control — not a soft suggestion.
- Billing provider (Stripe or LemonSqueezy) must support webhook-based plan updates; the app never processes payment card data directly.
- Budget at launch: near-zero infra cost; Pro revenue covers AI inference as the user base grows.

# **11. Glossary**

| **Term** | **Definition** |
| --- | --- |
| Roadmap Node | A single assessment item (assignment, quiz, exam, project, lab) on a course's semester roadmap, either extracted or manually created. |
| Placeholder Node | A roadmap node with one or more fields intentionally left blank because the source document didn't specify them yet. |
| Confirm-before-lock | The mandatory student review step that must occur before any AI-extracted data is treated as authoritative. |
| Topic | A discrete unit of course content extracted from instructor notes/slides, tracked as complete or incomplete. |
| Topic Coverage | The proportion of a course's topics marked complete at a given point in the semester. |
| Note Graph | The bi-directional link structure connecting personal notes, roadmap nodes, and topics, viewable as a network graph. |
| Note-Density Correlation | A profile insight comparing how much a student wrote/linked notes on a topic or node against their self-rated quality or grade for it. |
| Free Tier | Default account plan: roadmap extraction from syllabus included; up to 3 doc uploads per course per semester; no payment needed. |
| Pro Tier | Paid subscription plan: adds AI topic extraction from notes/slides, up to 20 doc uploads per course, priority queue. |
| Platform API Key | The LLM API key owned and managed by Koala used for all extraction calls; its cost is recovered via Pro subscriptions. |
| Upload Limit | Max documents a user may upload per course per semester, enforced by their plan tier (3 = Free, 20 = Pro). |
| Confidence Gap | The difference between confidence rated at node creation and quality self-rated at submission. |
| Hours Gap | The difference between estimated and actual hours logged on a roadmap node. |
| Procrastination Fingerprint | A computed metric showing how far before or after a deadline a student typically submits work. |
| Academic Profile | The auto-generated view of patterns derived from a student's historical roadmap, topic, and note data across all semesters. |
| Retrospective Report | An end-of-semester summary generated from all logged data for that semester. |
| GPA | Grade Point Average — weighted average of grade points across courses in a semester. Formula: Σ(grade_points × credit_hours) / Σ(credit_hours). |
| CGPA | Cumulative GPA — weighted average of semester GPAs across all recorded semesters. |
| Grade Point | The numeric value mapped from a letter grade on the selected scale (e.g. B+ = 3.3 on 4.0 scale). |
| Quality Points | Grade Points × Credit Hours for a single course entry; summed across all courses to produce the GPA numerator. |
| Credit Hours | The unit-weight of a course reflecting instructional contact hours per week. |
| What-If Scenario | A GPA simulation: either computing the minimum grade needed in a remaining course to hit a target GPA, or predicting the resulting GPA given an assumed grade. |
| GPA Goal | A goal (FR-08 type) flagged with a target GPA value, displayed with a live tracking status in the GPA Calculator. |
| Standalone Calculator | A GPA calculator mode operating entirely on user-typed inputs with no link to any Koala course or semester; results are never persisted. |

_Koala SRS v2.2 — End of Document_

_This document supersedes v2.1 (GPA Calculator) and v2.0. It should be reviewed at the start of each development phase._
