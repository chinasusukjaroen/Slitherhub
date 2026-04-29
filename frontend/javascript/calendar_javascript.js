document.addEventListener('DOMContentLoaded', async function () {

  const calendarEl = document.getElementById('calendar');

  const params = new URLSearchParams(window.location.search);
  const student_id = params.get('id');

  let deadlines = {};
  let calendar; //

  try {
    // ====== MOCK DATA ======
    const mockData = [
      { course_name: 'Web Programming', title: 'ส่งโปรเจคกลางภาค', deadline: '2026-04-29T23:59:00' },
      { course_name: 'Database', title: 'Quiz ครั้งที่ 3', deadline: '2026-04-29T18:00:00' },
      { course_name: 'Algorithm', title: 'Assignment 5', deadline: '2026-05-05T23:59:00' },
      { course_name: 'Web Programming', title: 'ส่งโปรเจคปลายภาค', deadline: '2026-05-15T23:59:00' },
      { course_name: 'Network', title: 'Lab Report', deadline: '2026-05-20T17:00:00' },
    ];

    mockData.forEach(task => {
      const date = task.deadline.split('T')[0];
      if (!deadlines[date]) deadlines[date] = [];
      deadlines[date].push(`[${task.course_name}] ${task.title}`);
    });

    // ====== API จริง (เปิดใช้ภายหลัง) ======
    /*
    const url = student_id
      ? `/api/user_task?student_id=${student_id}`
      : '/api/user_task';

    const response = await fetch(url);
    const result = await response.json();

    if (result.success) {
      result.data.forEach(task => {
        const date = task.deadline.split('T')[0];
        if (!deadlines[date]) deadlines[date] = [];
        deadlines[date].push(`[${task.course_name}] ${task.title}`);
      });
    }
    */

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

    datesSet: function () {
      Object.keys(deadlines).forEach(date => {
        const cell = document.querySelector(`[data-date="${date}"]`);
        if (cell) cell.classList.add('fc-day-has-deadline');
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

    if (e.deltaY > 0) {
      calendar.next(); // ไปเดือนถัดไป
    } else {
      calendar.prev(); // ไปเดือนก่อนหน้า
    }

  }, { passive: false });

});


// ================= POPUP =================
function showPopup(dateStr, mouseEvent, deadlines) {

  const old = document.getElementById('date-popup');
  if (old) old.remove();

  const tasks = deadlines[dateStr] || [];

  const taskHTML = tasks.length > 0
    ? tasks.map(t => `
        <div class="popup-task-item">
          <span class="popup-dot"></span>
          <span>${t}</span>
        </div>
      `).join('')
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

  let top = mouseEvent.clientY + window.scrollY - 20;
  let left = mouseEvent.clientX + window.scrollX - 20;

  if (left + 280 > window.innerWidth) {
    left = window.innerWidth - 300;
  }

  popup.style.top = top + 'px';
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
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}