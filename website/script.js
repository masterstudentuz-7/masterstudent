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


// ===== COMMENTS SYSTEM (localStorage) =====
const commentForm = document.getElementById('commentForm');
const commentsList = document.getElementById('commentsList');

function loadComments() {
    const comments = JSON.parse(localStorage.getItem('ms_comments') || '[]');
    commentsList.innerHTML = '';
    comments.forEach(c => {
        const stars = '★'.repeat(c.rating) + '☆'.repeat(5 - c.rating);
        const date = new Date(c.date).toLocaleDateString('uz-UZ', { day: 'numeric', month: 'short', year: 'numeric' });
        const initial = c.name.charAt(0).toUpperCase();
        const el = document.createElement('div');
        el.className = 'comment-item';
        el.innerHTML = `
            <div class="comment-header">
                <div class="comment-author">
                    <div class="comment-ava">${initial}</div>
                    <span class="comment-name">${c.name}</span>
                </div>
                <div>
                    <span class="comment-rating">${stars}</span>
                    <span class="comment-date">${date}</span>
                </div>
            </div>
            <p class="comment-text">${c.text}</p>
        `;
        commentsList.appendChild(el);
    });
}

commentForm.addEventListener('submit', e => {
    e.preventDefault();
    const name = document.getElementById('commentName').value.trim();
    const rating = parseInt(document.getElementById('commentRating').value);
    const text = document.getElementById('commentText').value.trim();
    if (!name || !text) return;

    const comments = JSON.parse(localStorage.getItem('ms_comments') || '[]');
    comments.unshift({ name, rating, text, date: Date.now() });
    localStorage.setItem('ms_comments', JSON.stringify(comments));
    
    commentForm.reset();
    loadComments();
    
    // Success animation
    const btn = commentForm.querySelector('.btn-submit');
    btn.textContent = '✓ Yuborildi!';
    btn.style.background = '#10b981';
    setTimeout(() => { btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg> Yuborish'; btn.style.background = ''; }, 2000);
});

loadComments();

// ===== DONATE =====
document.querySelectorAll('.donate-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.donate-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

function copyCard() {
    navigator.clipboard.writeText('8600000000000000').then(() => {
        const btn = document.querySelector('.dm-copy');
        const orig = btn.textContent;
        btn.textContent = '✓ Nusxalandi!';
        btn.style.background = '#10b981';
        setTimeout(() => { btn.textContent = orig; btn.style.background = ''; }, 2000);
    });
}
