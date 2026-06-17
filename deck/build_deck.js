// NemoDesk pitch deck generator - India Agentic AI Open Hackathon, Track A
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const Fa = require("react-icons/fa");

// ---- Palette: NVIDIA-green on charcoal (premium, on-brand) ----
const NV = "76B900";       // NVIDIA green (accent)
const DARK = "0D1B0A";     // near-black green-tinted
const CHARCOAL = "1A1A1A"; // dark slate
const LIGHT = "F4F7F0";    // off-white
const MUTED = "9CA3AF";    // muted gray
const WHITE = "FFFFFF";
const CARD = "242B22";     // dark card on dark bg

const HEAD = "Georgia";
const BODY = "Calibri";

async function icon(IconComponent, color = "#76B900", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

const shadow = () => ({ type: "outer", color: "000000", blur: 8, offset: 3, angle: 135, opacity: 0.25 });

(async () => {
  const p = new pptxgen();
  p.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
  p.author = "Yash Kavaiya";
  p.title = "NemoDesk - Enterprise IT Ticket AI";
  const W = 13.3, H = 7.5;

  // Pre-render icons
  const icProblem = await icon(Fa.FaExclamationTriangle, "#76B900");
  const icBolt = await icon(Fa.FaBolt, "#76B900");
  const icShield = await icon(Fa.FaShieldAlt, "#76B900");
  const icBook = await icon(Fa.FaBook, "#76B900");
  const icRoute = await icon(Fa.FaRoute, "#76B900");
  const icRobot = await icon(Fa.FaRobot, "#76B900");
  const icChart = await icon(Fa.FaChartLine, "#76B900");
  const icCheck = await icon(Fa.FaCheckCircle, "#76B900");
  const icGithub = await icon(Fa.FaGithub, "#FFFFFF");
  const icRocket = await icon(Fa.FaRocket, "#76B900");
  const icCogs = await icon(Fa.FaCogs, "#76B900");
  const icServer = await icon(Fa.FaServer, "#76B900");

  // Helper: footer on content slides
  function footer(slide, n) {
    slide.addShape(p.shapes.RECTANGLE, { x: 0, y: H - 0.32, w: W, h: 0.32, fill: { color: DARK } });
    slide.addText("NemoDesk - Enterprise IT Ticket AI", { x: 0.5, y: H - 0.34, w: 6, h: 0.32, fontSize: 9, color: MUTED, fontFace: BODY, valign: "middle" });
    slide.addText(`${n} / 12`, { x: W - 1.3, y: H - 0.34, w: 0.8, h: 0.32, fontSize: 9, color: MUTED, fontFace: BODY, align: "right", valign: "middle" });
    slide.addText("Track A - Agentic Workflows", { x: W/2 - 2, y: H - 0.34, w: 4, h: 0.32, fontSize: 9, color: NV, fontFace: BODY, align: "center", valign: "middle" });
  }
  // Helper: content slide title
  function title(slide, t, n) {
    slide.background = { color: CHARCOAL };
    slide.addText(t, { x: 0.5, y: 0.35, w: W - 1, h: 0.8, fontSize: 30, bold: true, color: WHITE, fontFace: HEAD, margin: 0 });
    slide.addShape(p.shapes.RECTANGLE, { x: 0.5, y: 1.18, w: 0.9, h: 0.07, fill: { color: NV } });
    footer(slide, n);
  }

  // ============ SLIDE 1: TITLE ============
  let s = p.addSlide();
  s.background = { color: DARK };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.25, h: H, fill: { color: NV } });
  s.addText("NVIDIA NeMo Agent Toolkit  -  Nemotron NIMs", { x: 0.8, y: 0.7, w: 11, h: 0.4, fontSize: 14, color: NV, fontFace: BODY, charSpacing: 2 });
  s.addText("NemoDesk", { x: 0.8, y: 1.9, w: 11.5, h: 1.3, fontSize: 72, bold: true, color: WHITE, fontFace: HEAD, margin: 0 });
  s.addText("Enterprise IT Ticket AI", { x: 0.8, y: 3.1, w: 11.5, h: 0.8, fontSize: 32, color: LIGHT, fontFace: HEAD, italic: true, margin: 0 });
  s.addText("Agentic IT service-desk automation that triages, routes, and resolves tickets end-to-end.", { x: 0.8, y: 4.1, w: 11, h: 0.6, fontSize: 16, color: MUTED, fontFace: BODY });
  s.addImage({ data: icRobot, x: 0.8, y: 5.2, w: 0.5, h: 0.5 });
  s.addText("India Agentic AI Open Hackathon  (NVIDIA + gnani.ai)   |   Track A: Agentic Workflows", { x: 1.45, y: 5.25, w: 11, h: 0.4, fontSize: 14, color: LIGHT, fontFace: BODY, valign: "middle" });
  s.addImage({ data: icGithub, x: 0.8, y: 5.85, w: 0.4, h: 0.4 });
  s.addText("github.com/Yash-Kavaiya/nemodesk-it-agent", { x: 1.35, y: 5.85, w: 8, h: 0.4, fontSize: 14, color: NV, fontFace: "Consolas", valign: "middle" });

  // ============ SLIDE 2: PROBLEM ============
  s = p.addSlide(); title(s, "The Problem", 2);
  s.addImage({ data: icProblem, x: 0.5, y: 0.42, w: 0.0, h: 0.0 }); // (kept invisible; title already set)
  const probs = [
    ["High volume, rising cost", "Service desks face relentless ticket inflow and growing headcount cost."],
    ["Slow, inconsistent triage", "First response lags; categorization and priority vary by agent."],
    ["Tribal-knowledge fixes", "L1 agents hunt through scattered runbooks; resolutions aren't standardized."],
    ["Sensitive data exposure", "Tickets routinely contain emails, IPs, and credentials that leak into tools."],
  ];
  let py = 1.7;
  for (const [h, d] of probs) {
    s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: py, w: 12.3, h: 1.05, fill: { color: CARD }, shadow: shadow() });
    s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: py, w: 0.08, h: 1.05, fill: { color: NV } });
    s.addImage({ data: icProblem, x: 0.8, y: py + 0.32, w: 0.42, h: 0.42 });
    s.addText(h, { x: 1.45, y: py + 0.12, w: 4.5, h: 0.45, fontSize: 17, bold: true, color: WHITE, fontFace: BODY, valign: "middle", margin: 0 });
    s.addText(d, { x: 6.1, y: py + 0.1, w: 6.5, h: 0.85, fontSize: 13, color: MUTED, fontFace: BODY, valign: "middle", margin: 0 });
    py += 1.2;
  }

  // ============ SLIDE 3: OPPORTUNITY (stat callouts) ============
  s = p.addSlide(); title(s, "The Opportunity", 3);
  const stats = [
    ["60-80%", "of L1 tickets are repetitive & runbook-resolvable", icBook],
    ["1st touch", "agentic AI can own triage -> route -> resolve -> record", icBolt],
    ["24/7", "consistent, instant first response with no fatigue", icChart],
  ];
  let sx = 0.5;
  for (const [big, lbl, ic] of stats) {
    s.addShape(p.shapes.RECTANGLE, { x: sx, y: 1.8, w: 3.95, h: 3.6, fill: { color: CARD }, shadow: shadow() });
    s.addImage({ data: ic, x: sx + 0.35, y: 2.15, w: 0.7, h: 0.7 });
    s.addText(big, { x: sx + 0.2, y: 3.0, w: 3.55, h: 1.0, fontSize: 46, bold: true, color: NV, fontFace: HEAD, align: "left", margin: 0 });
    s.addText(lbl, { x: sx + 0.35, y: 4.1, w: 3.3, h: 1.1, fontSize: 14, color: LIGHT, fontFace: BODY, margin: 0 });
    sx += 4.15;
  }
  s.addText("NemoDesk targets measurable auto-resolution, faster MTTR, and higher SLA adherence.", { x: 0.5, y: 5.7, w: 12.3, h: 0.5, fontSize: 14, italic: true, color: MUTED, fontFace: BODY });

  // ============ SLIDE 4: SOLUTION ============
  s = p.addSlide(); title(s, "Solution: NemoDesk", 4);
  s.addText("A team of cooperating agents takes a raw ticket and returns a complete, auditable outcome:", { x: 0.5, y: 1.55, w: 12, h: 0.5, fontSize: 16, color: LIGHT, fontFace: BODY });
  const outs = [["Category", icCogs], ["Priority P1-P4", icBolt], ["Owning team + SLA", icRoute], ["Runbook steps", icBook], ["ITSM ticket id", icServer], ["PII redacted first", icShield]];
  let ox = 0.5, oy = 2.4;
  outs.forEach((o, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.5 + col * 4.15, y = 2.4 + row * 1.65;
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 3.95, h: 1.45, fill: { color: CARD }, shadow: shadow() });
    s.addImage({ data: o[1], x: x + 0.3, y: y + 0.45, w: 0.55, h: 0.55 });
    s.addText(o[0], { x: x + 1.05, y: y, w: 2.8, h: 1.45, fontSize: 17, bold: true, color: WHITE, fontFace: BODY, valign: "middle", margin: 0 });
  });

  // ============ SLIDE 5: ARCHITECTURE ============
  s = p.addSlide(); title(s, "Architecture", 5);
  // Supervisor box
  function box(x, y, w, h, label, sub, fill, txt) {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: NV, width: 1.5 }, rectRadius: 0.08, shadow: shadow() });
    const subColor = (txt === DARK) ? "1F3D00" : MUTED; // dark subtitle on green box, muted on dark card
    s.addText([{ text: label, options: { bold: true, fontSize: 15, color: txt || WHITE, breakLine: true } },
               { text: sub, options: { fontSize: 10, color: subColor } }],
      { x, y, w, h, align: "center", valign: "middle", fontFace: BODY, margin: 4 });
  }
  box(4.9, 1.55, 3.5, 1.0, "Supervisor", "react_agent  -  Nemotron NIM", NV, DARK);
  // connectors (positive w/h only; use flipH for the left diagonal)
  s.addShape(p.shapes.LINE, { x: 4.3, y: 2.55, w: 1.1, h: 0.85, flipH: true, line: { color: NV, width: 2 } });
  s.addShape(p.shapes.LINE, { x: 7.9, y: 2.55, w: 1.1, h: 0.85, line: { color: NV, width: 2 } });
  // two expert agents
  box(1.4, 3.4, 5.0, 1.0, "triage_agent", "tool_calling_agent", CARD);
  box(6.9, 3.4, 5.0, 1.0, "resolution_agent", "tool_calling_agent", CARD);
  // tool chips
  function chips(items, x0, y0) {
    let cx = x0;
    items.forEach(t => {
      const w = 0.22 + t.length * 0.092;
      s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: cx, y: y0, w, h: 0.5, fill: { color: DARK }, line: { color: NV, width: 1 }, rectRadius: 0.06 });
      s.addText(t, { x: cx, y: y0, w, h: 0.5, fontSize: 10, color: LIGHT, fontFace: "Consolas", align: "center", valign: "middle", margin: 0 });
      cx += w + 0.18;
    });
  }
  s.addShape(p.shapes.LINE, { x: 3.9, y: 4.4, w: 0, h: 0.55, line: { color: NV, width: 1.5 } });
  s.addShape(p.shapes.LINE, { x: 9.4, y: 4.4, w: 0, h: 0.55, line: { color: NV, width: 1.5 } });
  chips(["pii_redactor", "ticket_classifier", "escalation_router"], 1.0, 5.05);
  chips(["kb_search (RAG)", "itsm_connector"], 7.0, 5.05);
  s.addText("Canonical NeMo Agent Toolkit multi-agent pattern: a reasoning supervisor delegates to focused expert agents, each with a small tool surface.", { x: 0.5, y: 6.2, w: 12.3, h: 0.7, fontSize: 13, italic: true, color: MUTED, fontFace: BODY });

  // ============ SLIDE 6: NVIDIA STACK ============
  s = p.addSlide(); title(s, "Built on the NVIDIA Stack", 6);
  const stack = [
    ["NeMo Agent Toolkit", "Multi-agent orchestration, evaluation, observability; MCP & A2A ready.", icRobot],
    ["Nemotron NIM", "nemotron-3-nano-30b-a3b for supervisor reasoning + deterministic tool calls.", icCogs],
    ["nv-embedqa-e5-v5", "High-quality embeddings powering runbook RAG retrieval.", icBook],
    ["NIM-portable", "Run on build.nvidia.com or on-prem NIM containers - no tool code changes.", icServer],
  ];
  stack.forEach((o, i) => {
    const x = 0.5 + (i % 2) * 6.3, y = 1.7 + Math.floor(i / 2) * 2.35;
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 6.0, h: 2.1, fill: { color: CARD }, shadow: shadow() });
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.08, h: 2.1, fill: { color: NV } });
    s.addImage({ data: o[2], x: x + 0.35, y: y + 0.35, w: 0.6, h: 0.6 });
    s.addText(o[0], { x: x + 1.15, y: y + 0.32, w: 4.7, h: 0.6, fontSize: 18, bold: true, color: NV, fontFace: BODY, valign: "middle", margin: 0 });
    s.addText(o[1], { x: x + 0.35, y: y + 1.05, w: 5.4, h: 0.95, fontSize: 13, color: LIGHT, fontFace: BODY, margin: 0 });
  });

  // ============ SLIDE 7: LIVE DEMO ============
  s = p.addSlide(); title(s, "Live Demo", 7);
  const demos = [
    ["P1 outage", "\"VPN is down for the whole office\"", "-> Network-Operations, SLA 15 min, escalated"],
    ["Phishing report", "\"I entered my password on a fake page\"", "-> PII redacted, escalated to SecOps-CSIRT as P1"],
    ["Outlook crash", "\"Outlook crashes after the latest update\"", "-> RAG pulls RB-001, numbered fix, INC ticket created"],
  ];
  let dy = 1.7;
  demos.forEach(([tag, inp, out], i) => {
    s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: dy, w: 12.3, h: 1.45, fill: { color: CARD }, shadow: shadow() });
    s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: dy, w: 2.4, h: 1.45, fill: { color: NV } });
    s.addText(tag, { x: 0.5, y: dy, w: 2.4, h: 1.45, fontSize: 16, bold: true, color: DARK, fontFace: BODY, align: "center", valign: "middle", margin: 0 });
    s.addText([{ text: inp + "\n", options: { fontSize: 14, color: LIGHT, italic: true, breakLine: true } },
               { text: out, options: { fontSize: 13, color: NV } }],
      { x: 3.1, y: dy, w: 9.5, h: 1.45, valign: "middle", fontFace: BODY, margin: 4 });
    dy += 1.6;
  });

  // ============ SLIDE 8: ENTERPRISE-GRADE ============
  s = p.addSlide(); title(s, "Enterprise-Grade by Design", 8);
  const eg = [
    ["PII redaction at the boundary", "Deterministic masking of emails, IPs, phones, cards, secrets before any LLM call.", icShield],
    ["Grounded resolutions", "RAG over approved runbooks - no hallucinated fixes.", icBook],
    ["Deterministic SLA & routing", "Explicit priority->team and SLA tables: testable and predictable.", icRoute],
    ["Auditable system of record", "Every ticket persisted with a unique INC id, category, priority, team.", icServer],
    ["Graceful degradation", "Keyword + severity fallback if a model call cannot be parsed.", icCheck],
    ["Framework-agnostic", "NAT instrumentation, profiling and eval out of the box.", icCogs],
  ];
  eg.forEach((o, i) => {
    const x = 0.5 + (i % 2) * 6.3, y = 1.65 + Math.floor(i / 3) * 0; // placeholder
  });
  // 2 columns x 3 rows
  eg.forEach((o, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 6.3, y = 1.6 + row * 1.65;
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 6.0, h: 1.45, fill: { color: CARD }, shadow: shadow() });
    s.addImage({ data: o[2], x: x + 0.3, y: y + 0.5, w: 0.45, h: 0.45 });
    s.addText(o[0], { x: x + 0.95, y: y + 0.12, w: 4.9, h: 0.5, fontSize: 14, bold: true, color: WHITE, fontFace: BODY, valign: "middle", margin: 0 });
    s.addText(o[1], { x: x + 0.95, y: y + 0.62, w: 4.9, h: 0.75, fontSize: 11, color: MUTED, fontFace: BODY, margin: 0 });
  });

  // ============ SLIDE 9: EVALUATION ============
  s = p.addSlide(); title(s, "Evaluation", 9);
  s.addText("nat eval with RAGAS metrics, judged by a Nemotron NIM.", { x: 0.5, y: 1.6, w: 12, h: 0.5, fontSize: 16, color: LIGHT, fontFace: BODY });
  s.addImage({ data: icChart, x: 0.5, y: 2.4, w: 0.0, h: 0.0 });
  // metric cards
  const evs = [["AnswerAccuracy", "Is the triage + resolution correct vs. the labelled answer?"], ["ResponseGroundedness", "Are the steps grounded in retrieved runbooks, not invented?"], ["10-ticket dataset", "Labelled across all 8 categories, incl. P1 security cases."]];
  let ex = 0.5;
  evs.forEach(([h, d]) => {
    s.addShape(p.shapes.RECTANGLE, { x: ex, y: 2.4, w: 3.95, h: 2.6, fill: { color: CARD }, shadow: shadow() });
    s.addImage({ data: icCheck, x: ex + 0.3, y: 2.7, w: 0.5, h: 0.5 });
    s.addText(h, { x: ex + 0.3, y: 3.35, w: 3.4, h: 0.8, fontSize: 17, bold: true, color: NV, fontFace: BODY, margin: 0 });
    s.addText(d, { x: ex + 0.3, y: 4.05, w: 3.4, h: 0.85, fontSize: 12, color: LIGHT, fontFace: BODY, margin: 0 });
    ex += 4.15;
  });
  s.addText("Run:  nat eval --config_file configs/eval_config.yml", { x: 0.5, y: 5.4, w: 12, h: 0.5, fontSize: 14, color: NV, fontFace: "Consolas" });

  // ============ SLIDE 10: IMPACT ============
  s = p.addSlide(); title(s, "Impact & ROI", 10);
  s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: 1.7, w: 12.3, h: 1.3, fill: { color: CARD }, line: { color: NV, width: 1.5 }, shadow: shadow() });
  s.addText("Deflected tickets  x  avg handle time  x  loaded agent cost  =  $ saved", { x: 0.5, y: 1.7, w: 12.3, h: 1.3, fontSize: 22, bold: true, color: NV, fontFace: HEAD, align: "center", valign: "middle" });
  const imp = [["Faster MTTR", icBolt], ["Fewer SLA breaches", icRoute], ["Consistent quality", icCheck], ["24/7 coverage", icChart]];
  imp.forEach((o, i) => {
    const x = 0.5 + i * 3.18, y = 3.5;
    s.addShape(p.shapes.RECTANGLE, { x, y, w: 2.95, h: 2.2, fill: { color: CARD }, shadow: shadow() });
    s.addImage({ data: o[1], x: x + 1.12, y: y + 0.4, w: 0.7, h: 0.7 });
    s.addText(o[0], { x: x + 0.1, y: y + 1.3, w: 2.75, h: 0.7, fontSize: 15, bold: true, color: WHITE, fontFace: BODY, align: "center", margin: 0 });
  });

  // ============ SLIDE 11: ROADMAP ============
  s = p.addSlide(); title(s, "Roadmap", 11);
  const road = [
    ["MCP server", "Expose NemoDesk tools for other agents to consume."],
    ["A2A mesh", "Register NemoDesk as a distributed agent node."],
    ["Real ITSM connectors", "Swap mock store for ServiceNow / Jira REST."],
    ["RL fine-tuning", "Train the classifier on historical resolved tickets with NeMo."],
    ["Observability", "Native Phoenix / LangSmith tracing in NAT config."],
  ];
  let ry = 1.65;
  road.forEach(([h, d], i) => {
    s.addShape(p.shapes.OVAL, { x: 0.6, y: ry + 0.05, w: 0.6, h: 0.6, fill: { color: NV } });
    s.addText(String(i + 1), { x: 0.6, y: ry + 0.05, w: 0.6, h: 0.6, fontSize: 18, bold: true, color: DARK, align: "center", valign: "middle", fontFace: BODY, margin: 0 });
    s.addText(h, { x: 1.45, y: ry, w: 4.0, h: 0.7, fontSize: 17, bold: true, color: WHITE, fontFace: BODY, valign: "middle", margin: 0 });
    s.addText(d, { x: 5.6, y: ry, w: 7.2, h: 0.7, fontSize: 13, color: MUTED, fontFace: BODY, valign: "middle", margin: 0 });
    ry += 1.0;
  });

  // ============ SLIDE 12: CLOSE ============
  s = p.addSlide();
  s.background = { color: DARK };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.25, h: H, fill: { color: NV } });
  s.addImage({ data: icRocket, x: 0.8, y: 0.9, w: 0.8, h: 0.8 });
  s.addText("Let's deploy NemoDesk", { x: 0.8, y: 1.9, w: 12, h: 1.0, fontSize: 48, bold: true, color: WHITE, fontFace: HEAD, margin: 0 });
  s.addText("Enterprise IT ticket automation, agentic and grounded - built on NVIDIA NeMo Agent Toolkit.", { x: 0.8, y: 3.0, w: 11.5, h: 0.6, fontSize: 18, color: LIGHT, fontFace: BODY, italic: true });
  s.addText([{ text: "What we need:  ", options: { bold: true, color: NV } },
             { text: "compute, mentorship, and pilot ticket data.", options: { color: LIGHT } }],
    { x: 0.8, y: 3.9, w: 11.5, h: 0.5, fontSize: 16, fontFace: BODY });
  s.addImage({ data: icGithub, x: 0.8, y: 4.9, w: 0.45, h: 0.45 });
  s.addText("github.com/Yash-Kavaiya/nemodesk-it-agent", { x: 1.4, y: 4.9, w: 9, h: 0.45, fontSize: 16, color: NV, fontFace: "Consolas", valign: "middle" });
  s.addText("India Agentic AI Open Hackathon  -  Track A: Agentic Workflows", { x: 0.8, y: 6.4, w: 11, h: 0.4, fontSize: 13, color: MUTED, fontFace: BODY });

  await p.writeFile({ fileName: "NemoDesk_Pitch_Deck.pptx" });
  console.log("WROTE NemoDesk_Pitch_Deck.pptx");
})();
