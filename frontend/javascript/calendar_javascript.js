import { CONFIG } from './config.js';

document.addEventListener('DOMContentLoaded', async function () {

  const calendarEl = document.getElementById('calendar');

  let deadlines = {};
  let calendarEvents = [];
  let calendar;

  try {
    console.log("Starting fetch...");
    const response = await fetch(`${CONFIG.BACKEND_API_URL}/tasks`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
    });

    console.log("Response received:", response.status);
    const jsonData = await response.json();
    const data = jsonData.data;
    console.log("Data parsed:", data);

    if (data) {
      data.forEach(task => {
        // ข้ามงานที่ไม่มี deadline จริง
        if (!task.deadline || task.deadline.startsWith('1970')) {
    if (task.status !== 'overdue') return; // ถ้าไม่ใช่ overdue ก็ข้ามไป
    task.deadline = new Date().toISOString().split('T')[0] + ' 23:59:00'; // ใช้วันนี้แทน
}

        // รองรับทั้ง "2026-02-10 23:59:00" และ "2026-02-10T23:59:00"
        const date = task.deadline.split(/T| /)[0];
        const link = task.source_url || null;

        if (!deadlines[date]) deadlines[date] = [];
        deadlines[date].push({
          text:        `[${task.course_name}] ${task.title}`,
          link:        link,
          deadline:    task.deadline,
          course_name: task.course_name,
          status:      task.status,
        });

        // เพิ่ม event สำหรับ FullCalendar
        calendarEvents.push({
          title: task.course_name,
          date:  date,
          color: task.status === 'submitted' ? '#16a34a'
     : task.status === 'pending'   ? '#ab0000'
     : task.status === 'overdue'   ? '#7c3aed'  // ม่วง
     : '#7c3aed',
          url:   link || undefined,
        });
      });
    }

  } catch (err) {
    console.error('โหลด deadline ไม่สำเร็จ:', err);
  }

  // ================= FULLCALENDAR =================
  calendar = new FullCalendar.Calendar(calendarEl, {

    initialView: 'dayGridMonth',

    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: ''
    },

    events: calendarEvents,

    // ป้องกัน FullCalendar navigate ออกเมื่อ url มีค่า
    eventClick: function (info) {
      if (info.event.url) {
        info.jsEvent.preventDefault();
        window.open(info.event.url, '_blank');
      }
    },

    datesSet: function () {
      Object.keys(deadlines).forEach(date => {
        const cell = document.querySelector(`[data-date="${date}"]`);
        if (!cell) return;

        cell.classList.add('fc-day-has-deadline');

        // ถ้าทุกงานในวันนั้น submitted → ใช้ class พิเศษ
        const allSubmitted = deadlines[date].every(t => t.status === 'submitted');
        if (allSubmitted) {
          cell.classList.add('urgency-submitted');
          return;
        }

        const order = ['urgency-late', 'urgency-critical', 'urgency-warning', 'urgency-safe'];
        const topClass = deadlines[date]
          .map(t => getUrgencyClass(t.deadline))
          .sort((a, b) => order.indexOf(a) - order.indexOf(b))[0];

        cell.classList.add(topClass);
      });
    },

    dateClick: function (info) {
      showPopup(info.dateStr, info.jsEvent, deadlines);
    }

  });

  calendar.render();

  // ================= WHEEL SCROLL =================
  calendarEl.addEventListener('wheel', function (e) {
    e.preventDefault();
    if (e.deltaY > 0) calendar.next();
    else              calendar.prev();
  }, { passive: false });

});


// ================= URGENCY CLASS =================
function getUrgencyClass(deadlineStr) {
  const now = new Date();
  const deadline = new Date(deadlineStr);
  const diffDays = (deadline - now) / (1000 * 60 * 60 * 24);

  if (diffDays < 0)   return 'urgency-late';
  if (diffDays <= 3)  return 'urgency-critical';
  if (diffDays <= 30) return 'urgency-warning';
  return 'urgency-safe';
}


// ================= POPUP =================
function showPopup(dateStr, mouseEvent, deadlines) {

  const old = document.getElementById('date-popup');
  if (old) old.remove();

  const tasks = deadlines[dateStr] || [];
  const taskHTML = tasks.length > 0
    ? tasks.map(t => {
        const cls = t.status === 'submitted' ? 'urgency-safe' : getUrgencyClass(t.deadline);
        return `
          <div class="popup-task-item ${cls}">
            <span class="popup-dot"></span>
            ${t.link
              ? `<a href="${t.link}" target="_blank" rel="noopener noreferrer">${t.text}</a>`
              : `<span>${t.text}</span>`
            }
          </div>
        `;
      }).join('')
    : `<p class="popup-empty">ไม่มีงานในวันนี้</p>`;

  const popup = document.createElement('div');
  popup.id = 'date-popup';

  popup.innerHTML = `
    <div class="popup-header">
      <span class="popup-date">${formatDate(dateStr)}</span>
      <button class="popup-close" onclick="document.getElementById('date-popup').remove()">✕</button>
    </div>
    <div class="popup-tasks">
      ${taskHTML}
    </div>
  `;

  let top  = mouseEvent.clientY + window.scrollY - 20;
  let left = mouseEvent.clientX + window.scrollX - 20;

  if (left + 280 > window.innerWidth) left = window.innerWidth - 300;

  popup.style.top  = top  + 'px';
  popup.style.left = left + 'px';

  document.body.appendChild(popup);

  setTimeout(() => {
    document.addEventListener('click', function handler(e) {
      if (!popup.contains(e.target)) {
        popup.remove();
        document.removeEventListener('click', handler);
      }
    });
  }, 100);
}


// ================= FORMAT DATE =================
function formatDate(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleDateString('th-TH', {
    weekday: 'long',
    year:    'numeric',
    month:   'long',
    day:     'numeric'
  });
}