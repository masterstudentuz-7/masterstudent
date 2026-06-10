// Preloader
window.addEventListener('load', () => {
    setTimeout(() => {
        document.getElementById('preloader').style.opacity = '0';
        setTimeout(() => document.getElementById('preloader').style.display = 'none', 500);
    }, 1200);
});

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
    document.querySelectorAll('a, button, .btn-hero, .btn-premium, .btn-card').forEach(el => {
        el.addEventListener('mouseenter', () => { cursor.style.transform = 'scale(2)'; follower.style.transform = 'scale(1.5)'; });
        el.addEventListener('mouseleave', () => { cursor.style.transform = 'scale(1)'; follower.style.transform = 'scale(1)'; });
    });
}

// Navbar scroll
const header = document.getElementById('header');
window.addEventListener('scroll', () => header.classList.toggle('scrolled', window.scrollY > 60));

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
const revealEls = document.querySelectorAll('.feature-card, .svc-row, .pricing-card, .review-item, .showcase-card');
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

// Parallax showcase cards
window.addEventListener('scroll', () => {
    const scrolled = window.scrollY;
    document.querySelectorAll('.showcase-card').forEach((card, i) => {
        const speed = (i + 1) * 0.03;
        card.style.transform = `translateY(${scrolled * speed}px)`;
    });
});
