"""
Power Point Break Premium Store Bot
Full A-to-Z base code (single-file version).
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ==========================
# PART 1 – CONFIG
# ==========================

# FILL THESE BEFORE RUNNING
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # <- your bot token

ADMIN_IDS = [123456789]            # <- your admin numeric IDs
ADMIN_USERNAME = "YourAdminUsername"
SUPPORT_USERNAME = "YourSupportUsername"
ADMIN_GROUP_ID = -1001234567890    # <- admin group/channel id (negative for group)

DB_FILE = "database.json"
BOT_NAME = "Power Point Break Premium Store"

# ==========================
# PART 2 – DB HELPERS
# ==========================

def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        db = {
            "users": {},
            "orders": {},
            "coupons": {},
            "stocks": {},
            "settings": {
                "next_order_number": 1001,
                "bot_online": True,
            },
        }
        save_db(db)
        return db
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db: Dict[str, Any]) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def get_setting(db: Dict[str, Any], key: str, default=None):
    return db.get("settings", {}).get(key, default)


def set_setting(db: Dict[str, Any], key: str, value: Any) -> None:
    db.setdefault("settings", {})[key] = value
    save_db(db)


# ==========================
# PART 3 – STATIC DATA & SESSIONS
# ==========================

CATEGORIES = {
    "ChatGPT & AI": ["GPT-PLUS-1M", "GPT-PLUS-3M", "GPT-TEAM"],
}

PRODUCTS = {
    "GPT-PLUS-1M": {
        "name": "ChatGPT Plus — 1 Month",
        "category": "ChatGPT & AI",
        "price": 499,
        "duration_days": 30,
    },
    "GPT-PLUS-3M": {
        "name": "ChatGPT Plus — 3 Months",
        "category": "ChatGPT & AI",
        "price": 1299,
        "duration_days": 90,
    },
    "GPT-TEAM": {
        "name": "GPT-4 Team Access",
        "category": "ChatGPT & AI",
        "price": 1999,
        "duration_days": 30,
    },
}

PAYMENT_METHODS = ["bKash", "Nagad", "Upay", "Rocket", "Crypto"]

PERSONAL_NUMBERS = {
    "bKash": "01877576843",
    "Nagad": "01888776655",
    "Upay": "01855667744",
    "Rocket": "01844556622",
}

# in-memory user sessions (per chat)
sessions: Dict[int, Dict[str, Any]] = {}

# ==========================
# PART 4 – COMMON HELPERS
# ==========================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def bot_is_online() -> bool:
    db = load_db()
    return bool(get_setting(db, "bot_online", True))


def ensure_session(user_id: int) -> Dict[str, Any]:
    if user_id not in sessions:
        sessions[user_id] = {}
    return sessions[user_id]


def generate_order_id(db: Dict[str, Any]) -> str:
    next_num = int(get_setting(db, "next_order_number", 1001))
    order_id = f"CG-{next_num}"
    set_setting(db, "next_order_number", next_num + 1)
    return order_id


def generate_unique_coupon_code(db: Dict[str, Any]) -> str:
    import random
    while True:
        xyz = f"{random.randint(0, 999):03d}"
        abcd = f"{random.randint(0, 9999):04d}"
        code = f"POWER-{xyz}-POINT{abcd}-BREAKT"
        if code not in db.get("coupons", {}):
            return code


def parse_expiry(expiry_str: str) -> Optional[str]:
    """
    Parse date in 'DD-MM-YYYY HH:MM AM/PM' and return ISO string.
    """
    try:
        dt = datetime.strptime(expiry_str.strip(), "%d-%m-%Y %I:%M %p")
        return dt.isoformat()
    except ValueError:
        return None


def format_datetime(dt_str: str) -> str:
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%d-%m-%Y at %I:%M %p")


def find_first_unused_stock(db: Dict[str, Any], product_id: str) -> Optional[str]:
    for stock_id, stock in db.get("stocks", {}).items():
        if stock.get("product_id") == product_id and not stock.get("used", False):
            return stock_id
    return None


def payment_emoji(method: str) -> str:
    return {
        "bKash": "🟣",
        "Nagad": "🟡",
        "Upay": "🟠",
        "Rocket": "🔵",
    }.get(method, "💳")


def make_main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        ["🛒 All Categories", "🪪 My Profile"],
        ["🛍 Active Orders", "📦 My Orders"],
        ["⏳ Pending Orders", "🆘 Help Center"],
        ["📚 Tutorial"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def create_user_if_needed(user_id: int, full_name: str, username: Optional[str]) -> None:
    db = load_db()
    users = db.setdefault("users", {})
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "name": full_name,
            "username": username or "",
            "joined_at": datetime.utcnow().isoformat(),
        }
        save_db(db)

  # ==========================
# PART 5 – BOT ONLINE GUARD
# ==========================

async def guard_bot_online(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if user is None:
        return False
    if is_admin(user.id):
        return True
    if not bot_is_online():
        await update.effective_message.reply_text(
            "⚠️ The bot is temporarily unavailable due to technical issues.\n\n"
            "We are working to fix it as soon as possible.\n"
            f"For urgent help, please contact: @{SUPPORT_USERNAME}"
        )
        return False
    return True

# ==========================
# PART 6 – /start and /openstore
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard_bot_online(update, context):
        return
    user = update.effective_user
    create_user_if_needed(user.id, user.full_name, user.username)
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "⭐️⚡ POWER POINT BREAK PREMIUM STORE ⚡️⭐️\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 Welcome {user.full_name}!\n\n"
        f"This is ⚡ {BOT_NAME} ⚡\n"
        "💎 Premium Accounts\n"
        "💰 Lowest Price\n"
        "⚡ Ultra Fast Delivery\n"
        "🔒 100% Secure System\n\n"
        "👉 Tap /openstore to enter the store."
    )
    await update.message.reply_text(text, reply_markup=make_main_menu())


async def openstore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard_bot_online(update, context):
        return
    user = update.effective_user
    db = load_db()
    uid = str(user.id)
    if uid not in db.get("users", {}):
        db["users"][uid] = {
            "name": user.full_name,
            "username": user.username or "",
            "joined_at": datetime.utcnow().isoformat(),
        }
        save_db(db)
        await update.message.reply_text(
            "🎉 Your account has been successfully created!\n"
            "Welcome to Power Point Break Premium Store ❤️",
            reply_markup=make_main_menu(),
        )
    else:
        await update.message.reply_text(
            "✅ You are already registered.\n"
            "Use the menu below to browse the store.",
            reply_markup=make_main_menu(),
  )

  # ==========================
# PART 7 – MENU TEXT HANDLER & BASIC PAGES
# ==========================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard_bot_online(update, context):
        return
    user = update.effective_user
    sess = ensure_session(user.id)
    text = (update.message.text or "").strip()

    # If user is in coupon or payment flow:
    if "awaiting_coupon_for" in sess:
        await process_coupon_code(update, context, sess["awaiting_coupon_for"], text)
        sess.pop("awaiting_coupon_for", None)
        return
    if "awaiting_payment_for" in sess:
        await process_payment_info(update, context, sess["awaiting_payment_for"], text)
        sess.pop("awaiting_payment_for", None)
        return

    # Menu actions
    if text == "🛒 All Categories":
        await show_categories(update, context)
    elif text == "🪪 My Profile":
        await show_profile(update, context)
    elif text == "📦 My Orders":
        await show_my_orders(update, context)
    elif text == "🛍 Active Orders":
        await show_active_orders(update, context)
    elif text == "⏳ Pending Orders":
        await show_pending_orders(update, context)
    elif text == "🆘 Help Center":
        await show_help_center(update, context)
    elif text == "📚 Tutorial":
        await show_tutorial(update, context)
    else:
        await update.message.reply_text(
            "Please use the menu buttons below.",
            reply_markup=make_main_menu(),
        )


async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"🤖 {name}", callback_data=f"cat:{name}")]
        for name in CATEGORIES.keys()
    ]
    keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="back:main")])
    await update.message.reply_text(
        "📂 SELECT A CATEGORY:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    data = db.get("users", {}).get(str(user.id))
    if not data:
        await update.message.reply_text("You are not registered yet. Use /openstore first.")
        return
    joined = data.get("joined_at")
    joined_str = format_datetime(joined) if joined else "N/A"
    orders = [o for o in db.get("orders", {}).values() if o["user_id"] == user.id]
    total = len(orders)
    completed = sum(1 for o in orders if o["status"] == "APPROVED")
    pending = sum(1 for o in orders if o["status"] in {"PENDING", "WAITING_PAYMENT"})
    text = (
        "🪪 MY PROFILE\n\n"
        f"👤 Name: {data.get('name')}\n"
        f"🔗 Username: @{data.get('username') or 'N/A'}\n"
        f"🆔 User ID: {user.id}\n\n"
        f"📅 Joined: {joined_str}\n\n"
        f"📊 Total Orders: {total}\n"
        f"🏆 Completed: {completed}\n"
        f"⏳ Pending: {pending}\n\n"
        "Badge: 👑 VIP MAX\n\n"
        f"📞 Support: @{SUPPORT_USERNAME}"
    )
    await update.message.reply_text(text, reply_markup=make_main_menu())


async def show_help_center(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🆘 HELP CENTER\n\n"
        "If you face any issue, confusion, or delay please contact:\n\n"
        f"📞 @{SUPPORT_USERNAME}\n\n"
        "⏱ Average Response Time: 1–15 minutes"
    )
    await update.message.reply_text(text, reply_markup=make_main_menu())


async def show_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 No tutorial added yet.",
        reply_markup=make_main_menu(),
    )


async def show_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    orders = [o for o in db.get("orders", {}).values() if o["user_id"] == user.id]
    if not orders:
        await update.message.reply_text("You have no orders yet.", reply_markup=make_main_menu())
        return
    lines = ["📋 MY ORDERS\n"]
    for o in sorted(orders, key=lambda x: x["created_at"], reverse=True):
        product_name = PRODUCTS.get(o["product_id"], {}).get("name", "Unknown Product")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"📦 Order ID: {o['order_id']}")
        lines.append(f"🛒 {product_name}")
        lines.append(f"💵 Paid: {o['final_price']}৳")
        status = o["status"]
        if status == "APPROVED":
            status_label = "✅ APPROVED"
        elif status == "PENDING":
            status_label = "⏳ PENDING"
        elif status == "CANCELLED":
            status_label = "🚫 CANCELLED"
        else:
            status_label = status
        lines.append(f"📌 Status: {status_label}")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    await update.message.reply_text("\n".join(lines), reply_markup=make_main_menu())


async def show_active_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    orders = [
        o for o in db.get("orders", {}).values()
        if o["user_id"] == user.id and o["status"] == "PENDING"
    ]
    if not orders:
        await update.message.reply_text("You have no active orders.", reply_markup=make_main_menu())
        return
    lines = ["🛍 ACTIVE ORDERS\n"]
    for o in orders:
        product_name = PRODUCTS.get(o["product_id"], {}).get("name", "Unknown Product")
        lines.append(f"📦 Order ID: {o['order_id']}")
        lines.append(f"🛒 {product_name}")
        lines.append("⏳ Status: Waiting for Admin Approval\n")
    await update.message.reply_text("\n".join(lines), reply_markup=make_main_menu())


async def show_pending_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()
    orders = [
        o for o in db.get("orders", {}).values()
        if o["user_id"] == user.id and o["status"] == "WAITING_PAYMENT"
    ]
    if not orders:
        await update.message.reply_text("You have no pending payment orders.", reply_markup=make_main_menu())
        return
    lines = ["⏳ PENDING ORDERS\n"]
    for o in orders:
        product_name = PRODUCTS.get(o["product_id"], {}).get("name", "Unknown Product")
        lines.append(f"📦 Order ID: {o['order_id']}")
        lines.append(f"🛒 {product_name}")
        lines.append(f"💵 Amount: {o['final_price']}৳")
        lines.append("Status: Awaiting Payment Confirmation 🕒\n")
    await update.message.reply_text("\n".join(lines), reply_markup=make_main_menu())

# ==========================
# PART 8 – CALLBACKS: CATEGORY, PRODUCT, ORDER SUMMARY
# ==========================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await guard_bot_online(update, context):
        return
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    user = update.effective_user
    sess = ensure_session(user.id)

    if data.startswith("cat:"):
        category = data[4:]
        await show_products_for_category(update, context, category)
    elif data.startswith("prod:"):
        product_id = data[5:]
        await show_product_details(update, context, product_id)
    elif data == "buy":
        product_id = sess.get("selected_product_id")
        if product_id:
            await show_order_summary(update, context, product_id)
    elif data == "coupon_apply":
        sess["awaiting_coupon_for"] = sess.get("selected_product_id")
        await query.edit_message_text(
            "✍️ SEND YOUR COUPON CODE\n\nExample:\nPOWER-641-POINT9043-BREAKT"
        )
    elif data == "coupon_skip":
        await show_payment_method_picker_from_query(update, context)
    elif data.startswith("pay:"):
        method = data.split(":", 1)[1]
        sess["payment_method"] = method
        if method == "Crypto":
            await show_crypto_payment(update, context)
        else:
            await show_standard_payment(update, context)
    elif data.startswith("admin_approve:"):
        order_id = data.split(":", 1)[1]
        await admin_approve_order(update, context, order_id)
    elif data.startswith("admin_reject:"):
        order_id = data.split(":", 1)[1]
        await admin_reject_order(update, context, order_id)
    elif data == "back:main":
        await query.edit_message_text("Back to main menu.", reply_markup=None)


async def show_products_for_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    query = update.callback_query
    product_ids = CATEGORIES.get(category, [])
    if not product_ids:
        await query.edit_message_text("No products in this category yet.")
        return
    buttons = []
    for pid in product_ids:
        name = PRODUCTS[pid]["name"]
        buttons.append([InlineKeyboardButton(name, callback_data=f"prod:{pid}")])
    buttons.append([InlineKeyboardButton("⬅ Back", callback_data="back:main")])
    await query.edit_message_text(
        f"🛍 Category: {category}",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    query = update.callback_query
    user = update.effective_user
    sess = ensure_session(user.id)
    sess["selected_product_id"] = product_id
    p = PRODUCTS[product_id]
    db = load_db()
    stock_available = sum(
        1 for s in db.get("stocks", {}).values()
        if s.get("product_id") == product_id and not s.get("used", False)
    )
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"🤖 {p['name']}\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"⏳ Duration: {p['duration_days']} Days\n"
        f"💰 Price: ৳{p['price']}\n"
        f"📊 Stock: {stock_available} Available\n\n"
        "⭐ Benefits:\n"
        "• GPT-4 Full Access\n"
        "• Ultra Fast\n"
        "• Priority Servers\n"
    )
    if stock_available <= 0:
        text += "\n📛 OUT OF STOCK ❌"
        buttons = [[InlineKeyboardButton("⬅ Back", callback_data=f"cat:{p['category']}")]]
    else:
        buttons = [
            [InlineKeyboardButton("🛒 Buy Now", callback_data="buy")],
            [InlineKeyboardButton("⬅ Back", callback_data=f"cat:{p['category']}")],
        ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))


async def show_order_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    query = update.callback_query
    p = PRODUCTS[product_id]
    user = update.effective_user
    sess = ensure_session(user.id)
    sess["coupon_code"] = None
    sess["discount_amount"] = 0
    sess["final_price"] = p["price"]

    text = (
        "🧾 ORDER SUMMARY\n\n"
        f"Product: {p['name']}\n"
        f"💰 Base Price: ৳{p['price']}\n\n"
        "If you have a coupon code, you can apply it below 👇"
    )
    buttons = [
        [
            InlineKeyboardButton("🎟 Apply Coupon", callback_data="coupon_apply"),
            InlineKeyboardButton("➡ Skip Payment", callback_data="coupon_skip"),
        ]
    ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# ==========================
# PART 9 – COUPON PROCESSING & PAYMENT METHOD PICKER
# ==========================

async def process_coupon_code(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str, code: str):
    user = update.effective_user
    sess = ensure_session(user.id)
    db = load_db()
    coupon = db.get("coupons", {}).get(code)
    product = PRODUCTS[product_id]

    if not coupon:
        await update.message.reply_text(
            "❌ INVALID COUPON\n\nThis coupon does not exist.",
            reply_markup=make_main_menu(),
        )
        return
    if coupon.get("product_id") != product_id:
        correct_product = PRODUCTS.get(coupon["product_id"], {}).get("name", "this product")
        await update.message.reply_text(
            "🚫 COUPON NOT VALID FOR THIS PRODUCT\n\n"
            f"This coupon can only be used for:\n👉 {correct_product}",
            reply_markup=make_main_menu(),
        )
        return
    if coupon.get("used", False):
        await update.message.reply_text(
            "🛑 COUPON ALREADY USED\n\nThis coupon cannot be used again.",
            reply_markup=make_main_menu(),
        )
        return
    exp = coupon.get("expires_at")
    if exp:
        dt = datetime.fromisoformat(exp)
        if datetime.utcnow() > dt:
            await update.message.reply_text(
                f"⏰ COUPON EXPIRED\n\nThis coupon expired on:\n{format_datetime(exp)}",
                reply_markup=make_main_menu(),
            )
            return

    discount = coupon["discount_amount"]
    final_price = max(product["price"] - discount, 0)
    sess["coupon_code"] = code
    sess["discount_amount"] = discount
    sess["final_price"] = final_price

    await update.message.reply_text(
        "🎟 COUPON APPLIED SUCCESSFULLY! 🎉\n\n"
        f"Coupon: {code}\n"
        f"💵 Discount: ৳{discount}\n"
        f"💰 Original Price: ৳{product['price']}\n"
        f"✅ New Payable Amount: ৳{final_price}",
        reply_markup=make_main_menu(),
    )
    await show_payment_method_picker_from_message(update, context)


async def show_payment_method_picker_from_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [
            InlineKeyboardButton("🟣 bKash", callback_data="pay:bKash"),
            InlineKeyboardButton("🟡 Nagad", callback_data="pay:Nagad"),
        ],
        [
            InlineKeyboardButton("🟠 Upay", callback_data="pay:Upay"),
            InlineKeyboardButton("🔵 Rocket", callback_data="pay:Rocket"),
        ],
        [InlineKeyboardButton("🪙 Crypto (USDT)", callback_data="pay:Crypto")],
    ]
    await query.edit_message_text(
        "💳 PAYMENT METHOD\n\nPlease select your payment method:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_payment_method_picker_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🟣 bKash", callback_data="pay:bKash"),
            InlineKeyboardButton("🟡 Nagad", callback_data="pay:Nagad"),
        ],
        [
            InlineKeyboardButton("🟠 Upay", callback_data="pay:Upay"),
            InlineKeyboardButton("🔵 Rocket", callback_data="pay:Rocket"),
        ],
        [InlineKeyboardButton("🪙 Crypto (USDT)", callback_data="pay:Crypto")],
    ]
    await update.message.reply_text(
        "💳 PAYMENT METHOD\n\nPlease select your payment method:",
        reply_markup=InlineKeyboardMarkup(keyboard),
  )

# ==========================
# PART 10 – PAYMENT PAGES (STANDARD + CRYPTO)
# ==========================

async def show_standard_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    sess = ensure_session(user.id)
    product_id = sess.get("selected_product_id")
    if not product_id:
        await query.edit_message_text("Product not found in session.")
        return
    product = PRODUCTS[product_id]
    coupon_code = sess.get("coupon_code")
    discount = sess.get("discount_amount", 0)
    final_price = sess.get("final_price", product["price"])
    method = sess.get("payment_method", "bKash")
    personal_number = PERSONAL_NUMBERS.get(method, "N/A")

    text = (
        f"{payment_emoji(method)} {method.upper()} PAYMENT\n\n"
        "You're purchasing:\n"
        f"🛒 {product['name']}\n\n"
        f"💰 Original Price: ৳{product['price']}\n"
        f"🎟 Coupon Applied: {coupon_code or 'None'}\n"
        f"💵 Discount: ৳{discount}\n"
        f"✅ Amount to Pay: ৳{final_price}\n\n"
        "Please Send Money to:\n"
        f"📲 {personal_number} (Personal Number)\n\n"
        "⚠ RULES:\n"
        "👉 Only Send Money allowed\n"
        "❌ Mobile Recharge NOT accepted\n\n"
        "After payment send this format:\n\n"
        "📝 Sender Number | Amount | TXID\n\n"
        "Example:\n"
        f"01811112222 | {final_price} | TX9L92QE0"
    )
    await query.edit_message_text(text)
    sess["awaiting_payment_for"] = product_id


async def show_crypto_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "🪙 CRYPTO USDT PAYMENT\n\n"
        "✨ Thank you for choosing us!\n"
        "💵 We support payments in USDT 👈\n"
        "🌐 Available Network: All Networks\n\n"
        "💰 Available Crypto Platforms:\n"
        "• Binance\n"
        "• Bybit\n\n"
        "🛡️ Your payments are safe, fast, and fully verified.\n"
        "⚡ Processing is quick — just contact us and we’ll handle everything.\n"
        "📞 Our team is always ready to assist you.\n\n"
        "📩 For any crypto payment, please contact our admin directly:\n"
        "👉 @MinexxProo\n"
    )
    keyboard = [[InlineKeyboardButton("⬅ Back", callback_data="coupon_skip")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ==========================
# PART 11 – PAYMENT INFO → ORDER CREATION
# ==========================

async def process_payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: str):
    user = update.effective_user
    sess = ensure_session(user.id)
    db = load_db()
    product = PRODUCTS[product_id]
    coupon_code = sess.get("coupon_code")
    discount = sess.get("discount_amount", 0)
    final_price = sess.get("final_price", product["price"])
    method = sess.get("payment_method", "bKash")

    parts = [p.strip() for p in (update.message.text or "").split("|")]
    if len(parts) != 3:
        await update.message.reply_text(
            "⚠️ INVALID FORMAT\n\n"
            "Correct format:\nSender Number | Amount | TXID\n\n"
            f"Example:\n01811112222 | {final_price} | TX9L92QE0"
        )
        return
    sender, amount_str, txid = parts

    order_id = generate_order_id(db)
    now_iso = datetime.utcnow().isoformat()

    order = {
        "order_id": order_id,
        "user_id": user.id,
        "product_id": product_id,
        "original_price": product["price"],
        "discount_amount": discount,
        "final_price": final_price,
        "coupon_code": coupon_code,
        "payment_method": method,
        "sender_number": sender,
        "amount_sent": amount_str,
        "txid": txid,
        "status": "PENDING",
        "created_at": now_iso,
        "delivered_at": None,
        "stock_id": None,
    }
    db.setdefault("orders", {})[order_id] = order
    save_db(db)

    dt_str = format_datetime(now_iso)
    text_user = (
        "🎉 Your order request has been submitted!\n\n"
        f"📅 Date/Time: {dt_str}\n"
        f"🧾 Order ID: {order_id}\n"
        "⏳ Status: Waiting for Admin approval...\n\n"
        f"🛒 Product: {product['name']}\n"
        f"💰 Original Price: ৳{product['price']}\n"
        f"🎟 Coupon: {coupon_code or 'None'}\n"
        f"💵 Discount: ৳{discount}\n"
        f"✅ Payable Amount: ৳{final_price}\n\n"
        "⏱ Estimated Approval Time: 1–15 minutes\n"
        "📌 Please stay available for verification if needed.\n\n"
        f"📞 Admin Support: @{SUPPORT_USERNAME}\n"
        "❤️ Thank you for choosing Power Point Break!"
    )
    await update.message.reply_text(text_user, reply_markup=make_main_menu())

    await send_new_order_to_admin(context, order)


async def send_new_order_to_admin(context: ContextTypes.DEFAULT_TYPE, order: Dict[str, Any]):
    product = PRODUCTS.get(order["product_id"], {})
    product_name = product.get("name", "Unknown Product")
    dt_str = format_datetime(order["created_at"])
    text = (
        "📦 NEW ORDER DETAILS\n\n"
        f"Order ID: {order['order_id']}\n"
        f"User ID: {order['user_id']}\n\n"
        f"🛒 Product: {product_name}\n"
        f"💰 Original Amount: ৳{order['original_price']}\n"
        f"🎟 Coupon: {order['coupon_code'] or 'None'}\n"
        f"💵 Discount: ৳{order['discount_amount']}\n"
        f"✅ Final Amount: ৳{order['final_price']}\n\n"
        f"💳 Payment Method: {order['payment_method']}\n"
        f"📲 Sender: {order['sender_number']}\n"
        f"🔖 TXID: {order['txid']}\n\n"
        f"📅 Date: {dt_str}\n\n"
        "Action:"
    )
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve:{order['order_id']}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject:{order['order_id']}"),
        ]
    ]
    await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
  )

# ==========================
# PART 12 – ADMIN APPROVE / REJECT + DELIVERY LOG
# ==========================

async def admin_approve_order(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str):
    query = update.callback_query
    admin = update.effective_user
    if not is_admin(admin.id):
        await query.answer("Not authorized.", show_alert=True)
        return
    db = load_db()
    order = db.get("orders", {}).get(order_id)
    if not order:
        await query.answer("Order not found.", show_alert=True)
        return
    if order["status"] == "APPROVED":
        await query.answer("Order already approved.", show_alert=True)
        return

    product_id = order["product_id"]
    stock_id = find_first_unused_stock(db, product_id)
    if not stock_id:
        await query.answer("No stock available for this product.", show_alert=True)
        return

    stock = db["stocks"][stock_id]
    stock["used"] = True
    order["status"] = "APPROVED"
    order["stock_id"] = stock_id
    order["delivered_at"] = datetime.utcnow().isoformat()
    save_db(db)

    product_name = PRODUCTS.get(product_id, {}).get("name", "Unknown Product")
    email = stock.get("email", "N/A")
    password = stock.get("password", "N/A")

    user_id = order["user_id"]
    text_user = (
        "🎉✨ CONGRATULATIONS! YOUR ORDER IS APPROVED ✨🎉\n\n"
        f"Order ID: {order_id}\n"
        f"Product: {product_name}\n\n"
        f"📧 Login Email:\n{email}\n\n"
        f"🔑 Password:\n{password}\n\n"
        "⚠ Important Instructions:\n"
        "✔ After logging in, please check the account properly\n"
        "✔ Enable Two-Factor Authentication as soon as possible\n"
        "✔ Do not share this account with anyone\n"
        "✔ If you face any issue, please report it immediately\n\n"
        f"📞 Admin Support: @{SUPPORT_USERNAME}\n\n"
        "🌹 Thank you for your order 🌹"
    )
    await context.bot.send_message(chat_id=user_id, text=text_user)

    await query.edit_message_text(query.message.text + "\n\n✅ This order has been APPROVED.")

    await send_delivery_log(context, order, email, password)


async def send_delivery_log(context: ContextTypes.DEFAULT_TYPE, order: Dict[str, Any], email: str, password: str):
    product_name = PRODUCTS.get(order["product_id"], {}).get("name", "Unknown Product")
    delivered_at = order.get("delivered_at")
    delivered_str = format_datetime(delivered_at) if delivered_at else "N/A"
    text = (
        "📦✅ ORDER DELIVERED (AUTO LOG)\n\n"
        f"👤 User ID: {order['user_id']}\n"
        f"🧾 Order ID: {order['order_id']}\n"
        f"🛒 Product: {product_name}\n\n"
        f"💰 Original: ৳{order['original_price']}\n"
        f"🎟 Coupon: {order['coupon_code'] or 'None'}\n"
        f"💵 Discount: ৳{order['discount_amount']}\n"
        f"✅ Paid: ৳{order['final_price']}\n\n"
        "🔐 Delivered Account:\n"
        f"Email: {email}\n"
        f"Password: {password}\n\n"
        f"📅 Delivered At: {delivered_str}\n\n"
        "ℹ This message was generated automatically when the order was approved."
    )
    await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=text)


async def admin_reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str):
    query = update.callback_query
    admin = update.effective_user
    if not is_admin(admin.id):
        await query.answer("Not authorized.", show_alert=True)
        return
    db = load_db()
    order = db.get("orders", {}).get(order_id)
    if not order:
        await query.answer("Order not found.", show_alert=True)
        return
    if order["status"] == "APPROVED":
        await query.answer("Order already approved.", show_alert=True)
        return
    order["status"] = "CANCELLED"
    save_db(db)

    user_id = order["user_id"]
    final_price = order["final_price"]
    text_user = (
        "❌ Your order has been rejected.\n\n"
        "Reason: Payment could not be verified.\n\n"
        "⏳ You have 10 minutes to re-submit correctly.\n\n"
        "Correct Format:\nSender | Amount | TXID\n"
        f"Example:\n01811112222 | {final_price} | TX9L92QE0"
    )
    await context.bot.send_message(chat_id=user_id, text=text_user)

    await query.edit_message_text(query.message.text + "\n\n❌ This order has been REJECTED.")

# ==========================
# PART 13 – /offbot /onbot (ADMIN)
# ==========================

async def offbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return
    db = load_db()
    set_setting(db, "bot_online", False)
    await update.message.reply_text(
        "⚠️ The bot is now OFF.\n"
        "Users will see a maintenance message."
    )


async def onbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return
    db = load_db()
    set_setting(db, "bot_online", True)
    await update.message.reply_text(
        "✨ The bot is now ONLINE again!\n"
        "Users can continue using the store."
    )

# ==========================
# PART 14 – /generatecoupon (ADMIN SIMPLE VERSION)
# ==========================

async def generatecoupon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return
    db = load_db()
    # Ask admin to send details in one line
    msg = (
        "🎟 COUPON GENERATOR\n\n"
        "Send coupon details in this format:\n\n"
        "product_id | discount_taka | expiry (DD-MM-YYYY HH:MM AM/PM)\n\n"
        "Example:\nGPT-PLUS-1M | 100 | 30-11-2025 11:59 PM"
    )
    await update.message.reply_text(msg)
    sess = ensure_session(user.id)
    sess["awaiting_new_coupon"] = True


async def handle_admin_coupon_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        return False
    sess = ensure_session(user.id)
    if not sess.get("awaiting_new_coupon"):
        return False

    text = (update.message.text or "").strip()
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 3:
        await update.message.reply_text(
            "❌ Invalid format.\n\n"
            "Use:\nproduct_id | discount_taka | expiry (DD-MM-YYYY HH:MM AM/PM)"
        )
        return True
    product_id, discount_str, expiry_str = parts
    if product_id not in PRODUCTS:
        await update.message.reply_text("❌ Unknown product_id.")
        return True
    try:
        discount = int(discount_str)
    except ValueError:
        await update.message.reply_text("❌ Discount must be a number.")
        return True
    expiry_iso = parse_expiry(expiry_str)
    if not expiry_iso:
        await update.message.reply_text("❌ Invalid expiry date format.")
        return True

    db = load_db()
    code = generate_unique_coupon_code(db)
    db.setdefault("coupons", {})[code] = {
        "product_id": product_id,
        "discount_amount": discount,
        "expires_at": expiry_iso,
        "used": False,
    }
    save_db(db)

    sess["awaiting_new_coupon"] = False

    await update.message.reply_text(
        "✅ COUPON GENERATED SUCCESSFULLY!\n\n"
        f"Product: {PRODUCTS[product_id]['name']}\n"
        f"🎟 Coupon Code: {code}\n"
        f"💵 Discount: ৳{discount}\n"
        f"⏰ Expires: {format_datetime(expiry_iso)}\n\n"
        "This coupon is one-time and product-locked."
    )
    return True

# ==========================
# PART 15 – MAIN
# ==========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("openstore", openstore))
    app.add_handler(CommandHandler("offbot", offbot))
    app.add_handler(CommandHandler("onbot", onbot))
    app.add_handler(CommandHandler("generatecoupon", generatecoupon))

    app.add_handler(CallbackQueryHandler(callback_handler))

    # Text handler: try admin coupon text first, then general flow
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            lambda u, c: handle_admin_coupon_text(u, c) or handle_text(u, c),
        )
    )

    print("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
