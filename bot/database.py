import aiosqlite
import time
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                language TEXT DEFAULT 'uz',
                balance INTEGER DEFAULT 0,
                bonus INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                total_orders INTEGER DEFAULT 0,
                referral_count INTEGER DEFAULT 0,
                referred_by INTEGER,
                premium_plan TEXT DEFAULT 'free',
                is_banned INTEGER DEFAULT 0,
                created_at REAL,
                last_active REAL
            );

            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_type TEXT,
                service_name TEXT,
                details TEXT,
                price INTEGER,
                status TEXT DEFAULT 'pending',
                is_ai INTEGER DEFAULT 0,
                file_path TEXT,
                rating INTEGER,
                review TEXT,
                created_at REAL,
                completed_at REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                method TEXT,
                status TEXT DEFAULT 'pending',
                transaction_id TEXT,
                receipt_file TEXT,
                created_at REAL,
                confirmed_at REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                order_id INTEGER,
                file_name TEXT,
                telegram_file_id TEXT,
                file_type TEXT,
                created_at REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            );

            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                bonus_given INTEGER DEFAULT 0,
                created_at REAL,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                FOREIGN KEY (referred_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS bonuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                reason TEXT,
                created_at REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS promo_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                discount_percent INTEGER,
                discount_amount INTEGER,
                max_uses INTEGER DEFAULT 1,
                used_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                expires_at REAL,
                created_at REAL
            );

            CREATE TABLE IF NOT EXISTS promo_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                promo_id INTEGER,
                used_at REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (promo_id) REFERENCES promo_codes(id)
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                order_id INTEGER,
                rating INTEGER,
                comment TEXT,
                created_at REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                is_read INTEGER DEFAULT 0,
                created_at REAL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)
        await db.commit()


# ===== USER OPERATIONS =====

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = await cursor.fetchone()
        if not user:
            # Foydalanuvchi bazada yo'q — avtomatik yaratish
            await db.execute(
                """INSERT OR IGNORE INTO users 
                (user_id, username, full_name, created_at, last_active) 
                VALUES (?, ?, ?, ?, ?)""",
                (user_id, "", "", time.time(), time.time())
            )
            await db.commit()
            cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = await cursor.fetchone()
        return user


async def create_user(user_id: int, username: str, full_name: str, referred_by: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users 
            (user_id, username, full_name, referred_by, created_at, last_active) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, username, full_name, referred_by, time.time(), time.time())
        )
        await db.commit()


async def update_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        await db.commit()


async def get_user_language(user_id: int) -> str:
    user = await get_user(user_id)
    if user:
        return user["language"]
    return "uz"


async def add_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()


async def add_bonus(user_id: int, amount: int, reason: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET bonus = bonus + ? WHERE user_id = ?", (amount, user_id))
        await db.execute(
            "INSERT INTO bonuses (user_id, amount, reason, created_at) VALUES (?, ?, ?, ?)",
            (user_id, amount, reason, time.time())
        )
        await db.commit()


async def deduct_balance(user_id: int, amount: int) -> bool:
    user = await get_user(user_id)
    if not user:
        return False
    total_available = user["balance"] + user["bonus"]
    if total_available < amount:
        return False
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Use bonus first, then balance
        bonus_used = min(user["bonus"], amount)
        balance_used = amount - bonus_used
        await db.execute(
            "UPDATE users SET balance = balance - ?, bonus = bonus - ?, total_spent = total_spent + ?, total_orders = total_orders + 1 WHERE user_id = ?",
            (balance_used, bonus_used, amount, user_id)
        )
        await db.commit()
    return True


async def update_user_activity(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (time.time(), user_id))
        await db.commit()


async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users")
        return await cursor.fetchall()


async def get_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0]


# ===== ORDER OPERATIONS =====

async def create_order(user_id: int, service_type: str, service_name: str, details: str, price: int, is_ai: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO orders 
            (user_id, service_type, service_name, details, price, is_ai, status, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)""",
            (user_id, service_type, service_name, details, price, is_ai, time.time())
        )
        await db.commit()
        return cursor.lastrowid


async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        completed_at = time.time() if status in ("ready", "completed") else None
        if completed_at:
            await db.execute(
                "UPDATE orders SET status = ?, completed_at = ? WHERE order_id = ?",
                (status, completed_at, order_id)
            )
        else:
            await db.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        await db.commit()


async def update_order_file(order_id: int, file_path: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET file_path = ? WHERE order_id = ?", (file_path, order_id))
        await db.commit()


async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        return await cursor.fetchone()


async def get_user_orders(user_id: int, limit: int = 20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        return await cursor.fetchall()


async def get_pending_admin_orders():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders WHERE is_ai = 0 AND status IN ('pending', 'accepted', 'in_progress') ORDER BY created_at DESC"
        )
        return await cursor.fetchall()


async def get_all_orders(status: str = None, limit: int = 50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            cursor = await db.execute(
                "SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
            )
        return await cursor.fetchall()


# ===== PAYMENT OPERATIONS =====

async def create_payment(user_id: int, amount: int, method: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO payments (user_id, amount, method, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
            (user_id, amount, method, time.time())
        )
        await db.commit()
        return cursor.lastrowid


async def confirm_payment(payment_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE payments SET status = 'confirmed', confirmed_at = ? WHERE payment_id = ?",
            (time.time(), payment_id)
        )
        cursor = await db.execute("SELECT user_id, amount FROM payments WHERE payment_id = ?", (payment_id,))
        row = await cursor.fetchone()
        if row:
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (row[1], row[0]))
        await db.commit()
        return row


async def get_pending_payments():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM payments WHERE status = 'pending' ORDER BY created_at DESC"
        )
        return await cursor.fetchall()


async def get_user_payments(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        )
        return await cursor.fetchall()


# ===== FILE OPERATIONS =====

async def save_file(user_id: int, order_id: int, file_name: str, telegram_file_id: str, file_type: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO files (user_id, order_id, file_name, telegram_file_id, file_type, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, order_id, file_name, telegram_file_id, file_type, time.time())
        )
        await db.commit()


async def get_user_files(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM files WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        )
        return await cursor.fetchall()


# ===== REFERRAL OPERATIONS =====

async def add_referral(referrer_id: int, referred_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO referrals (referrer_id, referred_id, created_at) VALUES (?, ?, ?)",
            (referrer_id, referred_id, time.time())
        )
        await db.execute(
            "UPDATE users SET referral_count = referral_count + 1 WHERE user_id = ?",
            (referrer_id,)
        )
        await db.commit()


async def get_referral_count(user_id: int) -> int:
    user = await get_user(user_id)
    return user["referral_count"] if user else 0


# ===== PROMO CODE OPERATIONS =====

async def create_promo(code: str, discount_percent: int = 0, discount_amount: int = 0, max_uses: int = 1, expires_at: float = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO promo_codes (code, discount_percent, discount_amount, max_uses, expires_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (code, discount_percent, discount_amount, max_uses, expires_at, time.time())
        )
        await db.commit()


async def use_promo(user_id: int, code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM promo_codes WHERE code = ? AND is_active = 1", (code,))
        promo = await cursor.fetchone()
        if not promo:
            return None
        if promo["used_count"] >= promo["max_uses"]:
            return None
        if promo["expires_at"] and time.time() > promo["expires_at"]:
            return None
        # Check if user already used
        cursor2 = await db.execute(
            "SELECT * FROM promo_usage WHERE user_id = ? AND promo_id = ?", (user_id, promo["id"])
        )
        if await cursor2.fetchone():
            return None
        await db.execute("UPDATE promo_codes SET used_count = used_count + 1 WHERE id = ?", (promo["id"],))
        await db.execute(
            "INSERT INTO promo_usage (user_id, promo_id, used_at) VALUES (?, ?, ?)",
            (user_id, promo["id"], time.time())
        )
        if promo["discount_amount"] > 0:
            await db.execute("UPDATE users SET bonus = bonus + ? WHERE user_id = ?", (promo["discount_amount"], user_id))
        await db.commit()
        return promo


# ===== REVIEW OPERATIONS =====

async def add_review(user_id: int, order_id: int, rating: int, comment: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO reviews (user_id, order_id, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, order_id, rating, comment, time.time())
        )
        await db.execute("UPDATE orders SET rating = ?, review = ? WHERE order_id = ?", (rating, comment, order_id))
        await db.commit()


# ===== STATS =====

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        users = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        orders = await (await db.execute("SELECT COUNT(*) FROM orders")).fetchone()
        revenue = await (await db.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'confirmed'")).fetchone()
        pending = await (await db.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")).fetchone()
        return {
            "users": users[0],
            "orders": orders[0],
            "revenue": revenue[0],
            "pending_orders": pending[0],
        }
