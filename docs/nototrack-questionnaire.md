# NotoTrack — Project Completion Questionnaire

**For:** lsr2025 (Project Owner)
**From:** oluwatosindot (Developer)
**Date:** 2026-05-17

---

> **How to use this file:**
> - Tick `[ ]` → `[x]` next to each question you have answered
> - Type your answer in the `Answer:` line directly below the question
> - You can edit this file directly on GitHub — no software needed
> - Questions marked 🔴 **BLOCKING** must be answered before I can continue

---

## Section 1 — Repository Scope 🔴 BLOCKING

- [ ] **Q1.** Is this repository the full notoTrack application, or a patch/fix submission on top of a larger codebase elsewhere? *(There is no `package.json` or root app config — this looks like a partial repo, which changes how I work on it significantly.)*
  > **Answer:**

- [ ] **Q2.** If this is a patch/fix submission — where is the main notoTrack application repository? *(Please share a GitHub URL, private repo invite, or zip of the full codebase.)*
  > **Answer:**

- [ ] **Q3.** What branch should be treated as production-ready? *(The current branch is `olu` — is `main` the stable base, or is a different branch used for deployments?)*
  > **Answer:**

---

## Section 2 — Supabase Project 🔴 BLOCKING

- [ ] **Q4.** What is the Supabase project URL for notoTrack? *(The codebase references 593 live assessments — this project already exists. Please share the project URL, e.g. `https://xxxx.supabase.co`)*
  > **Answer:**

- [ ] **Q5.** What is the Supabase anon (public) key? *(Safe to share — this is the public client-side key, not the service role key.)*
  > **Answer:**

- [ ] **Q6.** Does a `.env` file exist for this project? *(If yes, please share the variable names — not the values — so I can confirm I have all required keys.)*
  > **Answer:**

- [ ] **Q7.** Should I have access to the Supabase dashboard, or will you apply schema/migration changes yourself? *(Determines how I deliver database fixes.)*
  > **Answer:**

---

## Section 3 — Deployment & Hosting 🔴 BLOCKING

- [ ] **Q8.** Is notoTrack currently deployed anywhere? *(If yes, please share the URL so I can test the live environment.)*
  > **Answer:**

- [ ] **Q9.** Where should the production deployment live?
  - [ ] Vercel
  - [ ] Netlify
  - [ ] Cloudflare Pages
  - [ ] Self-hosted / VPS
  - [ ] Not yet decided
  > **Answer:**

- [ ] **Q10.** Is there a custom domain for notoTrack? *(e.g., `nototrack.yamiminesolutions.co.za`)*
  > **Answer:**

- [ ] **Q11.** Who manages DNS and hosting credentials — you, or the client (Yami Mine Solutions / IDC SEF)? *(Determines who configures the domain and deployment pipeline.)*
  > **Answer:**

---

## Section 4 — Python Report Script vs. Frontend Integration

- [ ] **Q12.** Is the Python `reportlab` script the intended long-term solution for compliance report generation, or should it be replaced with a frontend-native approach? *(A Python script requires a server to run — a frontend solution using jsPDF or a Supabase Edge Function would be fully serverless and easier to deploy.)*
  - [ ] Keep Python script — run it server-side
  - [ ] Replace with frontend-native (jsPDF / Edge Function)
  - [ ] Unsure — recommend an approach
  > **Answer:**

- [ ] **Q13.** If the Python script stays — what triggers it? *(Manual run by a developer, a cron job, an API endpoint, or a user button in the dashboard?)*
  > **Answer:**

- [ ] **Q14.** Is there a server or VM where the Python script is currently (or will be) hosted? *(e.g., Ubuntu VPS, AWS Lambda, local machine — needed to understand the runtime environment.)*
  > **Answer:**

---

## Section 5 — Report Formats Required

- [ ] **Q15.** Which report formats must the app produce at go-live?
  - [ ] PDF (compliance summary / full report)
  - [ ] CSV (raw assessment data export)
  - [ ] Excel (.xlsx)
  - [ ] All three
  > **Answer:**

- [ ] **Q16.** For PDF reports — what should they contain?
  - [ ] Compliance summary per spaza shop / business
  - [ ] Municipality-level aggregate report
  - [ ] Full raw assessment data
  - [ ] Executive summary for IDC / funder reporting
  > **Answer:**

- [ ] **Q17.** For CSV/Excel exports — is a specific column layout or template required? *(e.g., does the IDC Social Employment Fund or a municipality require a standard reporting format?)*
  > **Answer:**

- [ ] **Q18.** Is there a branded report template (logo, colours, header) that must be applied to PDF output? *(Please share any assets if yes.)*
  > **Answer:**

---

## Section 6 — Users & Roles

- [ ] **Q19.** Who are the end users of notoTrack? *(Tick all that apply.)*
  - [ ] Field assessors (capture data on-site at spaza shops)
  - [ ] Municipal compliance officers (review submitted assessments)
  - [ ] Yami Mine Solutions staff (manage assessors and reports)
  - [ ] IDC / funder representatives (read-only reporting view)
  - [ ] System administrator
  > **Answer:**

- [ ] **Q20.** How many active users are expected at go-live? *(Rough number is fine — helps size the Supabase tier.)*
  > **Answer:**

- [ ] **Q21.** Are field assessors expected to capture data on mobile devices without internet? *(i.e., is offline/sync capability required for the assessment form?)*
  - [ ] Yes — offline capture is required
  - [ ] No — always connected
  - [ ] Unsure
  > **Answer:**

- [ ] **Q22.** Who is the first admin user? *(Name + email — needed to seed the initial account and confirm role setup.)*
  > **Answer:**

---

## Section 7 — Assessment Data & Municipalities

- [ ] **Q23.** Which municipalities does the current dataset of 593 assessments span? *(Understanding coverage helps with the analytics dashboard filters and report groupings.)*
  > **Answer:**

- [ ] **Q24.** What compliance checklist / questionnaire do assessors complete on-site? *(If there is a paper form or Excel checklist, please share it — I need to verify the database schema matches all required fields.)*
  > **Answer:**

- [ ] **Q25.** Is the 593-assessment dataset in Supabase the live production data, or test/seed data? *(Determines how carefully I handle migrations.)*
  - [ ] Live production data — treat with care
  - [ ] Test / seed data — safe to reset if needed
  > **Answer:**

- [ ] **Q26.** Are there any data privacy or POPIA obligations around the spaza shop owner information captured during assessments? *(e.g., ID numbers, addresses, contact details)*
  - [ ] Yes — details below
  - [ ] No
  > **Answer:**

---

## Section 8 — Analytics Dashboard

- [ ] **Q27.** What was wrong with the analytics dashboard before the current fixes? *(Understanding the original bug helps me verify the fix is complete and test edge cases.)*
  > **Answer:**

- [ ] **Q28.** What metrics must the dashboard show? *(Tick all that apply.)*
  - [ ] Total assessments by municipality
  - [ ] Compliance pass/fail rate
  - [ ] Assessment trend over time
  - [ ] Assessor performance / activity
  - [ ] Business category breakdown (e.g., spaza, tuck shop, informal trader)
  > **Answer:**

- [ ] **Q29.** Should the dashboard be filterable by date range, municipality, or assessor?
  - [ ] Yes — date range
  - [ ] Yes — municipality
  - [ ] Yes — assessor
  - [ ] No filters needed
  > **Answer:**

---

## Section 9 — Incomplete & Missing Features

- [ ] **Q30.** What features are currently incomplete or broken in the app? *(Please list anything you know about — I will add it to the fix list.)*
  > **Answer:**

- [ ] **Q31.** Are there any features on the roadmap that are not yet in the codebase? *(e.g., SMS notifications to assessors, a mobile app version, bulk upload of assessment data)*
  > **Answer:**

- [ ] **Q32.** Is there a staging/test environment separate from production, or is everything on one Supabase project?
  - [ ] Separate staging environment exists
  - [ ] One project for both
  - [ ] No environment at all yet
  > **Answer:**

---

## Section 10 — Branding & Assets

- [ ] **Q33.** Are there logo files or brand assets for notoTrack or Yami Mine Solutions I should use in the UI and reports? *(Please share PNG/SVG files, or confirm if the repo already has them.)*
  > **Answer:**

- [ ] **Q34.** Are the brand colours confirmed as the current ones in the codebase? *(If there is a brand guide or specific hex values from the client, please share.)*
  > **Answer:**

---

## Section 11 — Timeline & Sign-off 🔴 BLOCKING

- [ ] **Q35.** What is the hard delivery deadline for this patch/fix submission? *(Day / Month / Year — determines build priority and scope.)*
  > **Answer:**

- [ ] **Q36.** Who signs off that the report output (PDF/CSV) is correct before it goes to the IDC or municipality?
  - [ ] You (project owner / lsr2025)
  - [ ] Yami Mine Solutions management
  - [ ] IDC Social Employment Fund representative
  - [ ] A compliance consultant
  > **Answer:**

- [ ] **Q37.** Is there a UAT (user acceptance testing) period before final delivery?
  - [ ] Yes — duration below
  - [ ] No — sign off on delivery
  > **Answer:**

- [ ] **Q38.** Are there any features or pages not currently in the codebase that are expected at delivery?
  > **Answer:**

---

## Quick Priority Guide for lsr2025

If time is short, please prioritise these first:

| # | Question | Why it's urgent |
|---|---|---|
| Q1–Q2 | Is this a partial repo and where is the full app? | Determines my entire approach — I cannot build features on a patch repo without access to the main app |
| Q4–Q5 | Supabase project URL and anon key | Unblocks all live testing, report generation, and dashboard verification |
| Q35 | Hard delivery deadline | Determines build order and whether optional features (Excel, offline) are in scope |

Thank you — I will proceed as answers come in.

---
*notoTrack dev session — 2026-05-17*
