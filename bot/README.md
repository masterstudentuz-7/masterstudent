# 🖥 Online Premium Kompyuter Xizmatlari Bot

Telegram bot for automated online computer services with AI-powered and admin-managed features.

## Features

### AI Services (Automatic, 1-5 min)
- 📊 Professional PPT (10 designs)
- 📝 Referat / Mustaqil ish
- ✍️ Esse
- 🌐 Tarjima (Translation)
- 📱 QR Code
- ✏️ AI Text Writing
- 📝 AI Content Creation
- 🎤 Speech Preparation
- 🖼 Banner & Posts
- Word/Excel/PDF services

### Admin Services (Manual)
- CV/Resume
- Internet services
- My.gov.uz
- Reports
- Design services (Diploma, Certificate, Business Card, etc.)
- Logo Creation

### System Features
- 🌐 Multilingual (UZ, RU, EN)
- 💳 Payment System (Payme, Click, Bank Card)
- 🎁 Referral System
- 🪙 Bonus System
- ⭐ Rating System
- 👑 Premium Plans (Silver, Gold, Premium)
- 🛡 Anti-spam/flood protection
- 📊 Admin Panel

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

4. Configure your `.env`:
```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
ADMIN_IDS=your_telegram_id
BANK_CARD=your_bank_card_number
```

5. Run the bot:
```bash
python main.py
```

## Project Structure

```
bot/
├── main.py              # Entry point
├── config.py            # Configuration
├── database.py          # Database operations
├── handlers/            # Message/callback handlers
│   ├── start.py         # /start command
│   ├── menu.py          # Main menu handlers
│   ├── services.py      # Service catalog
│   ├── ppt.py           # PPT generation flow
│   ├── documents.py     # Document/Essay/QR/Translation
│   ├── payment.py       # Payment flow
│   ├── admin.py         # Admin panel
│   └── ai_helper.py     # AI chat assistant
├── keyboards/           # Keyboards
│   ├── main_kb.py       # Reply keyboards
│   └── inline_kb.py     # Inline keyboards
├── locales/             # Translations
│   └── texts.py         # All bot texts (UZ/RU/EN)
├── services/            # Business logic
│   └── ai_service.py    # AI generation services
├── middlewares/          # Middleware
│   └── antiflood.py     # Anti-flood protection
└── utils/               # Utilities
```

## Admin Commands

- `/admin` - Open admin panel
- Dashboard with stats
- Order management (accept/reject/upload files)
- Payment confirmation
- User management
- Broadcast messages
- Promo code creation

## Payment Flow

1. **Payme/Click** - Automated (demo mode auto-confirms)
2. **Bank Card** - User sends receipt photo → Admin confirms

## Database

Uses SQLite (easy to migrate to PostgreSQL for production).

Tables: users, orders, payments, files, referrals, bonuses, promo_codes, promo_usage, reviews, notifications
