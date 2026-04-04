# NotoTrack YMS — Report Generation Fix

## Problem Identified

The **"Generate Report"** buttons on the Analytics page (`/analytics`) were **non-functional placeholders**. When clicked, they:
1. Showed a fake spinner for 1.5 seconds
2. Displayed a browser `alert()` saying: *"[Report Name] export is ready. (Connect your backend to produce real files.)"*
3. Did **not** generate or download any actual file

The root cause was in `app/analytics/page.tsx` — the button `onClick` handler was:

```tsx
onClick={() => {
  setGenerating(idx);
  setTimeout(() => {
    setGenerating(null);
    alert(`"${reportConfigs[idx].title}" export is ready. (Connect your backend to produce real files.)`);
  }, 1500);
}}
```

---

## Fix

### Option A — Use the pre-generated reports (immediate)

The following real reports have been generated from live Supabase data (593 assessments as of 04 April 2026):

| File | Description |
|------|-------------|
| `compliance_report.pdf` | 3-page PDF with executive summary, tier distribution, municipality breakdown, top fieldworkers, and risk hotspots |
| `agent_activity_report.csv` | Per-agent assessment counts, average scores, and compliance rates (165 agents) |
| `municipality_summary.csv` | Geographic compliance summary across 14 municipalities |

### Option B — Integrate real-time generation into the app

1. **Install dependencies:**
   ```bash
   pnpm add jspdf jspdf-autotable
   ```

2. **Copy `analytics_report_fix.tsx`** into your project (e.g., `lib/reportGenerators.ts`)

3. **Update `app/analytics/page.tsx`:**

   Import the generators:
   ```tsx
   import { generateCompliancePDF, generateAgentCSV, generateMunicipalityCSV } from "@/lib/reportGenerators";
   ```

   Replace the placeholder `onClick` with:
   ```tsx
   const reportGenerators = [generateCompliancePDF, generateAgentCSV, generateMunicipalityCSV];

   // In the button:
   onClick={() => {
     setGenerating(idx);
     try {
       reportGenerators[idx](allAssessments, dateRanges[idx].from, dateRanges[idx].to);
     } finally {
       setGenerating(null);
     }
   }}
   ```

   Make sure `allAssessments` is the full assessments array already fetched by the component.

4. **Deploy to Vercel** — the fix will work client-side with no backend changes needed.

### Option C — Python standalone generator (for server/admin use)

Run `generate_reports.py` directly on any machine with Python 3.11+ and `reportlab`:

```bash
pip install reportlab
python generate_reports.py
```

This fetches live data from Supabase and generates all three reports locally.

---

## Report Contents

### Compliance Report (PDF)
- Cover page with programme details
- Executive summary table (total, compliant, partial, non-compliant, avg score)
- Compliance tier distribution (Tier 1–4)
- Municipality compliance breakdown (all 14 municipalities)
- Top 10 fieldworkers by assessment volume
- Risk hotspots — non-compliant shops (score < 40)

### Agent Activity Report (CSV)
Columns: `Fieldworker`, `Municipalities`, `Assessments`, `Avg Score`, `Compliance Rate (%)`

### Municipality Summary (CSV)
Columns: `Municipality`, `Total Shops`, `Compliant`, `Partial`, `Non-Compliant`, `Avg Score`, `Risk Hotspots`

---

*NotoTrack YMS — IDC Social Employment Fund | Yami Mine Solutions*
