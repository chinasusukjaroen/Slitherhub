// ── Data ──────────────────────────────────────────────────────────────────────
const TASKS = [
  {
    task_id: 1,
    title: "Final Exam — Computer Networks",
    course_name: "CN401 Computer Networks",
    hours_left: 10,
    urgency_score: 60, keyword_score: 30, duration_score: 7,
    priority_score: 97, priority_label: "URGENT",
  },
  {
    task_id: 5,
    title: "Quiz 3 — Data Structures",
    course_name: "CS201 Data Structures",
    hours_left: 20,
    urgency_score: 60, keyword_score: 20, duration_score: 7,
    priority_score: 87, priority_label: "URGENT",
  },
  {
    task_id: 4,
    title: "โปรเจกต์กลุ่ม — ระบบ E-Commerce",
    course_name: "SE302 Software Engineering",
    hours_left: 72,
    urgency_score: 45, keyword_score: 30, duration_score: 2,
    priority_score: 77, priority_label: "HIGH",
  },
  {
    task_id: 2,
    title: "Lab 5 — TCP/IP",
    course_name: "CN401 Computer Networks",
    hours_left: 50,
    urgency_score: 45, keyword_score: 20, duration_score: 2,
    priority_score: 67, priority_label: "HIGH",
  },
  {
    task_id: 3,
    title: "ประกาศแจ้งข่าว — ปิดระบบชั่วคราว",
    course_name: "ฝ่ายวิชาการ",
    hours_left: 200,
    urgency_score: 15, keyword_score: 10, duration_score: 2,
    priority_score: 27, priority_label: "LOW",
  },
];

// ── Light-theme colour palette (matching dashboard style.css) ─────────────────
const LABEL_META = {
  URGENT: { color: "#b91c1c", bg: "#ffe1e1", text: "#b91c1c", glow: "rgba(185,28,28,.12)", emoji: "🔴" },
  HIGH:   { color: "#c2410c", bg: "#ffe6d5", text: "#c2410c", glow: "rgba(194,65,12,.10)", emoji: "🟠" },
  MEDIUM: { color: "#b45309", bg: "#fef3c7", text: "#b45309", glow: "rgba(180,83,9,.10)",  emoji: "🟡" },
  LOW:    { color: "#0f766e", bg: "#ccfbf1", text: "#0f766e", glow: "rgba(15,118,110,.10)", emoji: "🟢" },
};

const FILTERS = ["ALL", "URGENT", "HIGH", "MEDIUM", "LOW"];
let activeFilter = "ALL";

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatHours(h) {
  if (h <= 0) return "Overdue";
  if (h < 24) return `${Math.round(h)}h left`;
  const days = Math.floor(h / 24);
  const hrs  = Math.round(h % 24);
  return hrs ? `${days}d ${hrs}h` : `${days}d`;
}

function el(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "style" && typeof v === "object") Object.assign(e.style, v);
    else if (k.startsWith("on")) e.addEventListener(k.slice(2).toLowerCase(), v);
    else e.setAttribute(k, v);
  }
  for (const c of children) {
    if (c == null) continue;
    e.append(typeof c === "string" ? document.createTextNode(c) : c);
  }
  return e;
}

// ── Render stat pills ─────────────────────────────────────────────────────────
function renderStats() {
  const row = document.getElementById("stat-row");
  row.innerHTML = "";
  ["URGENT", "HIGH", "MEDIUM", "LOW"].forEach(label => {
    const m     = LABEL_META[label];
    const count = TASKS.filter(t => t.priority_label === label).length;
    const pill  = el("div", {
      class: "stat-pill",
      style: {
        background:  m.bg,
        borderColor: m.color + "55",
        color:       m.color,
      },
    },
      `${m.emoji} ${label} `,
      el("span", { style: { opacity: ".65", fontWeight: "400" } }, `×${count}`)
    );
    row.appendChild(pill);
  });
}

// ── Render filter bar ─────────────────────────────────────────────────────────
function renderFilters() {
  const bar = document.getElementById("filter-bar");
  bar.innerHTML = "";
  FILTERS.forEach(label => {
    const btn = el("button", {
      class: "filter-btn" + (label === activeFilter ? " active" : ""),
      onclick: () => {
        activeFilter = label;
        renderFilters();
        renderTasks();
      },
    }, label === "ALL" ? "ALL" : `${LABEL_META[label].emoji} ${label}`);
    bar.appendChild(btn);
  });
}

// ── Render score bar ──────────────────────────────────────────────────────────
function makeScoreBar(label, value, max, color) {
  const row   = el("div", { class: "score-bar-row" });
  const meta  = el("div", { class: "score-bar-meta" });
  meta.appendChild(el("span", {}, label));
  meta.appendChild(el("span", {}, `${value}/${max}`));
  const track = el("div", { class: "score-bar-track" });
  const fill  = el("div", { class: "score-bar-fill", style: { width: "0%", background: color } });
  track.appendChild(fill);
  row.append(meta, track);
  setTimeout(() => { fill.style.width = `${(value / max) * 100}%`; }, 50);
  return row;
}

// ── Render single task card ───────────────────────────────────────────────────
function makeCard(task, index) {
  const m = LABEL_META[task.priority_label] || LABEL_META["LOW"];
  let expanded = false;

  const card = el("div", {
    class: "task-card",
    style: {
      animationDelay:   `${index * 0.07}s`,
      borderColor:      "#e5e7eb",
      borderLeftColor:  m.color,
    },
  });

  // Top row
  const top  = el("div", { class: "card-top" });
  const rank = el("div", { class: "rank-badge", style: {
    background:  m.bg,
    borderColor: m.color + "44",
    color:       m.color,
  }}, String(index + 1));

  const info = el("div", { class: "card-info" });
  info.appendChild(el("div", { class: "card-title"  }, task.title));
  info.appendChild(el("div", { class: "card-course" }, task.course_name));

  const right  = el("div", { class: "card-right" });
  const pbadge = el("div", { class: "priority-badge", style: { background: m.bg, color: m.text } }, task.priority_label);
  const pscore = el("div", { class: "priority-score", style: { color: m.color } }, String(task.priority_score));
  const scap   = el("div", { class: "score-cap" }, "/ 100");
  right.append(pbadge, pscore, scap);
  top.append(rank, info, right);

  // Time pill
  const timeRow  = el("div", { class: "time-row" });
  const isUrgent = task.hours_left <= 24;
  const timePill = el("span", { class: "time-pill", style: {
    background:  isUrgent ? "#ffe1e1" : "#f3f4f6",
    color:       isUrgent ? "#b91c1c" : "#6b7280",
    borderColor: isUrgent ? "#b91c1c44" : "#e5e7eb",
  }}, `⏱ ${formatHours(task.hours_left)}`);
  timeRow.appendChild(timePill);

  // Score breakdown (hidden by default)
  const breakdown = el("div", { class: "breakdown" });
  breakdown.appendChild(el("div", { class: "breakdown-label" }, "Score Breakdown"));
  breakdown.appendChild(makeScoreBar("⏱ Time Urgency",    task.urgency_score,  60, "#b91c1c"));
  breakdown.appendChild(makeScoreBar("🔍 Keyword Weight",  task.keyword_score,  30, "#c2410c"));
  breakdown.appendChild(makeScoreBar("⏳ Task Duration",   task.duration_score, 10, "#0f766e"));
  const total = el("div", { class: "breakdown-total" });
  total.append("Total: ", el("span", { style: { color: m.color } }, String(task.priority_score)));
  breakdown.appendChild(total);

  card.append(top, timeRow, breakdown);

  // Toggle expand on click
  card.addEventListener("click", () => {
    expanded = !expanded;
    breakdown.classList.toggle("open", expanded);
    card.style.boxShadow = expanded
      ? `0 8px 32px ${m.glow}, 0 4px 15px rgba(0,0,0,0.04)`
      : "0 4px 15px rgba(0,0,0,0.02)";
  });

  return card;
}

// ── Render task list ──────────────────────────────────────────────────────────
function renderTasks() {
  const list = document.getElementById("task-list");
  list.innerHTML = "";
  const filtered = activeFilter === "ALL"
    ? TASKS
    : TASKS.filter(t => t.priority_label === activeFilter);
  filtered.forEach((task, i) => list.appendChild(makeCard(task, i)));
}

// ── Boot ──────────────────────────────────────────────────────────────────────
renderStats();
renderFilters();
renderTasks();