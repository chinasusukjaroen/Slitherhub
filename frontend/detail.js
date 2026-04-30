const task = JSON.parse(localStorage.getItem('selectedAssignment') || 'null');
const area = document.getElementById('detailArea');

if (!task) {
  area.innerHTML = `
    <div class="not-found">
      <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
        <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
      </svg>
      <p>ไม่พบข้อมูลงาน กรุณากลับไปเลือกใหม่</p>
    </div>`;
} else {
  renderDetail(task);
}

// Parse deadline from title string e.g. "... (Due: วันอังคารที่ 28 เม.ย. 2569 เวลา 23.59 น.)"
function parseDueDateFromTitle(title) {
  const match = title.match(/Due:\s*\S+\s+(\d+)\s+(\S+)\s+(\d+)\s+เวลา\s+(\d+)\.(\d+)/);
  if (!match) return null;

  const [, day, monthStr, yearBE, hour, minute] = match;

  const monthMap = {
    'ม.ค.': 0, 'ก.พ.': 1, 'มี.ค.': 2, 'เม.ย.': 3,
    'พ.ค.': 4, 'มิ.ย.': 5, 'ก.ค.': 6, 'ส.ค.': 7,
    'ก.ย.': 8, 'ต.ค.': 9, 'พ.ย.': 10, 'ธ.ค.': 11
  };

  const month = monthMap[monthStr];
  if (month === undefined) return null;

  const yearCE = parseInt(yearBE) - 543; // แปลง พ.ศ. → ค.ศ.
  const date = new Date(yearCE, month, parseInt(day), parseInt(hour), parseInt(minute));
  return isNaN(date.getTime()) ? null : date;
}

function renderDetail(a) {
  const stripeColor = { submitted: '#0f766e', pending: '#d97706', late: '#dc2626' }[a.status] || '#9ca3af';

  // ใช้ duedate ถ้ามี ถ้าไม่มีให้ parse จาก title
  let due = a.duedate > 0 ? new Date(a.duedate * 1000) : parseDueDateFromTitle(a.title || '');

  const dateStr = due
    ? due.toLocaleDateString('th-TH', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
    : '-';

  const now = Date.now() / 1000;
  const dueTimestamp = due ? due.getTime() / 1000 : null;
  const daysLeft = dueTimestamp ? Math.ceil((dueTimestamp - now) / 86400) : null;

  let daysLabel = '-';
  if (daysLeft !== null) {
    if (daysLeft <= 0)       daysLabel = '<span style="color:#dc2626;font-weight:700">วันนี้!</span>';
    else if (daysLeft === 1) daysLabel = '<span style="color:#dc2626;font-weight:700">พรุ่งนี้</span>';
    else if (daysLeft <= 5)  daysLabel = `<span style="color:#d97706;font-weight:600">อีก ${daysLeft} วัน</span>`;
    else                     daysLabel = `<span style="color:#0f766e">อีก ${daysLeft} วัน</span>`;
  }

  const statusLabel = { submitted: 'ส่งแล้ว', pending: 'ยังไม่ส่ง', late: 'ส่งล่าช้า' }[a.status] || a.status;
  const badgeClass  = `badge badge-${a.status}`;

  area.innerHTML = `
    <div class="detail-card">
      <div class="detail-stripe" style="background:${stripeColor}"></div>
      <div class="detail-body">
        <div class="detail-subject">
          <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="margin-right:6px">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          ${escHtml(a.subject)}
        </div>

        <div class="detail-title">${escHtml(a.title)}</div>

        <div class="detail-meta">
          <div class="detail-meta-row">
            <span class="detail-meta-label">สถานะ</span>
            <span class="detail-meta-value"><span class="${badgeClass}">${statusLabel}</span></span>
          </div>
          <div class="detail-meta-row">
            <span class="detail-meta-label">กำหนดส่ง</span>
            <span class="detail-meta-value">${dateStr}</span>
          </div>
          ${daysLeft !== null && a.status === 'pending' ? `
          <div class="detail-meta-row">
            <span class="detail-meta-label">เหลือเวลา</span>
            <span class="detail-meta-value">${daysLabel}</span>
          </div>` : ''}
        </div>

        ${a.intro ? `<div class="detail-intro">${a.intro}</div>` : ''}

        <div class="detail-actions">
          ${a.source_url ? `
            <a class="btn-primary" href="${a.source_url}" target="_blank">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
              ไปที่งาน
            </a>` : ''}
          <button class="btn-secondary" onclick="history.back()">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/>
            </svg>
            กลับ
          </button>
        </div>
      </div>
    </div>
  `;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}