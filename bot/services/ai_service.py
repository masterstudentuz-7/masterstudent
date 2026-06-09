import io
import json
import logging
import asyncio
import google.generativeai as genai
from pptx import Presentation
from pptx.util import Inches, Pt, Cm, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from docx import Document
from docx.shared import Pt as DocxPt, Cm as DocxCm, Inches as DocxInches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
import qrcode

from config import (
    AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODELS,
    OPENAI_API_KEY, OPENAI_MODEL
)

logger = logging.getLogger(__name__)

# ===== GEMINI SETUP =====
genai.configure(api_key=GEMINI_API_KEY)


# ============================================================
# UNIVERSAL AI CALL
# ============================================================

async def ai_generate(prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
    """AI orqali matn generatsiya qilish."""
    if AI_PROVIDER == "openai":
        return await _openai_generate(prompt, max_tokens, temperature)
    return await _gemini_generate(prompt, max_tokens, temperature)


async def _gemini_generate(prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
    """Gemini modellarini ketma-ket sinab ko'radi. Quota xatosida kutib qayta sinaydi."""
    last_error = None
    max_retries = 2

    for attempt in range(max_retries):
        for model_name in GEMINI_MODELS:
            try:
                logger.info(f"Trying Gemini model: {model_name} (attempt {attempt + 1})")
                model = genai.GenerativeModel(model_name)
                generation_config = genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
                response = await model.generate_content_async(
                    prompt, generation_config=generation_config,
                )
                if response and response.text:
                    logger.info(f"Success with model: {model_name}")
                    return response.text.strip()
                else:
                    logger.warning(f"Empty response from model: {model_name}")
                    continue
            except Exception as e:
                last_error = e
                error_msg = str(e)
                if "429" in error_msg or "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
                    logger.warning(f"Model {model_name} quota exceeded, trying next...")
                elif "404" in error_msg or "NotFound" in error_msg:
                    logger.warning(f"Model {model_name} not found, skipping...")
                else:
                    logger.warning(f"Model {model_name} failed: {type(e).__name__}: {e}")
                continue

        if attempt < max_retries - 1:
            logger.info("All models failed. Waiting 15s before retry...")
            await asyncio.sleep(15)

    raise Exception(f"Barcha Gemini modellari ishlamadi. Oxirgi xato: {last_error}")


async def _openai_generate(prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
    """OpenAI orqali generatsiya (O'CHIRILGAN)."""
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"OpenAI xatosi: {e}")


# ============================================================
# GOST STANDARTLARI
# ============================================================

# GOST: Referat/Mustaqil ish sahifa sozlamalari
GOST_DOC = {
    "font_name": "Times New Roman",
    "font_size": DocxPt(14),
    "line_spacing": 1.5,
    "align": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "first_line_indent": DocxCm(1.25),
    "margin_left": DocxCm(3.0),
    "margin_right": DocxCm(1.5),
    "margin_top": DocxCm(2.0),
    "margin_bottom": DocxCm(2.0),
}

# GOST: Slayd shriftlari
GOST_PPT = {
    "title_font": "Times New Roman",
    "title_size": Pt(32),      # 28-36 pt
    "body_font": "Times New Roman",
    "body_size": Pt(20),       # 18-24 pt
}


def _apply_gost_paragraph(paragraph, font_name="Times New Roman", font_size=None,
                           bold=False, alignment=None, first_indent=None):
    """GOST formatini paragrafga qo'llash."""
    pf = paragraph.paragraph_format
    if alignment:
        pf.alignment = alignment
    if first_indent:
        pf.first_line_indent = first_indent
    pf.line_spacing = 1.5
    
    for run in paragraph.runs:
        run.font.name = font_name
        if font_size:
            run.font.size = font_size
        run.font.bold = bold


def _setup_gost_document(doc: Document):
    """GOST sahifa sozlamalarini o'rnatish: A4, maydonlar, shrift."""
    for section in doc.sections:
        section.page_width = DocxCm(21.0)   # A4
        section.page_height = DocxCm(29.7)  # A4
        section.left_margin = GOST_DOC["margin_left"]
        section.right_margin = GOST_DOC["margin_right"]
        section.top_margin = GOST_DOC["margin_top"]
        section.bottom_margin = GOST_DOC["margin_bottom"]


def _add_gost_title_page(doc: Document, title: str, doc_type: str, lang: str):
    """GOST titul varag'ini yaratish."""
    # Universitet nomi
    uni_text = {
        "uz": "O'ZBEKISTON RESPUBLIKASI\nOLIY VA O'RTA MAXSUS TA'LIM VAZIRLIGI",
        "ru": "РЕСПУБЛИКА УЗБЕКИСТАН\nМИНИСТЕРСТВО ВЫСШЕГО И СРЕДНЕГО СПЕЦИАЛЬНОГО ОБРАЗОВАНИЯ",
        "en": "REPUBLIC OF UZBEKISTAN\nMINISTRY OF HIGHER AND SECONDARY SPECIALIZED EDUCATION",
    }
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(uni_text.get(lang, uni_text["uz"]))
    run.font.name = "Times New Roman"
    run.font.size = DocxPt(14)
    
    # Bo'sh joy
    for _ in range(4):
        doc.add_paragraph()
    
    # Hujjat turi
    type_names = {
        "uz": {"referat": "REFERAT", "mustaqil_ish": "MUSTAQIL ISH"},
        "ru": {"referat": "РЕФЕРАТ", "mustaqil_ish": "САМОСТОЯТЕЛЬНАЯ РАБОТА"},
        "en": {"referat": "ESSAY/REPORT", "mustaqil_ish": "INDEPENDENT WORK"},
    }
    type_name = type_names.get(lang, type_names["uz"]).get(doc_type, "REFERAT")
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(type_name)
    run.font.name = "Times New Roman"
    run.font.size = DocxPt(20)
    run.font.bold = True
    
    # Bo'sh joy
    doc.add_paragraph()
    
    # Mavzu
    mavzu_label = {"uz": "Mavzu:", "ru": "Тема:", "en": "Topic:"}
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"{mavzu_label.get(lang, 'Mavzu:')} {title}")
    run.font.name = "Times New Roman"
    run.font.size = DocxPt(16)
    run.font.bold = True
    
    # Bo'sh joy
    for _ in range(8):
        doc.add_paragraph()
    
    # Sana
    import time
    from datetime import datetime
    now = datetime.now()
    city = {"uz": "Toshkent", "ru": "Ташкент", "en": "Tashkent"}
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"{city.get(lang, 'Toshkent')} — {now.year}")
    run.font.name = "Times New Roman"
    run.font.size = DocxPt(14)
    
    doc.add_page_break()


def _add_gost_heading(doc: Document, text: str, level: int = 1):
    """GOST sarlavha qo'shish: Bold, markazda, oxirida nuqta yo'q."""
    p = doc.add_paragraph()
    if level == 1:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Oxirida nuqtani olib tashlash
    clean_text = text.rstrip(".")
    
    run = p.add_run(clean_text.upper() if level == 1 else clean_text)
    run.font.name = "Times New Roman"
    run.font.size = DocxPt(14)
    run.font.bold = True
    
    # Bo'sh joy
    p.paragraph_format.space_before = DocxPt(12)
    p.paragraph_format.space_after = DocxPt(6)
    
    return p


def _add_gost_paragraph(doc: Document, text: str):
    """GOST asosiy matn paragrafi: 14pt, 1.5 interval, abzats 1.25sm, Justify."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = DocxCm(1.25)
    p.paragraph_format.line_spacing = 1.5
    
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = DocxPt(14)
    
    return p


# ============================================================
# PPT GENERATION — GOST
# ============================================================

PPT_COLOR_SCHEMES = {
    "business": {"bg": "1F3864", "title": "FFFFFF", "text": "D9E2F3"},
    "minimal": {"bg": "FFFFFF", "title": "2D2D2D", "text": "555555"},
    "dark": {"bg": "1A1A2E", "title": "E94560", "text": "EAEAEA"},
    "modern": {"bg": "F8F9FA", "title": "212529", "text": "495057"},
    "education": {"bg": "E8F5E9", "title": "1B5E20", "text": "2E7D32"},
    "corporate": {"bg": "0D47A1", "title": "FFFFFF", "text": "BBDEFB"},
    "startup": {"bg": "FFF3E0", "title": "E65100", "text": "F57C00"},
    "creative": {"bg": "F3E5F5", "title": "6A1B9A", "text": "8E24AA"},
    "elegant": {"bg": "FBE9E7", "title": "3E2723", "text": "5D4037"},
    "premium": {"bg": "212121", "title": "FFD700", "text": "BDBDBD"},
}

# GOST slayd tuzilishi
GOST_SLIDE_STRUCTURE = {
    "uz": [
        "Titul slaydi",
        "Mavzu dolzarbligi",
        "Maqsad va vazifalar",
        # ... asosiy qism ...
        "Natijalar",
        "Xulosa",
        "Foydalanilgan adabiyotlar",
    ],
    "ru": [
        "Титульный слайд",
        "Актуальность темы",
        "Цель и задачи",
        "Результаты",
        "Заключение",
        "Использованная литература",
    ],
    "en": [
        "Title Slide",
        "Topic Relevance",
        "Goals and Objectives",
        "Results",
        "Conclusion",
        "References",
    ],
}


async def generate_ppt_content(topic: str, slides: int, purpose: str, lang: str, extra: str = "") -> list:
    """Generate GOST-compliant PPT content using AI."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    
    # GOST tuzilishini hisobga olamiz
    structure = GOST_SLIDE_STRUCTURE.get(lang, GOST_SLIDE_STRUCTURE["uz"])
    # Asosiy qism slaydalari = jami - (titul + dolzarblik + maqsad + natijalar + xulosa + adabiyotlar)
    main_slides = slides - 6  # 6 ta majburiy slayd
    if main_slides < 1:
        main_slides = 1
    
    prompt = f"""Create a professional GOST-standard academic presentation in {lang_name} language.
Topic: {topic}
Purpose: {purpose}
{f'Additional requirements: {extra}' if extra else ''}

STRICT STRUCTURE (GOST standard):
1. First slide: "{structure[0]}" - title of presentation
2. Second slide: "{structure[1]}" - why this topic is relevant/important
3. Third slide: "{structure[2]}" - main goal and 3-5 specific tasks
4. Slides 4 to {3 + main_slides}: Main content ({main_slides} slides with detailed information)
5. Slide {4 + main_slides}: "{structure[3]}" - key findings/results
6. Slide {5 + main_slides}: "{structure[4]}" - conclusion and recommendations
7. Last slide: "{structure[5]}" - list of 5-8 academic sources

Return a JSON array with exactly {slides} objects. Each object must have:
- "title": slide title
- "content": array of 3-5 bullet points (academic style)
- "notes": speaker notes (1-2 sentences)

Return ONLY valid JSON array, no other text, no markdown."""

    content = await ai_generate(prompt, max_tokens=6000, temperature=0.7)
    
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]
    content = content.strip()
    
    return json.loads(content)


async def create_ppt_file(topic: str, slides_count: int, design: str, purpose: str, lang: str, extra: str = "") -> io.BytesIO:
    """Create GOST-standard PPTX file."""
    slides_data = await generate_ppt_content(topic, slides_count, purpose, lang, extra)
    
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    colors = PPT_COLOR_SCHEMES.get(design, PPT_COLOR_SCHEMES["business"])
    slide_layout = prs.slide_layouts[5]  # Blank
    
    for idx, slide_data in enumerate(slides_data):
        slide = prs.slides.add_slide(slide_layout)
        
        # Background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor.from_string(colors["bg"])
        
        # === GOST: Title — Times New Roman / Arial, 28-36pt, Bold ===
        left = Inches(0.8)
        top = Inches(0.4)
        width = Inches(11.5)
        height = Inches(1.4)
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        
        if idx == 0:
            # Titul slaydi — kattaroq shrift
            p.text = topic
            p.font.size = Pt(36)  # GOST: 28-36pt
        else:
            p.text = slide_data["title"]
            p.font.size = Pt(30)  # GOST: 28-36pt
        
        p.font.name = "Times New Roman"  # GOST
        p.font.bold = True
        p.font.color.rgb = RGBColor.from_string(colors["title"])
        p.alignment = PP_ALIGN.CENTER
        
        # === GOST: Content — Times New Roman, 18-24pt ===
        if idx > 0:  # Titul slaydida content yo'q
            left = Inches(1)
            top = Inches(2.0)
            width = Inches(11)
            height = Inches(4.8)
            txBox = slide.shapes.add_textbox(left, top, width, height)
            tf = txBox.text_frame
            tf.word_wrap = True
            
            for i, bullet in enumerate(slide_data.get("content", [])):
                if i == 0:
                    p = tf.paragraphs[0]
                else:
                    p = tf.add_paragraph()
                p.text = f"• {bullet}"
                p.font.name = "Times New Roman"  # GOST
                p.font.size = Pt(20)             # GOST: 18-24pt
                p.font.color.rgb = RGBColor.from_string(colors["text"])
                p.space_after = Pt(14)
        
        # Notes
        if slide_data.get("notes"):
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = slide_data["notes"]
    
    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output


# ============================================================
# DOCUMENT GENERATION — GOST (Referat, Mustaqil ish)
# ============================================================

async def generate_document_content(topic: str, doc_type: str, pages: int, lang: str, references: bool = True) -> dict:
    """Generate GOST-compliant document content using AI."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    words_per_page = 250
    total_words = pages * words_per_page
    
    # GOST tuzilishi
    structure_desc = {
        "uz": "Kirish, Asosiy qism (bir nechta bo'lim), Xulosa, Foydalanilgan adabiyotlar",
        "ru": "Введение, Основная часть (несколько разделов), Заключение, Список литературы",
        "en": "Introduction, Main body (multiple sections), Conclusion, References",
    }
    
    prompt = f"""Write a GOST-standard academic {doc_type} in {lang_name} language.
Topic: {topic}
Approximate length: {total_words} words (about {pages} pages)

GOST STRUCTURE (strictly follow this order):
1. Title
2. Introduction (Kirish/Введение) — relevance, goal, tasks, methods
3. Main body — 3-5 sections with subheadings, detailed academic analysis
4. Conclusion (Xulosa/Заключение) — summary of findings, recommendations
5. References — 5-10 real academic sources (books, articles, laws)

REQUIREMENTS:
- Academic writing style
- Each section should be substantial (multiple paragraphs)
- Introduction must state the relevance, goal, and tasks
- Conclusion must summarize key findings

Return as JSON:
{{
    "title": "full title",
    "introduction": "detailed introduction text (relevance, goal, tasks)",
    "sections": [
        {{"heading": "section title", "content": "detailed section content (multiple paragraphs)"}},
        {{"heading": "section title", "content": "detailed section content"}}
    ],
    "conclusion": "detailed conclusion text",
    "references": ["Author. Title. Publisher, Year.", "..."]
}}

Return ONLY valid JSON, no markdown formatting."""

    content = await ai_generate(prompt, max_tokens=8000, temperature=0.7)
    
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]
    content = content.strip()
    
    return json.loads(content)


async def create_document_file(topic: str, doc_type: str, pages: int, lang: str, references: bool = True) -> io.BytesIO:
    """Create GOST-standard DOCX file."""
    data = await generate_document_content(topic, doc_type, pages, lang, references)
    
    doc = Document()
    
    # === GOST sahifa sozlamalari ===
    _setup_gost_document(doc)
    
    # === TITUL VARAQ (GOST) ===
    _add_gost_title_page(doc, data.get("title", topic), doc_type, lang)
    
    # === MUNDARIJA ===
    toc_title = {"uz": "MUNDARIJA", "ru": "СОДЕРЖАНИЕ", "en": "TABLE OF CONTENTS"}
    _add_gost_heading(doc, toc_title.get(lang, toc_title["uz"]), level=1)
    
    # Mundarija elementlari
    intro_name = {"uz": "Kirish", "ru": "Введение", "en": "Introduction"}
    conclusion_name = {"uz": "Xulosa", "ru": "Заключение", "en": "Conclusion"}
    ref_name = {"uz": "Foydalanilgan adabiyotlar", "ru": "Список литературы", "en": "References"}
    
    toc_items = [intro_name.get(lang, "Kirish")]
    for i, section in enumerate(data.get("sections", []), 1):
        toc_items.append(f"{i}. {section.get('heading', '')}")
    toc_items.append(conclusion_name.get(lang, "Xulosa"))
    if references:
        toc_items.append(ref_name.get(lang, "Adabiyotlar"))
    
    for item in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        run = p.add_run(item)
        run.font.name = "Times New Roman"
        run.font.size = DocxPt(14)
    
    doc.add_page_break()
    
    # === KIRISH (GOST) ===
    _add_gost_heading(doc, intro_name.get(lang, "Kirish"), level=1)
    
    # Kirish matnini paragraflarga bo'lish
    intro_text = data.get("introduction", "")
    for para in intro_text.split("\n"):
        if para.strip():
            _add_gost_paragraph(doc, para.strip())
    
    doc.add_page_break()
    
    # === ASOSIY QISM (GOST) ===
    for i, section in enumerate(data.get("sections", []), 1):
        heading = section.get("heading", f"Bo'lim {i}")
        _add_gost_heading(doc, f"{i}. {heading}", level=1)
        
        content = section.get("content", "")
        for para in content.split("\n"):
            if para.strip():
                _add_gost_paragraph(doc, para.strip())
        
        # Har bir bo'limdan keyin bo'sh joy (lekin page break yo'q — GOST shunday)
    
    doc.add_page_break()
    
    # === XULOSA (GOST) ===
    _add_gost_heading(doc, conclusion_name.get(lang, "Xulosa"), level=1)
    
    conclusion_text = data.get("conclusion", "")
    for para in conclusion_text.split("\n"):
        if para.strip():
            _add_gost_paragraph(doc, para.strip())
    
    doc.add_page_break()
    
    # === FOYDALANILGAN ADABIYOTLAR (GOST) ===
    if references and data.get("references"):
        _add_gost_heading(doc, ref_name.get(lang, "Adabiyotlar"), level=1)
        
        for i, ref in enumerate(data["references"], 1):
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.first_line_indent = DocxCm(1.25)
            run = p.add_run(f"{i}. {ref}")
            run.font.name = "Times New Roman"
            run.font.size = DocxPt(14)
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output


# ============================================================
# ESSAY GENERATION — GOST
# ============================================================

async def create_essay_file(topic: str, lang: str, word_count: int, essay_type: str) -> io.BytesIO:
    """Create GOST-standard essay DOCX file."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    
    prompt = f"""Write a {essay_type} essay in {lang_name} language.
Topic: {topic}
Word count: approximately {word_count} words

Write in academic style with clear structure:
1. Introduction — state the topic and your thesis
2. Main body — 2-4 paragraphs with arguments and evidence
3. Conclusion — summarize and restate thesis

Return the full essay text only, no JSON, no markdown."""

    essay_text = await ai_generate(prompt, max_tokens=4000, temperature=0.7)
    
    doc = Document()
    _setup_gost_document(doc)
    
    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(topic.upper())
    run.font.name = "Times New Roman"
    run.font.size = DocxPt(16)
    run.font.bold = True
    
    doc.add_paragraph()  # bo'sh joy
    
    # Matn
    paragraphs = essay_text.split("\n\n")
    for para in paragraphs:
        if para.strip():
            if para.strip().startswith("#"):
                heading_text = para.strip().lstrip("#").strip()
                _add_gost_heading(doc, heading_text, level=2)
            else:
                _add_gost_paragraph(doc, para.strip())
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output


# ============================================================
# TRANSLATION
# ============================================================

async def translate_text(text: str, target_lang: str) -> str:
    """Translate text using AI."""
    lang_name = {"uz": "O'zbek (Uzbek)", "ru": "Русский (Russian)", "en": "English"}.get(target_lang, "English")
    prompt = f"Translate the following text to {lang_name}. Return only the translation, nothing else:\n\n{text}"
    return await ai_generate(prompt, max_tokens=4000, temperature=0.3)


# ============================================================
# QR CODE
# ============================================================

def create_qr_code(data: str, design: str = "simple") -> io.BytesIO:
    """Create a QR code image."""
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    
    colors = {
        "simple": {"fill": "black", "back": "white"},
        "minimal": {"fill": "#333333", "back": "#f5f5f5"},
        "business": {"fill": "#1a237e", "back": "#e8eaf6"},
        "premium": {"fill": "#212121", "back": "#ffd700"},
    }
    color = colors.get(design, colors["simple"])
    img = qr.make_image(fill_color=color["fill"], back_color=color["back"])
    
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output


# ============================================================
# AI HELPER (Chat)
# ============================================================

async def ai_chat(question: str, lang: str = "uz") -> str:
    """AI helper chat."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    prompt = f"""You are a helpful AI assistant for an online computer services bot. 
Answer in {lang_name} language. Be concise and helpful.
You help users with questions about services, computer-related topics, and general assistance.

User question: {question}"""
    return await ai_generate(prompt, max_tokens=1000, temperature=0.7)


# ============================================================
# AI TEXT / CONTENT
# ============================================================

async def generate_ai_text(topic: str, lang: str = "uz") -> str:
    """Generate AI text content."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    prompt = f"Write a professional text about: {topic}\nLanguage: {lang_name}\nLength: 300-500 words\n\nReturn only the text, no extra formatting."
    return await ai_generate(prompt, max_tokens=2000, temperature=0.7)


async def generate_speech(topic: str, lang: str = "uz", slides: int = 10) -> io.BytesIO:
    """Generate GOST-standard speech text for presentation."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    
    prompt = f"""Write a presentation speech in {lang_name} language following GOST structure.
Topic: {topic}
For {slides} slides presentation.

Structure the speech for these slides:
1. Title/Introduction
2. Topic relevance
3. Goals and objectives
4-{slides-3}. Main content
{slides-2}. Results
{slides-1}. Conclusion
{slides}. References acknowledgment

Include transitions between slides and engaging academic language.
Return the full speech text only."""

    speech_text = await ai_generate(prompt, max_tokens=4000, temperature=0.7)
    
    doc = Document()
    _setup_gost_document(doc)
    
    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"NUTQ: {topic.upper()}")
    run.font.name = "Times New Roman"
    run.font.size = DocxPt(16)
    run.font.bold = True
    
    doc.add_paragraph()
    
    for para in speech_text.split("\n\n"):
        if para.strip():
            _add_gost_paragraph(doc, para.strip())
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output
