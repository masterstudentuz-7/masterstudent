// Navbar
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => navbar.classList.toggle('scrolled', window.scrollY > 40));

// Mobile menu
document.getElementById('menuToggle').addEventListener('click', function() {
    const menu = document.getElementById('navMenu');
    menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
    menu.style.position = 'absolute';
    menu.style.top = '60px';
    menu.style.left = '0';
    menu.style.right = '0';
    menu.style.background = 'rgba(9,9,11,.98)';
    menu.style.flexDirection = 'column';
    menu.style.padding = '24px';
    menu.style.gap = '16px';
    menu.style.borderBottom = '1px solid var(--border)';
});

// Counter
const counters = document.querySelectorAll('.metric-value');
const obs = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const el = entry.target;
            const target = parseInt(el.dataset.count);
            let current = 0;
            const step = target / 30;
            const timer = setInterval(() => {
                current += step;
                if (current >= target) { el.textContent = target.toLocaleString(); clearInterval(timer); }
                else el.textContent = Math.floor(current).toLocaleString();
            }, 30);
            obs.unobserve(el);
        }
    });
}, { threshold: 0.5 });
counters.forEach(c => obs.observe(c));

// Scroll animation
const animEls = document.querySelectorAll('.service-item, .p-step, .price-card, .testimonial');
const sObs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.style.opacity='1'; e.target.style.transform='translateY(0)'; sObs.unobserve(e.target); }});
}, { threshold: 0.05 });
animEls.forEach(el => { el.style.opacity='0'; el.style.transform='translateY(20px)'; el.style.transition='all .5s ease'; sObs.observe(el); });

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => { e.preventDefault(); const t=document.querySelector(a.getAttribute('href')); if(t) t.scrollIntoView({behavior:'smooth',block:'start'}); });
});
