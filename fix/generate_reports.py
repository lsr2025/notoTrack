"""
NotoTrack YMS — Report Generator
Generates real PDF and CSV reports from live Supabase data.
Produces:
  1. compliance_report.pdf  — Compliance Report (PDF)
  2. agent_activity.csv     — Agent Activity Report (CSV)
  3. municipality_summary.csv — Municipality Summary (CSV)
"""

import json
import csv
import os
from datetime import datetime, date
from collections import defaultdict

# ── Load data ──────────────────────────────────────────────────────────────────
DATA_PATH = "/home/ubuntu/nototrack_assets/assessments_data.json"
OUT_DIR   = "/home/ubuntu/nototrack_assets/reports"
os.makedirs(OUT_DIR, exist_ok=True)

with open(DATA_PATH) as f:
    records = json.load(f)

REPORT_DATE = datetime.now().strftime("%d %B %Y")
TOTAL = len(records)

def tier_label(t):
    return {1: "Gold (T1)", 2: "Good (T2)", 3: "Partial (T3)", 4: "Risk (T4)"}.get(t, "Unknown")

def compliance_label(score):
    if score is None: return "Pending"
    if score >= 70:   return "Compliant"
    if score >= 40:   return "Partial"
    return "Non-Compliant"

# ── 1. Agent Activity CSV ──────────────────────────────────────────────────────
agent_stats = defaultdict(lambda: {"assessments": 0, "scores": [], "municipalities": set()})
for r in records:
    name = r.get("fieldworker_name") or "Unknown"
    agent_stats[name]["assessments"] += 1
    score = r.get("compliance_score")
    if score is not None:
        agent_stats[name]["scores"].append(score)
    muni = r.get("municipality")
    if muni:
        agent_stats[name]["municipalities"].add(muni)

agent_rows = []
for name, s in agent_stats.items():
    avg = round(sum(s["scores"]) / len(s["scores"]), 1) if s["scores"] else 0
    comp_rate = round(len([x for x in s["scores"] if x >= 70]) / len(s["scores"]) * 100, 1) if s["scores"] else 0
    agent_rows.append({
        "Fieldworker": name,
        "Municipalities": "; ".join(sorted(s["municipalities"])),
        "Assessments": s["assessments"],
        "Avg Score": avg,
        "Compliance Rate (%)": comp_rate,
    })
agent_rows.sort(key=lambda x: -x["Assessments"])

agent_csv = os.path.join(OUT_DIR, "agent_activity_report.csv")
with open(agent_csv, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Fieldworker", "Municipalities", "Assessments", "Avg Score", "Compliance Rate (%)"])
    writer.writeheader()
    writer.writerows(agent_rows)
print(f"✓ Agent Activity CSV: {agent_csv}  ({len(agent_rows)} agents)")

# ── 2. Municipality Summary CSV ────────────────────────────────────────────────
muni_stats = defaultdict(lambda: {"total": 0, "scores": [], "compliant": 0, "partial": 0, "non_compliant": 0, "risk_shops": []})
for r in records:
    muni = r.get("municipality") or "Unknown"
    score = r.get("compliance_score")
    muni_stats[muni]["total"] += 1
    if score is not None:
        muni_stats[muni]["scores"].append(score)
        if score >= 70:   muni_stats[muni]["compliant"] += 1
        elif score >= 40: muni_stats[muni]["partial"] += 1
        else:
            muni_stats[muni]["non_compliant"] += 1
            muni_stats[muni]["risk_shops"].append(r.get("shop_name", ""))

muni_rows = []
for muni, s in muni_stats.items():
    avg = round(sum(s["scores"]) / len(s["scores"]), 1) if s["scores"] else 0
    muni_rows.append({
        "Municipality": muni,
        "Total Shops": s["total"],
        "Compliant": s["compliant"],
        "Partial": s["partial"],
        "Non-Compliant": s["non_compliant"],
        "Avg Score": avg,
        "Risk Hotspots": "; ".join(s["risk_shops"][:5]),
    })
muni_rows.sort(key=lambda x: -x["Total Shops"])

muni_csv = os.path.join(OUT_DIR, "municipality_summary.csv")
with open(muni_csv, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Municipality", "Total Shops", "Compliant", "Partial", "Non-Compliant", "Avg Score", "Risk Hotspots"])
    writer.writeheader()
    writer.writerows(muni_rows)
print(f"✓ Municipality Summary CSV: {muni_csv}  ({len(muni_rows)} municipalities)")

# ── 3. Compliance Report PDF ───────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

pdf_path = os.path.join(OUT_DIR, "compliance_report.pdf")
doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)

styles = getSampleStyleSheet()
BRAND_GREEN  = colors.HexColor("#00A86B")
BRAND_DARK   = colors.HexColor("#0D1B2A")
BRAND_BLUE   = colors.HexColor("#1A73E8")
GOLD         = colors.HexColor("#F59E0B")
RED          = colors.HexColor("#EF4444")
LIGHT_GRAY   = colors.HexColor("#F4F6F9")

h1 = ParagraphStyle("h1", fontSize=22, fontName="Helvetica-Bold", textColor=BRAND_DARK, spaceAfter=4)
h2 = ParagraphStyle("h2", fontSize=14, fontName="Helvetica-Bold", textColor=BRAND_GREEN, spaceAfter=6, spaceBefore=14)
h3 = ParagraphStyle("h3", fontSize=11, fontName="Helvetica-Bold", textColor=BRAND_DARK, spaceAfter=4, spaceBefore=8)
body = ParagraphStyle("body", fontSize=9, fontName="Helvetica", textColor=colors.HexColor("#374151"), leading=14)
caption = ParagraphStyle("caption", fontSize=8, fontName="Helvetica", textColor=colors.gray, alignment=TA_CENTER)
right = ParagraphStyle("right", fontSize=9, fontName="Helvetica", textColor=colors.gray, alignment=TA_RIGHT)

story = []

# ── Cover ──
story.append(Spacer(1, 1.5*cm))
story.append(Paragraph("NotoTrack YMS", h1))
story.append(Paragraph("Compliance Report — iLembe District", ParagraphStyle("sub", fontSize=14, fontName="Helvetica", textColor=BRAND_GREEN)))
story.append(Spacer(1, 0.3*cm))
story.append(HRFlowable(width="100%", thickness=2, color=BRAND_GREEN))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(f"Generated: {REPORT_DATE} &nbsp;&nbsp;|&nbsp;&nbsp; Total Assessments: {TOTAL}", body))
story.append(Paragraph("Programme: IDC Social Employment Fund (SEF) — Workstream A", body))
story.append(Paragraph("Powered by Yami Mine Solutions", body))
story.append(Spacer(1, 1*cm))

# ── Executive Summary ──
compliant   = sum(1 for r in records if (r.get("compliance_score") or 0) >= 70)
partial     = sum(1 for r in records if 40 <= (r.get("compliance_score") or 0) < 70)
non_comp    = sum(1 for r in records if (r.get("compliance_score") or 0) < 40)
avg_score   = round(sum(r.get("compliance_score") or 0 for r in records) / TOTAL, 1)

story.append(Paragraph("Executive Summary", h2))
summary_data = [
    ["Metric", "Value", "% of Total"],
    ["Total Assessments", str(TOTAL), "100%"],
    ["Compliant (Score ≥ 70)", str(compliant), f"{round(compliant/TOTAL*100,1)}%"],
    ["Partial (Score 40–69)", str(partial), f"{round(partial/TOTAL*100,1)}%"],
    ["Non-Compliant (Score < 40)", str(non_comp), f"{round(non_comp/TOTAL*100,1)}%"],
    ["Average Compliance Score", f"{avg_score}/100", "—"],
]
t = Table(summary_data, colWidths=[9*cm, 4*cm, 4*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), BRAND_DARK),
    ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,-1), 9),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT_GRAY, colors.white]),
    ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
    ("LEFTPADDING",(0,0), (-1,-1), 8),
    ("RIGHTPADDING",(0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING",(0,0), (-1,-1), 6),
    ("ALIGN",      (1,0), (-1,-1), "CENTER"),
]))
story.append(t)

# ── Tier Distribution ──
story.append(Paragraph("Compliance Tier Distribution", h2))
tier_counts = defaultdict(int)
for r in records:
    tier_counts[r.get("compliance_tier") or 4] += 1

tier_data = [["Tier", "Label", "Count", "% of Total"]]
for tier in [1, 2, 3, 4]:
    cnt = tier_counts[tier]
    tier_data.append([
        f"Tier {tier}",
        tier_label(tier),
        str(cnt),
        f"{round(cnt/TOTAL*100,1)}%",
    ])
t2 = Table(tier_data, colWidths=[3*cm, 6*cm, 4*cm, 4*cm])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), BRAND_GREEN),
    ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,-1), 9),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT_GRAY, colors.white]),
    ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
    ("LEFTPADDING",(0,0), (-1,-1), 8),
    ("RIGHTPADDING",(0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING",(0,0), (-1,-1), 6),
    ("ALIGN",      (2,0), (-1,-1), "CENTER"),
]))
story.append(t2)

# ── Municipality Breakdown ──
story.append(Paragraph("Municipality Compliance Breakdown", h2))
muni_table_data = [["Municipality", "Shops", "Compliant", "Partial", "Non-Comp.", "Avg Score"]]
for row in muni_rows:
    muni_table_data.append([
        row["Municipality"],
        str(row["Total Shops"]),
        str(row["Compliant"]),
        str(row["Partial"]),
        str(row["Non-Compliant"]),
        str(row["Avg Score"]),
    ])
t3 = Table(muni_table_data, colWidths=[5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
t3.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), BRAND_BLUE),
    ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT_GRAY, colors.white]),
    ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
    ("LEFTPADDING",(0,0), (-1,-1), 6),
    ("RIGHTPADDING",(0,0), (-1,-1), 6),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0), (-1,-1), 5),
    ("ALIGN",      (1,0), (-1,-1), "CENTER"),
]))
story.append(t3)

# ── Top 10 Agents ──
story.append(Paragraph("Top 10 Fieldworkers by Assessment Volume", h2))
agent_table_data = [["Rank", "Fieldworker", "Assessments", "Avg Score", "Compliance Rate"]]
for i, row in enumerate(agent_rows[:10], 1):
    agent_table_data.append([
        str(i),
        row["Fieldworker"],
        str(row["Assessments"]),
        str(row["Avg Score"]),
        f"{row['Compliance Rate (%)']}%",
    ])
t4 = Table(agent_table_data, colWidths=[1.5*cm, 7*cm, 3*cm, 3*cm, 3*cm])
t4.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), BRAND_DARK),
    ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,-1), 9),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT_GRAY, colors.white]),
    ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
    ("LEFTPADDING",(0,0), (-1,-1), 8),
    ("RIGHTPADDING",(0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING",(0,0), (-1,-1), 6),
    ("ALIGN",      (0,0), (0,-1), "CENTER"),
    ("ALIGN",      (2,0), (-1,-1), "CENTER"),
]))
story.append(t4)

# ── Risk Hotspots ──
story.append(Paragraph("Risk Hotspots — Non-Compliant Shops (Score < 40)", h2))
risk_shops = [r for r in records if (r.get("compliance_score") or 100) < 40]
risk_data = [["Shop Name", "Owner", "Municipality", "Score", "Fieldworker"]]
for r in sorted(risk_shops, key=lambda x: x.get("compliance_score") or 0)[:30]:
    risk_data.append([
        (r.get("shop_name") or "—")[:35],
        (r.get("owner_name") or "—")[:20],
        r.get("municipality") or "—",
        str(r.get("compliance_score") or 0),
        (r.get("fieldworker_name") or "—")[:20],
    ])
t5 = Table(risk_data, colWidths=[5.5*cm, 3.5*cm, 3.5*cm, 2*cm, 3*cm])
t5.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), RED),
    ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#FEF2F2"), colors.white]),
    ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
    ("LEFTPADDING",(0,0), (-1,-1), 6),
    ("RIGHTPADDING",(0,0), (-1,-1), 6),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING",(0,0), (-1,-1), 5),
    ("ALIGN",      (3,0), (3,-1), "CENTER"),
]))
story.append(t5)

# ── Footer note ──
story.append(Spacer(1, 1*cm))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB")))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    f"NotoTrack YMS — IDC Social Employment Fund | Yami Mine Solutions | {REPORT_DATE}",
    caption
))

doc.build(story)
print(f"✓ Compliance Report PDF: {pdf_path}")
print("\nAll reports generated successfully.")
