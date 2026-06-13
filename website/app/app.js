// ===== Telegram Web App init =====
const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) {
    tg.ready();
    tg.expand();
}

// ===== 15 ta dizayn (rang sxemalari bilan) =====
const DESIGNS = [
    { id: "business",  name: "💼 Business",  bg: "#1F3864", title: "#FFFFFF", text: "#D9E2F3", accent: "#4C7CC9" },
    { id: "minimal",   name: "⚪ Minimal",   bg: "#FFFFFF", title: "#2D2D2D", text: "#555555", accent: "#BBBBBB" },
    { id: "dark",      name: "🌑 Dark",      bg: "#1A1A2E", title: "#E94560", text: "#EAEAEA", accent: "#E94560" },
    { id: "modern",    name: "🔷 Modern",    bg: "#F8F9FA", title: "#212529", text: "#495057", accent: "#3B82F6" },
    { id: "education", name: "📚 Education", bg: "#E8F5E9", title: "#1B5E20", text: "#2E7D32", accent: "#43A047" },
    { id: "corporate", name: "🏢 Corporate", bg: "#0D47A1", title: "#FFFFFF", text: "#BBDEFB", accent: "#42A5F5" },
    { id: "startup",   name: "🚀 Startup",   bg: "#FFF3E0", title: "#E65100", text: "#F57C00", accent: "#FF9800" },
    { id: "creative",  name: "🎨 Creative",  bg: "#F3E5F5", title: "#6A1B9A", text: "#8E24AA", accent: "#AB47BC" },
    { id: "elegant",   name: "✨ Elegant",   bg: "#FBE9E7", title: "#3E2723", text: "#5D4037", accent: "#8D6E63" },
    { id: "premium",   name: "👑 Premium",   bg: "#212121", title: "#FFD700", text: "#BDBDBD", accent: "#FFD700" },
    { id: "ocean",     name: "🌊 Ocean",     bg: "#01579B", title: "#FFFFFF", text: "#B3E5FC", accent: "#00BCD4" },
    { id: "sunset",    name: "🌅 Sunset",    bg: "#BF360C", title: "#FFF3E0", text: "#FFCCBC", accent: "#FF7043" },
    { id: "forest",    name: "🌲 Forest",    bg: "#1B5E20", title: "#FFFFFF", text: "#C8E6C9", accent: "#66BB6A" },
    { id: "royal",     name: "🟣 Royal",     bg: "#4A148C", title: "#FFD700", text: "#E1BEE7", accent: "#FFD700" },
    { id: "neon",      name: "⚡ Neon",      bg: "#0D0D0D", title: "#00E5FF", text: "#B2EBF2", accent: "#00E5FF" },
];

let selectedDesign = "business";

// Dizayn kartalarini chizish
const designsEl = document.getElementById("designs");
DESIGNS.forEach((d, i) => {
    const card = document.createElement("div");
    card.className = "design-card" + (i === 0 ? " selected" : "");
    card.dataset.id = d.id;
    card.innerHTML = `
        <div class="design-preview" style="background:${d.bg}">
            <div class="dp-accent" style="background:${d.accent};width:34px;height:34px;top:-8px;right:-8px"></div>
            <div class="dp-title" style="color:${d.title}">${d.name.replace(/^[^\s]+\s/, '')}</div>
            <div class="dp-line" style="background:${d.text}"></div>
            <div class="dp-line" style="background:${d.text}"></div>
            <div class="dp-line short" style="background:${d.text}"></div>
        </div>
        <div class="design-name">${d.name}</div>
    `;
    card.addEventListener("click", () => {
        document.querySelectorAll(".design-card").forEach(c => c.classList.remove("selected"));
        card.classList.add("selected");
        selectedDesign = d.id;
    });
    designsEl.appendChild(card);
});

// Radio kartalar (rasm usuli, tarif, format)
function setupRadios(groupId) {
    const group = document.getElementById(groupId);
    group.querySelectorAll(".radio-card").forEach(card => {
        card.addEventListener("click", () => {
            group.querySelectorAll(".radio-card").forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");
            card.querySelector("input").checked = true;
        });
    });
}
setupRadios("imageMode");
setupRadios("tariff");
setupRadios("format");

// ===== Yuborish =====
document.getElementById("submitBtn").addEventListener("click", () => {
    const topic = document.getElementById("topic").value.trim();
    const author = document.getElementById("author").value.trim();
    const lang = document.getElementById("lang").value;
    const slides = parseInt(document.getElementById("slides").value);
    const imgMode = document.querySelector('input[name="img"]:checked').value;
    const tariff = document.querySelector('input[name="tariff"]:checked').value;
    const format = document.querySelector('input[name="format"]:checked').value;
    const errEl = document.getElementById("error");

    if (!topic || topic.length < 3) {
        errEl.textContent = "❗ Iltimos, mavzuni to'liq yozing";
        return;
    }
    errEl.textContent = "";

    const payload = {
        type: "ppt_webapp",
        topic, author, lang, slides,
        design: selectedDesign,
        image_mode: imgMode,
        tariff, format
    };

    if (tg) {
        tg.sendData(JSON.stringify(payload));
        tg.close();
    } else {
        alert("Bu sahifa faqat Telegram bot ichida ishlaydi.\n\nMa'lumot:\n" + JSON.stringify(payload, null, 2));
    }
});
