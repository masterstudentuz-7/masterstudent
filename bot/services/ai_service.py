import io
import json
import logging
import google.generativeai as genai
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import qrcode

from config import (
    AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODELS,
    OPENAI_API_KEY, OPENAI_MODEL
)

logger = logging.getLogger(__name__)

# ===== GEMINI SETUP (ASOSIY - HOZIR ISHLAYDI) =====
genai.configure(api_key=GEMINI_API_KEY)

# ===== OPENAI SETUP (O'CHIRILGAN - KELAJAKDA ISHLATILADI) =====
# import openai
# openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)


# ============================================================
# UNIVERSAL AI CALL - Gemini modellarini ketma-ket sinab ko'radi
# Biri ishlamasa keyingisiga o'tadi
# ============================================================

async def ai_generate(prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
    """
    AI orqali matn generatsiya qilish.
    Gemini modellarini ketma-ket sinab ko'radi - biri ishlamasa keyingisiga o'tadi.
    
    Agar AI_PROVIDER = "openai" bo'lsa, OpenAI ishlatiladi (hozir o'chirilgan).
    """
    
    # ===== OPENAI (O'CHIRILGAN) =====
    if AI_PROVIDER == "openai":
        return await _openai_generate(prompt, max_tokens, temperature)
    
    # ===== GEMINI (ASOSIY) =====
    return await _gemini_generate(prompt, max_tokens, temperature)


async def _gemini_generate(prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
    """
    Gemini modellarini ketma-ket sinab ko'radi.
    Birinchi ishlagan model natijasini qaytaradi.
    """
    last_error = None
    
    for model_name in GEMINI_MODELS:
        try:
            logger.info(f"Trying Gemini model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            
            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config,
            )
            
            if response and response.text:
                logger.info(f"Success with model: {model_name}")
                return response.text.strip()
            else:
                logger.warning(f"Empty response from model: {model_name}")
                continue
                
        except Exception as e:
            last_error = e
            logger.warning(f"Model {model_name} failed: {type(e).__name__}: {e}")
            continue
    
    # Hech qaysi model ishlamadi
    raise Exception(f"Barcha Gemini modellari ishlamadi. Oxirgi xato: {last_error}")


async def _openai_generate(prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
    """
    OpenAI orqali generatsiya (HOZIR O'CHIRILGAN).
    AI_PROVIDER = "openai" qilganda ishlay boshlaydi.
    """
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
# PPT GENERATION
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


async def generate_ppt_content(topic: str, slides: int, purpose: str, lang: str, extra: str = "") -> list:
    """Generate PPT content using AI."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    
    prompt = f"""Create a professional presentation content in {lang_name} language.
Topic: {topic}
Purpose: {purpose}
Number of slides: {slides}
{f'Additional requirements: {extra}' if extra else ''}

Return a JSON array with exactly {slides} objects. Each object must have:
- "title": slide title
- "content": array of 3-5 bullet points
- "notes": speaker notes (1-2 sentences)

Return ONLY valid JSON array, no other text. No markdown formatting, no ```json blocks."""

    content = await ai_generate(prompt, max_tokens=4000, temperature=0.7)
    
    # Clean up potential markdown formatting
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]
    content = content.strip()
    
    return json.loads(content)


async def create_ppt_file(topic: str, slides_count: int, design: str, purpose: str, lang: str, extra: str = "") -> io.BytesIO:
    """Create a PPTX file with AI-generated content."""
    slides_data = await generate_ppt_content(topic, slides_count, purpose, lang, extra)
    
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    colors = PPT_COLOR_SCHEMES.get(design, PPT_COLOR_SCHEMES["business"])
    
    # Title slide
    slide_layout = prs.slide_layouts[5]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor.from_string(colors["bg"])
    
    left = Inches(1)
    top = Inches(2.5)
    width = Inches(11)
    height = Inches(2)
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = topic
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor.from_string(colors["title"])
    p.alignment = PP_ALIGN.CENTER
    
    # Content slides
    for slide_data in slides_data:
        slide = prs.slides.add_slide(slide_layout)
        
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor.from_string(colors["bg"])
        
        # Title
        left = Inches(0.8)
        top = Inches(0.5)
        width = Inches(11.5)
        height = Inches(1.2)
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = slide_data["title"]
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = RGBColor.from_string(colors["title"])
        
        # Content
        left = Inches(1)
        top = Inches(2)
        width = Inches(11)
        height = Inches(4.5)
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.word_wrap = True
        
        for i, bullet in enumerate(slide_data.get("content", [])):
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"• {bullet}"
            p.font.size = Pt(20)
            p.font.color.rgb = RGBColor.from_string(colors["text"])
            p.space_after = Pt(12)
        
        # Add notes
        if slide_data.get("notes"):
            notes_slide = slide.notes_slide
            notes_slide.notes_text_frame.text = slide_data["notes"]
    
    # Thank you slide
    slide = prs.slides.add_slide(slide_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor.from_string(colors["bg"])
    
    left = Inches(1)
    top = Inches(3)
    width = Inches(11)
    height = Inches(2)
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    thanks = {"uz": "E'tiboringiz uchun rahmat!", "ru": "Спасибо за внимание!", "en": "Thank you for your attention!"}
    p.text = thanks.get(lang, thanks["uz"])
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor.from_string(colors["title"])
    p.alignment = PP_ALIGN.CENTER
    
    output = io.BytesIO()
    prs.save(output)
    output.seek(0)
    return output


# ============================================================
# DOCUMENT GENERATION (Referat, Mustaqil ish)
# ============================================================

async def generate_document_content(topic: str, doc_type: str, pages: int, lang: str, references: bool = True) -> dict:
    """Generate document content using AI."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    words_per_page = 250
    total_words = pages * words_per_page
    
    prompt = f"""Write a {doc_type} in {lang_name} language.
Topic: {topic}
Approximate length: {total_words} words
{'Include a bibliography/references section at the end.' if references else ''}

Structure:
1. Title page info (title, subtitle)
2. Introduction
3. Main body (multiple sections with subheadings)
4. Conclusion
{'5. References (5-8 sources)' if references else ''}

Return as JSON:
{{
    "title": "...",
    "subtitle": "...",
    "introduction": "...",
    "sections": [{{"heading": "...", "content": "..."}}],
    "conclusion": "...",
    "references": ["..."] 
}}

Write substantial academic content. Return ONLY valid JSON, no markdown formatting."""

    content = await ai_generate(prompt, max_tokens=8000, temperature=0.7)
    
    # Clean up
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        if content.endswith("```"):
            content = content[:-3]
    content = content.strip()
    
    return json.loads(content)


async def create_document_file(topic: str, doc_type: str, pages: int, lang: str, references: bool = True) -> io.BytesIO:
    """Create a DOCX file."""
    data = await generate_document_content(topic, doc_type, pages, lang, references)
    
    doc = Document()
    
    title = doc.add_heading(data.get("title", topic), level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    if data.get("subtitle"):
        subtitle = doc.add_paragraph(data["subtitle"])
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_page_break()
    
    # Table of contents placeholder
    toc_title = {"uz": "Mundarija", "ru": "Содержание", "en": "Table of Contents"}
    doc.add_heading(toc_title.get(lang, toc_title["uz"]), level=1)
    doc.add_paragraph("")
    doc.add_page_break()
    
    # Introduction
    intro_title = {"uz": "Kirish", "ru": "Введение", "en": "Introduction"}
    doc.add_heading(intro_title.get(lang, intro_title["uz"]), level=1)
    doc.add_paragraph(data.get("introduction", ""))
    
    # Main sections
    for section in data.get("sections", []):
        doc.add_heading(section.get("heading", ""), level=2)
        doc.add_paragraph(section.get("content", ""))
    
    # Conclusion
    conclusion_title = {"uz": "Xulosa", "ru": "Заключение", "en": "Conclusion"}
    doc.add_heading(conclusion_title.get(lang, conclusion_title["uz"]), level=1)
    doc.add_paragraph(data.get("conclusion", ""))
    
    # References
    if references and data.get("references"):
        ref_title = {"uz": "Adabiyotlar", "ru": "Литература", "en": "References"}
        doc.add_heading(ref_title.get(lang, ref_title["uz"]), level=1)
        for i, ref in enumerate(data["references"], 1):
            doc.add_paragraph(f"{i}. {ref}")
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output


# ============================================================
# ESSAY GENERATION
# ============================================================

async def create_essay_file(topic: str, lang: str, word_count: int, essay_type: str) -> io.BytesIO:
    """Create an essay DOCX file."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    
    prompt = f"""Write a {essay_type} essay in {lang_name} language.
Topic: {topic}
Word count: approximately {word_count} words

Write a well-structured essay with introduction, body, and conclusion.
Return the full essay text only, no JSON, no markdown formatting."""

    essay_text = await ai_generate(prompt, max_tokens=4000, temperature=0.7)
    
    doc = Document()
    title = doc.add_heading(topic, level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    paragraphs = essay_text.split("\n\n")
    for para in paragraphs:
        if para.strip():
            if para.strip().startswith("#"):
                heading_text = para.strip().lstrip("#").strip()
                doc.add_heading(heading_text, level=2)
            else:
                doc.add_paragraph(para.strip())
    
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
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
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
    """Generate speech text for presentation."""
    lang_name = {"uz": "O'zbek", "ru": "Русский", "en": "English"}.get(lang, "O'zbek")
    
    prompt = f"""Write a presentation speech in {lang_name} language.
Topic: {topic}
For {slides} slides presentation.
Include transitions between slides and engaging language.
Return the full speech text only."""

    speech_text = await ai_generate(prompt, max_tokens=4000, temperature=0.7)
    
    doc = Document()
    doc.add_heading(f"Nutq: {topic}", level=0)
    
    for para in speech_text.split("\n\n"):
        if para.strip():
            doc.add_paragraph(para.strip())
    
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output
