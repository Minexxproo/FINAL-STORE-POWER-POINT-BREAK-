import telebot
from telebot import types
from datetime import datetime
from typing import Dict, Any, Optional
import random

# ============ CONFIG ============
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"          # <-- Bot token from BotFather
MAIN_ADMIN_ID = 123456789                  # <-- Your Telegram numeric user ID
ORDER_LOG_CHAT_ID = MAIN_ADMIN_ID          # <-- Admin group/channel ID or same as MAIN_ADMIN_ID
ADMIN_USERNAME = "MinexxProo"              # <-- Main admin username (without @)
SUPPORT_USERNAME = "YourSupportUsername"   # <-- Support admin username (without @)
HOST_TAG = "PowerPointBreak"               # <-- Brand / host tag (without @)
PAYMENT_NUMBER = "01877576843"             # <-- bKash personal number (Send Money)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ============ GLOBAL STATE ============
users: Dict[int, Dict[str, Any]] = {}
orders: Dict[str, Dict[str, Any]] = {}
user_states: Dict[int, str] = {}
pending_payment_ctx: Dict[int, Dict[str, Any]] = {}
coupons: Dict[str, Dict[str, Any]] = {}
tutorial_text: Optional[str] = None
custom_texts: Dict[str, str] = {}

admins: set[int] = set()
super_admins: set[int] = {MAIN_ADMIN_ID}

mega_offer_text: Optional[str] = None
channel_or_group: Dict[str, str] = {}
notify_stats: Dict[int, Dict[str, Any]] = {}

products_info: Dict[str, Dict[str, Any]] = {
    "ChatGPT Plus — 1 Month": {
        "price": 499,
        "duration": "30 Days",
        "stock_limit": None,
        "stocks": []  # each: {"email": "...", "password": "..."}
    }
}

categories = [
    "🤖 ChatGPT & AI",
    "▶️ YouTube Premium",
    "🎵 Spotify Premium",
    "🎬 Netflix",
    "🔒 VPN & Security",
    "👨‍💻 Developer Tools",
    "🧩 Office 365",
    "🎮 Gaming / Combo",
]

_next_order_id = 1000
bot_off = False


def new_order_id() -> str:
    global _next_order_id
    _next_order_id += 1
    return f"CG-{_next_order_id}"


# ============ DEMO TEXTS 1–40 ============
DEMO_TEXTS: Dict[int, str] = {
    1: """🟥 1) /start — Welcome Screen

┏━━━━━━━━━━━━━━━━━━━━━━┓
⭐⚡ POWER POINT BREAK PREMIUM STORE ⚡⭐
┗━━━━━━━━━━━━━━━━━━━━━━┛

👋 Welcome {FullName}!

This is POWER POINT BREAK PREMIUM STORE
💎 Premium Accounts • 💰 Lowest Price • ⚡ Fast Delivery • 🔒 Secure Service

👉 Enter Store:
/openstore

👤 User Info:
🆔 User ID: {user_id}
🔗 Username: @{username}

📞 Support: @YourSupportUsername
🏷 Hosted by: @PowerPointBreak""",

    2: """🟥 2) /openstore — Registration Gate

If user NOT registered:

🔐 ACCOUNT REQUIRED
To access the store, please Sign Up or Log In.

Buttons:
🆕 Sign Up
🔓 Log In

If already registered → MAIN MENU 🏠""",

    3: """🟥 3) SIGN UP FLOW

📝 SIGN UP

Name: {FullName}
Username: @{username}
User ID: {user_id}

Buttons:
✅ Confirm Sign Up
❌ Cancel

If Confirmed →
✅ Account created!

If Cancel →
❌ Sign Up cancelled.
Use /openstore again.""",

    4: """🟥 4) LOG IN FLOW

If registered:
🔓 Welcome back, {FullName}!
Tap MAIN MENU to continue.

If not registered:
❌ No account found. Please Sign Up.""",

    5: """🟥 5) MAIN MENU (Reply Keyboard)

🛒 All Categories      🪪 My Profile
🛍 Active Orders       📦 My Orders
⏳ Pending Orders      🆘 Help Center
📚 Tutorial            🎁 Mega Offer""",

    6: """🟥 6) ALL CATEGORIES (Back Button Added)

📂 SELECT A CATEGORY

🤖 ChatGPT & AI      ▶️ YouTube Premium      🎵 Spotify Premium
🎬 Netflix           🔒 VPN & Security       👨‍💻 Developer Tools
🧩 Office 365        🎮 Gaming / Combo
⬅ Back

Back → returns to Main Menu""",

    7: """🟥 7) PRODUCT LIST — ChatGPT & AI (Back Button Added)

🛍 CATEGORY: ChatGPT & AI

🤖 ChatGPT Plus — 1 Month
🤖 ChatGPT Plus — 3 Months
🚀 GPT-4 Team Access
⬅ Back

Back → returns to All Categories (6)""",

    8: """🟥 8) PRODUCT DETAILS PAGE (Back Button Added)

┏━━━━━━━━━━━━━━━━━━━━━━┓
🤖 CHATGPT PLUS — 1 MONTH
┗━━━━━━━━━━━━━━━━━━━━━━┛

⏳ Duration: 30 Days
💰 Price: ৳499
📊 Stock: 7 Available

⭐ Benefits:
• GPT-4 Full Access
• Ultra Fast Speed
• Priority Server

Buttons:
🛒 Buy Now
🎟 Apply Coupon
⬅ Back

If stock = 0 →
📛 OUT OF STOCK

Back → returns to Product List (7)""",

    9: """🟥 9) COUPON MENU (Back Button Added)

🎟 APPLY COUPON

Invalid → ❌ INVALID COUPON
Expired → ⏳ EXPIRED
Used → 🛑 ALREADY USED
Wrong Product → 🚫 NOT VALID

Valid Coupon →

🎉 COUPON APPLIED SUCCESSFULLY! 🎉

Coupon: {code}
💵 Discount: ৳{discount}
💰 Original Price: ৳{original}
✅ Payable: ৳{final}

Full-Free Coupon →
💚 Payable: 0
⚡ Auto-delivery enabled.

⬅ Back

Back → returns to Product Details (8)""",

    10: """🟥 10) BUY NOW → PAYMENT METHOD (Back Button Added)

💳 PAYMENT METHOD

You're buying:
🛒 ChatGPT Plus — 1 Month
💰 Payable Amount: ৳499

Select Payment:

🟣 bKash
🟡 Nagad
🟠 Upay
🔵 Rocket
🪙 Crypto (USDT)
⬅ Back

Back → returns to Product Details (8)""",

    11: """🟥 11) PAYMENT PAGE — bKash Example (Back Button Added)

🟣 BKASH PAYMENT

You're purchasing:
🛒 ChatGPT Plus — 1 Month

💰 Original Price: ৳499
🎟 Coupon: {if-any}
💵 Discount: {if-any}
✅ Payable: ৳499

Send Money to:
📲 01877576843 (bKash Personal)

⚠ RULES:
👉 Only Send Money allowed
❌ Mobile Recharge NOT accepted

Send info in format:
Sender | Amount | TXID

Example:
01811112222 | 499 | TX9L92QE0

⬅ Back

Back → returns to Payment Method (10)""",

    12: """🟥 12) PAYMENT PAGE — CRYPTO (Back Button Added)

🪙 CRYPTO USDT PAYMENT

✨ Thank you for choosing us!
💵 We support payments in USDT 👈
🌐 Available Network: All Networks

💰 Available Crypto Platforms:
• Binance
• Bybit

🛡️ Safe, fast & verified.
⚡ Processing is quick.
📞 Support always available.

📩 Crypto Payment Please Contract Admin: 👉 @MinexxProo

⬅ Back

Back → returns to Payment Method (10)""",

    13: """🟥 13) FORMAT VALIDATION

Wrong format →
⚠ Invalid Format

Correct format →
✅ Order Confirmed!""",

    14: """🟥 14) ORDER SUBMITTED (FINAL SMS)

🎉 Your order request has been submitted! 🎉

📅 Date/Time: 25-Nov-2025 | 01:28 AM
🧾 Order ID: CG-1001
⏳ Status: Waiting for Admin approval…
(⏳ Pending)

🛒 Product: ChatGPT Plus — 1 Month
💰 Original Price: ৳499
🎟 Coupon: POWER-641-POINT9043-BREAK
💵 Discount: ৳100
✅ Payable Amount: ৳399
👉 Payment Sender Number:

⏱ Estimated Approval Time: 1–15 minutes
📌 Stay online for verification if needed.

📞 Admin Support: @YourSupportUsername
🏷 Hosted by: @PowerPointBreak

❤️ Thank you for choosing Power Point Break! ❤️""",

    15: """🟥 15) ADMIN GROUP — NEW ORDER ALERT (Buttons Added)

📦 NEW ORDER RECEIVED 🔔

Order ID: CG-1001
Username: @username
User ID: 12345678

🛒 Product: ChatGPT Plus — 1 Month
💰 Original Amount: ৳499
🎟 Coupon: POWER-641-POINT9043-BREAK
💵 Discount: ৳100
✅ Final Amount: ৳399

💳 Payment Method: bKash
📲 Sender: 01811112222
🔖 TXID: TX9L92QE0

🕒 Date & Time: {date/time}

Buttons:
✅ Approve
❌ Reject""",

    16: """🟥 16) ADMIN → APPROVE (AUTO DELIVERY SYSTEM)

When admin taps Approve:

✔ Permission check
✔ First stock selected (FIFO)
✔ Stock removed
✔ Order marked APPROVED ✅
✔ Delivery auto-sent
✔ Delivery log saved
✔ Admin panel updated""",

    17: """🟥 17) USER — ORDER APPROVED SMS (UPDATED)

🎉✨ CONGRATULATIONS! ✨🎉
Hello Dear @{Username}, your order has been successfully APPROVED! ✅🚀

Your ChatGPT Plus has been successfully activated! ⚡🔥

🧾 Order Details:
———————————————
📦 Order ID: CG-1001
🛒 Product: ChatGPT Plus — 1 Month
———————————————

🔐 Login Credentials:
📧 Email: accdemo@gmail.com
🔑 Password: Abcd12345

⚠ IMPORTANT INSTRUCTIONS:
• After logging in, please check the account properly
• Enable Two-Factor Authentication immediately
• Do NOT share this account with anyone
• If you face any issue, please report it quickly

📞 Admin Support: 👉 @YourSupportUsername

🌹 Thank you so much for your order! 🌹""",

    18: """🟥 18) ADMIN → REJECT

❌ Your order has been rejected.

Reason: {reason}

⏳ You have 10 minutes to resubmit correctly.

Correct Format:
Sender | Amount | TXID
Example:
01811112222 | 499 | TX9L92QE0""",

    19: """🟥 19) AUTO CANCEL SYSTEM

🚫 Your order has been automatically cancelled
because you didn’t resubmit in time.

For help: @YourSupportUsername""",

    20: """🟥 20) ACTIVE ORDERS

🛍 ACTIVE ORDERS

Order ID: {id}
Product: {product}
Amount: {amount}
⏳ Status: Waiting for Admin Approval""",

    21: """🟥 21) PENDING ORDERS

⏳ MY PENDING ORDERS

Order ID: {id}
Product: {product}
Amount: {amount}
Status: Awaiting Payment Confirmation ⏳""",

    22: """🟥 22) MY ORDERS

📦 MY ORDERS HISTORY

Shows full list including:
• Approved ✅
• Pending ⏳
• Cancelled 🚫
• Date & Time""",

    23: """🟥 23) USER PROFILE

🪪 MY PROFILE

Name: {name}
Username: @{username}
User ID: {id}

Joined: {date}

Total Orders: {total}
Completed: {completed}
Pending: {pending} ⏳

Badge: 👑 VIP MAX
Support: @YourSupportUsername""",

    24: """🟥 24) HELP CENTER

🆘 SUPPORT CENTER

💬 If you have any questions or face any kind of problem,
📩 just message us in the inbox.

🛠️ We are always here and will try our best to solve your issue.
🙏 Thank you so much for staying with us!

👨‍💻 Admin Support: @YourSupportUsername

⚡ Hosted by: POWER POINT BREAK

Response Time: 1–15 minutes ⏱️""",

    25: """🟥 25) TUTORIAL

If added → show tutorial
If none →
📚 No tutorial added yet""",

    26: """🟥 26) BOT OFF MESSAGE

⚠️ Hey dear user, heads up!

🚧 Our Premium Service is temporarily unavailable due to unexpected issues.
🛠️ We’re working super fast to fix everything ASAP.

⏳ Please hold on — your patience means a lot.
🙏 Thank you for staying with us.
💛 We’ll be back stronger!

🏷 Hosted by: @PowerPointBreak
📞 Support: @MinexxProo""",

    27: """🟥 27) BOT ON MESSAGE

✨ Our services are LIVE again! ✨

🚀 You can now place orders anytime.
💛 We always deliver top-quality service.
🙏 Thank you for trusting us!

🌟 Your support means everything! 🌟

🏷 Hosted by: @PowerPointBreak
📞 Admin Support: @MinexxProo""",

    28: """🟥 28) NOTIFY ADMIN SYSTEM

🔔 Notify Admin (3 remaining)

After tap:
🔔 Notification sent.

Admin receives:
🔔 USER REMINDER — User @{username} reminded about Order ID: {id}

If cooldown not finished:
⏳ You must wait 1 hour.

If all 3 used:
🚫 No more notifications left.""",

    29: """🟥 29) AUTO DELIVERY LOG — ADMIN SIDE

📦 ORDER DELIVERED (AUTO LOG)

User: @{username}
User ID: {id}

Order ID: {OrderID}
Product: {ProductName}

🔐 Login:
📧 Email: {email}
🔑 Password: {password}

Delivered at: 🕒 {time}""",

    30: """🟥 30) COUPON GENERATOR — ADMIN

/genaretcupun → Opens coupon panel

🎟 COUPON GENERATOR

🎯 Single Product
🌍 All Products
⬅ Back""",

    31: """🟥 31) SINGLE PRODUCT COUPON

Format required:
discount | DD-MM-YYYY HH:MM AM/PM

Bot generates:
🎟 POWER-XXX-POINTXXXX-BREAK

One-time use only.""",

    32: """🟥 32) ALL PRODUCT COUPON + MULTI GENERATE

Admin sends:
150 | 30-12-2025 11:59 PM

Then sends quantity (1–10000)

Bot generates:

🎟 POWER-492-POINT8831-BREAK
🎟 POWER-157-POINT6724-BREAK
🎟 POWER-903-POINT1295-BREAK
🎟 POWER-288-POINT5479-BREAK
🎟 POWER-641-POINT9043-BREAK

Valid for ALL products
One-time use
Never regenerated again""",

    33: """🟥 33) MEGA OFFER SYSTEM

🎁 NEW MEGA OFFER
{offer_text}

Visible in Mega Offer button.""",

    34: """🟥 34) USER COUNT

👥 TOTAL USERS: {number}""",

    35: """🟥 35) FULL ADMIN COMMAND LIST

/panel
/addcategory
/removecategory
/addproduct
/removeproduct
/addstock
/removestoke
/allsellhistory
/allorderhistory
/pendingorders
/completedorders
/users
/senduser
/badge
/broadcast
/editwelcomesms
/editallsmscustomize
/addtutorial
/removetutorial
/genaretcupun
/setoffer
/userscount
/offbot
/onbot
/reset
/addChanelOrGroupLink""",

    36: """🟥 36) ADD CHANNEL / GROUP LINK OR USERNAME (ADMIN SYSTEM)

Admin Command: /addChanelOrGroupLink

📌 What do you want to add?
Choose option:

📎 Add Channel/Group Link
👤 Add Username
⬅ Cancel

OPTION 1 — Add Link
🔗 “Please send new Channel / Group link…”
→ Admin sends link
→ ✅ Saved Successfully!

OPTION 2 — Add Username
👤 “Please send new username…”
→ Admin sends username
→ ✅ Username Saved Successfully!

OPTION 3 — Cancel
❌ Operation cancelled

⚠ Error Handling Included.""",

    37: """🟥 37) ADD ADMIN SYSTEM (SUPER ADMIN ONLY)

👑 This system is ONLY for the Main Admin.
Normal admins cannot use these commands.

Available Commands:
/addadmin
/removeadmin""",

    38: """🟥 38) SUPER ADMIN MANAGEMENT SYSTEM

Only Super Admins can use:
/addsupperaddmin
/removesuperadmin
/adminlist""",

    39: """🟥 39) /setprice — Update Price

Who can use: Admin / Super Admin

Admin: /setprice
Bot: Choose product
Admin selects product
Bot: “Send new price:”
Admin sends → 599
Bot: “✅ Price updated successfully!”

Invalid price → ❌ Invalid number
Normal user → ❌ Permission denied""",

    40: """🟥 40) /setduration — Update Duration

Admin: /setduration
Bot: Choose product
Bot: Send new duration
Admin: 30 Days
Bot: “✅ Duration updated!”"""
}


def render_demo(n: int, user: Any = None, extra: Optional[Dict[str, Any]] = None) -> str:
    txt = DEMO_TEXTS[n]
    if user:
        txt = txt.replace("{FullName}", user.full_name)
        txt = txt.replace("{username}", user.username or "NoUsername")
        txt = txt.replace("{user_id}", str(user.id))
    if extra:
        for k, v in extra.items():
            txt = txt.replace("{" + k + "}", str(v))

    txt = txt.replace("@YourSupportUsername", f"@{SUPPORT_USERNAME}")
    txt = txt.replace("@PowerPointBreak", f"@{HOST_TAG}")
    txt = txt.replace("01877576843", PAYMENT_NUMBER)
    return txt


# ---------- KEYBOARDS ----------
def kb_main() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🛒 All Categories", "🪪 My Profile")
    kb.row("🛍 Active Orders", "📦 My Orders")
    kb.row("⏳ Pending Orders", "🆘 Help Center")
    kb.row("📚 Tutorial", "🎁 Mega Offer")
    return kb


def kb_categories() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🤖 ChatGPT & AI", "▶️ YouTube Premium", "🎵 Spotify Premium")
    kb.row("🎬 Netflix", "🔒 VPN & Security", "👨‍💻 Developer Tools")
    kb.row("🧩 Office 365", "🎮 Gaming / Combo")
    kb.row("⬅ Back")
    return kb


def kb_products() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🤖 ChatGPT Plus — 1 Month")
    kb.row("🤖 ChatGPT Plus — 3 Months")
    kb.row("🚀 GPT-4 Team Access")
    kb.row("⬅ Back")
    return kb


def kb_product_details() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🛒 Buy Now", "🎟 Apply Coupon")
    kb.row("⬅ Back")
    return kb


def kb_payment() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🟣 bKash", "🟡 Nagad")
    kb.row("🟠 Upay", "🔵 Rocket")
    kb.row("🪙 Crypto (USDT)")
    kb.row("⬅ Back")
    return kb


# ---------- /start ----------
@bot.message_handler(commands=["start"])
def cmd_start(message: types.Message):
    u = message.from_user
    if u.id not in users:
        users[u.id] = {
            "id": u.id,
            "name": u.full_name,
            "username": u.username or "NoUsername",
            "joined": datetime.now()
        }
    bot.send_message(u.id, render_demo(1, u), reply_markup=kb_main())


# ---------- /openstore ----------
@bot.message_handler(commands=["openstore"])
def cmd_openstore(message: types.Message):
    u = message.from_user
    if u.id not in users:
        bot.send_message(u.id, render_demo(2, u))
        users[u.id] = {
            "id": u.id,
            "name": u.full_name,
            "username": u.username or "NoUsername",
            "joined": datetime.now()
        }
        bot.send_message(u.id, render_demo(3, u), reply_markup=kb_main())
    else:
        bot.send_message(u.id, render_demo(4, u), reply_markup=kb_main())


# ---------- MAIN MENU ----------
@bot.message_handler(func=lambda m: m.text in [
    "🛒 All Categories", "🪪 My Profile", "🛍 Active Orders", "📦 My Orders",
    "⏳ Pending Orders", "🆘 Help Center", "📚 Tutorial", "🎁 Mega Offer"
])
def handle_main_menu(message: types.Message):
    uid = message.from_user.id
    txt = message.text

    if txt == "🛒 All Categories":
        bot.send_message(uid, render_demo(6, message.from_user), reply_markup=kb_categories())

    elif txt == "🪪 My Profile":
        handle_profile(message)

    elif txt == "🛍 Active Orders":
        show_active_orders(message)

    elif txt == "📦 My Orders":
        show_my_orders(message)

    elif txt == "⏳ Pending Orders":
        show_pending_orders(message)

    elif txt == "🆘 Help Center":
        base = render_demo(24, message.from_user)
        text = custom_texts.get("help_center", base)
        bot.send_message(uid, text)

    elif txt == "📚 Tutorial":
        global tutorial_text
        if tutorial_text:
            bot.send_message(uid, tutorial_text)
        else:
            bot.send_message(uid, "📚 No tutorial added yet")

    elif txt == "🎁 Mega Offer":
        global mega_offer_text
        if mega_offer_text:
            txt_offer = render_demo(33, extra={"offer_text": mega_offer_text})
            bot.send_message(uid, txt_offer)
        else:
            bot.send_message(uid, "🎁 No mega offer available right now.")


# ---------- CATEGORY & PRODUCT ----------
@bot.message_handler(func=lambda m: m.text in [
    "🤖 ChatGPT & AI", "▶️ YouTube Premium", "🎵 Spotify Premium",
    "🎬 Netflix", "🔒 VPN & Security", "👨‍💻 Developer Tools",
    "🧩 Office 365", "🎮 Gaming / Combo", "⬅ Back"
])
def handle_categories(message: types.Message):
    uid = message.from_user.id
    txt = message.text

    if txt == "⬅ Back":
        bot.send_message(uid, "🏠 MAIN MENU", reply_markup=kb_main())
        return

    if txt == "🤖 ChatGPT & AI":
        bot.send_message(uid, render_demo(7, message.from_user), reply_markup=kb_products())
    else:
        bot.send_message(uid, "⚠ This category is not configured yet.", reply_markup=kb_categories())


@bot.message_handler(func=lambda m: m.text in [
    "🤖 ChatGPT Plus — 1 Month",
    "🤖 ChatGPT Plus — 3 Months",
    "🚀 GPT-4 Team Access",
    "⬅ Back"
])
def handle_products(message: types.Message):
    uid = message.from_user.id
    txt = message.text

    if txt == "⬅ Back":
        bot.send_message(uid, render_demo(6, message.from_user), reply_markup=kb_categories())
        return

    if txt == "🤖 ChatGPT Plus — 1 Month":
        pending_payment_ctx[uid] = {
            "product": "ChatGPT Plus — 1 Month",
            "price": products_info["ChatGPT Plus — 1 Month"]["price"],
            "coupon": None,
            "discount": 0
        }
        bot.send_message(uid, render_demo(8, message.from_user), reply_markup=kb_product_details())
    else:
        bot.send_message(uid, "⚠ This product is not configured yet.", reply_markup=kb_products())


@bot.message_handler(func=lambda m: m.text in ["🛒 Buy Now", "🎟 Apply Coupon", "⬅ Back"])
def handle_product_details(message: types.Message):
    uid = message.from_user.id
    txt = message.text
    ctx = pending_payment_ctx.get(uid)

    if txt == "⬅ Back":
        bot.send_message(uid, render_demo(7, message.from_user), reply_markup=kb_products())
        return

    if not ctx:
        bot.send_message(uid, "⚠ No product selected.", reply_markup=kb_main())
        return

    if txt == "🎟 Apply Coupon":
        bot.send_message(uid, render_demo(9, message.from_user))
        bot.send_message(uid, "Please send your coupon code:")
        user_states[uid] = "coupon"

    elif txt == "🛒 Buy Now":
        price = ctx["price"]
        txt_pay = render_demo(10, message.from_user).replace("৳499", f"৳{price}")
        bot.send_message(uid, txt_pay, reply_markup=kb_payment())
        user_states[uid] = "pay_method"


# ---------- COUPON INPUT ----------
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "coupon")
def handle_coupon(message: types.Message):
    uid = message.from_user.id
    code = message.text.strip()
    ctx = pending_payment_ctx.get(uid)

    if not ctx:
        bot.send_message(uid, "⚠ No product selected.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return

    bot.send_message(uid, render_demo(9, message.from_user, {
        "code": code,
        "discount": ctx["discount"],
        "original": ctx["price"],
        "final": ctx["price"] - ctx["discount"]
    }))
    user_states.pop(uid, None)


# ---------- PAYMENT METHOD ----------
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "pay_method")
def handle_payment_method(message: types.Message):
    uid = message.from_user.id
    txt = message.text
    ctx = pending_payment_ctx.get(uid)

    if not ctx:
        bot.send_message(uid, "⚠ No product selected.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return

    if txt == "⬅ Back":
        bot.send_message(uid, render_demo(8, message.from_user), reply_markup=kb_product_details())
        user_states.pop(uid, None)
        return

    if txt == "🪙 Crypto (USDT)":
        bot.send_message(uid, render_demo(12, message.from_user), reply_markup=kb_payment())
        return

    if txt in ["🟣 bKash", "🟡 Nagad", "🟠 Upay", "🔵 Rocket"]:
        ctx["payment_method"] = txt
        pay_text = render_demo(11, message.from_user, {"if-any": "None"})
        pay_text = pay_text.replace("৳499", f"৳{ctx['price']}")
        bot.send_message(uid, pay_text)
        bot.send_message(uid, "Now send your payment info in format:\nSender | Amount | TXID")
        user_states[uid] = "pay_info"
        return

    bot.send_message(uid, "⚠ Please select a valid payment method.", reply_markup=kb_payment())


# ---------- PAYMENT INFO + ORDER CREATE ----------
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "pay_info")
def handle_payment_info(message: types.Message):
    uid = message.from_user.id
    txt = message.text.strip()
    ctx = pending_payment_ctx.get(uid)

    if not ctx:
        bot.send_message(uid, "⚠ No product selected.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return

    parts = [p.strip() for p in txt.split("|")]
    if len(parts) != 3:
        bot.send_message(uid, render_demo(13, message.from_user))
        return

    sender, amount, txid = parts

    order_id = new_order_id()
    order = {
        "order_id": order_id,
        "user_id": uid,
        "username": message.from_user.username or "NoUsername",
        "product": ctx["product"],
        "amount": amount,
        "payment_method": ctx.get("payment_method", ""),
        "sender": sender,
        "txid": txid,
        "status": "Pending",
        "time": datetime.now()
    }
    orders[order_id] = order

    bot.send_message(uid, render_demo(14, message.from_user))

    admin_text = render_demo(15, message.from_user, {
        "date/time": datetime.now().strftime("%d-%b-%Y | %I:%M %p")
    })
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve:{order_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject:{order_id}")
    )
    try:
        bot.send_message(ORDER_LOG_CHAT_ID, admin_text, reply_markup=kb)
    except Exception:
        bot.send_message(MAIN_ADMIN_ID, admin_text, reply_markup=kb)

    user_states.pop(uid, None)
    pending_payment_ctx.pop(uid, None)


def auto_cancel(order_id: str):
    order = orders.get(order_id)
    if not order:
        return
    if order["status"] == "Pending":
        order["status"] = "AutoCancelled"
        uid = order["user_id"]
        bot.send_message(uid, render_demo(19))


# ---------- ORDERS (20–22) ----------
def show_active_orders(message: types.Message):
    uid = message.from_user.id
    active = [o for o in orders.values() if o["user_id"] == uid and o["status"] == "Pending"]
    if not active:
        bot.send_message(uid, "No active orders.")
        return
    for o in active:
        txt = render_demo(20, extra={
            "id": o["order_id"],
            "product": o["product"],
            "amount": o["amount"]
        })
        bot.send_message(uid, txt)


def show_pending_orders(message: types.Message):
    uid = message.from_user.id
    pending = [o for o in orders.values() if o["user_id"] == uid and o["status"] == "Pending"]
    if not pending:
        bot.send_message(uid, "No pending orders.")
        return
    for o in pending:
        txt = render_demo(21, extra={
            "id": o["order_id"],
            "product": o["product"],
            "amount": o["amount"]
        })
        bot.send_message(uid, txt)


def show_my_orders(message: types.Message):
    uid = message.from_user.id
    all_o = [o for o in orders.values() if o["user_id"] == uid]
    if not all_o:
        bot.send_message(uid, "No order history found.")
        return

    bot.send_message(uid, render_demo(22))
    for o in all_o:
        line = (
            f"Order ID: {o['order_id']}\n"
            f"Product: {o['product']}\n"
            f"Amount: {o['amount']}\n"
            f"Status: {o['status']}\n"
            f"Time: {o['time'].strftime('%d-%b-%Y | %I:%M %p')}"
        )
        bot.send_message(uid, line)


# ---------- PROFILE (23) ----------
def handle_profile(message: types.Message):
    uid = message.from_user.id
    u = users.get(uid)
    if not u:
        bot.send_message(uid, "Profile not found. Use /openstore first.")
        return

    user_orders = [o for o in orders.values() if o["user_id"] == uid]
    total = len(user_orders)
    completed = len([o for o in user_orders if o["status"] == "Approved"])
    pending_count = len([o for o in user_orders if o["status"] == "Pending"])

    txt = render_demo(23, extra={
        "name": u["name"],
        "username": u["username"],
        "id": uid,
        "date": u["joined"].strftime("%d-%b-%Y"),
        "total": total,
        "completed": completed,
        "pending": pending_count
    })
    bot.send_message(uid, txt)


# ---------- BOT OFF / ON (26–27) ----------
@bot.message_handler(commands=["offbot"])
def cmd_offbot(message: types.Message):
    global bot_off
    if message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot_off = True
    bot.reply_to(message, "✅ Bot OFF status enabled for users.")
    bot.send_message(message.chat.id, render_demo(26, message.from_user))


@bot.message_handler(commands=["onbot"])
def cmd_onbot(message: types.Message):
    global bot_off
    if message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot_off = False
    bot.reply_to(message, "✅ Bot is LIVE again.")
    bot.send_message(message.chat.id, render_demo(27, message.from_user))


@bot.message_handler(func=lambda m: bot_off and m.from_user.id != MAIN_ADMIN_ID, content_types=["text"])
def handle_off_message(message: types.Message):
    bot.send_message(message.from_user.id, render_demo(26, message.from_user))


# ---------- NOTIFY ADMIN (28) ----------
@bot.message_handler(commands=["notifyadmin"])
def cmd_notify_admin(message: types.Message):
    uid = message.from_user.id
    now = datetime.now()
    info = notify_stats.get(uid, {"count": 0, "last": None})
    count = info["count"]
    last = info["last"]

    if count >= 3:
        bot.send_message(uid, "🚫 No more notifications left.")
        return

    if last is not None:
        diff = (now - last).total_seconds()
        if diff < 3600:
            bot.send_message(uid, "⏳ You must wait 1 hour.")
            return

    bot.send_message(uid, "🔔 Notification sent.")

    user_orders_list = [o for o in orders.values() if o["user_id"] == uid and o["status"] == "Pending"]
    if user_orders_list:
        order_for_notify = user_orders_list[0]
        aid = order_for_notify["order_id"]
    else:
        aid = "N/A"

    admin_msg = f"🔔 USER REMINDER — User @{message.from_user.username or 'NoUsername'} reminded about Order ID: {aid}"
    try:
        bot.send_message(ORDER_LOG_CHAT_ID, admin_msg)
    except Exception:
        bot.send_message(MAIN_ADMIN_ID, admin_msg)

    notify_stats[uid] = {"count": count + 1, "last": now}


# ---------- COUPON GENERATOR (30–32, 61) ----------
def generate_coupon_code() -> str:
    three = random.randint(100, 999)
    four = random.randint(1000, 9999)
    return f"POWER-{three}-POINT{four}-BREAK"


@bot.message_handler(commands=["genaretcupun"])
def cmd_genaretcupun(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return

    bot.send_message(message.chat.id, render_demo(30, message.from_user))

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🎯 Single Product", callback_data="coup_single"),
        types.InlineKeyboardButton("🌍 All Products", callback_data="coup_all")
    )
    kb.add(types.InlineKeyboardButton("⬅ Back", callback_data="coup_back"))

    bot.send_message(message.chat.id, "Choose coupon mode:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("coup_"))
def cb_coupon_mode(call: types.CallbackQuery):
    uid = call.from_user.id
    if uid not in super_admins and uid != MAIN_ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Permission denied")
        return

    mode = call.data
    if mode == "coup_back":
        bot.answer_callback_query(call.id, "Back")
        return

    if mode == "coup_single":
        bot.answer_callback_query(call.id, "Single Product Coupon")
        bot.send_message(uid, render_demo(31))
        bot.send_message(uid, "Send: discount | DD-MM-YYYY HH:MM AM/PM")
        user_states[uid] = "coupon_single"

    elif mode == "coup_all":
        bot.answer_callback_query(call.id, "All Product Coupon")
        bot.send_message(uid, render_demo(32))
        bot.send_message(uid, "First send: discount | DD-MM-YYYY HH:MM AM/PM")
        user_states[uid] = "coupon_all_step1"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "coupon_single")
def handle_coupon_single(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 2:
        bot.send_message(uid, "⚠ Invalid format. Use: discount | DD-MM-YYYY HH:MM AM/PM")
        return

    discount, expiry = parts
    code = generate_coupon_code()
    coupons[code] = {
        "discount": discount,
        "expiry": expiry,
        "scope": "single"
    }
    bot.send_message(uid, f"🎟 {code}\nDiscount: {discount}\nExpire: {expiry}\nOne-time use only.")
    user_states.pop(uid, None)


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "coupon_all_step1")
def handle_coupon_all_step1(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 2:
        bot.send_message(uid, "⚠ Invalid format. Use: discount | DD-MM-YYYY HH:MM AM/PM")
        return

    discount, expiry = parts
    pending_payment_ctx[uid] = {
        "discount": discount,
        "expiry": expiry
    }
    bot.send_message(uid, "Now send quantity (1–10000):")
    user_states[uid] = "coupon_all_step2"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "coupon_all_step2")
def handle_coupon_all_step2(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "⚠ Context lost. Start /genaretcupun again.")
        user_states.pop(uid, None)
        return

    try:
        qty = int(text)
    except ValueError:
        bot.send_message(uid, "❌ Invalid number")
        return

    if qty < 1 or qty > 10000:
        bot.send_message(uid, "❌ Invalid range (1–10000)")
        return

    discount = ctx["discount"]
    expiry = ctx["expiry"]
    msg_lines = []
    for _ in range(qty):
        code = generate_coupon_code()
        coupons[code] = {
            "discount": discount,
            "expiry": expiry,
            "scope": "all"
        }
        msg_lines.append(f"🎟 {code}")

    bot.send_message(uid, "\n".join(msg_lines))
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


# ---------- MEGA OFFER (33, 62) ----------
@bot.message_handler(commands=["setoffer"])
def cmd_setoffer(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.reply_to(message, "Send new Mega Offer text:")
    user_states[message.from_user.id] = "set_offer"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "set_offer")
def handle_set_offer(message: types.Message):
    global mega_offer_text
    mega_offer_text = message.text
    bot.send_message(message.from_user.id, "🎁 Mega Offer updated!")
    user_states.pop(message.from_user.id, None)


# ---------- USER COUNT (34, 63) ----------
@bot.message_handler(commands=["userscount"])
def cmd_userscount(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    total = len(users)
    txt = render_demo(34, extra={"number": total})
    bot.send_message(message.chat.id, txt)


# ---------- PANEL (35) ----------
@bot.message_handler(commands=["panel"])
def cmd_panel(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, DEMO_TEXTS[35])


# ---------- ADD CHANNEL/GROUP LINK (36, 67) ----------
@bot.message_handler(commands=["addChanelOrGroupLink"])
def cmd_add_channel_group(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return

    bot.send_message(message.chat.id, DEMO_TEXTS[36])

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("📎 Add Channel/Group Link", callback_data="chgl_link"),
        types.InlineKeyboardButton("👤 Add Username", callback_data="chgl_user")
    )
    kb.add(types.InlineKeyboardButton("⬅ Cancel", callback_data="chgl_cancel"))

    bot.send_message(message.chat.id, "Choose option:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("chgl_"))
def cb_chgl(call: types.CallbackQuery):
    uid = call.from_user.id
    if uid not in super_admins and uid != MAIN_ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Permission denied")
        return

    mode = call.data
    if mode == "chgl_cancel":
        bot.answer_callback_query(call.id, "❌ Operation cancelled")
        return

    if mode == "chgl_link":
        bot.send_message(uid, "Please send new Channel / Group link…")
        user_states[uid] = "add_link"
    elif mode == "chgl_user":
        bot.send_message(uid, "Please send new username…")
        user_states[uid] = "add_username"
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "add_link")
def handle_add_link(message: types.Message):
    global channel_or_group
    uid = message.from_user.id
    channel_or_group["link"] = message.text.strip()
    bot.send_message(uid, "✅ Saved Successfully!")
    user_states.pop(uid, None)


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "add_username")
def handle_add_username(message: types.Message):
    global channel_or_group
    uid = message.from_user.id
    channel_or_group["username"] = message.text.strip()
    bot.send_message(uid, "✅ Username Saved Successfully!")
    user_states.pop(uid, None)


# ---------- ADMIN / SUPER ADMIN (37–38) ----------
@bot.message_handler(commands=["addadmin"])
def cmd_addadmin(message: types.Message):
    if message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Please send Username or User ID of new admin:")
    user_states[message.from_user.id] = "add_admin"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "add_admin")
def handle_addadmin(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    if text.isdigit():
        target_id = int(text)
    else:
        target_id = abs(hash(text)) % 10**9

    if target_id in admins:
        bot.send_message(uid, "⚠️ User already admin")
    else:
        admins.add(target_id)
        bot.send_message(uid, f"✅ Admin added: {text}")
    user_states.pop(uid, None)


@bot.message_handler(commands=["removeadmin"])
def cmd_removeadmin(message: types.Message):
    if message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send Username/User ID to remove:")
    user_states[message.from_user.id] = "remove_admin"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "remove_admin")
def handle_removeadmin(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    if text.isdigit():
        target_id = int(text)
    else:
        target_id = abs(hash(text)) % 10**9

    if target_id == MAIN_ADMIN_ID:
        bot.send_message(uid, "❌ Cannot remove Main Admin")
    elif target_id in admins:
        admins.remove(target_id)
        bot.send_message(uid, "❌ Admin removed successfully!")
    else:
        bot.send_message(uid, "⚠️ This user is not an admin")
    user_states.pop(uid, None)


@bot.message_handler(commands=["addsupperaddmin"])
def cmd_addsuperadmin(message: types.Message):
    if message.from_user.id not in super_admins:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send Username/User ID to make Super Admin:")
    user_states[message.from_user.id] = "add_super_admin"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "add_super_admin")
def handle_addsuperadmin(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    if text.isdigit():
        target_id = int(text)
    else:
        target_id = abs(hash(text)) % 10**9

    if target_id in super_admins:
        bot.send_message(uid, "⚠️ Already Super Admin")
    else:
        super_admins.add(target_id)
        bot.send_message(uid, "👑 Super Admin added successfully!")
    user_states.pop(uid, None)


@bot.message_handler(commands=["removesuperadmin"])
def cmd_removesuperadmin(message: types.Message):
    if message.from_user.id not in super_admins:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send Username/User ID to remove:")
    user_states[message.from_user.id] = "remove_super_admin"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "remove_super_admin")
def handle_removesuperadmin(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    if text.isdigit():
        target_id = int(text)
    else:
        target_id = abs(hash(text)) % 10**9

    if target_id in super_admins and len(super_admins) == 1:
        bot.send_message(uid, "⚠️ You cannot remove the last Super Admin")
    elif target_id in super_admins:
        super_admins.remove(target_id)
        bot.send_message(uid, "❌ Super Admin removed!")
    else:
        bot.send_message(uid, "❌ Invalid Username")
    user_states.pop(uid, None)


@bot.message_handler(commands=["adminlist"])
def cmd_adminlist(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return

    lines = ["👥 ADMIN MANAGEMENT PANEL", "", "SUPER ADMINS:\n"]
    if super_admins:
        for i, sid in enumerate(super_admins, start=1):
            lines.append(f"{i}. ID: {sid} — Added on: (date not tracked)")
    else:
        lines.append("⚠️ No super admins found")

    lines.append("\n\nADMINS:\n")
    if admins:
        for i, aid in enumerate(admins, start=1):
            lines.append(f"{i}. ID: {aid} — Added on: (date not tracked)")
    else:
        lines.append("⚠️ No admins found")

    bot.send_message(message.chat.id, "\n".join(lines))


# ---------- STOCK HELPERS (41,42,48) ----------
def get_product_from_name(name: str):
    return products_info.get(name)


def choose_product_keyboard() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in products_info.keys():
        kb.row(name)
    kb.row("❌ Cancel")
    return kb


@bot.message_handler(commands=["addstock"])
def cmd_addstock(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Choose product to add stock:", reply_markup=choose_product_keyboard())
    user_states[message.from_user.id] = "addstock_choose"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "addstock_choose")
def handle_addstock_choose(message: types.Message):
    uid = message.from_user.id
    name = message.text.strip()
    if name == "❌ Cancel":
        bot.send_message(uid, "❌ Cancelled", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    pinfo = get_product_from_name(name)
    if not pinfo:
        bot.send_message(uid, "⚠ Unknown product. Try again.", reply_markup=choose_product_keyboard())
        return
    limit = pinfo.get("stock_limit")
    if limit is not None and len(pinfo["stocks"]) >= limit:
        bot.send_message(uid, "❌ Stock limit reached", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    pending_payment_ctx[uid] = {"product_edit": name}
    bot.send_message(uid, "Send stock credential in this format:\n\nemail | password")
    user_states[uid] = "addstock_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "addstock_value")
def handle_addstock_value(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "Context lost. Use /addstock again.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 2:
        bot.send_message(uid, "⚠ Invalid format. Use: email | password")
        return
    email, password = parts
    pinfo = get_product_from_name(ctx["product_edit"])
    if not pinfo:
        bot.send_message(uid, "Product not found.", reply_markup=kb_main())
    else:
        limit = pinfo.get("stock_limit")
        if limit is not None and len(pinfo["stocks"]) >= limit:
            bot.send_message(uid, "❌ Stock limit reached", reply_markup=kb_main())
        else:
            pinfo["stocks"].append({"email": email, "password": password})
            bot.send_message(uid, "✅ Stock added successfully!", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


@bot.message_handler(commands=["setstocklimit"])
def cmd_setstocklimit(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Choose product to set stock limit:", reply_markup=choose_product_keyboard())
    user_states[message.from_user.id] = "setstocklimit_choose"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "setstocklimit_choose")
def handle_setstocklimit_choose(message: types.Message):
    uid = message.from_user.id
    name = message.text.strip()
    if name == "❌ Cancel":
        bot.send_message(uid, "❌ Cancelled", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    pinfo = get_product_from_name(name)
    if not pinfo:
        bot.send_message(uid, "⚠ Unknown product. Try again.", reply_markup=choose_product_keyboard())
        return
    pending_payment_ctx[uid] = {"product_edit": name}
    bot.send_message(uid, "Send max stock limit (number):")
    user_states[uid] = "setstocklimit_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "setstocklimit_value")
def handle_setstocklimit_value(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "Context lost.")
        user_states.pop(uid, None)
        return
    try:
        limit = int(text)
    except ValueError:
        bot.send_message(uid, "❌ Invalid number")
        return
    pinfo = get_product_from_name(ctx["product_edit"])
    if not pinfo:
        bot.send_message(uid, "Product not found.")
    else:
        pinfo["stock_limit"] = limit
        bot.send_message(uid, f"Max stock updated: {limit}", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


@bot.message_handler(commands=["viewstock"])
def cmd_viewstock(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Choose product to view stock:", reply_markup=choose_product_keyboard())
    user_states[message.from_user.id] = "viewstock_choose"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "viewstock_choose")
def handle_viewstock_choose(message: types.Message):
    uid = message.from_user.id
    name = message.text.strip()
    if name == "❌ Cancel":
        bot.send_message(uid, "❌ Cancelled", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    pinfo = get_product_from_name(name)
    if not pinfo:
        bot.send_message(uid, "⚠ Unknown product.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    stocks = pinfo.get("stocks", [])
    if not stocks:
        bot.send_message(uid, "📛 No stock available.", reply_markup=kb_main())
    else:
        lines = [f"Stock list for {name}:"]
        for i, s in enumerate(stocks, start=1):
            lines.append(f"{i}. {s['email']} | {s['password']}")
        bot.send_message(uid, "\n".join(lines), reply_markup=kb_main())
    user_states.pop(uid, None)


@bot.message_handler(commands=["removestoke"])
def cmd_removestoke(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Choose product to remove stock from:", reply_markup=choose_product_keyboard())
    user_states[message.from_user.id] = "removestoke_choose"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "removestoke_choose")
def handle_removestoke_choose(message: types.Message):
    uid = message.from_user.id
    name = message.text.strip()
    if name == "❌ Cancel":
        bot.send_message(uid, "❌ Cancelled", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    pinfo = get_product_from_name(name)
    if not pinfo:
        bot.send_message(uid, "⚠ Unknown product.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    stocks = pinfo.get("stocks", [])
    if not stocks:
        bot.send_message(uid, "📛 No stock available", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    lines = [f"Stocks for {name}:"]
    for i, s in enumerate(stocks, start=1):
        lines.append(f"{i}. {s['email']} | {s['password']}")
    bot.send_message(uid, "\n".join(lines))
    bot.send_message(uid, "Send stock number to remove:")
    pending_payment_ctx[uid] = {"product_edit": name}
    user_states[uid] = "removestoke_index"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "removestoke_index")
def handle_removestoke_index(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "Context lost.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    pinfo = get_product_from_name(ctx["product_edit"])
    if not pinfo or not pinfo.get("stocks"):
        bot.send_message(uid, "No stock found.", reply_markup=kb_main())
        pending_payment_ctx.pop(uid, None)
        user_states.pop(uid, None)
        return
    try:
        idx = int(text)
    except ValueError:
        bot.send_message(uid, "❌ Invalid stock ID")
        return
    if idx < 1 or idx > len(pinfo["stocks"]):
        bot.send_message(uid, "❌ Invalid stock ID")
        return
    pinfo["stocks"].pop(idx - 1)
    bot.send_message(uid, "❌ Stock item removed.", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


# ---------- APPROVE / REJECT (16–18, 29, 50–53) ----------
@bot.callback_query_handler(func=lambda c: c.data.startswith("approve:"))
def cb_approve(call: types.CallbackQuery):
    if call.from_user.id != MAIN_ADMIN_ID and call.from_user.id not in super_admins:
        bot.answer_callback_query(call.id, "❌ Permission denied")
        return
    order_id = call.data.split(":", 1)[1]
    order = orders.get(order_id)
    if not order:
        bot.answer_callback_query(call.id, "❌ Order not found")
        return
    email = "accdemo@gmail.com"
    password = "Abcd12345"
    pinfo = products_info.get(order["product"])
    if pinfo and pinfo.get("stocks"):
        cred = pinfo["stocks"].pop(0)
        email = cred["email"]
        password = cred["password"]
    order["status"] = "Approved"
    base_sms = render_demo(17, extra={"Username": order["username"] or "username"})
    txt_user = custom_texts.get("approved", base_sms)
    txt_user = txt_user.replace("accdemo@gmail.com", email).replace("Abcd12345", password)
    bot.send_message(order["user_id"], txt_user)
    log_txt = render_demo(29, extra={
        "username": order["username"] or "username",
        "id": order["user_id"],
        "OrderID": order_id,
        "ProductName": order["product"],
        "email": email,
        "password": password,
        "time": datetime.now().strftime("%d-%b-%Y | %I:%M %p")
    })
    try:
        bot.send_message(ORDER_LOG_CHAT_ID, log_txt)
    except Exception:
        bot.send_message(MAIN_ADMIN_ID, log_txt)
    bot.answer_callback_query(call.id, "Approved ✅")


@bot.callback_query_handler(func=lambda c: c.data.startswith("reject:"))
def cb_reject(call: types.CallbackQuery):
    if call.from_user.id != MAIN_ADMIN_ID and call.from_user.id not in super_admins:
        bot.answer_callback_query(call.id, "❌ Permission denied")
        return
    order_id = call.data.split(":", 1)[1]
    order = orders.get(order_id)
    if not order:
        bot.answer_callback_query(call.id, "❌ Order not found")
        return
    order["status"] = "Rejected"
    base_rej = render_demo(18, extra={"reason": "Wrong payment information"})
    txt = custom_texts.get("rejected", base_rej)
    bot.send_message(order["user_id"], txt)
    bot.answer_callback_query(call.id, "Rejected ❌")


# ---------- /setprice (39) & /setduration (40) ----------
@bot.message_handler(commands=["setprice"])
def cmd_setprice(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Choose product:", reply_markup=choose_product_keyboard())
    user_states[message.from_user.id] = "setprice_choose"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "setprice_choose")
def handle_setprice_choose(message: types.Message):
    uid = message.from_user.id
    name = message.text.strip()
    if name == "❌ Cancel":
        bot.send_message(uid, "❌ Cancelled", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    if name not in products_info:
        bot.send_message(uid, "⚠ Unknown product. Try again.", reply_markup=choose_product_keyboard())
        return
    pending_payment_ctx[uid] = {"product_edit": name}
    bot.send_message(uid, "Send new price:")
    user_states[uid] = "setprice_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "setprice_value")
def handle_setprice_value(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "Context lost.")
        user_states.pop(uid, None)
        return
    try:
        val = float(text)
    except ValueError:
        bot.send_message(uid, "❌ Invalid number")
        return
    products_info[ctx["product_edit"]]["price"] = val
    bot.send_message(uid, "✅ Price updated successfully!", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


@bot.message_handler(commands=["setduration"])
def cmd_setduration(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Choose product:", reply_markup=choose_product_keyboard())
    user_states[message.from_user.id] = "setduration_choose"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "setduration_choose")
def handle_setduration_choose(message: types.Message):
    uid = message.from_user.id
    name = message.text.strip()
    if name == "❌ Cancel":
        bot.send_message(uid, "❌ Cancelled", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    if name not in products_info:
        bot.send_message(uid, "⚠ Unknown product. Try again.", reply_markup=choose_product_keyboard())
        return
    pending_payment_ctx[uid] = {"product_edit": name}
    bot.send_message(uid, "Send new duration (e.g., 30 Days):")
    user_states[uid] = "setduration_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "setduration_value")
def handle_setduration_value(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "Context lost.")
        user_states.pop(uid, None)
        return
    products_info[ctx["product_edit"]]["duration"] = text
    bot.send_message(uid, "✅ Duration updated!", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


# ---------- 41–47: edit product/category, ordersearch, usersearch, badge ----------
@bot.message_handler(commands=["editproductname"])
def cmd_editproductname(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Choose product to rename:", reply_markup=choose_product_keyboard())
    user_states[message.from_user.id] = "editproductname_choose"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "editproductname_choose")
def handle_editproductname_choose(message: types.Message):
    uid = message.from_user.id
    name = message.text.strip()
    if name == "❌ Cancel":
        bot.send_message(uid, "❌ Cancelled", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    if name not in products_info:
        bot.send_message(uid, "⚠ Unknown product.", reply_markup=choose_product_keyboard())
        return
    pending_payment_ctx[uid] = {"product_old": name}
    bot.send_message(uid, "Send new product name:")
    user_states[uid] = "editproductname_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "editproductname_value")
def handle_editproductname_value(message: types.Message):
    uid = message.from_user.id
    new_name = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "Context lost.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    old_name = ctx["product_old"]
    if old_name not in products_info:
        bot.send_message(uid, "Product not found.", reply_markup=kb_main())
    else:
        products_info[new_name] = products_info.pop(old_name)
        bot.send_message(uid, "Product name updated!", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


def kb_categories_edit() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in categories:
        kb.row(c)
    kb.row("❌ Cancel")
    return kb


@bot.message_handler(commands=["editcategoryname"])
def cmd_editcategoryname(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Choose category to rename:", reply_markup=kb_categories_edit())
    user_states[message.from_user.id] = "editcategoryname_choose"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "editcategoryname_choose")
def handle_editcategoryname_choose(message: types.Message):
    uid = message.from_user.id
    name = message.text.strip()
    if name == "❌ Cancel":
        bot.send_message(uid, "❌ Cancelled", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    if name not in categories:
        bot.send_message(uid, "⚠ Unknown category.", reply_markup=kb_categories_edit())
        return
    pending_payment_ctx[uid] = {"category_old": name}
    bot.send_message(uid, "Send new category name:")
    user_states[uid] = "editcategoryname_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "editcategoryname_value")
def handle_editcategoryname_value(message: types.Message):
    uid = message.from_user.id
    new_name = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "Context lost.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    old = ctx["category_old"]
    if old not in categories:
        bot.send_message(uid, "Category not found.", reply_markup=kb_main())
    else:
        idx = categories.index(old)
        categories[idx] = new_name
        bot.send_message(uid, "Category updated!", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


@bot.message_handler(commands=["ordersearch"])
def cmd_ordersearch(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send Order ID or Username (@username):")
    user_states[message.from_user.id] = "ordersearch_query"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "ordersearch_query")
def handle_ordersearch_query(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    results = []
    if text.upper().startswith("CG-"):
        o = orders.get(text)
        if o:
            results = [o]
    else:
        uname = text.lstrip("@").lower()
        results = [o for o in orders.values() if (o["username"] or "").lower() == uname]
    if not results:
        bot.send_message(uid, "❌ No order found.")
    else:
        for o in results:
            msg = (
                f"Order ID: {o['order_id']}\n"
                f"User: @{o['username']}\n"
                f"Product: {o['product']}\n"
                f"Amount: {o['amount']}\n"
                f"Status: {o['status']}\n"
                f"Payment: {o['payment_method']}\n"
                f"Sender: {o['sender']}\n"
                f"TXID: {o['txid']}\n"
                f"Time: {o['time'].strftime('%d-%b-%Y | %I:%M %p')}"
            )
            bot.send_message(uid, msg)
    user_states.pop(uid, None)


@bot.message_handler(commands=["usersearch"])
def cmd_usersearch(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send Username (@username) or User ID:")
    user_states[message.from_user.id] = "usersearch_query"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "usersearch_query")
def handle_usersearch_query(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    target = None
    if text.isdigit():
        tid = int(text)
        target = users.get(tid)
    else:
        uname = text.lstrip("@").lower()
        for u in users.values():
            if (u["username"] or "").lower() == uname:
                target = u
                break
    if not target:
        bot.send_message(uid, "❌ No user found.")
    else:
        tid = target["id"]
        u_orders = [o for o in orders.values() if o["user_id"] == tid]
        total = len(u_orders)
        completed = len([o for o in u_orders if o["status"] == "Approved"])
        pending = len([o for o in u_orders if o["status"] == "Pending"])
        msg = (
            f"🧍 USER FOUND\n"
            f"Name: {target['name']}\n"
            f"Username: @{target['username']}\n"
            f"User ID: {tid}\n"
            f"Join Date: {target['joined'].strftime('%d-%b-%Y')}\n"
            f"Total Orders: {total}\n"
            f"Completed: {completed}\n"
            f"Pending: {pending}"
        )
        bot.send_message(uid, msg)
    user_states.pop(uid, None)


@bot.message_handler(commands=["badge"])
def cmd_badge(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send Username or User ID to set badge:")
    user_states[message.from_user.id] = "badge_user"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "badge_user")
def handle_badge_user(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    target = None
    if text.isdigit():
        tid = int(text)
        target = users.get(tid)
    else:
        uname = text.lstrip("@").lower()
        for u in users.values():
            if (u["username"] or "").lower() == uname:
                target = u
                break
    if not target:
        bot.send_message(uid, "❌ User not found")
        user_states.pop(uid, None)
        return
    pending_payment_ctx[uid] = {"badge_user": target["id"]}
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("VIP", "VIP MAX")
    kb.row("Premium", "Trusted Buyer")
    kb.row("❌ Cancel")
    bot.send_message(uid, "Choose badge:", reply_markup=kb)
    user_states[uid] = "badge_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "badge_value")
def handle_badge_value(message: types.Message):
    uid = message.from_user.id
    choice = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if choice == "❌ Cancel":
        bot.send_message(uid, "❌ Cancelled", reply_markup=kb_main())
        pending_payment_ctx.pop(uid, None)
        user_states.pop(uid, None)
        return
    if choice not in ["VIP", "VIP MAX", "Premium", "Trusted Buyer"]:
        bot.send_message(uid, "⚠ Invalid badge, choose again.")
        return
    if not ctx:
        bot.send_message(uid, "Context lost.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    tid = ctx["badge_user"]
    if tid in users:
        users[tid]["badge"] = choice
        bot.send_message(uid, "👑 Badge updated successfully!", reply_markup=kb_main())
    else:
        bot.send_message(uid, "User not found.", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


# ---------- 49) /resetuser ----------
@bot.message_handler(commands=["resetuser"])
def cmd_resetuser(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send Username or User ID to reset:")
    user_states[message.from_user.id] = "resetuser_target"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "resetuser_target")
def handle_resetuser_target(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    target_id = None
    if text.isdigit():
        target_id = int(text)
    else:
        uname = text.lstrip("@").lower()
        for u in users.values():
            if (u["username"] or "").lower() == uname:
                target_id = u["id"]
                break
    if not target_id or target_id not in users:
        bot.send_message(uid, "❌ User not found")
        user_states.pop(uid, None)
        return
    pending_payment_ctx[uid] = {"reset_user": target_id}
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Yes", "No")
    bot.send_message(uid, "⚠️ Are you sure you want to reset this user?\nYes / No", reply_markup=kb)
    user_states[uid] = "resetuser_confirm"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "resetuser_confirm")
def handle_resetuser_confirm(message: types.Message):
    uid = message.from_user.id
    choice = message.text.strip()
    ctx = pending_payment_ctx.get(uid)
    if choice == "No":
        bot.send_message(uid, "❌ Cancelled.", reply_markup=kb_main())
        pending_payment_ctx.pop(uid, None)
        user_states.pop(uid, None)
        return
    if choice != "Yes" or not ctx:
        bot.send_message(uid, "Invalid reply.", reply_markup=kb_main())
        pending_payment_ctx.pop(uid, None)
        user_states.pop(uid, None)
        return
    target_id = ctx["reset_user"]
    for o in orders.values():
        if o["user_id"] == target_id and o["status"] == "Pending":
            o["status"] = "ResetCleared"
    if target_id in notify_stats:
        notify_stats.pop(target_id, None)
    bot.send_message(uid, "🔄 User reset successfully!", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


# ---------- 50–53: history commands ----------
@bot.message_handler(commands=["allsellhistory"])
def cmd_allsellhistory(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    sold = [o for o in orders.values() if o["status"] == "Approved"]
    if not sold:
        bot.send_message(message.chat.id, "⚠️ No sell history found.")
        return
    for o in sorted(sold, key=lambda x: x["time"]):
        msg = (
            f"Order ID: {o['order_id']}\n"
            f"User: @{o['username']}\n"
            f"Product: {o['product']}\n"
            f"Amount: {o['amount']}\n"
            f"Payment: {o['payment_method']}\n"
            f"Time: {o['time'].strftime('%d-%b-%Y | %I:%M %p')}"
        )
        bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=["allorderhistory"])
def cmd_allorderhistory(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    if not orders:
        bot.send_message(message.chat.id, "No order history.")
        return
    for o in sorted(orders.values(), key=lambda x: x["time"]):
        msg = (
            f"Order ID: {o['order_id']}\n"
            f"User: @{o['username']}\n"
            f"Product: {o['product']}\n"
            f"Amount: {o['amount']}\n"
            f"Status: {o['status']}\n"
            f"Time: {o['time'].strftime('%d-%b-%Y | %I:%M %p')}"
        )
        bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=["pendingorders"])
def cmd_pendingorders_admin(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    pending = [o for o in orders.values() if o["status"] == "Pending"]
    if not pending:
        bot.send_message(message.chat.id, "⚠️ No pending orders.")
        return
    for o in pending:
        msg = (
            f"Order ID: {o['order_id']}\n"
            f"User: @{o['username']}\n"
            f"Product: {o['product']}\n"
            f"Amount: {o['amount']}\n"
            f"TXID: {o['txid']}\n"
            f"Sender: {o['sender']}\n"
            f"Time: {o['time'].strftime('%d-%b-%Y | %I:%M %p')}"
        )
        bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=["completedorders"])
def cmd_completedorders(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    completed = [o for o in orders.values() if o["status"] == "Approved"]
    if not completed:
        bot.send_message(message.chat.id, "No completed orders.")
        return
    for o in completed:
        msg = (
            f"Order ID: {o['order_id']}\n"
            f"User: @{o['username']}\n"
            f"Product: {o['product']}\n"
            f"Amount: {o['amount']}\n"
            f"Time: {o['time'].strftime('%d-%b-%Y | %I:%M %p')}"
        )
        bot.send_message(message.chat.id, msg)


# ---------- 54) /users ----------
@bot.message_handler(commands=["users"])
def cmd_users_admin(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    if not users:
        bot.send_message(message.chat.id, "⚠️ No users found.")
        return
    lines = []
    for u in users.values():
        lines.append(
            f"Name: {u['name']}\nUsername: @{u['username']}\nUser ID: {u['id']}\nJoined: {u['joined'].strftime('%d-%b-%Y')}\n"
        )
    bot.send_message(message.chat.id, "\n".join(lines))


# ---------- 55) /senduser ----------
@bot.message_handler(commands=["senduser"])
def cmd_senduser(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send Username or User ID:")
    user_states[message.from_user.id] = "senduser_target"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "senduser_target")
def handle_senduser_target(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()
    target_id = None
    if text.isdigit():
        target_id = int(text)
    else:
        uname = text.lstrip("@").lower()
        for u in users.values():
            if (u["username"] or "").lower() == uname:
                target_id = u["id"]
                break
    if not target_id:
        bot.send_message(uid, "❌ User not found")
        user_states.pop(uid, None)
        return
    pending_payment_ctx[uid] = {"send_to": target_id}
    bot.send_message(uid, "Send message to deliver:")
    user_states[uid] = "senduser_msg"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "senduser_msg")
def handle_senduser_msg(message: types.Message):
    uid = message.from_user.id
    text = message.text
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "Context lost.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    target_id = ctx["send_to"]
    try:
        bot.send_message(target_id, text)
        bot.send_message(uid, "📨 Message delivered!", reply_markup=kb_main())
    except Exception:
        bot.send_message(uid, "❌ Failed to deliver message.", reply_markup=kb_main())
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


# ---------- 56) /broadcast ----------
@bot.message_handler(commands=["broadcast"])
def cmd_broadcast(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send broadcast message:")
    user_states[message.from_user.id] = "broadcast_msg"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "broadcast_msg")
def handle_broadcast_msg(message: types.Message):
    uid = message.from_user.id
    text = message.text
    if len(text) > 4000:
        bot.send_message(uid, "❌ Text too long.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    total = len(users)
    sent = 0
    for u in users.values():
        try:
            bot.send_message(u["id"], text)
            sent += 1
        except Exception:
            pass
    bot.send_message(uid, f"📢 Broadcast completed! ({sent}/{total})", reply_markup=kb_main())
    user_states.pop(uid, None)


# ---------- 57) /editwelcomesms ----------
@bot.message_handler(commands=["editwelcomesms"])
def cmd_editwelcomesms(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send new welcome message for /start:")
    user_states[message.from_user.id] = "editwelcomesms_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "editwelcomesms_value")
def handle_editwelcomesms_value(message: types.Message):
    uid = message.from_user.id
    new_text = message.text
    DEMO_TEXTS[1] = new_text
    bot.send_message(uid, "✨ Welcome SMS updated!", reply_markup=kb_main())
    user_states.pop(uid, None)


# ---------- 58) /editallsmscustomize ----------
@bot.message_handler(commands=["editallsmscustomize"])
def cmd_editallsmscustomize(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Payment SMS", "Approved SMS")
    kb.row("Rejected SMS", "Help Center Text")
    kb.row("Tutorial Text", "Cancel")
    bot.send_message(message.chat.id, "Choose which SMS to edit:", reply_markup=kb)
    user_states[message.from_user.id] = "editallsms_menu"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "editallsms_menu")
def handle_editallsms_menu(message: types.Message):
    uid = message.from_user.id
    choice = message.text.strip()
    if choice == "Cancel":
        bot.send_message(uid, "❌ Cancelled.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    mapping = {
        "Payment SMS": "payment",
        "Approved SMS": "approved",
        "Rejected SMS": "rejected",
        "Help Center Text": "help_center",
        "Tutorial Text": "tutorial"
    }
    if choice not in mapping:
        bot.send_message(uid, "⚠ Invalid choice.")
        return
    key = mapping[choice]
    pending_payment_ctx[uid] = {"edit_key": key}
    bot.send_message(uid, f"Send new text for {choice}:", reply_markup=types.ReplyKeyboardRemove())
    user_states[uid] = "editallsms_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "editallsms_value")
def handle_editallsms_value(message: types.Message):
    uid = message.from_user.id
    text = message.text
    ctx = pending_payment_ctx.get(uid)
    if not ctx:
        bot.send_message(uid, "Context lost.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    key = ctx["edit_key"]
    custom_texts[key] = text
    bot.send_message(uid, "✅ SMS updated!", reply_markup=kb_main())
    if key == "tutorial":
        global tutorial_text
        tutorial_text = text
    pending_payment_ctx.pop(uid, None)
    user_states.pop(uid, None)


# ---------- 59) /addtutorial ----------
@bot.message_handler(commands=["addtutorial"])
def cmd_addtutorial(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    bot.send_message(message.chat.id, "Send tutorial text or video link:")
    user_states[message.from_user.id] = "addtutorial_value"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "addtutorial_value")
def handle_addtutorial_value(message: types.Message):
    global tutorial_text
    uid = message.from_user.id
    tutorial_text = message.text
    custom_texts["tutorial"] = tutorial_text
    bot.send_message(uid, "📚 Tutorial added!", reply_markup=kb_main())
    user_states.pop(uid, None)


# ---------- 60) /removetutorial ----------
@bot.message_handler(commands=["removetutorial"])
def cmd_removetutorial(message: types.Message):
    if message.from_user.id not in admins and message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    global tutorial_text
    tutorial_text = None
    custom_texts.pop("tutorial", None)
    bot.send_message(message.chat.id, "❌ Tutorial removed successfully.", reply_markup=kb_main())


# ---------- 63) /userscount already above
# ---------- 64–66: offbot/onbot/reset already above
# ---------- RESET SYSTEM (66) ----------
@bot.message_handler(commands=["reset"])
def cmd_reset_system(message: types.Message):
    if message.from_user.id not in super_admins and message.from_user.id != MAIN_ADMIN_ID:
        bot.reply_to(message, "❌ Permission denied")
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Yes", "No")
    bot.send_message(message.chat.id, "⚠️ Are you sure you want to reset system temp data?\nYes / No", reply_markup=kb)
    user_states[message.from_user.id] = "reset_system_confirm"


@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "reset_system_confirm")
def handle_reset_system_confirm(message: types.Message):
    uid = message.from_user.id
    choice = message.text.strip()
    if choice == "No":
        bot.send_message(uid, "❌ Cancelled.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    if choice != "Yes":
        bot.send_message(uid, "Invalid reply.", reply_markup=kb_main())
        user_states.pop(uid, None)
        return
    for o in orders.values():
        if o["status"] == "Pending":
            o["status"] = "ResetCleared"
    notify_stats.clear()
    user_states.clear()
    pending_payment_ctx.clear()
    bot.send_message(uid, "🔄 System reset successfully.", reply_markup=kb_main())


# ---------- RUN ----------
if __name__ == "__main__":
    print("POWER POINT BREAK PREMIUM STORE BOT — DEMO 1–67 FINAL")
    bot.infinity_polling()
