# POWER POINT BREAK PREMIUM STORE BOT
# 1 to 36 DEMO BASED FULL BOT (SINGLE FILE)

import time
from datetime import datetime, timedelta
import random

import telebot
from telebot.types import ReplyKeyboardMarkup

# ========= BASIC CONFIG =========

BOT_TOKEN = "8222148122:AAHNqdFu6ZrHM8VuwksuXI4pAa4QQaFmlWo"  # TODO: BotFather theke pawya token boshao

# Admin IDs (numeric telegram user id)
ADMIN_IDS = {
    5692210187,  # TODO: replace with real admin ID(s)
}

# Admin group / channel chat id for order alerts (supergroup / channel id)
# Example: -1001234567890
ADMIN_GROUP_ID =  -1003373930001  # TODO: replace or set to None

SUPPORT_USERNAME = "@MinexxProo"
HOSTED_BY = "@PowerPointBreak"

# BOT ON/OFF
BOT_ON = True  # /offbot -> False, /onbot -> True

# In-memory “database”
USERS = {}           # user_id -> dict
ORDERS = {}          # order_id(str) -> dict
COUPONS = {}         # code -> dict
SETTINGS = {
    "mega_offer": "",
    "tutorial": "",
    "channel_or_group_link": "",
    "contact_username": "@MinexxProo",
}

USER_NOTIFY_USAGE = {}  # user_id -> {order_id: {count, last_time}}

ORDER_ID_COUNTER = 1000


# ========= HELPERS =========

def now():
    # BD time approximate: UTC+6
    return datetime.utcnow() + timedelta(hours=6)


def fmt_dt(dt: datetime):
    return dt.strftime("%d-%b-%Y | %I:%M %p")


def get_user(message):
    uid = message.from_user.id
    uname = message.from_user.username or "unknown"
    fullname = message.from_user.full_name or "User"

    if uid not in USERS:
        USERS[uid] = {
            "id": uid,
            "name": fullname,
            "username": uname,
            "joined": now(),
            "registered": False,
            "orders": [],
        }
    else:
        USERS[uid]["name"] = fullname
        USERS[uid]["username"] = uname

    return USERS[uid]


def next_order_id(prefix="CG"):
    global ORDER_ID_COUNTER
    ORDER_ID_COUNTER += 1
    return f"{prefix}-{ORDER_ID_COUNTER}"


def gen_coupon_code():
    # POWER-641-POINT9043-BREAK style (close)
    left = random.randint(100, 999)
    mid = random.randint(1000, 9999)
    return f"POWER-{left}-POINT{mid}-BREAK"


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ========= PRODUCTS =========

PRODUCTS = {
    "chatgpt_1m": {
        "id": "chatgpt_1m",
        "title": "ChatGPT Plus — 1 Month",
        "category": "ChatGPT & AI",
        "duration_text": "30 Days",
        "price": 499,
        "stock": 7,
    },
    "chatgpt_3m": {
        "id": "chatgpt_3m",
        "title": "ChatGPT Plus — 3 Months",
        "category": "ChatGPT & AI",
        "duration_text": "90 Days",
        "price": 1399,
        "stock": 5,
    },
    "gpt4_team": {
        "id": "gpt4_team",
        "title": "GPT-4 Team Access",
        "category": "ChatGPT & AI",
        "duration_text": "30 Days",
        "price": 2499,
        "stock": 3,
    },
}

PAYMENT_METHODS = [
    "🟣 bKash",
    "🟡 Nagad",
    "🟠 Upay",
    "🔵 Rocket",
    "🪙 Crypto (USDT)",
]


# ========= KEYBOARDS =========

def main_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🛒 All Categories", "🪪 My Profile")
    kb.row("🛍 Active Orders", "📦 My Orders")
    kb.row("⏳ Pending Orders", "🆘 Help Center")
    kb.row("📚 Tutorial", "🎁 Mega Offer")
    return kb


def categories_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🤖 ChatGPT & AI", "▶️ YouTube Premium")
    kb.row("🎵 Spotify Premium", "🎬 Netflix")
    kb.row("🔒 VPN & Security", "👨‍💻 Developer Tools")
    kb.row("🧩 Office 365", "🎮 Gaming / Combo")
    kb.row("⬅ Back")
    return kb


def chatgpt_products_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🤖 ChatGPT Plus — 1 Month")
    kb.row("🤖 ChatGPT Plus — 3 Months")
    kb.row("🚀 GPT-4 Team Access")
    kb.row("⬅ Back")
    return kb


def product_actions_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🛒 Buy Now", "🎟 Apply Coupon")
    kb.row("⬅ Back")
    return kb


def payment_methods_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🟣 bKash", "🟡 Nagad")
    kb.row("🟠 Upay", "🔵 Rocket")
    kb.row("🪙 Crypto (USDT)")
    kb.row("⬅ Cancel")
    return kb


# ========= STATES =========

STATE_NONE = "none"
STATE_SIGNUP = "signup"
STATE_PRODUCT = "product"
STATE_COUPON_INPUT = "coupon_input"
STATE_PAYMENT_SELECT = "payment_select"
STATE_WAIT_PAYMENT_FORMAT = "wait_payment_format"

STATE_ADMIN_WAIT_CREDENTIALS = "admin_wait_credentials"
STATE_ADMIN_WAIT_REJECT_REASON = "admin_wait_reject_reason"

STATE_ADMIN_COUPON_MENU = "admin_coupon_menu"
STATE_ADMIN_SINGLE_COUPON_INPUT = "admin_single_coupon_input"
STATE_ADMIN_ALL_COUPON_INPUT = "admin_all_coupon_input"
STATE_ADMIN_MULTI_COUPON_QTY = "admin_multi_coupon_qty"

STATE_ADMIN_MEGA_OFFER = "admin_mega_offer"
STATE_ADMIN_TUTORIAL = "admin_tutorial"
STATE_ADMIN_LINK_OR_USERNAME = "admin_link_or_username"
STATE_ADMIN_ADD_LINK = "admin_add_link"
STATE_ADMIN_ADD_USERNAME = "admin_add_username"

USER_STATES = {}   # user_id -> state
USER_TEMP = {}     # user_id -> temp dict

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


def set_state(user_id, state, data=None):
    USER_STATES[user_id] = state
    if data is not None:
        USER_TEMP[user_id] = data
    elif state == STATE_NONE:
        USER_TEMP.pop(user_id, None)


def get_state(user_id):
    return USER_STATES.get(user_id, STATE_NONE)


def get_temp(user_id):
    return USER_TEMP.get(user_id, {})


def send_main_menu(chat_id, user):
    text = (
        "🏠 MAIN MENU\n\n"
        "🛒 All Categories      🪪 My Profile\n"
        "🛍 Active Orders      📦 My Orders\n"
        "⏳ Pending Orders      🆘 Help Center\n"
        "📚 Tutorial            🎁 Mega Offer"
    )
    bot.send_message(chat_id, text, reply_markup=main_menu_keyboard())


# ========= 1) /start — Welcome Screen =========
@bot.message_handler(commands=['start'])
def cmd_start(message):
    user = get_user(message)

    if not BOT_ON and not is_admin(user["id"]):
        # 26) BOT OFF MESSAGE
        off_text = (
            "⚠️ Hey dear user, heads up!\n\n"
            "🚧 Our Premium Service is temporarily unavailable due to unexpected issues.\n"
            "🛠️ We’re working super fast to fix everything ASAP.\n\n"
            "⏳ Please hold on — your patience means a lot.\n"
            "🙏 Thank you for staying with us.\n"
            "💛 We’ll be back stronger!\n\n"
            f"🏷 Hosted by: {HOSTED_BY}\n"
            f"📞 Support: @MinexxProo"
        )
        bot.send_message(message.chat.id, off_text)
        return

    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "⭐⚡ POWER POINT BREAK PREMIUM STORE ⚡⭐\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 Welcome {user['name']}!\n\n"
        "This is POWER POINT BREAK PREMIUM STORE\n"
        "💎 Premium Accounts • 💰 Lowest Price • ⚡ Fast Delivery • 🔒 Secure Service\n\n"
        "👉 Enter Store:\n"
        "/openstore\n\n"
        "👤 User Info:\n"
        f"🆔 User ID: <code>{user['id']}</code>\n"
        f"🔗 Username: @{user['username']}\n\n"
        f"📞 Support: {SUPPORT_USERNAME}\n"
        f"🏷 Hosted by: {HOSTED_BY}"
    )
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("/openstore")
    bot.send_message(message.chat.id, text, reply_markup=kb)


# ========= 2) /openstore — Registration Gate =========
@bot.message_handler(commands=['openstore'])
def cmd_openstore(message):
    user = get_user(message)

    if not user["registered"]:
        # 3) SIGN UP FLOW
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("✅ Confirm Sign Up", "❌ Cancel")

        text = (
            "📝 SIGN UP\n\n"
            f"Name: {user['name']}\n"
            f"Username: @{user['username']}\n"
            f"User ID: <code>{user['id']}</code>\n\n"
            "Buttons:\n"
            "✅ Confirm Sign Up\n"
            "❌ Cancel"
        )
        set_state(user["id"], STATE_SIGNUP)
        bot.send_message(message.chat.id, text, reply_markup=kb)
    else:
        # 4) LOG IN FLOW
        bot.send_message(
            message.chat.id,
            f"🔓 Welcome back, {user['name']}!\nTap MAIN MENU to continue.",
            reply_markup=main_menu_keyboard(),
        )
        set_state(user["id"], STATE_NONE)


def handle_signup(message, user):
    uid = user["id"]
    if message.text == "✅ Confirm Sign Up":
        user["registered"] = True
        set_state(uid, STATE_NONE)
        bot.send_message(
            message.chat.id,
            "✅ Account created!\n\nUse /openstore again.",
            reply_markup=main_menu_keyboard(),
        )
    elif message.text == "❌ Cancel":
        set_state(uid, STATE_NONE)
        bot.send_message(
            message.chat.id,
            "❌ Sign Up cancelled.\nUse /openstore again.",
        )
    else:
        bot.send_message(message.chat.id, "Please tap ✅ Confirm Sign Up or ❌ Cancel.")


# ========= MAIN MENU BUTTONS (5, 20, 21, 22, 23, 24, 25, 33, 34) =========

def send_active_orders(chat_id, user):
    items = [
        ORDERS[oid] for oid in user["orders"]
        if ORDERS.get(oid, {}).get("status") == "pending"
    ]
    if not items:
        bot.send_message(chat_id, "🛍 No active orders at the moment.")
        return

    lines = ["🛍 ACTIVE ORDERS\n"]
    for o in items:
        lines.append(
            f"\nOrder ID: {o['id']}\n"
            f"Product: {o['product_title']}\n"
            f"Amount: ৳{o['final_amount']}\n"
            "⏳ Status: Waiting for Admin Approval"
        )
    bot.send_message(chat_id, "\n".join(lines))


def send_pending_orders(chat_id, user):
    items = [
        ORDERS[oid] for oid in user["orders"]
        if ORDERS.get(oid, {}).get("status") == "waiting_payment"
    ]
    if not items:
        bot.send_message(chat_id, "⏳ You have no orders awaiting payment confirmation.")
        return

    lines = ["⏳ MY PENDING ORDERS\n"]
    for o in items:
        lines.append(
            f"\nOrder ID: {o['id']}\n"
            f"Product: {o['product_title']}\n"
            f"Amount: ৳{o['final_amount']}\n"
            "Status: Awaiting Payment Confirmation ⏳"
        )
    bot.send_message(chat_id, "\n".join(lines))


def send_my_orders(chat_id, user):
    if not user["orders"]:
        bot.send_message(chat_id, "📦 You have no orders yet.")
        return

    lines = ["📦 MY ORDERS HISTORY\n"]
    for oid in user["orders"][-20:]:
        o = ORDERS.get(oid)
        if not o:
            continue
        status_icon = {
            "approved": "✅",
            "pending": "⏳",
            "cancelled": "🚫",
        }.get(o["status"], "❔")
        lines.append(
            f"\n{status_icon} {o['id']} — {o['product_title']}\n"
            f"৳{o['final_amount']} | {fmt_dt(o['created_at'])}"
        )
    bot.send_message(chat_id, "\n".join(lines))


def handle_main_menu_buttons(message, user):
    text = message.text

    if text == "🛒 All Categories":
        bot.send_message(message.chat.id, "📂 SELECT A CATEGORY", reply_markup=categories_keyboard())
        return True

    if text == "🪪 My Profile":
        total_orders = len(user["orders"])
        completed = sum(1 for oid in user["orders"] if ORDERS.get(oid, {}).get("status") == "approved")
        pending = sum(1 for oid in user["orders"] if ORDERS.get(oid, {}).get("status") == "pending")

        profile_sms = (
            "🪪 MY PROFILE\n\n"
            f"Name: {user['name']}\n"
            f"Username: @{user['username']}\n"
            f"User ID: <code>{user['id']}</code>\n\n"
            f"Joined: {fmt_dt(user['joined'])}\n\n"
            f"Total Orders: {total_orders}\n"
            f"Completed: {completed}\n"
            f"Pending: {pending} ⏳\n\n"
            f"Badge: 👑 VIP MAX\n"
            f"Support: {SUPPORT_USERNAME}"
        )
        bot.send_message(message.chat.id, profile_sms, reply_markup=main_menu_keyboard())
        return True

    if text == "🛍 Active Orders":
        send_active_orders(message.chat.id, user)
        return True

    if text == "⏳ Pending Orders":
        send_pending_orders(message.chat.id, user)
        return True

    if text == "📦 My Orders":
        send_my_orders(message.chat.id, user)
        return True

    if text == "🆘 Help Center":
        help_sms = (
            "🆘 SUPPORT CENTER\n\n"
            "💬 If you have any questions or face any kind of problem,\n"
            "📩 just message us in the inbox.\n\n"
            "🛠️ We are always here and will try our best to solve your issue.\n"
            "🙏 Thank you so much for staying with us!\n\n"
            f"👨‍💻 Admin Support: {SUPPORT_USERNAME}\n\n"
            "⚡ Hosted by: POWER POINT BREAK\n\n"
            "Response Time: 1–15 minutes ⏱️"
        )
        bot.send_message(message.chat.id, help_sms, reply_markup=main_menu_keyboard())
        return True

    if text == "📚 Tutorial":
        if SETTINGS["tutorial"]:
            bot.send_message(message.chat.id, SETTINGS["tutorial"], reply_markup=main_menu_keyboard())
        else:
            bot.send_message(message.chat.id, "📚 No tutorial added yet", reply_markup=main_menu_keyboard())
        return True

    if text == "🎁 Mega Offer":
        if SETTINGS["mega_offer"]:
            bot.send_message(message.chat.id, f"🎁 NEW MEGA OFFER\n{SETTINGS['mega_offer']}", reply_markup=main_menu_keyboard())
        else:
            bot.send_message(message.chat.id, "🎁 No mega offer available right now.", reply_markup=main_menu_keyboard())
        return True

    if text == "⬅ Back":
        send_main_menu(message.chat.id, user)
        return True

    return False


# ========= CATEGORY & PRODUCT LIST (6, 7, 8) =========

def send_product_details(chat_id, product_id):
    p = PRODUCTS[product_id]
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"🤖 {p['title'].upper()}\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"⏳ Duration: {p['duration_text']}\n"
        f"💰 Price: ৳{p['price']}\n"
        f"📊 Stock: {p['stock']} Available\n\n"
        "⭐ Benefits:\n"
        "• GPT-4 Full Access\n"
        "• Ultra Fast Speed\n"
        "• Priority Server\n\n"
        "Buttons:\n"
        "🛒 Buy Now\n"
        "🎟 Apply Coupon\n"
        "⬅ Back"
    )
    bot.send_message(chat_id, text, reply_markup=product_actions_keyboard())


def handle_category_buttons(message, user):
    txt = message.text

    if txt == "🤖 ChatGPT & AI":
        bot.send_message(
            message.chat.id,
            "🛍 CATEGORY: ChatGPT & AI",
            reply_markup=chatgpt_products_keyboard(),
        )
        return True

    if txt in [
        "▶️ YouTube Premium",
        "🎵 Spotify Premium",
        "🎬 Netflix",
        "🔒 VPN & Security",
        "👨‍💻 Developer Tools",
        "🧩 Office 365",
        "🎮 Gaming / Combo",
    ]:
        bot.send_message(message.chat.id, "This category is demo only right now.", reply_markup=categories_keyboard())
        return True

    return False


def handle_product_list(message, user):
    uid = user["id"]
    txt = message.text

    if txt == "🤖 ChatGPT Plus — 1 Month":
        set_state(uid, STATE_PRODUCT, {"product_id": "chatgpt_1m", "coupon": None})
        send_product_details(message.chat.id, "chatgpt_1m")
        return True

    if txt == "🤖 ChatGPT Plus — 3 Months":
        set_state(uid, STATE_PRODUCT, {"product_id": "chatgpt_3m", "coupon": None})
        send_product_details(message.chat.id, "chatgpt_3m")
        return True

    if txt == "🚀 GPT-4 Team Access":
        set_state(uid, STATE_PRODUCT, {"product_id": "gpt4_team", "coupon": None})
        send_product_details(message.chat.id, "gpt4_team")
        return True

    return False


# ========= 9) COUPON MENU =========

def validate_coupon_for_product(code: str, product_id: str):
    c = COUPONS.get(code.upper())
    if not c:
        return "invalid", None

    now_t = now()
    if c["expires_at"] and c["expires_at"] < now_t:
        return "expired", None

    if c["used_by"] is not None:
        return "used", None

    if c["scope"] == "single" and c["product_id"] != product_id:
        return "wrong_product", None

    return "ok", c


def handle_product_actions(message, user):
    uid = user["id"]
    temp = get_temp(uid)
    if "product_id" not in temp:
        return False

    product_id = temp["product_id"]

    if message.text == "🎟 Apply Coupon":
        bot.send_message(message.chat.id, "🎟 APPLY COUPON\n\nPlease send your coupon code.")
        set_state(uid, STATE_COUPON_INPUT, {"product_id": product_id})
        return True

    if message.text == "🛒 Buy Now":
        product = PRODUCTS[product_id]
        coupon = temp.get("coupon")
        set_state(uid, STATE_PAYMENT_SELECT, {"product_id": product_id, "coupon": coupon})
        send_payment_menu(message.chat.id, product, coupon)
        return True

    if message.text == "⬅ Back":
        set_state(uid, STATE_NONE)
        bot.send_message(message.chat.id, "Back to category.", reply_markup=chatgpt_products_keyboard())
        return True

    return False


def handle_coupon_input(message, user):
    uid = user["id"]
    temp = get_temp(uid)
    product_id = temp.get("product_id")
    code = message.text.strip().upper()

    status, coupon = validate_coupon_for_product(code, product_id)

    if status == "invalid":
        bot.send_message(message.chat.id, "❌ INVALID COUPON")
        return
    if status == "expired":
        bot.send_message(message.chat.id, "⏳ EXPIRED")
        return
    if status == "used":
        bot.send_message(message.chat.id, "🛑 ALREADY USED")
        return
    if status == "wrong_product":
        bot.send_message(message.chat.id, "🚫 NOT VALID")
        return

    product = PRODUCTS[product_id]
    original = product["price"]
    discount = coupon["discount"]
    final_amount = max(0, original - discount)

    text = (
        "🎉 COUPON APPLIED SUCCESSFULLY! 🎉\n\n"
        f"Coupon: {code}\n"
        f"💵 Discount: ৳{discount}\n"
        f"💰 Original Price: ৳{original}\n"
        f"✅ Payable: ৳{final_amount}"
    )
    if final_amount == 0:
        text += "\n\n💚 Payable: 0\n⚡ Auto-delivery enabled."

    bot.send_message(message.chat.id, text)

    set_state(uid, STATE_PRODUCT, {"product_id": product_id, "coupon": coupon})
    send_product_details(message.chat.id, product_id)



# ========= 10) BUY NOW → PAYMENT METHOD =========

def send_payment_menu(chat_id, product, coupon):
    original = product["price"]
    discount = coupon["discount"] if coupon else 0
    final_amount = max(0, original - discount)

    text = (
        "💳 PAYMENT METHOD\n\n"
        "You're buying:\n"
        f"🛒 {product['title']}\n"
        f"💰 Payable Amount: ৳{final_amount}\n\n"
        "Select Payment:\n\n"
        "🟣 bKash\n"
        "🟡 Nagad\n"
        "🟠 Upay\n"
        "🔵 Rocket\n"
        "🪙 Crypto (USDT)"
    )
    bot.send_message(chat_id, text, reply_markup=payment_methods_keyboard())


def send_wallet_payment_page(chat_id, method_text, product, coupon):
    provider_name = method_text.split(" ", 1)[1] if " " in method_text else method_text
    original = product["price"]
    discount = coupon["discount"] if coupon else 0
    final_amount = max(0, original - discount)

    coupon_text = coupon["code"] if coupon else "{if-any}"
    discount_text = f"৳{discount}" if coupon else "{if-any}"

    text = (
        f"{method_text} {provider_name.upper()} PAYMENT\n\n"
        "You're purchasing:\n"
        f"🛒 {product['title']}\n\n"
        f"💰 Original Price: ৳{original}\n"
        f"🎟 Coupon: {coupon_text}\n"
        f"💵 Discount: {discount_text}\n"
        f"✅ Payable: ৳{final_amount}\n\n"
        "Send Money to:\n"
        "📲 01877576843 (bKash Personal)\n\n"
        "⚠ RULES:\n"
        "👉 Only Send Money allowed\n"
        "❌ Mobile Recharge NOT accepted\n\n"
        "Send info in format:\n"
        "Sender | Amount | TXID\n\n"
        "Example:\n"
        "01811112222 | 499 | TX9L92QE0"
    )
    bot.send_message(chat_id, text)


def send_crypto_page(chat_id):
    text = (
        "🪙 CRYPTO USDT PAYMENT\n\n"
        "✨ Thank you for choosing us!\n"
        "💵 We support payments in USDT 👈\n"
        "🌐 Available Network: All Networks\n\n"
        "💰 Available Crypto Platforms:\n"
        "• Binance\n"
        "• Bybit\n\n"
        "🛡️ Safe, fast & verified.\n"
        "⚡ Processing is quick.\n"
        "📞 Support always available.\n\n"
        "📩 Crypto Payment Please Contract Admin: 👉 @MinexxProo\n\n"
        "⬅ Back"
    )
    bot.send_message(chat_id, text)


def handle_payment_select(message, user):
    uid = user["id"]
    temp = get_temp(uid)
    if "product_id" not in temp:
        return False

    product = PRODUCTS[temp["product_id"]]
    coupon = temp.get("coupon")
    method = message.text

    if method == "⬅ Cancel":
        set_state(uid, STATE_NONE)
        send_main_menu(message.chat.id, user)
        return True

    if method not in PAYMENT_METHODS:
        bot.send_message(message.chat.id, "Please select a valid payment method button.")
        return True

    if method == "🪙 Crypto (USDT)":
        send_crypto_page(message.chat.id)
        return True

    # 11) PAYMENT PAGE — bKash / Others
    send_wallet_payment_page(message.chat.id, method, product, coupon)
    temp["payment_method"] = method
    set_state(uid, STATE_WAIT_PAYMENT_FORMAT, temp)
    return True


# ========= 13) FORMAT VALIDATION & 14–15) ORDER SUBMIT + ADMIN ALERT =========

def parse_payment_format(text):
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 3:
        return None
    sender, amount_str, txid = parts
    if not sender or not amount_str or not txid:
        return None
    try:
        amt = int(amount_str)
    except ValueError:
        return None
    return {"sender": sender, "amount": amt, "txid": txid}


def handle_wait_payment_format(message, user):
    uid = user["id"]
    temp = get_temp(uid)
    payment = parse_payment_format(message.text)
    if not payment:
        bot.send_message(
            message.chat.id,
            "⚠ Invalid Format\n\nCorrect Format:\nSender | Amount | TXID\nExample:\n01811112222 | 499 | TX9L92QE0",
        )
        return

    product = PRODUCTS[temp["product_id"]]
    coupon = temp.get("coupon")
    original = product["price"]
    discount = coupon["discount"] if coupon else 0
    final_amount = max(0, original - discount)

    order_id = next_order_id("CG")
    order = {
        "id": order_id,
        "user_id": uid,
        "username": user["username"],
        "product_id": product["id"],
        "product_title": product["title"],
        "original": original,
        "discount": discount,
        "final_amount": final_amount,
        "coupon_code": coupon["code"] if coupon else None,
        "payment_method": temp.get("payment_method"),
        "sender_number": payment["sender"],
        "txid": payment["txid"],
        "created_at": now(),
        "status": "pending",
    }
    ORDERS[order_id] = order
    user["orders"].append(order_id)

    sms = (
        "🎉 Your order request has been submitted! 🎉\n\n"
        f"📅 Date/Time: {fmt_dt(order['created_at'])}\n"
        f"🧾 Order ID: {order_id}\n"
        "⏳ Status: Waiting for Admin approval…\n(⏳ Pending)\n\n"
        f"🛒 Product: {product['title']}\n"
        f"💰 Original Price: ৳{original}\n"
        f"🎟 Coupon: {order['coupon_code'] or 'N/A'}\n"
        f"💵 Discount: ৳{discount}\n"
        f"✅ Payable Amount: ৳{final_amount}\n"
        f"👉 Payment Sender Number: {payment['sender']}\n\n"
        "⏱ Estimated Approval Time: 1–15 minutes\n"
        "📌 Stay online for verification if needed.\n\n"
        f"📞 Admin Support: {SUPPORT_USERNAME}\n"
        f"🏷 Hosted by: {HOSTED_BY}\n\n"
        "❤️ Thank you for choosing Power Point Break! ❤️"
    )
    bot.send_message(message.chat.id, sms, reply_markup=main_menu_keyboard())

    if ADMIN_GROUP_ID:
        alert = (
            "📦 NEW ORDER RECEIVED 🔔\n\n"
            f"Order ID: {order_id}\n"
            f"Username: @{user['username']}\n"
            f"User ID: {uid}\n\n"
            f"🛒 Product: {product['title']}\n"
            f"💰 Original Amount: ৳{original}\n"
            f"🎟 Coupon: {order['coupon_code'] or 'N/A'}\n"
            f"💵 Discount: ৳{discount}\n"
            f"✅ Final Amount: ৳{final_amount}\n\n"
            f"💳 Payment Method: {order['payment_method']}\n"
            f"📲 Sender: {payment['sender']}\n"
            f"🔖 TXID: {payment['txid']}\n\n"
            f"🕒 Date & Time: {fmt_dt(order['created_at'])}\n\n"
            f"/approve_{order_id}\n"
            f"/reject_{order_id}"
        )
        bot.send_message(ADMIN_GROUP_ID, alert)

    set_state(uid, STATE_NONE)


# ========= 16–19) ADMIN APPROVE / REJECT + AUTO LOG =========

def send_delivery_sms_to_user(order, credentials_text):
    user = USERS.get(order["user_id"])
    if not user:
        return
    sms = (
        "🎉✨ CONGRATULATIONS! ✨🎉\n"
        f"Hello Dear @{user['username']}, your order has been successfully APPROVED! ✅🚀\n\n"
        "Your ChatGPT Plus has been successfully activated! ⚡🔥\n\n"
        "🧾 Order Details:\n"
        "———————————————\n"
        f"📦 Order ID: {order['id']}\n"
        f"🛒 Product: {order['product_title']}\n"
        "———————————————\n\n"
        "🔐 Login Credentials:\n"
        f"{credentials_text}\n\n"
        "⚠ IMPORTANT INSTRUCTIONS:\n"
        "• After logging in, please check the account properly\n"
        "• Enable Two-Factor Authentication immediately\n"
        "• Do NOT share this account with anyone\n"
        "• If you face any issue, please report it quickly\n\n"
        f"📞 Admin Support: 👉 {SUPPORT_USERNAME}\n\n"
        "🌹 Thank you so much for your order! 🌹"
    )
    bot.send_message(order["user_id"], sms)


def send_auto_delivery_log(order, credentials_text):
    if not ADMIN_GROUP_ID:
        return
    log = (
        "📦 ORDER DELIVERED (AUTO LOG)\n\n"
        f"User: @{USERS[order['user_id']]['username']}\n"
        f"User ID: {order['user_id']}\n\n"
        f"Order ID: {order['id']}\n"
        f"Product: {order['product_title']}\n\n"
        "🔐 Login:\n"
        f"{credentials_text}\n\n"
        f"Delivered at: 🕒 {fmt_dt(now())}"
    )
    bot.send_message(ADMIN_GROUP_ID, log)


def auto_cancel_order(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return
    if order["status"] != "pending":
        return
    order["status"] = "cancelled"
    user = USERS.get(order["user_id"])
    if user:
        sms = (
            "🚫 Your order has been automatically cancelled\n"
            "because you didn’t resubmit in time.\n\n"
            f"For help: {SUPPORT_USERNAME}"
        )
        bot.send_message(order["user_id"], sms)


@bot.message_handler(func=lambda m: m.text and m.text.startswith(("/approve_", "/reject_")))
def admin_approve_reject_shortcut(message):
    if not is_admin(message.from_user.id):
        return

    txt = message.text
    if txt.startswith("/approve_"):
        order_id = txt.replace("/approve_", "").strip()
        admin_start_approve(message, order_id)
    elif txt.startswith("/reject_"):
        order_id = txt.replace("/reject_", "").strip()
        admin_reject_order(message, order_id)


def admin_start_approve(message, order_id):
    order = ORDERS.get(order_id)
    if not order:
        bot.reply_to(message, "Order not found.")
        return

    order["status"] = "approved"
    bot.reply_to(
        message,
        "Send login credentials in this format:\nEmail: ...\nPassword: ...",
    )
    USER_TEMP[message.from_user.id] = {"approve_order_id": order_id}
    USER_STATES[message.from_user.id] = STATE_ADMIN_WAIT_CREDENTIALS


def admin_reject_order(message, order_id):
    order = ORDERS.get(order_id)
    if not order:
        bot.reply_to(message, "Order not found.")
        return

    order["status"] = "cancelled"
    bot.reply_to(message, f"Order {order_id} marked as rejected.\nPlease send reason in next message.")
    USER_TEMP[message.from_user.id] = {"reject_order_id": order_id}
    USER_STATES[message.from_user.id] = STATE_ADMIN_WAIT_REJECT_REASON


def handle_admin_special_states(message):
    uid = message.from_user.id
    state = get_state(uid)

    if state == STATE_ADMIN_WAIT_CREDENTIALS:
        data = USER_TEMP.get(uid, {})
        order_id = data.get("approve_order_id")
        order = ORDERS.get(order_id)
        if order:
            credentials_text = message.text
            send_delivery_sms_to_user(order, credentials_text)
            send_auto_delivery_log(order, credentials_text)
            bot.reply_to(message, f"Order {order_id} approved and delivered.")
        else:
            bot.reply_to(message, "Order not found.")
        set_state(uid, STATE_NONE)
        return True

    if state == STATE_ADMIN_WAIT_REJECT_REASON:
        data = USER_TEMP.get(uid, {})
        order_id = data.get("reject_order_id")
        order = ORDERS.get(order_id)
        reason = message.text
        if order:
            user = USERS.get(order["user_id"])
            if user:
                sms = (
                    "❌ Your order has been rejected.\n\n"
                    f"Reason: {reason}\n\n"
                    "⏳ You have 10 minutes to resubmit correctly.\n\n"
                    "Correct Format:\n"
                    "Sender | Amount | TXID\n"
                    "Example:\n"
                    "01811112222 | 499 | TX9L92QE0"
                )
                bot.send_message(order["user_id"], sms)
        bot.reply_to(message, f"Reject reason saved for {order_id}.")
        set_state(uid, STATE_NONE)
        return True

    return False


# ========= 28) NOTIFY ADMIN SYSTEM =========

MAX_NOTIFY_PER_ORDER = 3
NOTIFY_COOLDOWN_SECONDS = 3600  # 1 hour


def handle_notify_admin(message, user):
    uid = user["id"]

    if not user["orders"]:
        bot.send_message(message.chat.id, "You have no order to notify about.")
        return

    last_order_id = user["orders"][-1]
    usage_dict = USER_NOTIFY_USAGE.setdefault(uid, {})
    usage = usage_dict.setdefault(last_order_id, {"count": 0, "last_time": 0})
    now_ts = time.time()

    if usage["count"] >= MAX_NOTIFY_PER_ORDER:
        bot.send_message(message.chat.id, "🚫 No more notifications left.")
        return

    if now_ts - usage["last_time"] < NOTIFY_COOLDOWN_SECONDS:
        bot.send_message(message.chat.id, "⏳ You must wait 1 hour.")
        return

    usage["count"] += 1
    usage["last_time"] = now_ts

    if ADMIN_GROUP_ID:
        bot.send_message(
            ADMIN_GROUP_ID,
            f"🔔 USER REMINDER — User @{user['username']} reminded about Order ID: {last_order_id}",
        )

    bot.send_message(message.chat.id, "🔔 Notification sent.")


# ========= 30–32) COUPON GENERATOR — ADMIN =========

def parse_coupon_template(text):
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 2:
        return None
    try:
        discount = int(parts[0])
    except ValueError:
        return None
    try:
        expires = datetime.strptime(parts[1], "%d-%m-%Y %I:%M %p")
    except ValueError:
        return None
    return {"discount": discount, "expires": expires}


def create_coupon(discount, expires_at, scope, product_id=None):
    code = gen_coupon_code()
    COUPONS[code] = {
        "code": code,
        "discount": discount,
        "expires_at": expires_at,
        "scope": scope,          # "single" or "all"
        "product_id": product_id,
        "used_by": None,
    }
    return COUPONS[code]


@bot.message_handler(commands=['genaretcupun'])
def cmd_genaretcupun(message):
    if not is_admin(message.from_user.id):
        return
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🎯 Single Product", "🌍 All Products")
    kb.row("⬅ Back")
    USER_STATES[message.from_user.id] = STATE_ADMIN_COUPON_MENU
    bot.reply_to(message, "🎟 COUPON GENERATOR\n\n🎯 Single Product\n🌍 All Products\n⬅ Back", reply_markup=kb)


def handle_admin_coupon_states(message):
    uid = message.from_user.id
    state = get_state(uid)

    if state == STATE_ADMIN_COUPON_MENU:
        if message.text == "⬅ Back":
            set_state(uid, STATE_NONE)
            bot.reply_to(message, "Back to panel.")
            return True
        if message.text == "🎯 Single Product":
            USER_TEMP[uid] = {"coupon_scope": "single"}
            USER_STATES[uid] = STATE_ADMIN_SINGLE_COUPON_INPUT
            bot.reply_to(
                message,
                "Format required:\n"
                "discount | DD-MM-YYYY HH:MM AM/PM\n\n"
                "This will generate SINGLE PRODUCT coupon.",
            )
            return True
        if message.text == "🌍 All Products":
            USER_TEMP[uid] = {"coupon_scope": "all"}
            USER_STATES[uid] = STATE_ADMIN_ALL_COUPON_INPUT
            bot.reply_to(
                message,
                "Format required:\n"
                "discount | DD-MM-YYYY HH:MM AM/PM\n\n"
                "This will prepare ALL PRODUCT coupons.",
            )
            return True

    if state == STATE_ADMIN_SINGLE_COUPON_INPUT:
        tpl = parse_coupon_template(message.text)
        if not tpl:
            bot.reply_to(message, "Format error. Try again:\n\ndiscount | DD-MM-YYYY HH:MM AM/PM")
            return True

        coupon = create_coupon(
            discount=tpl["discount"],
            expires_at=tpl["expires"],
            scope="single",
            product_id="chatgpt_1m",
        )
        sms = (
            "🎟 SINGLE PRODUCT COUPON\n\n"
            f"Code: {coupon['code']}\n"
            f"Discount: ৳{coupon['discount']}\n"
            f"Expires: {fmt_dt(coupon['expires_at'])}\n\n"
            "One-time use only."
        )
        bot.reply_to(message, sms)
        set_state(uid, STATE_NONE)
        return True

    if state == STATE_ADMIN_ALL_COUPON_INPUT:
        tpl = parse_coupon_template(message.text)
        if not tpl:
            bot.reply_to(message, "Format error. Try again:\n\ndiscount | DD-MM-YYYY HH:MM AM/PM")
            return True
        USER_TEMP[uid]["tpl"] = tpl
        USER_STATES[uid] = STATE_ADMIN_MULTI_COUPON_QTY
        bot.reply_to(
            message,
            "Now send quantity (1–10000) for ALL PRODUCT coupons.",
        )
        return True

    if state == STATE_ADMIN_MULTI_COUPON_QTY:
        try:
            qty = int(message.text)
        except ValueError:
            bot.reply_to(message, "Please send a number (1–10000).")
            return True
        qty = max(1, min(10000, qty))
        tpl = USER_TEMP[uid]["tpl"]

        lines = []
        for _ in range(qty):
            c = create_coupon(
                discount=tpl["discount"],
                expires_at=tpl["expires"],
                scope="all",
            )
            lines.append(f"🎟 {c['code']}")

        sms = (
            "MULTI COUPON GENERATE — ALL PRODUCTS\n\n"
            + "\n".join(lines)
            + "\n\nValid for ALL products\nOne-time use\nNever regenerated again."
        )
        bot.reply_to(message, sms)
        set_state(uid, STATE_NONE)
        return True

    return False


# ========= 33) MEGA OFFER, 25) TUTORIAL, 34) USERS COUNT =========

@bot.message_handler(commands=['setoffer'])
def cmd_setoffer(message):
    if not is_admin(message.from_user.id):
        return
    USER_STATES[message.from_user.id] = STATE_ADMIN_MEGA_OFFER
    bot.reply_to(message, "Send NEW MEGA OFFER text.")


@bot.message_handler(commands=['addtutorial'])
def cmd_addtutorial(message):
    if not is_admin(message.from_user.id):
        return
    USER_STATES[message.from_user.id] = STATE_ADMIN_TUTORIAL
    bot.reply_to(message, "Send tutorial text.")


@bot.message_handler(commands=['removetutorial'])
def cmd_removetutorial(message):
    if not is_admin(message.from_user.id):
        return
    SETTINGS["tutorial"] = ""
    bot.reply_to(message, "Tutorial removed.")


@bot.message_handler(commands=['userscount'])
def cmd_userscount(message):
    if not is_admin(message.from_user.id):
        return
    count = len(USERS)
    bot.reply_to(message, f"👥 TOTAL USERS: {count}")


# ========= 36) ADD CHANNEL / GROUP LINK OR USERNAME =========

@bot.message_handler(commands=['addChanelOrGroupLink'])
def cmd_add_channel_or_group_link(message):
    if not is_admin(message.from_user.id):
        return
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📎 Add Channel/Group Link", "👤 Add Username")
    kb.row("⬅ Cancel")
    USER_STATES[message.from_user.id] = STATE_ADMIN_LINK_OR_USERNAME
    bot.reply_to(
        message,
        "📌 What do you want to add?\nChoose option:\n\n📎 Add Channel/Group Link\n👤 Add Username\n⬅ Cancel",
        reply_markup=kb,
    )


def handle_admin_misc_states(message):
    uid = message.from_user.id
    state = get_state(uid)

    if state == STATE_ADMIN_MEGA_OFFER:
        SETTINGS["mega_offer"] = message.text
        set_state(uid, STATE_NONE)
        bot.reply_to(message, "Mega offer updated.")
        return True

    if state == STATE_ADMIN_TUTORIAL:
        SETTINGS["tutorial"] = message.text
        set_state(uid, STATE_NONE)
        bot.reply_to(message, "Tutorial saved.")
        return True

    if state == STATE_ADMIN_LINK_OR_USERNAME:
        if message.text == "⬅ Cancel":
            set_state(uid, STATE_NONE)
            bot.reply_to(message, "❌ Operation cancelled")
            return True
        if message.text == "📎 Add Channel/Group Link":
            USER_STATES[uid] = STATE_ADMIN_ADD_LINK
            bot.reply_to(message, "🔗 Please send new Channel / Group link…")
            return True
        if message.text == "👤 Add Username":
            USER_STATES[uid] = STATE_ADMIN_ADD_USERNAME
            bot.reply_to(message, "👤 Please send new username…")
            return True

    if state == STATE_ADMIN_ADD_LINK:
        SETTINGS["channel_or_group_link"] = message.text.strip()
        set_state(uid, STATE_NONE)
        bot.reply_to(message, "✅ Saved Successfully! (Link)")
        return True

    if state == STATE_ADMIN_ADD_USERNAME:
        SETTINGS["contact_username"] = message.text.strip()
        set_state(uid, STATE_NONE)
        bot.reply_to(message, "✅ Username Saved Successfully!")
        return True

    return False


# ========= 26–27) BOT OFF / ON =========

@bot.message_handler(commands=['offbot'])
def cmd_offbot(message):
    global BOT_ON
    if not is_admin(message.from_user.id):
        return
    BOT_ON = False
    bot.reply_to(message, "BOT is now OFF for normal users.")


@bot.message_handler(commands=['onbot'])
def cmd_onbot(message):
    global BOT_ON
    if not is_admin(message.from_user.id):
        return
    BOT_ON = True
    sms = (
        "✨ Our services are LIVE again! ✨\n\n"
        "🚀 You can now place orders anytime.\n"
        "💛 We always deliver top-quality service.\n"
        "🙏 Thank you for trusting us!\n\n"
        "🌟 Your support means everything! 🌟\n\n"
        f"🏷 Hosted by: {HOSTED_BY}\n"
        "📞 Admin Support: @MinexxProo"
    )
    bot.reply_to(message, sms)


# ========= 35) FULL ADMIN COMMAND LIST =========

@bot.message_handler(commands=['panel'])
def cmd_panel(message):
    if not is_admin(message.from_user.id):
        return
    sms = (
        "/panel\n"
        "/addcategory\n"
        "/removecategory\n"
        "/addproduct\n"
        "/removeproduct\n"
        "/addstock\n"
        "/removestoke\n"
        "/allsellhistory\n"
        "/allorderhistory\n"
        "/pendingorders\n"
        "/completedorders\n"
        "/users\n"
        "/senduser\n"
        "/badge\n"
        "/broadcast\n"
        "/editwelcomesms\n"
        "/editallsmscustomize\n"
        "/addtutorial\n"
        "/removetutorial\n"
        "/genaretcupun\n"
        "/setoffer\n"
        "/userscount\n"
        "/offbot\n"
        "/onbot\n"
        "/reset\n"
        "/addChanelOrGroupLink"
    )
    bot.reply_to(message, sms)


@bot.message_handler(commands=['notify'])
def cmd_notify(message):
    user = get_user(message)
    handle_notify_admin(message, user)


# ========= GLOBAL TEXT ROUTER =========

@bot.message_handler(func=lambda m: True)
def all_text_router(message):
    user = get_user(message)
    uid = user["id"]
    state = get_state(uid)

    # Admin special flows
    if is_admin(uid):
        if handle_admin_special_states(message):
            return
        if handle_admin_coupon_states(message):
            return
        if handle_admin_misc_states(message):
            return

    # Signup flow
    if state == STATE_SIGNUP:
        handle_signup(message, user)
        return

    # Main menu buttons (5, 20–25, 33)
    if handle_main_menu_buttons(message, user):
        return

    # Category handling (6)
    if handle_category_buttons(message, user):
        return

    # Product list (7)
    if handle_product_list(message, user):
        return

    # Product actions (8, 9, 10)
    if state == STATE_PRODUCT:
        if handle_product_actions(message, user):
            return

    # Coupon input (9)
    if state == STATE_COUPON_INPUT:
        handle_coupon_input(message, user)
        return

    # Payment select (10–12)
    if state == STATE_PAYMENT_SELECT:
        if handle_payment_select(message, user):
            return

    # Payment format & order (13–15)
    if state == STATE_WAIT_PAYMENT_FORMAT:
        handle_wait_payment_format(message, user)
        return

    # Default fallback
    bot.send_message(message.chat.id, "Use the menu buttons or /openstore to navigate.")


if __name__ == "__main__":
    print("Bot running...")
    bot.infinity_polling(skip_pending=True)
