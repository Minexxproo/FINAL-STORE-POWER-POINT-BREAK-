# ============================================
# POWER POINT BREAK PREMIUM STORE — BOT.PY
# PART 1 — Setup + JSON + Start/Openstore/Auth/Main Menu
# ============================================

import telebot
from telebot import types
import json
import os
from datetime import datetime

# ============================================
# PLACEHOLDER CONFIG (EDIT LATER)
# ============================================
BOT_TOKEN = "8222148122:AAHNqdFu6ZrHM8VuwksuXI4pAa4QQaFmlWo"
MAIN_ADMIN_ID = 5692210187          # Your numeric Telegram ID
ADMIN_USERNAME = "@MinexxProo"       # Main admin username
SUPPORT_USERNAME = "@MinexxProo"   # Support username
ORDER_LOG_CHAT_ID = -1003373930001  # Channel/Group ID for order logs

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ============================================
# DATA FILE PATHS
# ============================================
DATA_FILES = {
    "users": "users.json",
    "orders": "orders.json",
    "admins": "admins.json",
    "superadmins": "superadmins.json",
    "coupons": "coupons.json",
    "products": "products.json",
    "stocks": "stocks.json",
    "settings": "settings.json",
    "categories": "categories.json"
}

# ============================================
# JSON LOAD / SAVE HELPERS
# ============================================
def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4, ensure_ascii=False)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ============================================
# INITIAL DATA
# ============================================
users = load_json(DATA_FILES["users"], {})
orders = load_json(DATA_FILES["orders"], {})
admins = load_json(DATA_FILES["admins"], {str(MAIN_ADMIN_ID): ADMIN_USERNAME})
superadmins = load_json(DATA_FILES["superadmins"], {str(MAIN_ADMIN_ID): ADMIN_USERNAME})
coupons = load_json(DATA_FILES["coupons"], {})
products = load_json(DATA_FILES["products"], {})
stocks = load_json(DATA_FILES["stocks"], {})
settings = load_json(DATA_FILES["settings"], {
    "bot_off": False,
    "mega_offer": "",
    "welcome_sms": "",
    "tutorial": "",
    "help_center": "",
})
categories = load_json(DATA_FILES["categories"], {
    "list": [
        "🤖 ChatGPT & AI",
        "▶️ YouTube Premium",
        "🎵 Spotify Premium",
        "🎬 Netflix",
        "🔒 VPN & Security",
        "👨‍💻 Developer Tools",
        "🧩 Office 365",
        "🎮 Gaming / Combo"
    ]
})

# runtime states
user_states = {}      # user_id -> state string
pending_data = {}     # temp context

# ============================================
# SMALL HELPERS
# ============================================
def is_admin(user_id: int) -> bool:
    return str(user_id) in admins or is_superadmin(user_id)

def is_superadmin(user_id: int) -> bool:
    return str(user_id) in superadmins

def get_full_name(message):
    fn = (message.from_user.first_name or "").strip()
    ln = (message.from_user.last_name or "").strip()
    return (fn + " " + ln).strip() if (fn or ln) else "User"

def get_username(message):
    return message.from_user.username or "Unknown"

def ensure_user_profile(message):
    uid = message.from_user.id
    uid_str = str(uid)
    if uid_str not in users:
        users[uid_str] = {
            "id": uid,
            "name": get_full_name(message),
            "username": get_username(message),
            "joined": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
            "total_orders": 0,
            "completed_orders": 0,
            "pending_orders": 0,
            "badge": "👑 VIP MAX",
        }
        save_json(DATA_FILES["users"], users)

def is_registered(message):
    return str(message.from_user.id) in users

def bot_is_off() -> bool:
    return settings.get("bot_off", False)

def main_menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    row1 = types.KeyboardButton("🛒 All Categories")
    row2 = types.KeyboardButton("🪪 My Profile")
    row3 = types.KeyboardButton("🛍 Active Orders")
    row4 = types.KeyboardButton("📦 My Orders")
    row5 = types.KeyboardButton("⏳ Pending Orders")
    row6 = types.KeyboardButton("🆘 Help Center")
    row7 = types.KeyboardButton("📚 Tutorial")
    row8 = types.KeyboardButton("🎁 Mega Offer")
    kb.add(row1, row2)
    kb.add(row3, row4)
    kb.add(row5, row6)
    kb.add(row7, row8)
    return kb

def all_categories_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # dynamic from categories.json later, for now use list
    for cat in categories.get("list", []):
        kb.add(types.KeyboardButton(cat))
    kb.add(types.KeyboardButton("⬅ Back"))
    return kb

# ============================================
# STEP 1 — /start (Welcome Screen)
# ============================================
@bot.message_handler(commands=["start"])
def cmd_start(message):
    if bot_is_off() and not is_admin(message.from_user.id):
        # BOT OFF MESSAGE (26)
        text = (
            "⚠️ Hey dear user, heads up!\n\n"
            "🚧 Our Premium Service is temporarily unavailable due to unexpected issues.\n"
            "🛠️ We’re working super fast to fix everything ASAP.\n\n"
            "⏳ Please hold on — your patience means a lot.\n"
            "🙏 Thank you for staying with us.\n"
            "💛 We’ll be back stronger!\n\n"
            "🏷 Hosted by: @PowerPointBreak\n"
            f"📞 Support: {SUPPORT_USERNAME}"
        )
        bot.send_message(message.chat.id, text)
        return

    full_name = get_full_name(message)
    username = get_username(message)
    user_id = message.from_user.id

    box = (
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "⭐⚡ POWER POINT BREAK PREMIUM STORE ⚡⭐\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 Welcome {full_name}!\n\n"
        "This is POWER POINT BREAK PREMIUM STORE\n"
        "💎 Premium Accounts • 💰 Lowest Price • ⚡ Fast Delivery • 🔒 Secure Service\n\n"
        "👉 Enter Store:\n"
        "/openstore\n\n"
        "👤 User Info:\n"
        f"🆔 User ID: {user_id}\n"
        f"🔗 Username: @{username}\n\n"
        f"📞 Support: {SUPPORT_USERNAME}\n"
        "🏷 Hosted by: @PowerPointBreak"
    )

    ensure_user_profile(message)
    bot.send_message(message.chat.id, box)

# ============================================
# STEP 2 — /openstore (Registration Gate)
# ============================================
@bot.message_handler(commands=["openstore"])
def cmd_openstore(message):
    if bot_is_off() and not is_admin(message.from_user.id):
        text = (
            "⚠️ Hey dear user, heads up!\n\n"
            "🚧 Our Premium Service is temporarily unavailable due to unexpected issues.\n"
            "🛠️ We’re working super fast to fix everything ASAP.\n\n"
            "⏳ Please hold on — your patience means a lot.\n"
            "🙏 Thank you for staying with us.\n"
            "💛 We’ll be back stronger!\n\n"
            "🏷 Hosted by: @PowerPointBreak\n"
            f"📞 Support: {SUPPORT_USERNAME}"
        )
        bot.send_message(message.chat.id, text)
        return

    chat_id = message.chat.id
    uid = message.from_user.id

    if not is_registered(message):
        # show Sign Up / Log In
        text = (
            "🔐 ACCOUNT REQUIRED\n\n"
            "To access the store, please Sign Up or Log In.\n\n"
            "Buttons:\n"
            "🆕 Sign Up\n"
            "🔓 Log In\n\n"
            "If already registered → MAIN MENU 🏠"
        )
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("🆕 Sign Up"), types.KeyboardButton("🔓 Log In"))
        bot.send_message(chat_id, text, reply_markup=kb)
        user_states[uid] = "auth_gate"
    else:
        # already registered → Main Menu
        full_name = get_full_name(message)
        text = f"🔓 Welcome back, {full_name}!\nTap MAIN MENU to continue."
        kb = main_menu_keyboard()
        bot.send_message(chat_id, text, reply_markup=kb)

# ============================================
# SIGN UP + LOG IN FLOW (Buttons)
# ============================================
@bot.message_handler(func=lambda m: m.text in ["🆕 Sign Up", "🔓 Log In"])
def handle_auth_buttons(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    txt = message.text

    if txt == "🆕 Sign Up":
        # show SIGN UP FORM (3)
        full_name = get_full_name(message)
        username = get_username(message)
        user_id = message.from_user.id

        text = (
            "📝 SIGN UP\n\n"
            f"Name: {full_name}\n"
            f"Username: @{username}\n"
            f"User ID: {user_id}\n\n"
            "Buttons:\n"
            "✅ Confirm Sign Up\n"
            "❌ Cancel\n\n"
            "If Confirmed →\n"
            "✅ Account created!\n\n"
            "If Cancel →\n"
            "❌ Sign Up cancelled.\n"
            "Use /openstore again."
        )

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("✅ Confirm Sign Up"), types.KeyboardButton("❌ Cancel"))
        bot.send_message(chat_id, text, reply_markup=kb)

        pending_data[uid] = {
            "name": full_name,
            "username": get_username(message),
            "user_id": user_id,
        }
        user_states[uid] = "signup_confirm"

    elif txt == "🔓 Log In":
        # LOG IN FLOW (4)
        if is_registered(message):
            full_name = get_full_name(message)
            text = f"🔓 Welcome back, {full_name}!\nTap MAIN MENU to continue."
            kb = main_menu_keyboard()
            bot.send_message(chat_id, text, reply_markup=kb)
        else:
            text = "❌ No account found. Please Sign Up."
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(types.KeyboardButton("🆕 Sign Up"))
            bot.send_message(chat_id, text, reply_markup=kb)

# ============================================
# CONFIRM SIGN UP / CANCEL
# ============================================
@bot.message_handler(func=lambda m: m.text in ["✅ Confirm Sign Up", "❌ Cancel"])
def handle_signup_confirm_cancel(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    txt = message.text

    if user_states.get(uid) != "signup_confirm":
        return

    if txt == "✅ Confirm Sign Up":
        data = pending_data.get(uid, {})
        name = data.get("name", get_full_name(message))
        username = data.get("username", get_username(message))
        user_id = data.get("user_id", uid)

        users[str(uid)] = {
            "id": user_id,
            "name": name,
            "username": username,
            "joined": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
            "total_orders": 0,
            "completed_orders": 0,
            "pending_orders": 0,
            "badge": "👑 VIP MAX",
        }
        save_json(DATA_FILES["users"], users)

        bot.send_message(chat_id, "✅ Account created!", reply_markup=main_menu_keyboard())
        user_states[uid] = "main_menu"
        pending_data.pop(uid, None)

    elif txt == "❌ Cancel":
        bot.send_message(
            chat_id,
            "❌ Sign Up cancelled.\nUse /openstore again.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        user_states[uid] = None
        pending_data.pop(uid, None)

# ============================================
# MAIN MENU HANDLER (Buttons)
# ============================================
@bot.message_handler(func=lambda m: m.text in [
    "🛒 All Categories",
    "🪪 My Profile",
    "🛍 Active Orders",
    "📦 My Orders",
    "⏳ Pending Orders",
    "🆘 Help Center",
    "📚 Tutorial",
    "🎁 Mega Offer"
])
def handle_main_menu_buttons(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    txt = message.text

    if not is_registered(message):
        bot.send_message(chat_id, "❌ No account found. Please Sign Up using /openstore.")
        return

    # 6) ALL CATEGORIES
    if txt == "🛒 All Categories":
        text = (
            "📂 SELECT A CATEGORY\n\n"
            "🤖 ChatGPT & AI      ▶️ YouTube Premium      🎵 Spotify Premium\n"
            "🎬 Netflix           🔒 VPN & Security       👨‍💻 Developer Tools\n"
            "🧩 Office 365        🎮 Gaming / Combo\n"
            "⬅ Back"
        )
        bot.send_message(chat_id, text, reply_markup=all_categories_keyboard())
        user_states[uid] = "categories"

    # 23) USER PROFILE (basic info now, later extended)
    elif txt == "🪪 My Profile":
        u = users.get(str(uid), {})
        name = u.get("name", get_full_name(message))
        username = u.get("username", get_username(message))
        joined = u.get("joined", "N/A")
        total_orders = u.get("total_orders", 0)
        completed = u.get("completed_orders", 0)
        pending = u.get("pending_orders", 0)
        badge = u.get("badge", "👑 VIP MAX")

        text = (
            "🪪 MY PROFILE\n\n"
            f"Name: {name}\n"
            f"Username: @{username}\n"
            f"User ID: {uid}\n\n"
            f"Joined: {joined}\n\n"
            f"Total Orders: {total_orders}\n"
            f"Completed: {completed}\n"
            f"Pending: {pending} ⏳\n\n"
            f"Badge: {badge}\n"
            f"Support: {SUPPORT_USERNAME}"
        )
        bot.send_message(chat_id, text, reply_markup=main_menu_keyboard())

    # 20) ACTIVE ORDERS (basic placeholder, full logic later)
    elif txt == "🛍 Active Orders":
        text = "🛍 ACTIVE ORDERS\n\n(Active order details will be shown here.)"
        bot.send_message(chat_id, text, reply_markup=main_menu_keyboard())

    # 22) MY ORDERS
    elif txt == "📦 My Orders":
        text = (
            "📦 MY ORDERS HISTORY\n\n"
            "Shows full list including:\n"
            "• Approved ✅\n"
            "• Pending ⏳\n"
            "• Cancelled 🚫\n"
            "• Date & Time"
        )
        bot.send_message(chat_id, text, reply_markup=main_menu_keyboard())

    # 21) PENDING ORDERS
    elif txt == "⏳ Pending Orders":
        text = (
            "⏳ MY PENDING ORDERS\n\n"
            "Order ID: {id}\n"
            "Product: {product}\n"
            "Amount: {amount}\n"
            "Status: Awaiting Payment Confirmation ⏳"
        )
        bot.send_message(chat_id, text, reply_markup=main_menu_keyboard())

    # 24) HELP CENTER
    elif txt == "🆘 Help Center":
        text = (
            "🆘 SUPPORT CENTER\n\n"
            "💬 If you have any questions or face any kind of problem,\n"
            "📩 just message us in the inbox.\n\n"
            "🛠️ We are always here and will try our best to solve your issue.\n"
            "🙏 Thank you so much for staying with us!\n\n"
            f"👨‍💻 Admin Support: {SUPPORT_USERNAME}\n\n"
            "⚡ Hosted by: POWER POINT BREAK\n\n"
            "Response Time: 1–15 minutes ⏱️"
        )
        bot.send_message(chat_id, text, reply_markup=main_menu_keyboard())

    # 25) TUTORIAL
    elif txt == "📚 Tutorial":
        tut = settings.get("tutorial", "")
        if tut:
            bot.send_message(chat_id, tut, reply_markup=main_menu_keyboard())
        else:
            bot.send_message(chat_id, "📚 No tutorial added yet", reply_markup=main_menu_keyboard())

    # 33) MEGA OFFER
    elif txt == "🎁 Mega Offer":
        offer = settings.get("mega_offer", "")
        if offer:
            text = f"🎁 NEW MEGA OFFER\n{offer}"
        else:
            text = "🎁 No mega offer added yet."
        bot.send_message(chat_id, text, reply_markup=main_menu_keyboard())

# ============================================
# CATEGORIES BACK BUTTON HANDLER
# (Later parts will add product selection etc.)
# ============================================
@bot.message_handler(func=lambda m: m.text == "⬅ Back")
def handle_back_button(message):
    uid = message.from_user.id
    state = user_states.get(uid)

    # from categories → go back to main menu
    if state == "categories":
        bot.send_message(message.chat.id, "🏠 Main Menu", reply_markup=main_menu_keyboard())
        user_states[uid] = "main_menu"
    else:
        # default: go main menu
        bot.send_message(message.chat.id, "🏠 Main Menu", reply_markup=main_menu_keyboard())
        user_states[uid] = "main_menu"

# ============================================
# END OF PART 1
# NEXT: PART 2 → Categories → Products → Product Details → Coupon → Payment → Orders
# ============================================


# ============================================
# PART 2 — Categories → Products → Product Details → Coupon → Payment → Order
# ============================================

# Helper to get (or create) a default product for demo
def get_default_product():
    """
    Demo অনুযায়ী একটা default product ধরলাম:
    ChatGPT Plus — 1 Month
    এইটা না চাইলে তুমি পরে /addproduct দিয়ে ইচ্ছামতো add করতে পারবে।
    """
    global products
    if "chatgpt_plus_1m" not in products:
        products["chatgpt_plus_1m"] = {
            "id": "chatgpt_plus_1m",
            "name": "ChatGPT Plus — 1 Month",
            "category": "🤖 ChatGPT & AI",
            "duration_days": 30,
            "price": 499,
            "stock": 7
        }
        save_json(DATA_FILES["products"], products)
    return products["chatgpt_plus_1m"]

# Helper: create order id
def generate_order_id():
    base = 1001
    return f"CG-{base + len(orders)}"

# ============================================
# CATEGORY SELECTION (from All Categories)
# ============================================
@bot.message_handler(func=lambda m: m.text in categories.get("list", []))
def handle_category_select(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    cat = message.text

    if not is_registered(message):
        bot.send_message(chat_id, "❌ No account found. Please Sign Up using /openstore.")
        return

    # এখন শুধু 🤖 ChatGPT & AI এর জন্য full product list demo মতো
    if cat == "🤖 ChatGPT & AI":
        # 7) PRODUCT LIST — ChatGPT & AI
        text = (
            "🛍 CATEGORY: ChatGPT & AI\n\n"
            "🤖 ChatGPT Plus — 1 Month\n"
            "🤖 ChatGPT Plus — 3 Months\n"
            "🚀 GPT-4 Team Access\n"
            "⬅ Back"
        )
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("🤖 ChatGPT Plus — 1 Month"))
        kb.add(types.KeyboardButton("🤖 ChatGPT Plus — 3 Months"))
        kb.add(types.KeyboardButton("🚀 GPT-4 Team Access"))
        kb.add(types.KeyboardButton("⬅ Back"))
        bot.send_message(chat_id, text, reply_markup=kb)
        user_states[uid] = "category_chatgpt"
    else:
        # অন্য ক্যাটাগরিগুলার জন্য আপাতত placeholder
        bot.send_message(
            chat_id,
            f"{cat}\n\n🛠️ This category products will be managed via admin panel later.",
            reply_markup=all_categories_keyboard()
        )
        user_states[uid] = "categories"

# ============================================
# PRODUCT SELECTION UNDER ChatGPT & AI
# ============================================
@bot.message_handler(func=lambda m: m.text in [
    "🤖 ChatGPT Plus — 1 Month",
    "🤖 ChatGPT Plus — 3 Months",
    "🚀 GPT-4 Team Access"
])
def handle_product_select(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    txt = message.text

    if not is_registered(message):
        bot.send_message(chat_id, "❌ No account found. Please Sign Up using /openstore.")
        return

    # এখন মূল demo follow করে শুধু 1 Month টাকে full details বানালাম
    if txt == "🤖 ChatGPT Plus — 1 Month":
        product = get_default_product()
        price = product.get("price", 499)
        stock = product.get("stock", 0)

        if stock <= 0:
            text = (
                "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
                "🤖 CHATGPT PLUS — 1 MONTH\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                "📛 OUT OF STOCK"
            )
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.add(types.KeyboardButton("⬅ Back"))
            bot.send_message(chat_id, text, reply_markup=kb)
            user_states[uid] = "category_chatgpt"
            return

        text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "🤖 CHATGPT PLUS — 1 MONTH\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            f"⏳ Duration: 30 Days\n"
            f"💰 Price: ৳{price}\n"
            f"📊 Stock: {stock} Available\n\n"
            "⭐ Benefits:\n"
            "• GPT-4 Full Access\n"
            "• Ultra Fast Speed\n"
            "• Priority Server\n\n"
            "Buttons:\n"
            "🛒 Buy Now\n"
            "🎟 Apply Coupon\n"
            "⬅ Back\n\n"
            "If stock = 0 →\n"
            "📛 OUT OF STOCK"
        )

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("🛒 Buy Now"), types.KeyboardButton("🎟 Apply Coupon"))
        kb.add(types.KeyboardButton("⬅ Back"))

        pending_data[uid] = {
            "product_id": product["id"],
            "product_name": product["name"],
            "base_price": price,
            "final_price": price,
            "coupon_code": None,
            "discount": 0,
            "payment_method": None,
        }

        bot.send_message(chat_id, text, reply_markup=kb)
        user_states[uid] = "product_chatgpt_plus_1m"

    else:
        # অন্য দুইটা product আপাতত placeholder
        bot.send_message(
            chat_id,
            f"{txt}\n\n🛠️ This product will be fully configured from admin panel later.",
            reply_markup=main_menu_keyboard()
        )
        user_states[uid] = "main_menu"

# ============================================
# PRODUCT DETAILS PAGE BUTTONS (Buy Now / Apply Coupon)
# ============================================
@bot.message_handler(func=lambda m: m.text in ["🛒 Buy Now", "🎟 Apply Coupon"])
def handle_product_buttons(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    txt = message.text

    state = user_states.get(uid)
    if state != "product_chatgpt_plus_1m":
        return

    ctx = pending_data.get(uid)
    if not ctx:
        bot.send_message(chat_id, "⚠ Session expired. Please select product again.")
        return

    if txt == "🛒 Buy Now":
        # সরাসরি payment method page (10)
        price = ctx.get("final_price", ctx.get("base_price", 499))
        text = (
            "💳 PAYMENT METHOD\n\n"
            "You're buying:\n"
            "🛒 ChatGPT Plus — 1 Month\n"
            f"💰 Payable Amount: ৳{price}\n\n"
            "Select Payment:\n\n"
            "🟣 bKash\n"
            "🟡 Nagad\n"
            "🟠 Upay\n"
            "🔵 Rocket\n"
            "🪙 Crypto (USDT)\n"
            "⬅ Back"
        )

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("🟣 bKash"), types.KeyboardButton("🟡 Nagad"))
        kb.add(types.KeyboardButton("🟠 Upay"), types.KeyboardButton("🔵 Rocket"))
        kb.add(types.KeyboardButton("🪙 Crypto (USDT)"))
        kb.add(types.KeyboardButton("⬅ Back"))

        bot.send_message(chat_id, text, reply_markup=kb)
        user_states[uid] = "payment_method"

    elif txt == "🎟 Apply Coupon":
        # COUPON MENU — demo অনুযায়ী user থেকে code নিবো
        text = (
            "🎟 APPLY COUPON\n\n"
            "Please send your coupon code.\n\n"
            "Invalid → ❌ INVALID COUPON\n"
            "Expired → ⏳ EXPIRED\n"
            "Used → 🛑 ALREADY USED\n"
            "Wrong Product → 🚫 NOT VALID"
        )
        bot.send_message(chat_id, text)
        user_states[uid] = "await_coupon_code"

# ============================================
# COUPON CODE INPUT + VALIDATION
# ============================================
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_coupon_code")
def handle_coupon_code(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    code = message.text.strip()

    ctx = pending_data.get(uid)
    if not ctx:
        bot.send_message(chat_id, "⚠ Session expired. Please select product again.")
        user_states[uid] = "main_menu"
        return

    product_id = ctx.get("product_id")
    base_price = ctx.get("base_price", 499)

    # coupon structure:
    # coupons[code] = {
    #   "discount": int,
    #   "product_id": "chatgpt_plus_1m" or "ALL",
    #   "expires": "DD-MM-YYYY HH:MM",
    #   "used": False
    # }

    coupon = coupons.get(code)

    # INVALID
    if coupon is None:
        bot.send_message(chat_id, "❌ INVALID COUPON")
        # back to product page state
        user_states[uid] = "product_chatgpt_plus_1m"
        return

    # EXPIRED CHECK (very simple string compare, তুমি চাইলে পরে improve করতে পারো)
    expires = coupon.get("expires")
    if expires:
        try:
            exp_dt = datetime.strptime(expires, "%d-%m-%Y %H:%M")
            if datetime.now() > exp_dt:
                bot.send_message(chat_id, "⏳ EXPIRED")
                user_states[uid] = "product_chatgpt_plus_1m"
                return
        except Exception:
            pass

    # USED
    if coupon.get("used"):
        bot.send_message(chat_id, "🛑 ALREADY USED")
        user_states[uid] = "product_chatgpt_plus_1m"
        return

    # WRONG PRODUCT
    c_prod = coupon.get("product_id", "ALL")
    if c_prod not in ["ALL", product_id]:
        bot.send_message(chat_id, "🚫 NOT VALID")
        user_states[uid] = "product_chatgpt_plus_1m"
        return

    # VALID COUPON
    discount = int(coupon.get("discount", 0))
    final_price = base_price - discount
    if final_price < 0:
        final_price = 0

    ctx["coupon_code"] = code
    ctx["discount"] = discount
    ctx["final_price"] = final_price
    pending_data[uid] = ctx

    text = (
        "🎉 COUPON APPLIED SUCCESSFULLY! 🎉\n\n"
        f"Coupon: {code}\n"
        f"💵 Discount: ৳{discount}\n"
        f"💰 Original Price: ৳{base_price}\n"
        f"✅ Payable: ৳{final_price}\n\n"
        "Full-Free Coupon →\n"
        "💚 Payable: 0\n"
        "⚡ Auto-delivery enabled.\n\n"
        "⬅ Back"
    )
    bot.send_message(chat_id, text)

    # এখন চাইলে সরাসরি payment method এ নিতে পারো
    price = final_price
    text2 = (
        "💳 PAYMENT METHOD\n\n"
        "You're buying:\n"
        "🛒 ChatGPT Plus — 1 Month\n"
        f"💰 Payable Amount: {price}৳\n\n"
        "Select Payment:\n\n"
        "🟣 bKash\n"
        "🟡 Nagad\n"
        "🟠 Upay\n"
        "🔵 Rocket\n"
        "🪙 Crypto (USDT)\n"
        "⬅ Back"
    )

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("🟣 bKash"), types.KeyboardButton("🟡 Nagad"))
    kb.add(types.KeyboardButton("🟠 Upay"), types.KeyboardButton("🔵 Rocket"))
    kb.add(types.KeyboardButton("🪙 Crypto (USDT)"))
    kb.add(types.KeyboardButton("⬅ Back"))

    bot.send_message(chat_id, text2, reply_markup=kb)
    user_states[uid] = "payment_method"

# ============================================
# PAYMENT METHOD SELECTION
# ============================================
@bot.message_handler(func=lambda m: m.text in ["🟣 bKash", "🟡 Nagad", "🟠 Upay", "🔵 Rocket", "🪙 Crypto (USDT)"])
def handle_payment_method(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    txt = message.text

    state = user_states.get(uid)
    if state != "payment_method":
        return

    ctx = pending_data.get(uid)
    if not ctx:
        bot.send_message(chat_id, "⚠ Session expired. Please select product again.")
        user_states[uid] = "main_menu"
        return

    final_price = ctx.get("final_price", ctx.get("base_price", 499))
    ctx["payment_method"] = txt
    pending_data[uid] = ctx

    # 11) BKASH PAYMENT PAGE
    if txt == "🟣 bKash":
        text = (
            "🟣 BKASH PAYMENT\n\n"
            "You're purchasing:\n"
            "🛒 ChatGPT Plus — 1 Month\n\n"
            f"💰 Original Price: ৳{ctx.get('base_price', 499)}\n"
            f"🎟 Coupon: {ctx.get('coupon_code') if ctx.get('coupon_code') else '{if-any}'}\n"
            f"💵 Discount: {ctx.get('discount') if ctx.get('discount') else '{if-any}'}\n"
            f"✅ Payable: ৳{final_price}\n\n"
            "Send Money to:\n"
            "📲 01877576843 (bKash Personal)\n\n"
            "⚠ RULES:\n"
            "👉 Only Send Money allowed\n"
            "❌ Mobile Recharge NOT accepted\n\n"
            "Send info in format:\n"
            "Sender | Amount | TXID\n\n"
            "Example:\n"
            "01811112222 | 499 | TX9L92QE0\n\n"
            "⬅ Back"
        )
        bot.send_message(chat_id, text)
        user_states[uid] = "await_payment_info"

    # Other local methods same rules (copy of bKash text with name changed)
    elif txt in ["🟡 Nagad", "🟠 Upay", "🔵 Rocket"]:
        method_name = txt.split(" ")[0].replace("🟡", "Nagad").replace("🟠", "Upay").replace("🔵", "Rocket")
        text = (
            f"{txt} PAYMENT\n\n"
            "You're purchasing:\n"
            "🛒 ChatGPT Plus — 1 Month\n\n"
            f"💰 Original Price: ৳{ctx.get('base_price', 499)}\n"
            f"🎟 Coupon: {ctx.get('coupon_code') if ctx.get('coupon_code') else '{if-any}'}\n"
            f"💵 Discount: {ctx.get('discount') if ctx.get('discount') else '{if-any}'}\n"
            f"✅ Payable: ৳{final_price}\n\n"
            "Send Money to:\n"
            f"📲 Your {method_name} Number Here\n\n"
            "⚠ RULES:\n"
            "👉 Only Send Money allowed\n"
            "❌ Mobile Recharge NOT accepted\n\n"
            "Send info in format:\n"
            "Sender | Amount | TXID\n\n"
            "Example:\n"
            "01811112222 | 499 | TX9L92QE0\n\n"
            "⬅ Back"
        )
        bot.send_message(chat_id, text)
        user_states[uid] = "await_payment_info"

    # 12) CRYPTO USDT PAYMENT
    elif txt == "🪙 Crypto (USDT)":
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
            f"📩 Crypto Payment Please Contract Admin: 👉 {ADMIN_USERNAME}\n\n"
            "⬅ Back"
        )
        bot.send_message(chat_id, text, reply_markup=main_menu_keyboard())
        # Crypto case-e আমরা TXID confirm দিচ্ছি না এখানে, তুমি চাইলে পরে add করতে পারো।
        user_states[uid] = "main_menu"

# ============================================
# PAYMENT INFO FORMAT (Sender | Amount | TXID)
# 13) FORMAT VALIDATION + 14) ORDER SUBMIT
# ============================================
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_payment_info")
def handle_payment_info(message):
    chat_id = message.chat.id
    uid = message.from_user.id
    txt = message.text.strip()

    ctx = pending_data.get(uid)
    if not ctx:
        bot.send_message(chat_id, "⚠ Session expired. Please select product again.")
        user_states[uid] = "main_menu"
        return

    # Back করলে আগের জায়গায় যাবে
    if txt == "⬅ Back":
        # send payment method menu again
        price = ctx.get("final_price", ctx.get("base_price", 499))
        text2 = (
            "💳 PAYMENT METHOD\n\n"
            "You're buying:\n"
            "🛒 ChatGPT Plus — 1 Month\n"
            f"💰 Payable Amount: ৳{price}\n\n"
            "Select Payment:\n\n"
            "🟣 bKash\n"
            "🟡 Nagad\n"
            "🟠 Upay\n"
            "🔵 Rocket\n"
            "🪙 Crypto (USDT)\n"
            "⬅ Back"
        )

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("🟣 bKash"), types.KeyboardButton("🟡 Nagad"))
        kb.add(types.KeyboardButton("🟠 Upay"), types.KeyboardButton("🔵 Rocket"))
        kb.add(types.KeyboardButton("🪙 Crypto (USDT)"))
        kb.add(types.KeyboardButton("⬅ Back"))

        bot.send_message(chat_id, text2, reply_markup=kb)
        user_states[uid] = "payment_method"
        return

    parts = [p.strip() for p in txt.split("|")]
    if len(parts) != 3:
        # 13) WRONG FORMAT
        bot.send_message(chat_id, "⚠ Invalid Format")
        return

    sender_number, amount_text, txid = parts

    # basic numeric check
    try:
        amount_value = int(amount_text)
    except ValueError:
        bot.send_message(chat_id, "⚠ Invalid Format")
        return

    final_price = ctx.get("final_price", ctx.get("base_price", 499))
    if amount_value != final_price:
        # এখানে চাইলে তুমি mismatch handle আলাদা করতে পারো
        pass

    # 14) ORDER SUBMITTED MESSAGE
    order_id = generate_order_id()
    now_str = datetime.now().strftime("%d-%b-%Y | %I:%M %p")
    coupon_code = ctx.get("coupon_code")
    discount = ctx.get("discount", 0)
    base_price = ctx.get("base_price", 499)
    product_name = ctx.get("product_name", "ChatGPT Plus — 1 Month")
    payable = final_price

    # save orders.json
    orders[order_id] = {
        "order_id": order_id,
        "user_id": uid,
        "username": get_username(message),
        "product": product_name,
        "original_price": base_price,
        "coupon": coupon_code,
        "discount": discount,
        "payable": payable,
        "sender_number": sender_number,
        "txid": txid,
        "status": "PENDING",
        "method": ctx.get("payment_method"),
        "created_at": now_str,
    }
    save_json(DATA_FILES["orders"], orders)

    # update user stats
    u = users.get(str(uid), {})
    u["total_orders"] = u.get("total_orders", 0) + 1
    u["pending_orders"] = u.get("pending_orders", 0) + 1
    users[str(uid)] = u
    save_json(DATA_FILES["users"], users)

    text = (
        "🎉 Your order request has been submitted! 🎉\n\n"
        f"📅 Date/Time: {now_str}\n"
        f"🧾 Order ID: {order_id}\n"
        "⏳ Status: Waiting for Admin approval…\n"
        "(⏳ Pending)\n\n"
        f"🛒 Product: {product_name}\n"
        f"💰 Original Price: ৳{base_price}\n"
        f"🎟 Coupon: {coupon_code if coupon_code else 'None'}\n"
        f"💵 Discount: ৳{discount}\n"
        f"✅ Payable Amount: ৳{payable}\n"
        f"👉 Payment Sender Number: {sender_number}\n\n"
        "⏱ Estimated Approval Time: 1–15 minutes\n"
        "📌 Stay online for verification if needed.\n\n"
        f"📞 Admin Support: {SUPPORT_USERNAME}\n"
        "🏷 Hosted by: @PowerPointBreak\n\n"
        "❤️ Thank you for choosing Power Point Break! ❤️"
    )
    bot.send_message(chat_id, text, reply_markup=main_menu_keyboard())

    user_states[uid] = "main_menu"
    pending_data.pop(uid, None)

    # 15) ADMIN GROUP — NEW ORDER ALERT
    try:
        admin_text = (
            "📦 NEW ORDER RECEIVED 🔔\n\n"
            f"Order ID: {order_id}\n"
            f"Username: @{get_username(message)}\n"
            f"User ID: {uid}\n\n"
            f"🛒 Product: {product_name}\n"
            f"💰 Original Amount: ৳{base_price}\n"
            f"🎟 Coupon: {coupon_code if coupon_code else 'None'}\n"
            f"💵 Discount: ৳{discount}\n"
            f"✅ Final Amount: ৳{payable}\n\n"
            f"💳 Payment Method: {orders[order_id].get('method')}\n"
            f"📲 Sender: {sender_number}\n"
            f"🔖 TXID: {txid}\n\n"
            f"🕒 Date & Time: {now_str}"
        )
        # এখানে পরে inline button (Approve / Reject) Part 3-এ add করব
        bot.send_message(ORDER_LOG_CHAT_ID, admin_text)
    except Exception:
        pass



# ============================================
# PART 3 — Admin Approve / Reject / Auto Delivery / Cancel + Buttons
# ============================================

# small helper: find product_id by product name
def find_product_id_by_name(name: str):
    for pid, pdata in products.items():
        if pdata.get("name") == name:
            return pid
    return None

# small helper: send approved SMS + auto delivery log
def auto_deliver_order(order_id: str):
    order = orders.get(order_id)
    if not order:
        return False, "Order not found."

    user_id = order["user_id"]
    username = order.get("username", "User")
    product_name = order.get("product", "Unknown Product")

    # find product id by name
    pid = find_product_id_by_name(product_name)
    if not pid:
        return False, "Product not configured for stock."

    stock_list = stocks.get(pid, [])
    if not stock_list:
        return False, "No stock available for this product."

    # FIFO: first stock used
    cred = stock_list.pop(0)
    email = cred.get("email", "demo@example.com")
    password = cred.get("password", "changeme123")
    stocks[pid] = stock_list
    save_json(DATA_FILES["stocks"], stocks)

    # user stats update
    u = users.get(str(user_id), {})
    if u:
        u["pending_orders"] = max(0, u.get("pending_orders", 0) - 1)
        u["completed_orders"] = u.get("completed_orders", 0) + 1
        users[str(user_id)] = u
        save_json(DATA_FILES["users"], users)

    # 17) USER — ORDER APPROVED SMS
    text_user = (
        "🎉✨ CONGRATULATIONS! ✨🎉\n"
        f"Hello Dear @{username}, your order has been successfully APPROVED! ✅🚀\n\n"
        f"Your {product_name} has been successfully activated! ⚡🔥\n\n"
        "🧾 Order Details:\n"
        "———————————————\n"
        f"📦 Order ID: {order_id}\n"
        f"🛒 Product: {product_name}\n"
        "———————————————\n\n"
        "🔐 Login Credentials:\n"
        f"📧 Email: {email}\n"
        f"🔑 Password: {password}\n\n"
        "⚠ IMPORTANT INSTRUCTIONS:\n"
        "• After logging in, please check the account properly\n"
        "• Enable Two-Factor Authentication immediately\n"
        "• Do NOT share this account with anyone\n"
        "• If you face any issue, please report it quickly\n\n"
        f"📞 Admin Support: 👉 {SUPPORT_USERNAME}\n\n"
        "🌹 Thank you so much for your order! 🌹"
    )

    try:
        bot.send_message(user_id, text_user, reply_markup=main_menu_keyboard())
    except Exception:
        pass

    # 29) AUTO DELIVERY LOG — ADMIN SIDE
    log_text = (
        "📦 ORDER DELIVERED (AUTO LOG)\n\n"
        f"User: @{username}\n"
        f"User ID: {user_id}\n\n"
        f"Order ID: {order_id}\n"
        f"Product: {product_name}\n\n"
        "🔐 Login:\n"
        f"📧 Email: {email}\n"
        f"🔑 Password: {password}\n\n"
        f"Delivered at: 🕒 {datetime.now().strftime('%d-%b-%Y %I:%M %p')}"
    )
    try:
        bot.send_message(ORDER_LOG_CHAT_ID, log_text)
    except Exception:
        pass

    return True, "Delivered"


# ============================================
# Core Approve Logic (used by command + button)
# ============================================
def approve_order_internal(order_id: str):
    order = orders.get(order_id)
    if not order:
        return False, "❌ No order found with this ID."

    if order.get("status") == "APPROVED":
        return False, "⚠️ This order is already APPROVED."
    if order.get("status") == "REJECTED":
        return False, "⚠️ This order is already REJECTED."
    if order.get("status") == "CANCELLED":
        return False, "⚠️ This order is already CANCELLED."

    order["status"] = "APPROVED"
    orders[order_id] = order
    save_json(DATA_FILES["orders"], orders)

    ok, msg = auto_deliver_order(order_id)
    if not ok:
        return False, f"✅ Order approved, but delivery issue: {msg}"
    return True, f"✅ Order {order_id} APPROVED & delivered successfully!"


def reject_order_internal(order_id: str, reason: str):
    order = orders.get(order_id)
    if not order:
        return False, "❌ No order found with this ID."

    if order.get("status") == "APPROVED":
        return False, "⚠️ This order is already APPROVED."
    if order.get("status") == "REJECTED":
        return False, "⚠️ This order is already REJECTED."
    if order.get("status") == "CANCELLED":
        return False, "⚠️ This order is already CANCELLED."

    order["status"] = "REJECTED"
    orders[order_id] = order
    save_json(DATA_FILES["orders"], orders)

    uid = order["user_id"]
    u = users.get(str(uid), {})
    if u:
        u["pending_orders"] = max(0, u.get("pending_orders", 0) - 1)
        users[str(uid)] = u
        save_json(DATA_FILES["users"], users)

    # 18) USER REJECT SMS
    text_user = (
        "❌ Your order has been rejected.\n\n"
        f"Reason: {reason}\n\n"
        "⏳ You have 10 minutes to resubmit correctly.\n\n"
        "Correct Format:\n"
        "Sender | Amount | TXID\n"
        "Example:\n"
        "01811112222 | 499 | TX9L92QE0"
    )
    try:
        bot.send_message(uid, text_user, reply_markup=main_menu_keyboard())
    except Exception:
        pass

    return True, f"❌ Order {order_id} rejected."


# ============================================
# /approve COMMAND — Optional (Text Command)
# ============================================
@bot.message_handler(commands=["approve"])
def cmd_approve(message):
    if not is_admin(message.from_user.id):
        return

    chat_id = message.chat.id
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(chat_id, "Usage: /approve CG-1001")
        return

    order_id = parts[1].strip()
    ok, msg = approve_order_internal(order_id)
    bot.send_message(chat_id, msg)


# ============================================
# /reject COMMAND — Optional (Text Command)
# ============================================
@bot.message_handler(commands=["reject"])
def cmd_reject(message):
    if not is_admin(message.from_user.id):
        return

    chat_id = message.chat.id
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        bot.send_message(chat_id, "Usage: /reject CG-1001 [Reason]")
        return

    order_id = parts[1].strip()
    reason = ""
    if len(parts) == 3:
        reason = parts[2].strip()
    if not reason:
        reason = "Payment information incorrect or could not be verified."

    ok, msg = reject_order_internal(order_id, reason)
    bot.send_message(chat_id, msg)


# ============================================
# INLINE BUTTON HANDLER — Approve / Reject
# ============================================
@bot.callback_query_handler(func=lambda c: c.data.startswith("approve:") or c.data.startswith("reject:"))
def on_admin_buttons(call):
    admin_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data

    if not is_admin(admin_id):
        bot.answer_callback_query(call.id, "❌ Permission denied")
        return

    if data.startswith("approve:"):
        order_id = data.split("approve:")[1]
        ok, msg = approve_order_internal(order_id)
        try:
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        except Exception:
            pass
        bot.answer_callback_query(call.id, "Done")
        bot.send_message(chat_id, msg)

    elif data.startswith("reject:"):
        order_id = data.split("reject:")[1]
        # button diye default reason use korbo
        reason = "Payment information incorrect or could not be verified."
        ok, msg = reject_order_internal(order_id, reason)
        try:
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        except Exception:
            pass
        bot.answer_callback_query(call.id, "Done")
        bot.send_message(chat_id, msg)


# ============================================
# /cancelorder ORDER_ID — Auto Cancel System (19)
# ============================================
@bot.message_handler(commands=["cancelorder"])
def cmd_cancelorder(message):
    if not is_admin(message.from_user.id):
        return

    chat_id = message.chat.id
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(chat_id, "Usage: /cancelorder CG-1001")
        return

    order_id = parts[1].strip()
    order = orders.get(order_id)
    if not order:
        bot.send_message(chat_id, "❌ No order found with this ID.")
        return

    if order.get("status") in ["APPROVED", "REJECTED", "CANCELLED"]:
        bot.send_message(chat_id, "⚠️ This order is already processed.")
        return

    order["status"] = "CANCELLED"
    orders[order_id] = order
    save_json(DATA_FILES["orders"], orders)

    uid = order["user_id"]
    u = users.get(str(uid), {})
    if u:
        u["pending_orders"] = max(0, u.get("pending_orders", 0) - 1)
        users[str(uid)] = u
        save_json(DATA_FILES["users"], users)

    # 19) AUTO CANCEL SYSTEM — User message
    text_user = (
        "🚫 Your order has been automatically cancelled\n"
        "because you didn’t resubmit in time.\n\n"
        f"For help: {SUPPORT_USERNAME}"
    )
    try:
        bot.send_message(uid, text_user, reply_markup=main_menu_keyboard())
    except Exception:
        pass

    bot.send_message(chat_id, f"🚫 Order {order_id} cancelled.")




# ============================================
# PART 4 — ADMIN PANEL + CORE ADMIN COMMANDS
# ============================================

# Simple helper: check is text from admin
def admin_only(message):
    return is_admin(message.from_user.id)


# ============================================
# /panel — Full Admin Command List (35)
# ============================================
@bot.message_handler(commands=["panel"])
def cmd_panel(message):
    if not is_admin(message.from_user.id):
        return

    text = (
        "👑 ADMIN CONTROL PANEL\n\n"
        "Available Commands:\n\n"
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
        "/addChanelOrGroupLink\n\n"
        "Extra Internal:\n"
        "/approve\n"
        "/reject\n"
        "/cancelorder\n"
        "/cancelorder CG-1001\n"
    )
    bot.send_message(message.chat.id, text)


# ============================================
# /userscount — Total Users Count (34, 63)
# ============================================
@bot.message_handler(commands=["userscount"])
def cmd_userscount(message):
    if not is_admin(message.from_user.id):
        return

    total = len(users)
    text = f"👥 TOTAL USERS: {total}"
    bot.send_message(message.chat.id, text)


# ============================================
# /offbot — Turn OFF the Bot (64)
# /onbot  — Turn ON the Bot (65)
# ============================================
@bot.message_handler(commands=["offbot"])
def cmd_offbot(message):
    if not is_admin(message.from_user.id):
        return

    settings["bot_off"] = True
    save_json(DATA_FILES["settings"], settings)
    bot.send_message(message.chat.id, "⚠️ Bot turned OFF.\nUsers will see OFF message.")

@bot.message_handler(commands=["onbot"])
def cmd_onbot(message):
    if not is_admin(message.from_user.id):
        return

    settings["bot_off"] = False
    save_json(DATA_FILES["settings"], settings)
    bot.send_message(message.chat.id, "✨ Bot is now LIVE again!")


# ============================================
# /setoffer — Set Mega Offer (62, 33)
# ============================================
@bot.message_handler(commands=["setoffer"])
def cmd_setoffer(message):
    if not is_admin(message.from_user.id):
        return

    chat_id = message.chat.id
    bot.send_message(chat_id, "🎁 Send new Mega Offer text:")
    user_states[message.from_user.id] = "await_mega_offer"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_mega_offer")
def handle_setoffer_text(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    offer_text = message.text.strip()
    settings["mega_offer"] = offer_text
    save_json(DATA_FILES["settings"], settings)

    bot.send_message(message.chat.id, "🎁 Mega Offer updated!", reply_markup=main_menu_keyboard())
    user_states[uid] = "main_menu"


# ============================================
# /addtutorial — Add Tutorial Section (59)
# /removetutorial — Remove Tutorial (60)
# ============================================
@bot.message_handler(commands=["addtutorial"])
def cmd_addtutorial(message):
    if not is_admin(message.from_user.id):
        return

    bot.send_message(message.chat.id, "📚 Send tutorial text or video link:")
    user_states[message.from_user.id] = "await_tutorial_text"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_tutorial_text")
def handle_addtutorial_text(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    tutorial_text = message.text.strip()
    settings["tutorial"] = tutorial_text
    save_json(DATA_FILES["settings"], settings)

    bot.send_message(message.chat.id, "📚 Tutorial added!", reply_markup=main_menu_keyboard())
    user_states[uid] = "main_menu"


@bot.message_handler(commands=["removetutorial"])
def cmd_removetutorial(message):
    if not is_admin(message.from_user.id):
        return

    settings["tutorial"] = ""
    save_json(DATA_FILES["settings"], settings)
    bot.send_message(message.chat.id, "❌ Tutorial removed successfully.")


# ============================================
# /editwelcomesms — Edit /start Message Text (57)
# NOTE: ekhane save korbo, pore /start e use korte chaile manually integrate korte parba
# ============================================
@bot.message_handler(commands=["editwelcomesms"])
def cmd_editwelcomesms(message):
    if not is_admin(message.from_user.id):
        return

    bot.send_message(message.chat.id, "✨ Send new welcome message (/start):")
    user_states[message.from_user.id] = "await_welcome_sms"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_welcome_sms")
def handle_editwelcomesms_text(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    txt = message.text
    settings["welcome_sms"] = txt
    save_json(DATA_FILES["settings"], settings)
    bot.send_message(message.chat.id, "✨ Welcome SMS updated!", reply_markup=main_menu_keyboard())
    user_states[uid] = "main_menu"


# ============================================
# /genaretcupun — Coupon Generator Panel (61, 30–32)
# ============================================
@bot.message_handler(commands=["genaretcupun"])
def cmd_genaretcupun(message):
    if not is_admin(message.from_user.id):
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("🎯 Single Product Coupon"))
    kb.add(types.KeyboardButton("🌍 All Product Coupon"))
    kb.add(types.KeyboardButton("⬅ Back"))
    bot.send_message(
        message.chat.id,
        "🎟 COUPON GENERATOR\n\n🎯 Single Product\n🌍 All Products\n⬅ Back",
        reply_markup=kb
    )
    user_states[message.from_user.id] = "coupon_menu"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "coupon_menu")
def handle_coupon_menu(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    txt = message.text

    if not is_admin(uid):
        return

    if txt == "🎯 Single Product Coupon":
        bot.send_message(
            chat_id,
            "Send coupon in format:\n\ndiscount | DD-MM-YYYY HH:MM\n\nExample:\n150 | 30-12-2025 11:59"
        )
        user_states[uid] = "coupon_single"
    elif txt == "🌍 All Product Coupon":
        bot.send_message(
            chat_id,
            "Send base coupon in format:\n\ndiscount | DD-MM-YYYY HH:MM\n\nExample:\n150 | 30-12-2025 11:59"
        )
        user_states[uid] = "coupon_all_base"
    elif txt == "⬅ Back":
        bot.send_message(chat_id, "Back to Admin Panel.", reply_markup=main_menu_keyboard())
        user_states[uid] = "main_menu"


# SINGLE PRODUCT COUPON
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "coupon_single")
def handle_coupon_single(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) != 2:
        bot.send_message(chat_id, "❌ Invalid format. Use:\n\ndiscount | DD-MM-YYYY HH:MM")
        return

    discount_str, expiry_str = parts
    try:
        discount = int(discount_str)
        datetime.strptime(expiry_str, "%d-%m-%Y %H:%M")
    except Exception:
        bot.send_message(chat_id, "❌ Invalid discount or date format.")
        return

    # Simple random-like code
    code = f"POWER-{discount}-POINT{len(coupons)+1000}-BREAK"
    coupons[code] = {
        "discount": discount,
        "product_id": "chatgpt_plus_1m",  # single product for now
        "expires": expiry_str,
        "used": False
    }
    save_json(DATA_FILES["coupons"], coupons)

    bot.send_message(
        chat_id,
        f"🎟 SINGLE PRODUCT COUPON GENERATED:\n\n{code}\n\nOne-time use only.",
        reply_markup=main_menu_keyboard()
    )
    user_states[uid] = "main_menu"


# ALL PRODUCT COUPON (Base: discount | date) → Then quantity
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "coupon_all_base")
def handle_coupon_all_base(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) != 2:
        bot.send_message(chat_id, "❌ Invalid format. Use:\n\ndiscount | DD-MM-YYYY HH:MM")
        return

    discount_str, expiry_str = parts
    try:
        discount = int(discount_str)
        datetime.strptime(expiry_str, "%d-%m-%Y %H:%M")
    except Exception:
        bot.send_message(chat_id, "❌ Invalid discount or date format.")
        return

    pending_data[uid] = {
        "coupon_discount": discount,
        "coupon_expiry": expiry_str
    }
    bot.send_message(chat_id, "Now send quantity (1–10000):")
    user_states[uid] = "coupon_all_qty"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "coupon_all_qty")
def handle_coupon_all_qty(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    try:
        qty = int(message.text.strip())
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid quantity. Send a number 1–10000.")
        return

    if qty < 1 or qty > 10000:
        bot.send_message(chat_id, "❌ Quantity must be between 1 and 10000.")
        return

    base = pending_data.get(uid, {})
    discount = base.get("coupon_discount")
    expiry = base.get("coupon_expiry")

    if discount is None or expiry is None:
        bot.send_message(chat_id, "⚠ Session expired. Please start again: /genaretcupun")
        user_states[uid] = "main_menu"
        return

    generated_codes = []
    start_index = len(coupons) + 1000

    for i in range(qty):
        code = f"POWER-{discount}-POINT{start_index + i}-BREAK"
        coupons[code] = {
            "discount": discount,
            "product_id": "ALL",
            "expires": expiry,
            "used": False
        }
        generated_codes.append(code)

    save_json(DATA_FILES["coupons"], coupons)
    pending_data.pop(uid, None)

    msg = "🎟 ALL PRODUCT COUPONS GENERATED:\n\n"
    for c in generated_codes[:10]:
        msg += f"{c}\n"
    if qty > 10:
        msg += f"\n...and {qty - 10} more.\n"

    msg += "\nValid for ALL products\nOne-time use\nNever regenerated again."

    bot.send_message(chat_id, msg, reply_markup=main_menu_keyboard())
    user_states[uid] = "main_menu"



# ============================================
# PART 5 — Users / Orders / Category / Product / Stock / Broadcast / Reset / ChannelLink
# ============================================

# ========== /users — All Users List (54) ==========
@bot.message_handler(commands=["users"])
def cmd_users(message):
    if not is_admin(message.from_user.id):
        return

    chat_id = message.chat.id
    if not users:
        bot.send_message(chat_id, "⚠️ No users found.")
        return

    lines = ["📋 ALL USERS LIST:\n"]
    for i, (uid_str, u) in enumerate(users.items(), start=1):
        lines.append(
            f"{i}. {u.get('name','User')} | @{u.get('username','Unknown')} | ID: {uid_str} | Joined: {u.get('joined','N/A')}"
        )
        if i >= 50:
            lines.append("\n⚠️ Showing first 50 users only.")
            break

    bot.send_message(chat_id, "\n".join(lines))


# ========== /allsellhistory — Completed Sell History (50) ==========
@bot.message_handler(commands=["allsellhistory"])
def cmd_allsellhistory(message):
    if not is_admin(message.from_user.id):
        return

    chat_id = message.chat.id
    completed = [o for o in orders.values() if o.get("status") == "APPROVED"]
    if not completed:
        bot.send_message(chat_id, "⚠️ No sell history found.")
        return

    lines = ["📊 COMPLETED SELL HISTORY:\n"]
    for o in completed[:50]:
        lines.append(
            f"Order ID: {o['order_id']} | @{o.get('username','User')} | {o.get('product')} | ৳{o.get('payable')} | {o.get('method')} | {o.get('created_at')}"
        )
    if len(completed) > 50:
        lines.append("\n⚠️ Showing first 50 completed orders only.")

    bot.send_message(chat_id, "\n".join(lines))


# ========== /allorderhistory — All Order History (51) ==========
@bot.message_handler(commands=["allorderhistory"])
def cmd_allorderhistory(message):
    if not is_admin(message.from_user.id):
        return

    chat_id = message.chat.id
    if not orders:
        bot.send_message(chat_id, "⚠️ No order history found.")
        return

    lines = ["📜 ALL ORDER HISTORY:\n"]
    for o in list(orders.values())[:50]:
        lines.append(
            f"{o['order_id']} | @{o.get('username','User')} | {o.get('product')} | ৳{o.get('payable')} | {o.get('status')} | {o.get('created_at')}"
        )
    if len(orders) > 50:
        lines.append("\n⚠️ Showing first 50 orders only.")

    bot.send_message(chat_id, "\n".join(lines))


# ========== /pendingorders — All Pending Orders (52) ==========
@bot.message_handler(commands=["pendingorders"])
def cmd_pendingorders(message):
    if not is_admin(message.from_user.id):
        return

    chat_id = message.chat.id
    pending_list = [o for o in orders.values() if o.get("status") == "PENDING"]
    if not pending_list:
        bot.send_message(chat_id, "⚠️ No pending orders.")
        return

    lines = ["⏳ PENDING ORDERS:\n"]
    for o in pending_list[:50]:
        lines.append(
            f"{o['order_id']} | @{o.get('username','User')} | {o.get('product')} | ৳{o.get('payable')} | TXID: {o.get('txid')}"
        )
    if len(pending_list) > 50:
        lines.append("\n⚠️ Showing first 50 pending orders only.")

    bot.send_message(chat_id, "\n".join(lines))


# ========== /completedorders — Approved/Completed Orders (53) ==========
@bot.message_handler(commands=["completedorders"])
def cmd_completedorders(message):
    if not is_admin(message.from_user.id):
        return

    chat_id = message.chat.id
    completed = [o for o in orders.values() if o.get("status") == "APPROVED"]
    if not completed:
        bot.send_message(chat_id, "⚠️ No completed orders.")
        return

    lines = ["✅ COMPLETED ORDERS:\n"]
    for o in completed[:50]:
        lines.append(
            f"{o['order_id']} | @{o.get('username','User')} | {o.get('product')} | ৳{o.get('payable')} | Delivered"
        )
    if len(completed) > 50:
        lines.append("\n⚠️ Showing first 50 completed orders only.")

    bot.send_message(chat_id, "\n".join(lines))


# ========== /senduser — Message to Specific User (55) ==========
@bot.message_handler(commands=["senduser"])
def cmd_senduser(message):
    if not is_admin(message.from_user.id):
        return

    bot.send_message(message.chat.id, "Send Username or User ID to message:")
    user_states[message.from_user.id] = "await_senduser_target"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_senduser_target")
def handle_senduser_target(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    target = message.text.strip().replace("@", "")
    pending_data[uid] = {"senduser_target": target}
    bot.send_message(chat_id, "Now send the message to deliver:")
    user_states[uid] = "await_senduser_message"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_senduser_message")
def handle_senduser_message(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    ctx = pending_data.get(uid, {})
    target = ctx.get("senduser_target")
    if not target:
        bot.send_message(chat_id, "⚠ Session expired.")
        user_states[uid] = "main_menu"
        return

    # find by username or id
    target_id = None
    for u_id_str, u in users.items():
        if str(u["id"]) == target or u.get("username","").lower() == target.lower():
            target_id = int(u_id_str)
            break

    if not target_id:
        bot.send_message(chat_id, "❌ User not found.")
        user_states[uid] = "main_menu"
        pending_data.pop(uid, None)
        return

    text_to_send = message.text
    try:
        bot.send_message(target_id, text_to_send)
        bot.send_message(chat_id, "📨 Message delivered!", reply_markup=main_menu_keyboard())
    except Exception:
        bot.send_message(chat_id, "❌ Failed to send message.")

    user_states[uid] = "main_menu"
    pending_data.pop(uid, None)


# ========== /broadcast — Message to All Users (56) ==========
@bot.message_handler(commands=["broadcast"])
def cmd_broadcast(message):
    if not is_admin(message.from_user.id):
        return

    bot.send_message(message.chat.id, "Send broadcast message:")
    user_states[message.from_user.id] = "await_broadcast_message"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_broadcast_message")
def handle_broadcast_message(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    text_to_send = message.text
    total = len(users)
    sent = 0

    for u_id_str in users.keys():
        try:
            bot.send_message(int(u_id_str), text_to_send)
            sent += 1
        except Exception:
            continue

    bot.send_message(chat_id, f"📢 Broadcast completed!\nSent: {sent}/{total}")
    user_states[uid] = "main_menu"


# ========== /badge — Assign User Badge (47) ==========
@bot.message_handler(commands=["badge"])
def cmd_badge(message):
    if not is_admin(message.from_user.id):
        return

    bot.send_message(message.chat.id, "Send Username or User ID to set badge:")
    user_states[message.from_user.id] = "await_badge_user"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_badge_user")
def handle_badge_user(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    target = message.text.strip().replace("@","")
    target_id = None
    for u_id_str, u in users.items():
        if str(u["id"]) == target or u.get("username","").lower() == target.lower():
            target_id = u_id_str
            break

    if not target_id:
        bot.send_message(chat_id, "❌ User not found.")
        user_states[uid] = "main_menu"
        return

    pending_data[uid] = {"badge_user": target_id}
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        types.KeyboardButton("VIP"),
        types.KeyboardButton("VIP MAX"),
        types.KeyboardButton("Premium"),
        types.KeyboardButton("Trusted Buyer")
    )
    bot.send_message(chat_id, "Choose badge:", reply_markup=kb)
    user_states[uid] = "await_badge_choice"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_badge_choice")
def handle_badge_choice(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    badge = message.text
    if badge not in ["VIP", "VIP MAX", "Premium", "Trusted Buyer"]:
        bot.send_message(chat_id, "❌ Invalid badge.")
        return

    ctx = pending_data.get(uid, {})
    target_id_str = ctx.get("badge_user")
    if not target_id_str or target_id_str not in users:
        bot.send_message(chat_id, "⚠ Session expired.")
        user_states[uid] = "main_menu"
        return

    users[target_id_str]["badge"] = badge
    save_json(DATA_FILES["users"], users)

    bot.send_message(chat_id, f"👑 Badge updated successfully! ({badge})", reply_markup=main_menu_keyboard())
    pending_data.pop(uid, None)
    user_states[uid] = "main_menu"


# ========== CATEGORY MANAGEMENT (add/remove) ==========
@bot.message_handler(commands=["addcategory"])
def cmd_addcategory(message):
    if not is_admin(message.from_user.id):
        return

    bot.send_message(message.chat.id, "Send new category name (with emoji):")
    user_states[message.from_user.id] = "await_add_category"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_add_category")
def handle_addcategory(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    name = message.text.strip()
    if not name:
        bot.send_message(chat_id, "❌ Category name cannot be empty.")
        return

    if name in categories["list"]:
        bot.send_message(chat_id, "⚠️ This category already exists.")
    else:
        categories["list"].append(name)
        save_json(DATA_FILES["categories"], categories)
        bot.send_message(chat_id, f"✅ Category added: {name}")

    user_states[uid] = "main_menu"


@bot.message_handler(commands=["removecategory"])
def cmd_removecategory(message):
    if not is_admin(message.from_user.id):
        return

    text = "Send category name to remove. Available:\n\n" + "\n".join(categories.get("list", []))
    bot.send_message(message.chat.id, text)
    user_states[message.from_user.id] = "await_remove_category"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_remove_category")
def handle_removecategory(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    name = message.text.strip()
    if name in categories["list"]:
        categories["list"].remove(name)
        save_json(DATA_FILES["categories"], categories)
        bot.send_message(chat_id, f"❌ Category removed: {name}")
    else:
        bot.send_message(chat_id, "⚠️ Category not found.")

    user_states[uid] = "main_menu"


# ========== PRODUCT MANAGEMENT (add/remove) ==========
def slugify(text):
    return text.lower().replace(" ", "_").replace("—", "_").replace("-", "_")


@bot.message_handler(commands=["addproduct"])
def cmd_addproduct(message):
    if not is_admin(message.from_user.id):
        return

    text = (
        "Send product info in format:\n\n"
        "Name | Category | DurationDays | Price\n\n"
        "Example:\n"
        "ChatGPT Plus — 1 Month | 🤖 ChatGPT & AI | 30 | 499"
    )
    bot.send_message(message.chat.id, text)
    user_states[message.from_user.id] = "await_add_product"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_add_product")
def handle_addproduct(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) != 4:
        bot.send_message(chat_id, "❌ Invalid format. Try again.")
        return

    name, category, duration_str, price_str = parts
    try:
        duration = int(duration_str)
        price = int(price_str)
    except ValueError:
        bot.send_message(chat_id, "❌ Duration and price must be numbers.")
        return

    pid = slugify(name)
    products[pid] = {
        "id": pid,
        "name": name,
        "category": category,
        "duration_days": duration,
        "price": price,
        "stock": 0
    }
    save_json(DATA_FILES["products"], products)

    bot.send_message(chat_id, f"✅ Product added: {name}", reply_markup=main_menu_keyboard())
    user_states[uid] = "main_menu"


@bot.message_handler(commands=["removeproduct"])
def cmd_removeproduct(message):
    if not is_admin(message.from_user.id):
        return

    text = "Send product name or ID to remove.\n\nExisting products:\n"
    for p in products.values():
        text += f"- {p.get('name')} (ID: {p.get('id')})\n"

    bot.send_message(message.chat.id, text)
    user_states[message.from_user.id] = "await_remove_product"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_remove_product")
def handle_removeproduct(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    val = message.text.strip()
    target_id = None

    for pid, p in products.items():
        if p.get("name") == val or pid == val:
            target_id = pid
            break

    if not target_id:
        bot.send_message(chat_id, "⚠️ Product not found.")
    else:
        products.pop(target_id, None)
        stocks.pop(target_id, None)
        save_json(DATA_FILES["products"], products)
        save_json(DATA_FILES["stocks"], stocks)
        bot.send_message(chat_id, "❌ Product and its stock removed.")

    user_states[uid] = "main_menu"


# ========== STOCK MANAGEMENT (addstock / removestoke) ==========
@bot.message_handler(commands=["addstock"])
def cmd_addstock(message):
    if not is_admin(message.from_user.id):
        return

    text = (
        "Send stock in format:\n\n"
        "ProductNameOrID | email | password\n\n"
        "Example:\n"
        "ChatGPT Plus — 1 Month | accdemo@gmail.com | Abcd12345"
    )
    bot.send_message(message.chat.id, text)
    user_states[message.from_user.id] = "await_add_stock"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_add_stock")
def handle_addstock(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) != 3:
        bot.send_message(chat_id, "❌ Invalid format.")
        return

    prod_val, email, password = parts
    pid = None
    for p_id, p in products.items():
        if p.get("name") == prod_val or p_id == prod_val:
            pid = p_id
            break

    if not pid:
        bot.send_message(chat_id, "⚠️ Product not found.")
        return

    stock_list = stocks.get(pid, [])
    stock_list.append({"email": email, "password": password})
    stocks[pid] = stock_list
    products[pid]["stock"] = len(stock_list)
    save_json(DATA_FILES["stocks"], stocks)
    save_json(DATA_FILES["products"], products)

    bot.send_message(chat_id, "✅ Stock item added.", reply_markup=main_menu_keyboard())
    user_states[uid] = "main_menu"


@bot.message_handler(commands=["removestoke"])
def cmd_removestoke(message):
    if not is_admin(message.from_user.id):
        return

    text = "Send product name or ID to view and remove stock items."
    bot.send_message(message.chat.id, text)
    user_states[message.from_user.id] = "await_removestoke_product"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_removestoke_product")
def handle_removestoke_product(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    val = message.text.strip()
    pid = None
    for p_id, p in products.items():
        if p.get("name") == val or p_id == val:
            pid = p_id
            break

    if not pid:
        bot.send_message(chat_id, "⚠️ Product not found.")
        user_states[uid] = "main_menu"
        return

    stock_list = stocks.get(pid, [])
    if not stock_list:
        bot.send_message(chat_id, "📛 No stock available")
        user_states[uid] = "main_menu"
        return

    lines = ["Stock items:\n"]
    for i, s in enumerate(stock_list, start=1):
        lines.append(f"{i}. {s.get('email')} | {s.get('password')}")
    lines.append("\nSend stock number to remove (e.g., 1):")
    bot.send_message(chat_id, "\n".join(lines))

    pending_data[uid] = {"removestoke_pid": pid}
    user_states[uid] = "await_removestoke_index"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_removestoke_index")
def handle_removestoke_index(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    ctx = pending_data.get(uid, {})
    pid = ctx.get("removestoke_pid")
    if not pid:
        bot.send_message(chat_id, "⚠ Session expired.")
        user_states[uid] = "main_menu"
        return

    try:
        index = int(message.text.strip())
    except ValueError:
        bot.send_message(chat_id, "❌ Invalid stock ID.")
        return

    stock_list = stocks.get(pid, [])
    if index < 1 or index > len(stock_list):
        bot.send_message(chat_id, "❌ Invalid stock ID.")
        return

    stock_list.pop(index - 1)
    stocks[pid] = stock_list
    products[pid]["stock"] = len(stock_list)
    save_json(DATA_FILES["stocks"], stocks)
    save_json(DATA_FILES["products"], products)

    bot.send_message(chat_id, "❌ Stock item removed.", reply_markup=main_menu_keyboard())
    pending_data.pop(uid, None)
    user_states[uid] = "main_menu"


# ========== /reset — System Reset (66, super admin only) ==========
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    if not is_superadmin(message.from_user.id):
        return

    bot.send_message(
        message.chat.id,
        "⚠️ Are you sure you want to reset system temp data?\n\n"
        "This will clear:\n"
        "• Pending orders flags\n"
        "• Notify counters\n"
        "• Some runtime caches\n\n"
        "But will NOT remove:\n"
        "• Users\n"
        "• Stock\n"
        "• Orders history\n"
        "• Products\n"
        "• Categories\n\n"
        "Reply: YES to confirm, anything else to cancel."
    )
    user_states[message.from_user.id] = "await_reset_confirm"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_reset_confirm")
def handle_reset_confirm(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_superadmin(uid):
        return

    if message.text.strip().upper() == "YES":
        # clear runtime only
        global notify_stats
        notify_stats = {}
        # pending orders flag reset: not strictly needed, but you can adjust if you want
        bot.send_message(chat_id, "🔄 System reset successfully.")
    else:
        bot.send_message(chat_id, "❌ Reset cancelled.")

    user_states[uid] = "main_menu"


# ========== /addChanelOrGroupLink — Add Channel/Group Link or Username (36, 67) ==========
@bot.message_handler(commands=["addChanelOrGroupLink"])
def cmd_addChanelOrGroupLink(message):
    if not is_admin(message.from_user.id):
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📎 Add Channel/Group Link"))
    kb.add(types.KeyboardButton("👤 Add Username"))
    kb.add(types.KeyboardButton("❌ Cancel"))
    bot.send_message(
        message.chat.id,
        "📌 What do you want to add?\nChoose option:",
        reply_markup=kb
    )
    user_states[message.from_user.id] = "await_channel_link_menu"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_channel_link_menu")
def handle_channel_link_menu(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    txt = message.text
    if txt == "📎 Add Channel/Group Link":
        bot.send_message(chat_id, "🔗 Please send new Channel / Group link…")
        user_states[uid] = "await_new_channel_link"
    elif txt == "👤 Add Username":
        bot.send_message(chat_id, "👤 Please send new username…")
        user_states[uid] = "await_new_channel_username"
    elif txt == "❌ Cancel":
        bot.send_message(chat_id, "❌ Operation cancelled", reply_markup=main_menu_keyboard())
        user_states[uid] = "main_menu"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) in ["await_new_channel_link", "await_new_channel_username"])
def handle_channel_link_set(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(uid):
        return

    state = user_states.get(uid)
    if state == "await_new_channel_link":
        settings["channel_or_group_link"] = message.text.strip()
        save_json(DATA_FILES["settings"], settings)
        bot.send_message(chat_id, "✅ Saved Successfully!", reply_markup=main_menu_keyboard())
        user_states[uid] = "main_menu"
    elif state == "await_new_channel_username":
        settings["channel_or_group_username"] = message.text.strip()
        save_json(DATA_FILES["settings"], settings)
        bot.send_message(chat_id, "✅ Username Saved Successfully!", reply_markup=main_menu_keyboard())
        user_states[uid] = "main_menu"


# ============================================
# PART 6 — Notify Admin System (28) + Admin / Super Admin Management (37–38)
# ============================================

# Runtime notify stats: user+order wise
notify_stats = {}


# ========== /notifyadmin — Notify Admin (28) ==========
@bot.message_handler(commands=["notifyadmin"])
def cmd_notifyadmin(message):
    uid = message.from_user.id
    chat_id = message.chat.id

    if not is_registered(message):
        bot.send_message(chat_id, "❌ No account found. Please Sign Up using /openstore.")
        return

    # user-er pending orders theke latest ta niye kaj korbo
    pending_list = [
        o for o in orders.values()
        if o.get("user_id") == uid and o.get("status") == "PENDING"
    ]

    if not pending_list:
        bot.send_message(chat_id, "⏳ You have no pending orders.")
        return

    # latest order choose (order id numeric part diye sort kore)
    pending_list.sort(key=lambda o: int(str(o["order_id"]).split("-")[1]))
    order = pending_list[-1]
    order_id = order["order_id"]

    key = f"{uid}:{order_id}"
    data = notify_stats.get(key, {"count": 0, "last": 0})
    from_time = data.get("last", 0)

    now_ts = datetime.now().timestamp()

    # 3 bar er beshi hole
    if data["count"] >= 3:
        bot.send_message(chat_id, "🚫 No more notifications left.")
        return

    # 1 ghontar moddhe abar dile
    if from_time and (now_ts - from_time) < 3600:
        bot.send_message(chat_id, "⏳ You must wait 1 hour.")
        return

    # valid notify
    data["count"] += 1
    data["last"] = now_ts
    notify_stats[key] = data

    # user-ke confirm msg
    bot.send_message(chat_id, "🔔 Notification sent.")

    # admin group-e reminder msg
    username = order.get("username", "User")
    admin_text = (
        f"🔔 USER REMINDER — User @{username} reminded about Order ID: {order_id}"
    )
    try:
        bot.send_message(ORDER_LOG_CHAT_ID, admin_text)
    except Exception:
        pass


# ============================================
# ADMIN / SUPER ADMIN MANAGEMENT (37–38)
# ============================================

# /addadmin — Add New Admin (Main/Super Admin only)
@bot.message_handler(commands=["addadmin"])
def cmd_addadmin(message):
    if not is_superadmin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Permission denied")
        return

    bot.send_message(message.chat.id, "Please send Username or User ID of new admin:")
    user_states[message.from_user.id] = "await_add_admin_user"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_add_admin_user")
def handle_addadmin_user(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_superadmin(uid):
        return

    target = message.text.strip().replace("@", "")
    target_id = None
    target_username = None

    for u_id_str, u in users.items():
        if str(u["id"]) == target or u.get("username", "").lower() == target.lower():
            target_id = u_id_str
            target_username = u.get("username", "Unknown")
            break

    if not target_id:
        bot.send_message(chat_id, "❌ Invalid user")
        user_states[uid] = "main_menu"
        return

    # already super admin?
    if target_id in superadmins:
        bot.send_message(chat_id, "⚠️ User already admin")
        user_states[uid] = "main_menu"
        return

    # already admin?
    if target_id in admins:
        bot.send_message(chat_id, "⚠️ User already admin")
        user_states[uid] = "main_menu"
        return

    admins[target_id] = {
        "username": f"@{target_username}",
        "added_at": datetime.now().strftime("%d-%b-%Y | %I:%M %p")
    }
    save_json(DATA_FILES["admins"], admins)

    bot.send_message(chat_id, f"✅ Admin added: @{target_username}")
    user_states[uid] = "main_menu"


# /removeadmin — Remove Admin (Main/Super Admin only)
@bot.message_handler(commands=["removeadmin"])
def cmd_removeadmin(message):
    if not is_superadmin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Permission denied")
        return

    bot.send_message(message.chat.id, "Send Username/User ID to remove:")
    user_states[message.from_user.id] = "await_remove_admin_user"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_remove_admin_user")
def handle_removeadmin_user(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_superadmin(uid):
        return

    target = message.text.strip().replace("@", "")
    target_id = None
    target_username = None

    for u_id_str, u in users.items():
        if str(u["id"]) == target or u.get("username", "").lower() == target.lower():
            target_id = u_id_str
            target_username = u.get("username", "Unknown")
            break

    if not target_id:
        bot.send_message(chat_id, "⚠️ This user is not an admin")
        user_states[uid] = "main_menu"
        return

    # main admin ke remove korte dibo na
    if int(target_id) == MAIN_ADMIN_ID:
        bot.send_message(chat_id, "❌ Cannot remove Main Admin")
        user_states[uid] = "main_menu"
        return

    if target_id not in admins:
        bot.send_message(chat_id, "⚠️ This user is not an admin")
        user_states[uid] = "main_menu"
        return

    admins.pop(target_id, None)
    save_json(DATA_FILES["admins"], admins)

    bot.send_message(chat_id, "❌ Admin removed successfully!")
    user_states[uid] = "main_menu"


# /addsupperaddmin — Add Super Admin (Super Admin only)
@bot.message_handler(commands=["addsupperaddmin"])
def cmd_addsupperaddmin(message):
    if not is_superadmin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Permission denied")
        return

    bot.send_message(message.chat.id, "Send Username/User ID to make Super Admin:")
    user_states[message.from_user.id] = "await_add_superadmin_user"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_add_superadmin_user")
def handle_addsupperadmin_user(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_superadmin(uid):
        return

    target = message.text.strip().replace("@", "")
    target_id = None
    target_username = None

    for u_id_str, u in users.items():
        if str(u["id"]) == target or u.get("username", "").lower() == target.lower():
            target_id = u_id_str
            target_username = u.get("username", "Unknown")
            break

    if not target_id:
        bot.send_message(chat_id, "❌ Invalid Username")
        user_states[uid] = "main_menu"
        return

    if target_id in superadmins:
        bot.send_message(chat_id, "⚠️ Already Super Admin")
        user_states[uid] = "main_menu"
        return

    superadmins[target_id] = {
        "username": f"@{target_username}",
        "added_at": datetime.now().strftime("%d-%b-%Y | %I:%M %p")
    }
    save_json(DATA_FILES["superadmins"], superadmins)

    # optionally admin list eo rakhte chao
    admins[target_id] = {
        "username": f"@{target_username}",
        "added_at": datetime.now().strftime("%d-%b-%Y | %I:%M %p")
    }
    save_json(DATA_FILES["admins"], admins)

    bot.send_message(chat_id, "👑 Super Admin added successfully!")
    user_states[uid] = "main_menu"


# /removesuperadmin — Remove Super Admin (Super Admin only)
@bot.message_handler(commands=["removesuperadmin"])
def cmd_removesuperadmin(message):
    if not is_superadmin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Permission denied")
        return

    bot.send_message(message.chat.id, "Send Username/User ID to remove:")
    user_states[message.from_user.id] = "await_remove_superadmin_user"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "await_remove_superadmin_user")
def handle_removesuperadmin_user(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    if not is_superadmin(uid):
        return

    target = message.text.strip().replace("@", "")
    target_id = None
    target_username = None

    for u_id_str, data in superadmins.items():
        uname = data["username"].replace("@", "") if isinstance(data, dict) else str(data).replace("@", "")
        if u_id_str == target or uname.lower() == target.lower():
            target_id = u_id_str
            target_username = uname
            break

    if not target_id:
        bot.send_message(chat_id, "❌ Invalid Username")
        user_states[uid] = "main_menu"
        return

    if len(superadmins.keys()) <= 1:
        bot.send_message(chat_id, "⚠️ You cannot remove the last Super Admin")
        user_states[uid] = "main_menu"
        return

    superadmins.pop(target_id, None)
    save_json(DATA_FILES["superadmins"], superadmins)

    bot.send_message(chat_id, "❌ Super Admin removed!")
    user_states[uid] = "main_menu"


# /adminlist — Full Admin List (38)
@bot.message_handler(commands=["adminlist"])
def cmd_adminlist(message):
    if not is_admin(message.from_user.id):
        return

    lines = ["👥 ADMIN MANAGEMENT PANEL\n"]

    # SUPER ADMINS
    lines.append("\nSUPER ADMINS:\n")
    if superadmins:
        i = 1
        for uid_str, data in superadmins.items():
            if isinstance(data, dict):
                uname = data.get("username", "@Unknown")
                added = data.get("added_at", "Unknown")
            else:
                uname = str(data)
                added = "Unknown"
            lines.append(f"{i}. {uname} — Added on: {added}")
            i += 1
    else:
        lines.append("⚠️ No Super Admins found")

    # ADMINS
    lines.append("\n\nADMINS:\n")
    normal_admins = {k: v for k, v in admins.items() if k not in superadmins}
    if normal_admins:
        i = 1
        for uid_str, data in normal_admins.items():
            if isinstance(data, dict):
                uname = data.get("username", "@Unknown")
                added = data.get("added_at", "Unknown")
            else:
                uname = str(data)
                added = "Unknown"
            lines.append(f"{i}. {uname} — Added on: {added}")
            i += 1
    else:
        lines.append("⚠️ No admins found")

    bot.send_message(message.chat.id, "\n".join(lines))


# ============================================
# BOT RUNNER
# ============================================
if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling()
