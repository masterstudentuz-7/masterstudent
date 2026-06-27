// Navbar scroll
const header = document.getElementById('header');
window.addEventListener('scroll', () => header.classList.toggle('scrolled', window.scrollY > 60));

// Custom cursor (desktop only)
if (window.innerWidth > 768) {
    const cursor = document.getElementById('cursor');
    const follower = document.getElementById('cursorFollower');
    document.addEventListener('mousemove', e => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
        setTimeout(() => {
            follower.style.left = e.clientX + 'px';
            follower.style.top = e.clientY + 'px';
        }, 80);
    });
    document.querySelectorAll('a, button').forEach(el => {
        el.addEventListener('mouseenter', () => { cursor.style.transform = 'scale(2)'; follower.style.transform = 'scale(1.5)'; });
        el.addEventListener('mouseleave', () => { cursor.style.transform = 'scale(1)'; follower.style.transform = 'scale(1)'; });
    });
}

// Mobile menu
document.getElementById('mobileToggle').addEventListener('click', function() {
    this.classList.toggle('active');
    document.getElementById('nav').classList.toggle('open');
});

// Counter animation
const statNums = document.querySelectorAll('.stat-num');
const cObs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target, target = parseInt(el.dataset.count);
            let cur = 0;
            const step = Math.max(1, target / 40);
            const timer = setInterval(() => {
                cur += step;
                if (cur >= target) { el.textContent = target.toLocaleString(); clearInterval(timer); }
                else el.textContent = Math.floor(cur).toLocaleString();
            }, 35);
            cObs.unobserve(el);
        }
    });
}, { threshold: 0.5 });
statNums.forEach(s => cObs.observe(s));

// Scroll reveal
const revealEls = document.querySelectorAll('.feature-card, .svc-row, .pricing-card, .review-item');
const rObs = new IntersectionObserver(entries => {
    entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.classList.add('revealed');
            }, i * 60);
            rObs.unobserve(entry.target);
        }
    });
}, { threshold: 0.08 });
revealEls.forEach(el => rObs.observe(el));

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        e.preventDefault();
        const t = document.querySelector(a.getAttribute('href'));
        if (t) { t.scrollIntoView({ behavior: 'smooth', block: 'start' }); document.getElementById('nav').classList.remove('open'); }
    });
});


// ===== COMMENTS SYSTEM (Firebase — hammaga ko'rinadi) =====
// Sozlash: pastdagi firebaseConfig ni o'z loyihangiz ma'lumotlari bilan to'ldiring.
// Firebase bepul: https://console.firebase.google.com → Firestore Database yarating.
const firebaseConfig = {
    apiKey: "AIzaSyBx9FnQyRnymIF163TWaV81Cti4oelx73o",
    authDomain: "master-student-58976.firebaseapp.com",
    projectId: "master-student-58976",
    storageBucket: "master-student-58976.firebasestorage.app",
    messagingSenderId: "22664104679",
    appId: "1:22664104679:web:60aa70dcd821758b6f7042"
};

// Admin kaliti — izoh o'chirish uchun. URL'ga ?admin=KALIT qo'shilsa, o'chirish tugmasi chiqadi.
// Misol: masterstudent.netlify.app/?admin=MasterAdmin2026
const ADMIN_KEY = "MasterAdmin2026";

const commentForm = document.getElementById('commentForm');
const commentsList = document.getElementById('commentsList');
const urlParams = new URLSearchParams(window.location.search);
const isAdmin = urlParams.get('admin') === ADMIN_KEY;

let db = null;
let firebaseReady = false;

// Firebase'ni ishga tushirish (agar sozlangan bo'lsa)
try {
    if (typeof firebase !== 'undefined' && firebaseConfig.apiKey !== "SIZNING_API_KEY") {
        firebase.initializeApp(firebaseConfig);
        db = firebase.firestore();
        firebaseReady = true;
    }
} catch (e) {
    console.warn('Firebase sozlanmagan:', e);
}

function renderComment(c, id) {
    const stars = '★'.repeat(c.rating) + '☆'.repeat(5 - c.rating);
    const date = c.date ? new Date(c.date).toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short', year: 'numeric' }) : '';
    const initial = (c.name || '?').charAt(0).toUpperCase();
    const delBtn = isAdmin ? `<button class="comment-del" onclick="deleteComment('${id}')">🗑 O'chirish</button>` : '';
    const el = document.createElement('div');
    el.className = 'comment-item';
    el.innerHTML = `
        <div class="comment-header">
            <div class="comment-author">
                <div class="comment-ava">${initial}</div>
                <span class="comment-name">${escapeHtml(c.name)}</span>
            </div>
            <div>
                <span class="comment-rating">${stars}</span>
                <span class="comment-date">${date}</span>
            </div>
        </div>
        <p class="comment-text">${escapeHtml(c.text)}</p>
        ${delBtn}
    `;
    return el;
}

function escapeHtml(s) {
    return (s || '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function loadComments() {
    if (!commentsList) return;
    if (firebaseReady) {
        // Real-time — hamma yangi izohlarni darhol ko'radi
        db.collection('comments').orderBy('date', 'desc').limit(100)
          .onSnapshot(snap => {
              commentsList.innerHTML = '';
              if (snap.empty) {
                  commentsList.innerHTML = '<p style="text-align:center;color:var(--text-3)">Hozircha izohlar yo\'q. Birinchi bo\'lib fikr qoldiring! 😊</p>';
              }
              snap.forEach(doc => commentsList.appendChild(renderComment(doc.data(), doc.id)));
          });
    } else {
        // Firebase sozlanmagan — localStorage (faqat shu brauzerda)
        const comments = JSON.parse(localStorage.getItem('ms_comments') || '[]');
        commentsList.innerHTML = '';
        comments.forEach((c, i) => commentsList.appendChild(renderComment(c, 'local_' + i)));
    }
}

window.deleteComment = async function(id) {
    if (!isAdmin) return;
    if (!confirm("Bu izohni o'chirmoqchimisiz?")) return;
    if (firebaseReady) {
        await db.collection('comments').doc(id).delete();
    } else {
        const comments = JSON.parse(localStorage.getItem('ms_comments') || '[]');
        const idx = parseInt(id.replace('local_', ''));
        comments.splice(idx, 1);
        localStorage.setItem('ms_comments', JSON.stringify(comments));
        loadComments();
    }
};

if (commentForm) {
    commentForm.addEventListener('submit', async e => {
        e.preventDefault();
        const name = document.getElementById('commentName').value.trim();
        const rating = parseInt(document.getElementById('commentRating').value);
        const text = document.getElementById('commentText').value.trim();
        if (!name || !text) return;

        const comment = { name, rating, text, date: Date.now() };
        if (firebaseReady) {
            await db.collection('comments').add(comment);
        } else {
            const comments = JSON.parse(localStorage.getItem('ms_comments') || '[]');
            comments.unshift(comment);
            localStorage.setItem('ms_comments', JSON.stringify(comments));
            loadComments();
        }

        commentForm.reset();
        const btn = commentForm.querySelector('.btn-submit');
        btn.textContent = '✓ Yuborildi!';
        btn.style.background = '#10b981';
        setTimeout(() => { btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg> Yuborish'; btn.style.background = ''; }, 2000);
    });
    loadComments();
}

// ===== DONATE =====
document.querySelectorAll('.donate-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.donate-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

function copyCard() {
    navigator.clipboard.writeText('9860010128293650').then(() => {
        const btn = document.querySelector('.dm-copy');
        const orig = btn.textContent;
        btn.textContent = '✓ Nusxalandi!';
        btn.style.background = '#10b981';
        setTimeout(() => { btn.textContent = orig; btn.style.background = ''; }, 2000);
    });
}
