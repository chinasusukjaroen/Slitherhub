import { CONFIG } from '../config.js';
let assignments = [];
let currentTab = 'all';
let quickFilterStatus = null;

const SUBJECT_COLORS = [
  { bg: '#eff6ff', text: '#1d1b54', icon: '📘' },
  { bg: '#f0fdfa', text: '#0f766e', icon: '🧪' },
  { bg: '#fff7ed', text: '#c2410c', icon: '📐' },
  { bg: '#fdf4ff', text: '#7e22ce', icon: '🎨' },
  { bg: '#fef2f2', text: '#b91c1c', icon: '📊' },
  { bg: '#f0fdf4', text: '#15803d', icon: '🌱' },
];

/* ============================================================
   DONUT CHART
============================================================ */
function drawDonut(submitted, pending, late) {
  const total = submitted + pending + late;
  const svg = document.getElementById('donutSvg');
  document.getElementById('donutTotal').textContent = total;

  if (total === 0) {
    svg.innerHTML = `<circle cx="70" cy="70" r="52" fill="none" stroke="#f3f4f6" stroke-width="18"/>`;
    return;
  }

  const cx = 70, cy = 70, r = 52, stroke = 18;
  const circ = 2 * Math.PI * r;
  const gap = 3;

  const segments = [
    { val: submitted, color: '#0f766e' },
    { val: pending,   color: '#d97706' },
    { val: late,      color: '#dc2626' },
  ].filter(s => s.val > 0);

  let html = '';
  let offset = -circ * 0.25;

  for (const seg of segments) {
    const frac = seg.val / total;
    const dash = Math.max(0, circ * frac - gap);
    html += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none"
      stroke="${seg.color}" stroke-width="${stroke}"
      stroke-dasharray="${dash} ${circ - dash}"
      stroke-dashoffset="${-offset}"
      stroke-linecap="round"
      style="transition: stroke-dasharray 0.6s ease"/>`;
    offset += circ * frac;
  }

  svg.innerHTML = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#f3f4f6" stroke-width="${stroke}"/>` + html;

  const pct = v => total > 0 ? Math.round(v / total * 100) : 0;
  document.getElementById('legendSubmitted').textContent = submitted;
  document.getElementById('legendPending').textContent = pending;
  document.getElementById('legendLate').textContent = late;
  document.getElementById('legendPctSubmitted').textContent = `(${pct(submitted)}%)`;
  document.getElementById('legendPctPending').textContent = `(${pct(pending)}%)`;
  document.getElementById('legendPctLate').textContent = `(${pct(late)}%)`;
}

/* ============================================================
   UPCOMING DEADLINES TIMELINE
============================================================ */
function renderTimeline() {
  const now = Date.now() / 1000;
  const upcoming = assignments
    .filter(a => a.status === 'pending' && a.duedate > 0)
    .sort((a,b) => a.duedate - b.duedate)
    .slice(0, 5);

  const el = document.getElementById('timelineList');
  if (!upcoming.length) {
    el.innerHTML = `<div style="text-align:center;color:#9ca3af;font-size:14px;padding:20px 0">ไม่มีงานที่ยังไม่ส่ง 🎉</div>`;
    return;
  }

  el.innerHTML = upcoming.map(a => {
    const daysLeft = Math.ceil((a.duedate - now) / 86400);
    let daysClass = 'days-ok', daysLabel = `อีก ${daysLeft} วัน`;
    let dotColor = '#0f766e';
    if (daysLeft <= 0) { daysClass = 'days-urgent'; daysLabel = 'วันนี้!'; dotColor = '#dc2626'; }
    else if (daysLeft <= 2) { daysClass = 'days-urgent'; dotColor = '#dc2626'; }
    else if (daysLeft <= 5) { daysClass = 'days-warn'; dotColor = '#d97706'; }

    return `<div class="timeline-item">
      <div class="timeline-dot" style="background:${dotColor}"></div>
      <div class="timeline-title" title="${escHtml(a.title)}">${escHtml(a.title)}</div>
      <span class="timeline-days ${daysClass}">${daysLabel}</span>
    </div>`;
  }).join('');
}

/* ============================================================
   QUICK FILTER FROM STAT CARDS
============================================================ */
function quickFilter(status, el) {
  quickFilterStatus = (quickFilterStatus === status) ? null : status;
  document.querySelectorAll('.stat-card').forEach(c => c.classList.remove('active-filter'));
  if (quickFilterStatus) el.classList.add('active-filter');

  const tabMap = { all: 0, submitted: 3, pending: 2, late: 4 };
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(b => b.classList.remove('active'));
  if (quickFilterStatus && tabMap[quickFilterStatus] !== undefined) {
    currentTab = quickFilterStatus === 'all' ? 'all' : quickFilterStatus;
    tabBtns[tabMap[quickFilterStatus]].classList.add('active');
  } else {
    currentTab = 'all';
    tabBtns[0].classList.add('active');
  }
  renderCurrentTab();
}

/* ============================================================
   BACKEND API FETCH (แทนที่ Moodle เดิม)
============================================================ */
async function fetchMoodleData() {
  if (!CONFIG?.BACKEND_API_URL || CONFIG.BACKEND_API_URL.includes('yourdomain')) {
    showToast('⚠️ กรุณาตั้งค่า BACKEND_API_URL ใน CONFIG');
    console.warn('CONFIG:', CONFIG);
    return;
  }

  const btn = document.getElementById('syncBtn');
  btn?.classList.add('loading');
  btn.innerHTML = `<svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" style="animation:spin 1s linear infinite"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg> กำลังโหลด...`;
  showSkeleton();
  console.log("🚀 Starting fetch...");

  try {
    const response = await fetch(`${CONFIG.BACKEND_API_URL}/tasks`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
    });

    console.log("✅ Response received:", response.status);
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);

    const jsonData = await response.json();
    const data = jsonData.data;
    console.log("📦 Data parsed:", data);

    // แปลงโครงสร้างข้อมูลให้ตรงกับระบบ
    assignments = (Array.isArray(data) ? data : []).map(task => {
      let dueTs = 0;
      if (task.duedate) {
        const d = new Date(task.duedate);
        dueTs = isNaN(d.getTime()) ? 0 : Math.floor(d.getTime() / 1000);
      }

      let status = (task.status || 'pending').toLowerCase();
      if (!['pending', 'submitted', 'late'].includes(status)) status = 'pending';

      return {
        id: task.id,
        title: task.title || 'ไม่มีชื่อ',
        subject: task.subject || task.course || 'วิชาไม่ระบุ',
        courseId: task.courseId || task.course_id || 0,
        duedate: dueTs,
        status: status,
        intro: task.description || task.intro || ''
      };
    });

    processAndRender();
    const lastSyncEl = document.getElementById('lastSync');
    if (lastSyncEl) lastSyncEl.textContent = `อัปเดตล่าสุด: ${new Date().toLocaleString('th-TH')}`;
    showToast(`✅ โหลดสำเร็จ ${assignments.length} งาน`);

  } catch (err) {
    console.error("❌ Fetch error:", err);
    showToast('❌ ' + (err.message || 'ดึงข้อมูลไม่สำเร็จ'));
    renderEmpty(`เชื่อมต่อเซิร์ฟเวอร์ไม่สำเร็จ<br><small style="color:#9ca3af">${err.message || ''}</small>`);
  } finally {
    const btn = document.getElementById('syncBtn');
    btn?.classList.remove('loading');
    if (btn) {
      btn.innerHTML = `<svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg> ซิงค์ข้อมูล`;
    }
  }
}

/* ============================================================
   DEMO DATA
============================================================ */
function loadDemoData() {
  const now = Date.now() / 1000;
  assignments = [
    { id:1, title:'Lab Report: Data Structures', subject:'CS211 โครงสร้างข้อมูล', courseId:1, duedate: now + 86400*2, status:'pending', intro:'เขียนรายงานการทดลอง Linked List และ Stack' },
    { id:2, title:'โจทย์ Programming ชุดที่ 3', subject:'CS211 โครงสร้างข้อมูล', courseId:1, duedate: now + 86400*5, status:'submitted', intro:'' },
    { id:3, title:'สรุปบทที่ 4: Database Normalization', subject:'CS231 ฐานข้อมูล', courseId:2, duedate: now - 86400*1, status:'late', intro:'สรุปเนื้อหา 1NF 2NF 3NF พร้อมตัวอย่าง' },
    { id:4, title:'ER Diagram Project', subject:'CS231 ฐานข้อมูล', courseId:2, duedate: now + 86400*10, status:'pending', intro:'' },
    { id:5, title:'Quiz บทที่ 2', subject:'MATH201 คณิตศาสตร์วิศวกรรม', courseId:3, duedate: now - 86400*3, status:'submitted', intro:'' },
    { id:6, title:'Homework: Calculus Set 5', subject:'MATH201 คณิตศาสตร์วิศวกรรม', courseId:3, duedate: now - 86400*2, status:'late', intro:'โจทย์ 1-20 จากหนังสือหน้า 145' },
    { id:7, title:'รายงานวิเคราะห์ Algorithm', subject:'CS301 Algorithm Design', courseId:4, duedate: now + 86400*7, status:'pending', intro:'' },
    { id:8, title:'Presentation: Sorting Algorithms', subject:'CS301 Algorithm Design', courseId:4, duedate: now + 86400*14, status:'submitted', intro:'' },
    { id:9, title:'Lab: Network Topology', subject:'NET401 เครือข่ายคอมพิวเตอร์', courseId:5, duedate: now + 86400*3, status:'pending', intro:'' },
    { id:10, title:'Final Project Proposal', subject:'NET401 เครือข่ายคอมพิวเตอร์', courseId:5, duedate: now + 86400*20, status:'pending', intro:'' },
  ];
  processAndRender();
  document.getElementById('lastSync').textContent = '⚠️ ข้อมูลตัวอย่าง — เชื่อมต่อ Backend จริงเพื่อดูงานของคุณ';
}

/* ============================================================
   RENDER & UTILS
============================================================ */
function processAndRender() {
  updateStats();
  updateSubjectFilter();
  renderTimeline();
  renderCurrentTab();
}

function updateStats() {
  const total = assignments.length;
  const submitted = assignments.filter(a => a.status === 'submitted').length;
  const pending = assignments.filter(a => a.status === 'pending').length;
  const late = assignments.filter(a => a.status === 'late').length;

  document.getElementById('statTotal').textContent = total;
  document.getElementById('statSubmitted').textContent = submitted;
  document.getElementById('statPending').textContent = pending;
  document.getElementById('statLate').textContent = late;

  const pct = (n) => total > 0 ? Math.round(n / total * 100) : 0;
  document.getElementById('barSubmitted').style.width = pct(submitted) + '%';
  document.getElementById('barPending').style.width = pct(pending) + '%';
  document.getElementById('barLate').style.width = pct(late) + '%';

  drawDonut(submitted, pending, late);
}

function updateSubjectFilter() {
  const sel = document.getElementById('subjectFilter');
  const subjects = [...new Set(assignments.map(a => a.subject))].sort();
  sel.innerHTML = '<option value="all">วิชาทั้งหมด</option>';
  subjects.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s; opt.textContent = s;
    sel.appendChild(opt);
  });
}

function switchTab(tab, btn) {
  currentTab = tab;
  quickFilterStatus = null;
  document.querySelectorAll('.stat-card').forEach(c => c.classList.remove('active-filter'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderCurrentTab();
}

function renderCurrentTab() {
  if (currentTab === 'bySubject') renderBySubject();
  else renderList(getFilteredAssignments());
}

function getFilteredAssignments() {
  let list = [...assignments];
  if (currentTab === 'pending') list = list.filter(a => a.status === 'pending');
  else if (currentTab === 'submitted') list = list.filter(a => a.status === 'submitted');
  else if (currentTab === 'late') list = list.filter(a => a.status === 'late');

  const subjectFilter = document.getElementById('subjectFilter').value;
  if (subjectFilter !== 'all') list = list.filter(a => a.subject === subjectFilter);

  const q = document.getElementById('searchInput').value.toLowerCase();
  if (q) list = list.filter(a => a.title.toLowerCase().includes(q) || a.subject.toLowerCase().includes(q));

  const sort = document.getElementById('sortSelect').value;
  if (sort === 'dueAsc') list.sort((a,b) => (a.duedate||Infinity) - (b.duedate||Infinity));
  else if (sort === 'dueDesc') list.sort((a,b) => (b.duedate||0) - (a.duedate||0));
  else if (sort === 'name') list.sort((a,b) => a.title.localeCompare(b.title));
  else if (sort === 'subject') list.sort((a,b) => a.subject.localeCompare(b.subject));

  document.getElementById('filterCount').textContent = `${list.length} รายการ`;
  return list;
}

function renderList(list) {
  const area = document.getElementById('contentArea');
  if (!list.length) { renderEmpty(); return; }
  area.innerHTML = `<div class="assignment-list">${list.map(assignmentCard).join('')}</div>`;
}

function renderBySubject() {
  let list = [...assignments];
  const subjectFilter = document.getElementById('subjectFilter').value;
  if (subjectFilter !== 'all') list = list.filter(a => a.subject === subjectFilter);
  const q = document.getElementById('searchInput').value.toLowerCase();
  if (q) list = list.filter(a => a.title.toLowerCase().includes(q) || a.subject.toLowerCase().includes(q));

  const subjects = [...new Set(list.map(a => a.subject))].sort();
  const area = document.getElementById('contentArea');
  if (!subjects.length) { renderEmpty(); return; }

  const subjectColorMap = {};
  subjects.forEach((s, i) => { subjectColorMap[s] = SUBJECT_COLORS[i % SUBJECT_COLORS.length]; });

  area.innerHTML = subjects.map(subject => {
    const items = list.filter(a => a.subject === subject);
    const color = subjectColorMap[subject];
    const submittedCount = items.filter(a => a.status === 'submitted').length;
    const pendingCount = items.filter(a => a.status === 'pending').length;
    const lateCount = items.filter(a => a.status === 'late').length;
    const total = items.length;
    const pct = total > 0 ? Math.round(submittedCount / total * 100) : 0;

    return `
      <div class="subject-section">
        <div class="subject-header">
          <div class="subject-icon" style="background:${color.bg};color:${color.text}">${color.icon}</div>
          <div>
            <span class="subject-name">${subject}</span>
            <div class="subject-progress-wrap" style="width:120px;margin-top:4px">
              <div class="subject-progress-fill" style="width:${pct}%"></div>
            </div>
          </div>
          <div class="subject-mini-stats">
            ${submittedCount > 0 ? `<span class="mini-stat mini-submitted">✓ ${submittedCount} ส่งแล้ว</span>` : ''}
            ${pendingCount > 0 ? `<span class="mini-stat mini-pending">⏳ ${pendingCount} ยังไม่ส่ง</span>` : ''}
            ${lateCount > 0 ? `<span class="mini-stat mini-late">⚠ ${lateCount} ล่าช้า</span>` : ''}
          </div>
        </div>
        <div class="assignment-list">${items.map(assignmentCard).join('')}</div>
      </div>
    `;
  }).join('');

  document.getElementById('filterCount').textContent = `${list.length} รายการ`;
}

function assignmentCard(a) {
  const now = Date.now() / 1000;
  const due = a.duedate > 0 ? new Date(a.duedate * 1000) : null;
  const daysLeft = due ? Math.ceil((a.duedate - now) / 86400) : null;

  const statusBadge = {
    submitted: `<span class="badge badge-submitted"><svg width="10" height="10" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg> ส่งแล้ว</span>`,
    pending: `<span class="badge badge-pending"><svg width="10" height="10" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg> ยังไม่ส่ง</span>`,
    late: `<span class="badge badge-late"><svg width="10" height="10" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> ล่าช้า</span>`,
  }[a.status];

  const iconBox = {
    submitted: `<div class="status-icon-box icon-submitted"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg></div>`,
    pending: `<div class="status-icon-box icon-pending"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div>`,
    late: `<div class="status-icon-box icon-late"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>`,
  }[a.status];

  let dueHtml = '';
  if (due) {
    const dateStr = due.toLocaleDateString('th-TH', { day:'numeric', month:'short', year:'numeric' });
    if (a.status === 'pending') {
      let remClass = 'due-ok', remLabel = `อีก ${daysLeft} วัน`;
      if (daysLeft <= 0) { remClass = 'due-urgent'; remLabel = 'วันนี้!'; }
      else if (daysLeft <= 2) remClass = 'due-urgent';
      else if (daysLeft <= 5) remClass = 'due-warn';
      dueHtml = `<div class="assignment-due"><div class="due-label">ครบกำหนด</div><div class="due-date">${dateStr}</div><div class="due-remaining ${remClass}">${remLabel}</div></div>`;
    } else if (a.status === 'late') {
      dueHtml = `<div class="assignment-due"><div class="due-label">เกินกำหนด</div><div class="due-date due-urgent">${dateStr}</div></div>`;
    } else {
      dueHtml = `<div class="assignment-due"><div class="due-label">ส่งแล้ว</div><div class="due-date">${dateStr}</div></div>`;
    }
  }

  return `
    <div class="assignment-card">
      <div class="card-status-stripe stripe-${a.status}"></div>
      <div class="card-body">
        ${iconBox}
        <div class="assignment-info">
          <div class="assignment-title">${escHtml(a.title)}</div>
          <div class="assignment-meta">
            <span><svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg><span class="badge-subject">${escHtml(a.subject)}</span></span>
            ${a.intro ? `<span style="color:#9ca3af;font-size:12px">${escHtml(a.intro.substring(0,60))}${a.intro.length>60?'…':''}</span>` : ''}
          </div>
          <div class="card-status-row">${statusBadge}</div>
        </div>
        <div class="card-right">${dueHtml}</div>
      </div>
    </div>
  `;
}

function renderEmpty(msg = 'ไม่พบงานที่ตรงกับเงื่อนไข') {
  document.getElementById('contentArea').innerHTML = `
    <div class="empty-state">
      <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
      <p>${msg}</p>
    </div>`;
  document.getElementById('filterCount').textContent = '0 รายการ';
}

function showSkeleton() {
  document.getElementById('contentArea').innerHTML = Array(5).fill('<div class="skeleton skel-card"></div>').join('');
}

function filterAssignments() { renderCurrentTab(); }

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

/* ============================================================
   INIT
============================================================ */
// เรียกใช้ฟังก์ชันตามการตั้งค่า
if (CONFIG.BACKEND_API_URL && !CONFIG.BACKEND_API_URL.includes('yourdomain')) {
  fetchMoodleData(); // ดึงข้อมูลจาก Backend จริง
} else {
  loadDemoData(); // ใช้ข้อมูลตัวอย่างถ้ายังไม่ได้ตั้งค่า
}