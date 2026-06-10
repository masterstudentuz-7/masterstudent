// Navbar scroll
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => { navbar.classList.toggle('scrolled', window.scrollY > 50); });

// Mobile menu
const mobileBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.getElementById('navLinks');
mobileBtn.addEventListener('click', () => { navLinks.classList.toggle('active'); });
navLinks.querySelectorAll('a').forEach(l => l.addEventListener('click', () => navLinks.classList.remove('active')));

// Counter animation
const counters = document.querySelectorAll('.stat-number');
const counterObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target, target = parseInt(el.dataset.count);
            let current = 0;
            const timer = setInterval(() => {
                current += target / 40;
                if (current >= target) { el.textContent = target.toLocaleString(); clearInterval(timer); }
                else { el.textContent = Math.floor(current).toLocaleString(); }
            }, 40);
            counterObs.unobserve(el);
        }
    });
}, { threshold: 0.5 });
counters.forEach(c => counterObs.observe(c));

// FAQ
document.querySelectorAll('.faq-item').forEach(item => {
    item.querySelector('.faq-question').addEventListener('click', () => {
        const active = item.classList.contains('active');
        document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));
        if (!active) item.classList.add('active');
    });
});

// Scroll animations
const animEls = document.querySelectorAll('.service-card, .step, .price-card, .review-card');
const scrollObs = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.style.opacity='1'; e.target.style.transform='translateY(0)'; scrollObs.unobserve(e.target); }});
}, { threshold: 0.1 });
animEls.forEach(el => { el.style.opacity='0'; el.style.transform='translateY(30px)'; el.style.transition='all 0.6s ease'; scrollObs.observe(el); });

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => { e.preventDefault(); const t = document.querySelector(a.getAttribute('href')); if(t) t.scrollIntoView({behavior:'smooth'}); });
});
