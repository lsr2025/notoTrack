/**
 * NotoTrack YMS — Analytics Page Report Generation Fix
 * 
 * PROBLEM: The "Generate Report" buttons were placeholders that only showed a fake
 * spinner and then displayed a browser alert saying "Connect your backend to produce
 * real files." No actual file was generated or downloaded.
 *
 * FIX: Replace the placeholder onClick handler with real client-side report generation
 * using jsPDF (for PDF) and PapaParse/native CSV (for CSV), pulling from the live
 * Supabase data already loaded on the page.
 *
 * INSTRUCTIONS:
 * 1. Install dependencies:
 *    pnpm add jspdf jspdf-autotable
 *
 * 2. Replace the report config array `E` and the button onClick in your analytics page
 *    with the code below.
 *
 * 3. The `assessments` data is already fetched in the component — pass it to the
 *    generator functions below.
 */

// ─── Install: pnpm add jspdf jspdf-autotable ───────────────────────────────

import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

// ─── Types ──────────────────────────────────────────────────────────────────
interface Assessment {
  id: string;
  shop_name: string | null;
  owner_name: string | null;
  municipality: string | null;
  ward_no: string | null;
  compliance_score: number | null;
  compliance_tier: number | null;
  status: string | null;
  submitted_at: string | null;
  fieldworker_name: string | null;
  is_cipc_registered: boolean | null;
  num_employees: number | null;
  structure_type: string | null;
  store_size: string | null;
}

// ─── Helper: Download a blob as a file ──────────────────────────────────────
function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ─── 1. Compliance Report (PDF) ─────────────────────────────────────────────
export function generateCompliancePDF(
  assessments: Assessment[],
  dateFrom: string,
  dateTo: string
) {
  const filtered = assessments.filter((r) => {
    if (!dateFrom && !dateTo) return true;
    const d = r.submitted_at ? new Date(r.submitted_at) : null;
    if (!d) return true;
    if (dateFrom && d < new Date(dateFrom)) return false;
    if (dateTo && d > new Date(dateTo)) return false;
    return true;
  });

  const total = filtered.length;
  const compliant = filtered.filter((r) => (r.compliance_score ?? 0) >= 70).length;
  const partial = filtered.filter(
    (r) => (r.compliance_score ?? 0) >= 40 && (r.compliance_score ?? 0) < 70
  ).length;
  const nonCompliant = filtered.filter((r) => (r.compliance_score ?? 0) < 40).length;
  const avgScore =
    total > 0
      ? (filtered.reduce((s, r) => s + (r.compliance_score ?? 0), 0) / total).toFixed(1)
      : "0";

  // Municipality breakdown
  const muniMap: Record<string, { total: number; scores: number[]; compliant: number; partial: number; nonCompliant: number }> = {};
  filtered.forEach((r) => {
    const m = r.municipality ?? "Unknown";
    if (!muniMap[m]) muniMap[m] = { total: 0, scores: [], compliant: 0, partial: 0, nonCompliant: 0 };
    muniMap[m].total++;
    const s = r.compliance_score ?? 0;
    muniMap[m].scores.push(s);
    if (s >= 70) muniMap[m].compliant++;
    else if (s >= 40) muniMap[m].partial++;
    else muniMap[m].nonCompliant++;
  });

  const doc = new jsPDF();
  const BRAND_GREEN: [number, number, number] = [0, 168, 107];
  const BRAND_DARK: [number, number, number] = [13, 27, 42];
  const BRAND_BLUE: [number, number, number] = [26, 115, 232];
  const today = new Date().toLocaleDateString("en-ZA", { day: "2-digit", month: "long", year: "numeric" });

  // Header
  doc.setFontSize(20);
  doc.setTextColor(...BRAND_DARK);
  doc.setFont("helvetica", "bold");
  doc.text("NotoTrack YMS", 14, 20);
  doc.setFontSize(12);
  doc.setTextColor(...BRAND_GREEN);
  doc.text("Compliance Report — iLembe District", 14, 28);
  doc.setDrawColor(...BRAND_GREEN);
  doc.setLineWidth(0.8);
  doc.line(14, 32, 196, 32);
  doc.setFontSize(9);
  doc.setTextColor(100, 100, 100);
  doc.setFont("helvetica", "normal");
  doc.text(`Generated: ${today}  |  Period: ${dateFrom || "All"} to ${dateTo || "All"}  |  Total: ${total}`, 14, 38);
  doc.text("Programme: IDC Social Employment Fund (SEF) — Workstream A | Yami Mine Solutions", 14, 44);

  // Executive Summary
  doc.setFontSize(13);
  doc.setTextColor(...BRAND_GREEN);
  doc.setFont("helvetica", "bold");
  doc.text("Executive Summary", 14, 56);

  autoTable(doc, {
    startY: 60,
    head: [["Metric", "Value", "% of Total"]],
    body: [
      ["Total Assessments", String(total), "100%"],
      ["Compliant (Score ≥ 70)", String(compliant), `${((compliant / total) * 100).toFixed(1)}%`],
      ["Partial (Score 40–69)", String(partial), `${((partial / total) * 100).toFixed(1)}%`],
      ["Non-Compliant (Score < 40)", String(nonCompliant), `${((nonCompliant / total) * 100).toFixed(1)}%`],
      ["Average Compliance Score", `${avgScore}/100`, "—"],
    ],
    headStyles: { fillColor: BRAND_DARK, textColor: [255, 255, 255], fontStyle: "bold" },
    alternateRowStyles: { fillColor: [244, 246, 249] },
    styles: { fontSize: 9 },
    columnStyles: { 1: { halign: "center" }, 2: { halign: "center" } },
  });

  // Municipality Breakdown
  const muniY = (doc as any).lastAutoTable.finalY + 10;
  doc.setFontSize(13);
  doc.setTextColor(...BRAND_BLUE);
  doc.text("Municipality Compliance Breakdown", 14, muniY);

  const muniRows = Object.entries(muniMap)
    .sort((a, b) => b[1].total - a[1].total)
    .map(([muni, s]) => {
      const avg = s.scores.length > 0 ? (s.scores.reduce((a, b) => a + b, 0) / s.scores.length).toFixed(1) : "0";
      return [muni, String(s.total), String(s.compliant), String(s.partial), String(s.nonCompliant), avg];
    });

  autoTable(doc, {
    startY: muniY + 4,
    head: [["Municipality", "Shops", "Compliant", "Partial", "Non-Comp.", "Avg Score"]],
    body: muniRows,
    headStyles: { fillColor: BRAND_BLUE, textColor: [255, 255, 255], fontStyle: "bold" },
    alternateRowStyles: { fillColor: [244, 246, 249] },
    styles: { fontSize: 8 },
    columnStyles: { 1: { halign: "center" }, 2: { halign: "center" }, 3: { halign: "center" }, 4: { halign: "center" }, 5: { halign: "center" } },
  });

  // Footer
  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    doc.text(
      `NotoTrack YMS — IDC Social Employment Fund | Yami Mine Solutions | ${today}  |  Page ${i} of ${pageCount}`,
      14,
      doc.internal.pageSize.height - 8
    );
  }

  doc.save(`NotoTrack_Compliance_Report_${today.replace(/ /g, "_")}.pdf`);
}

// ─── 2. Agent Activity Report (CSV) ─────────────────────────────────────────
export function generateAgentCSV(
  assessments: Assessment[],
  dateFrom: string,
  dateTo: string
) {
  const filtered = assessments.filter((r) => {
    if (!dateFrom && !dateTo) return true;
    const d = r.submitted_at ? new Date(r.submitted_at) : null;
    if (!d) return true;
    if (dateFrom && d < new Date(dateFrom)) return false;
    if (dateTo && d > new Date(dateTo)) return false;
    return true;
  });

  const agentMap: Record<string, { assessments: number; scores: number[]; municipalities: Set<string> }> = {};
  filtered.forEach((r) => {
    const name = r.fieldworker_name ?? "Unknown";
    if (!agentMap[name]) agentMap[name] = { assessments: 0, scores: [], municipalities: new Set() };
    agentMap[name].assessments++;
    if (r.compliance_score !== null) agentMap[name].scores.push(r.compliance_score);
    if (r.municipality) agentMap[name].municipalities.add(r.municipality);
  });

  const rows = Object.entries(agentMap)
    .sort((a, b) => b[1].assessments - a[1].assessments)
    .map(([name, s]) => {
      const avg = s.scores.length > 0 ? (s.scores.reduce((a, b) => a + b, 0) / s.scores.length).toFixed(1) : "0";
      const compRate = s.scores.length > 0 ? ((s.scores.filter((x) => x >= 70).length / s.scores.length) * 100).toFixed(1) : "0";
      return [name, Array.from(s.municipalities).join("; "), s.assessments, avg, `${compRate}%`];
    });

  const header = ["Fieldworker", "Municipalities", "Assessments", "Avg Score", "Compliance Rate"];
  const csvContent = [header, ...rows].map((row) => row.map((cell) => `"${cell}"`).join(",")).join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  downloadBlob(blob, `NotoTrack_Agent_Activity_${new Date().toISOString().slice(0, 10)}.csv`);
}

// ─── 3. Municipality Summary (CSV) ──────────────────────────────────────────
export function generateMunicipalityCSV(
  assessments: Assessment[],
  dateFrom: string,
  dateTo: string
) {
  const filtered = assessments.filter((r) => {
    if (!dateFrom && !dateTo) return true;
    const d = r.submitted_at ? new Date(r.submitted_at) : null;
    if (!d) return true;
    if (dateFrom && d < new Date(dateFrom)) return false;
    if (dateTo && d > new Date(dateTo)) return false;
    return true;
  });

  const muniMap: Record<string, { total: number; scores: number[]; compliant: number; partial: number; nonCompliant: number; riskShops: string[] }> = {};
  filtered.forEach((r) => {
    const m = r.municipality ?? "Unknown";
    if (!muniMap[m]) muniMap[m] = { total: 0, scores: [], compliant: 0, partial: 0, nonCompliant: 0, riskShops: [] };
    muniMap[m].total++;
    const s = r.compliance_score ?? 0;
    muniMap[m].scores.push(s);
    if (s >= 70) muniMap[m].compliant++;
    else if (s >= 40) muniMap[m].partial++;
    else {
      muniMap[m].nonCompliant++;
      if (r.shop_name) muniMap[m].riskShops.push(r.shop_name);
    }
  });

  const header = ["Municipality", "Total Shops", "Compliant", "Partial", "Non-Compliant", "Avg Score", "Risk Hotspots (top 5)"];
  const rows = Object.entries(muniMap)
    .sort((a, b) => b[1].total - a[1].total)
    .map(([muni, s]) => {
      const avg = s.scores.length > 0 ? (s.scores.reduce((a, b) => a + b, 0) / s.scores.length).toFixed(1) : "0";
      return [muni, s.total, s.compliant, s.partial, s.nonCompliant, avg, s.riskShops.slice(0, 5).join("; ")];
    });

  const csvContent = [header, ...rows].map((row) => row.map((cell) => `"${cell}"`).join(",")).join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  downloadBlob(blob, `NotoTrack_Municipality_Summary_${new Date().toISOString().slice(0, 10)}.csv`);
}

// ─── Updated report config array (replaces `E` in analytics/page.tsx) ───────
// Replace the existing `E` array and button onClick with this:
//
// const reportGenerators = [generateCompliancePDF, generateAgentCSV, generateMunicipalityCSV];
//
// In the button onClick:
// onClick={() => {
//   setGenerating(idx);
//   try {
//     reportGenerators[idx](allAssessments, dateRanges[idx].from, dateRanges[idx].to);
//   } finally {
//     setGenerating(null);
//   }
// }}
