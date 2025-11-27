import re
from datetime import datetime

import telebot
from telebot.types import Message, CallbackQuery

import config
from db import (
    init_db,
    get_or_create_user,
    get_settings,
    set_bot_on,
    set_mega_offer,
    set_tutorial,
    add_category,
    get_categories,
    add_product,
    get_product,
    add_stock,
    validate_coupon,
    mark_coupon_used,
    create_order,
    update_order_coupon,
    update_order_payment,
    get_order,
    get_orders_by_user,
    get_pending_orders,
    get_next_stock,
    mark_stock_used,
    set_order_status,
    users_count,
)
from keyboards import (
    main_menu_kb,
    categories_kb,
    products_inline_kb,
    product_detail_kb,
    payment_method_kb,
    admin_order_kb,
)

# ---------- INIT ----------
init_db()
bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="HTML")

# Simple in-memory states
pending_payment_state = {}   # user_id -> order_id
pending_reject_state = {}    # admin_id -> order_id


# ---------- HELPERS ----------
def is_admin(user_id: int) -> bool:
    return user_id in config.ADMINS or user_id in config.SUPER_ADMINS


def is_super_admin(user_id: int) -> bool:
    return user_id in config.SUPER_ADMINS


def check_bot_on() -> bool:
    s = get_settings()
    return bool(s["bot_on"])


def off_message_text():
    s = get_settings()
    if s["off_message"]:
        return s["off_message"]
    return (
        "⚠️ Hey dear user, heads up!\n\n"
        "🚧 Our Premium Service is temporarily unavailable due to unexpected issues.\n"
        "🛠️ We’re working super fast to fix everything ASAP.\n\n"
        "⏳ Please hold on — your patience means a lot.\n"
        "🙏 Thank you for staying with us.\n"
        f"🏷 Hosted by: {config.HOSTED_BY}\n"
        f"📞 Support: {config.ADMIN_SUPPORT_USERNAME}"
    )


def on_message_text():
    s = get_settings()
    if s["on_message"]:
        return s["on_message"]
    return (
        "✨ Our services are LIVE again! ✨\n\n"
        "🚀 You can now place orders anytime.\n"
        "💛 We always deliver top-quality service.\n"
        "🙏 Thank you for trusting us!\n\n"
        f"🏷 Hosted by: {config.HOSTED_BY}\n"
        f"📞 Admin Support: {config.ADMIN_SUPPORT_USERNAME}"
    )


def ensure_user(message: Message):
    user = message.from_user
    return get_or_create_user(user.id, user.username, user.full_name or user.first_name)


# ---------- USER COMMANDS ----------

@bot.message_handler(commands=["start"])
def cmd_start(message: Message):
    user = ensure_user(message)
    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"⭐⚡ <b>{config.STORE_NAME}</b> ⚡⭐\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"👋 Welcome <b>{user['full_name']}</b>!\n\n"
        f"This is <b>{config.STORE_NAME}</b>\n"
        "💎 Premium Accounts • 💰 Lowest Price • ⚡ Fast Delivery • 🔒 Secure Service\n\n"
        "👉 Enter Store:\n"
        "/openstore\n\n"
        "<b>👤 User Info:</b>\n"
        f"🆔 User ID: <code>{user['tg_id']}</code>\n"
        f"🔗 Username: @{message.from_user.username or 'N/A'}\n\n"
        f"📞 Support: {config.SUPPORT_USERNAME}\n"
        f"🏷 Hosted by: {config.HOSTED_BY}"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["openstore"])
def cmd_openstore(message: Message):
    if not check_bot_on() and not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, off_message_text())
        return

    user = ensure_user(message)
    # simple registration: যদি DB-তে পাওয়া যায় ধরব registered
    # এখানে আলাদা "registered" flag লাগালে later যোগ করতে পারো
    text = (
        "🔐 <b>ACCOUNT REQUIRED</b>\n"
        "To access the store, please Sign Up or Log In."
    )
    # for now ধরে নিচ্ছি সব user-ই registered, কিন্তু পূর্ণতা আনতে চাইলে
    # users table-এ আলাদা column দিয়ে check করতে পারো।
    # সহজ ভাবে: new হলে Sign Up দেখাই, পুরনো হলে main menu
    if user["total_orders"] == 0 and user["pending_orders"] == 0:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("🆕 Sign Up", callback_data="signup"),
            telebot.types.InlineKeyboardButton("🔓 Log In", callback_data="login"),
        )
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "🏠 MAIN MENU", reply_markup=main_menu_kb())


# ---------- CALLBACKS: SIGNUP / LOGIN ----------

@bot.callback_query_handler(func=lambda c: c.data in ["signup", "login"])
def cb_signup_login(call: CallbackQuery):
    user = ensure_user(call.message)
    if call.data == "signup":
        text = (
            "📝 <b>SIGN UP</b>\n\n"
            f"Name: {user['full_name']}\n"
            f"Username: @{call.from_user.username or 'N/A'}\n"
            f"User ID: {user['tg_id']}\n\n"
            "Confirm Sign Up?"
        )
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("✅ Confirm Sign Up", callback_data="signup_confirm"),
            telebot.types.InlineKeyboardButton("❌ Cancel", callback_data="signup_cancel"),
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        # LOGIN
        text = f"🔓 Welcome back, {user['full_name']}!\nTap MAIN MENU to continue."
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, "🏠 MAIN MENU", reply_markup=main_menu_kb())
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("signup_"))
def cb_signup_confirm(call: CallbackQuery):
    if call.data == "signup_confirm":
        bot.edit_message_text("✅ Account created!\nUse /openstore again.", call.message.chat.id, call.message.message_id)
    else:
        bot.edit_message_text("❌ Sign Up cancelled.\nUse /openstore again.", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)


# ---------- TEXT HANDLERS: MAIN MENU BUTTONS ----------

@bot.message_handler(func=lambda m: m.text == "🛒 All Categories")
def btn_all_categories(message: Message):
    if not check_bot_on() and not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, off_message_text())
        return
    if not get_categories():
        bot.send_message(message.chat.id, "📂 No category found. Please contact admin.")
        return
    bot.send_message(message.chat.id, "📂 <b>SELECT A CATEGORY</b>", reply_markup=categories_kb())


@bot.message_handler(func=lambda m: m.text == "⬅ Back")
def btn_back_to_menu(message: Message):
    bot.send_message(message.chat.id, "🏠 MAIN MENU", reply_markup=main_menu_kb())


@bot.message_handler(func=lambda m: m.text == "🪪 My Profile")
def btn_my_profile(message: Message):
    user = ensure_user(message)
    orders = get_orders_by_user(user["id"])
    completed = len([o for o in orders if o["status"] == "approved"])
    pending = len([o for o in orders if o["status"] == "pending_admin"])
    text = (
        "🪪 <b>MY PROFILE</b>\n\n"
        f"Name: {user['full_name']}\n"
        f"Username: @{message.from_user.username or 'N/A'}\n"
        f"User ID: {user['tg_id']}\n\n"
        f"Joined: {user['joined_at']}\n\n"
        f"Total Orders: {len(orders)}\n"
        f"Completed: {completed}\n"
        f"Pending: {pending} ⏳\n\n"
        "Badge: 👑 VIP MAX\n"
        f"Support: {config.SUPPORT_USERNAME}"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "🛍 Active Orders")
def btn_active_orders(message: Message):
    user = ensure_user(message)
    orders = get_orders_by_user(user["id"], status_filter="pending_admin")
    if not orders:
        bot.send_message(message.chat.id, "🛍 No active orders right now.")
        return
    lines = ["🛍 <b>ACTIVE ORDERS</b>\n"]
    for o in orders:
        p = get_product(o["product_id"])
        lines.append(
            f"Order ID: {config.ORDER_PREFIX}{o['order_code']}\n"
            f"Product: {p['name']}\n"
            f"Amount: ৳{o['final_price']}\n"
            "⏳ Status: Waiting for Admin Approval\n"
            "----------------------"
        )
    bot.send_message(message.chat.id, "\n".join(lines))


@bot.message_handler(func=lambda m: m.text == "⏳ Pending Orders")
def btn_pending_orders(message: Message):
    btn_active_orders(message)


@bot.message_handler(func=lambda m: m.text == "📦 My Orders")
def btn_my_orders(message: Message):
    user = ensure_user(message)
    orders = get_orders_by_user(user["id"])
    if not orders:
        bot.send_message(message.chat.id, "📦 No orders yet.")
        return
    lines = ["📦 <b>MY ORDERS HISTORY</b>\n"]
    for o in orders:
        p = get_product(o["product_id"])
        lines.append(
            f"Order ID: {config.ORDER_PREFIX}{o['order_code']}\n"
            f"Product: {p['name']}\n"
            f"Amount: ৳{o['final_price']}\n"
            f"Status: {o['status']}\n"
            f"Time: {o['created_at']}\n"
            "----------------------"
        )
    bot.send_message(message.chat.id, "\n".join(lines))


@bot.message_handler(func=lambda m: m.text == "🆘 Help Center")
def btn_help_center(message: Message):
    text = (
        "🆘 <b>SUPPORT CENTER</b>\n\n"
        "💬 If you have any questions or face any kind of problem,\n"
        "📩 just message us in the inbox.\n\n"
        "🛠️ We are always here and will try our best to solve your issue.\n"
        "🙏 Thank you so much for staying with us!\n\n"
        f"👨‍💻 Admin Support: {config.SUPPORT_USERNAME}\n\n"
        f"⚡ Hosted by: {config.STORE_NAME}\n"
        "Response Time: 1–15 minutes ⏱️"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: m.text == "📚 Tutorial")
def btn_tutorial(message: Message):
    s = get_settings()
    if s["tutorial"]:
        bot.send_message(message.chat.id, s["tutorial"])
    else:
        bot.send_message(message.chat.id, "📚 No tutorial added yet")


@bot.message_handler(func=lambda m: m.text == "🎁 Mega Offer")
def btn_mega_offer(message: Message):
    s = get_settings()
    if s["mega_offer"]:
        bot.send_message(message.chat.id, f"🎁 NEW MEGA OFFER\n{s['mega_offer']}")
    else:
        bot.send_message(message.chat.id, "🎁 No mega offer currently.")


# ---------- CATEGORY / PRODUCT BROWSING ----------

@bot.message_handler(func=lambda m: re.match(r"^\d+\.", m.text or ""))
def handle_category_selection(message: Message):
    # text like "1. ChatGPT & AI"
    idx = int(message.text.split(".")[0])
    cats = get_categories()
    cat = next((c for c in cats if c["id"] == idx), None)
    if not cat:
        bot.send_message(message.chat.id, "⚠ Invalid category.")
        return
    bot.send_message(
        message.chat.id,
        f"🛍 CATEGORY: {cat['name']}",
        reply_markup=None,
    )
    bot.send_message(
        message.chat.id,
        "Choose a product:",
        reply_markup=None,
        reply_markup=products_inline_kb(cat["id"]),
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("product:"))
def cb_product_details(call: CallbackQuery):
    product_id = int(call.data.split(":")[1])
    p = get_product(product_id)
    if not p:
        bot.answer_callback_query(call.id, "Product not found", show_alert=True)
        return
    stock = p["stock_count"]
    if stock <= 0:
        stock_text = "📛 OUT OF STOCK"
    else:
        stock_text = f"📊 Stock: {stock} Available"

    text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"🤖 {p['name'].upper()}\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"⏳ Duration: {p['duration']}\n"
        f"💰 Price: ৳{p['price']}\n"
        f"{stock_text}\n\n"
        "⭐ Benefits:\n"
        "• GPT-4 Full Access\n"
        "• Ultra Fast Speed\n"
        "• Priority Server"
    )
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=product_detail_kb(product_id),
    )
    bot.answer_callback_query(call.id)


# ---------- BUY + COUPON FLOW ----------

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy:"))
def cb_buy(call: CallbackQuery):
    product_id = int(call.data.split(":")[1])
    p = get_product(product_id)
    if not p:
        bot.answer_callback_query(call.id, "Product not found", show_alert=True)
        return
    if p["stock_count"] <= 0:
        bot.answer_callback_query(call.id, "📛 OUT OF STOCK", show_alert=True)
        return
    user = ensure_user(call.message)
    order_id = create_order(user["id"], product_id, p["price"])
    pending_payment_state[call.from_user.id] = order_id
    text = (
        "💳 <b>PAYMENT METHOD</b>\n\n"
        f"You're buying:\n🛒 {p['name']}\n"
        f"💰 Payable Amount: ৳{p['price']}"
    )
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=payment_method_kb(order_id),
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("coupon:"))
def cb_coupon(call: CallbackQuery):
    product_id = int(call.data.split(":")[1])
    user = ensure_user(call.message)
    # দ্রুত সমাধান: নতুন order বানিয়ে রাখি coupon apply এর জন্য, পরে payment এ reuse করব
    p = get_product(product_id)
    if not p:
        bot.answer_callback_query(call.id, "Product not found", show_alert=True)
        return
    order_id = create_order(user["id"], product_id, p["price"])
    pending_payment_state[call.from_user.id] = order_id
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        "🎟 APPLY COUPON\n\nPlease send your coupon code:",
    )
    bot.register_next_step_handler(msg, handle_coupon_code, order_id, product_id, p["price"])


def handle_coupon_code(message: Message, order_id: int, product_id: int, original_price: int):
    code = message.text.strip()
    now = datetime.now()
    ok, row, reason = validate_coupon(code, product_id, now)
    if not ok:
        status_map = {
            "INVALID": "❌ INVALID COUPON",
            "EXPIRED": "⏳ EXPIRED",
            "USED": "🛑 ALREADY USED",
            "WRONG_PRODUCT": "🚫 NOT VALID FOR THIS PRODUCT",
        }
        bot.send_message(message.chat.id, status_map.get(reason, "❌ Coupon error"))
        return

    discount = row["discount"]
    final_price = max(0, original_price - discount)
    update_order_coupon(order_id, code, discount, final_price)
    mark_coupon_used(row["id"])

    text = (
        "🎉 COUPON APPLIED SUCCESSFULLY! 🎉\n\n"
        f"Coupon: {code}\n"
        f"💵 Discount: ৳{discount}\n"
        f"💰 Original Price: ৳{original_price}\n"
        f"✅ Payable: ৳{final_price}"
    )
    bot.send_message(message.chat.id, text)
    p = get_product(product_id)
    msg = bot.send_message(
        message.chat.id,
        "Now choose payment method:",
        reply_markup=payment_method_kb(order_id),
    )
    pending_payment_state[message.from_user.id] = order_id


# ---------- PAYMENT METHOD ----------

@bot.callback_query_handler(func=lambda c: c.data.startswith("pay:"))
def cb_payment_method(call: CallbackQuery):
    _, order_id_str, method = call.data.split(":")
    order_id = int(order_id_str)
    order = get_order(order_id)
    if not order:
        bot.answer_callback_query(call.id, "Order not found", show_alert=True)
        return
    product = get_product(order["product_id"])
    if method == "crypto":
        bot.edit_message_text(
            config.CRYPTO_TEXT + "\n\n⬅ Back to choose other method using /openstore.",
            call.message.chat.id,
            call.message.message_id,
        )
        bot.answer_callback_query(call.id)
        return

    # bkash / nagad / others – এখানে একই format ব্যবহার করব
    text = (
        f"🟣 {method.upper()} PAYMENT\n\n"
        f"You're purchasing:\n🛒 {product['name']}\n\n"
        f"💰 Original Price: ৳{order['original_price']}\n"
        f"🎟 Coupon: {order['coupon_code'] or 'None'}\n"
        f"💵 Discount: ৳{order['discount']}\n"
        f"✅ Payable: ৳{order['final_price']}\n\n"
        f"Send Money to:\n"
        f"📲 {config.BKASH_NUMBER} ({method.capitalize()} Personal)\n\n"
        "⚠ RULES:\n"
        "👉 Only Send Money allowed\n"
        "❌ Mobile Recharge NOT accepted\n\n"
        "Send info in format:\n"
        "Sender | Amount | TXID\n\n"
        "Example:\n"
        "01811112222 | 499 | TX9L92QE0"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
    pending_payment_state[call.from_user.id] = order_id
    msg = bot.send_message(call.message.chat.id, "Please send payment details in the correct format:")
    bot.register_next_step_handler(msg, handle_payment_details, order_id, method)
    bot.answer_callback_query(call.id)


def handle_payment_details(message: Message, order_id: int, method: str):
    text = message.text
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 3:
        bot.send_message(message.chat.id, "⚠ Invalid Format\n\nCorrect format:\nSender | Amount | TXID")
        return
    sender, amount_str, txid = parts
    if not amount_str.isdigit():
        bot.send_message(message.chat.id, "⚠ Invalid amount.")
        return
    amount = int(amount_str)
    order = get_order(order_id)
    if not order:
        bot.send_message(message.chat.id, "Order not found.")
        return
    update_order_payment(order_id, method, sender, amount, txid, status="pending_admin")

    # Send to admin group
    product = get_product(order["product_id"])
    txt_admin = (
        "📦 NEW ORDER RECEIVED 🔔\n\n"
        f"Order ID: {config.ORDER_PREFIX}{order['order_code']}\n"
        f"Username: @{message.from_user.username or 'N/A'}\n"
        f"User ID: {message.from_user.id}\n\n"
        f"🛒 Product: {product['name']}\n"
        f"💰 Original Amount: ৳{order['original_price']}\n"
        f"🎟 Coupon: {order['coupon_code'] or 'None'}\n"
        f"💵 Discount: ৳{order['discount']}\n"
        f"✅ Final Amount: ৳{order['final_price']}\n\n"
        f"💳 Payment Method: {method}\n"
        f"📲 Sender: {sender}\n"
        f"🔖 TXID: {txid}\n\n"
        f"🕒 Date & Time: {datetime.now().strftime('%d-%b-%Y | %I:%M %p')}"
    )
    bot.send_message(config.ADMIN_ORDER_CHAT_ID, txt_admin, reply_markup=admin_order_kb(order_id))

    # User final sms
    text_user = (
        "🎉 Your order request has been submitted! 🎉\n\n"
        f"📅 Date/Time: {datetime.now().strftime('%d-%b-%Y | %I:%M %p')}\n"
        f"🧾 Order ID: {config.ORDER_PREFIX}{order['order_code']}\n"
        "⏳ Status: Waiting for Admin approval… (⏳ Pending)\n\n"
        f"🛒 Product: {product['name']}\n"
        f"💰 Original Price: ৳{order['original_price']}\n"
        f"🎟 Coupon: {order['coupon_code'] or 'None'}\n"
        f"💵 Discount: ৳{order['discount']}\n"
        f"✅ Payable Amount: ৳{order['final_price']}\n"
        f"👉 Payment Sender Number: {sender}\n\n"
        "⏱ Estimated Approval Time: 1–15 minutes\n"
        f"📞 Admin Support: {config.SUPPORT_USERNAME}\n"
        f"🏷 Hosted by: {config.HOSTED_BY}\n\n"
        "❤️ Thank you for choosing Power Point Break! ❤️"
    )
    bot.send_message(message.chat.id, text_user)


# ---------- ADMIN INLINE: APPROVE / REJECT ----------

@bot.callback_query_handler(func=lambda c: c.data.startswith("admin_"))
def cb_admin_order(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "Permission denied", show_alert=True)
        return
    action, order_id_str = call.data.split(":")
    order_id = int(order_id_str)
    order = get_order(order_id)
    if not order:
        bot.answer_callback_query(call.id, "Order not found", show_alert=True)
        return
    if action == "admin_approve":
        # FIFO stock
        stock = get_next_stock(order["product_id"])
        if not stock:
            bot.answer_callback_query(call.id, "No stock available!", show_alert=True)
            return
        mark_stock_used(stock["id"])
        set_order_status(order_id, "approved")
        user_id = order["user_id"]
        # find tg_id for user
        # দ্রুত সমাধান: users table থেকে read
        import sqlite3
        from db import get_conn
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT tg_id, username FROM users WHERE id = ?", (user_id,))
        u = cur.fetchone()
        conn.close()
        tg_id = u["tg_id"]
        uname = u["username"]

        product = get_product(order["product_id"])

        # User approved SMS
        txt_user = (
            "🎉✨ CONGRATULATIONS! ✨🎉\n"
            f"Hello Dear @{uname}, your order has been successfully APPROVED! ✅🚀\n\n"
            "Your ChatGPT Plus has been successfully activated! ⚡🔥\n\n"
            "🧾 Order Details:\n"
            "———————————————\n"
            f"📦 Order ID: {config.ORDER_PREFIX}{order['order_code']}\n"
            f"🛒 Product: {product['name']}\n"
            "———————————————\n\n"
            "🔐 Login Credentials:\n"
            f"📧 Email: {stock['email']}\n"
            f"🔑 Password: {stock['password']}\n\n"
            "⚠ IMPORTANT INSTRUCTIONS:\n"
            "• After logging in, please check the account properly\n"
            "• Enable Two-Factor Authentication immediately\n"
            "• Do NOT share this account with anyone\n"
            "• If you face any issue, please report it quickly\n\n"
            f"📞 Admin Support: 👉 {config.SUPPORT_USERNAME}\n\n"
            "🌹 Thank you so much for your order! 🌹"
        )
        bot.send_message(tg_id, txt_user)

        # Admin auto-delivery log
        txt_log = (
            "📦 ORDER DELIVERED (AUTO LOG)\n\n"
            f"User: @{uname}\n"
            f"User ID: {tg_id}\n\n"
            f"Order ID: {config.ORDER_PREFIX}{order['order_code']}\n"
            f"Product: {product['name']}\n\n"
            "🔐 Login:\n"
            f"📧 Email: {stock['email']}\n"
            f"🔑 Password: {stock['password']}\n\n"
            f"Delivered at: 🕒 {datetime.now().strftime('%d-%b-%Y | %I:%M %p')}"
        )
        bot.send_message(config.ADMIN_ORDER_CHAT_ID, txt_log)
        bot.answer_callback_query(call.id, "Order approved")
    else:
        # Reject flow – ask reason
        pending_reject_state[call.from_user.id] = order_id
        msg = bot.send_message(call.message.chat.id, "Please send reject reason:")
        bot.register_next_step_handler(msg, handle_reject_reason, order_id, call.from_user.id)
        bot.answer_callback_query(call.id)


def handle_reject_reason(message: Message, order_id: int, admin_id: int):
    reason = message.text.strip()
    order = get_order(order_id)
    if not order:
        bot.send_message(message.chat.id, "Order not found.")
        return
    set_order_status(order_id, "rejected")

    # user
    from db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT tg_id FROM users WHERE id = ?", (order["user_id"],))
    u = cur.fetchone()
    conn.close()
    tg_id = u["tg_id"]

    txt_user = (
        "❌ Your order has been rejected.\n\n"
        f"Reason: {reason}\n\n"
        "⏳ You have 10 minutes to resubmit correctly.\n\n"
        "Correct Format:\n"
        "Sender | Amount | TXID\n"
        "Example:\n"
        "01811112222 | 499 | TX9L92QE0"
    )
    bot.send_message(tg_id, txt_user)
    bot.send_message(message.chat.id, "User notified about rejection.")


# ---------- ADMIN COMMANDS (BASIC PANEL) ----------

@bot.message_handler(commands=["panel"])
def cmd_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    text = (
        "👑 ADMIN PANEL\n\n"
        "/pendingorders - View pending orders\n"
        "/userscount - Total users\n"
        "/addcategory - Add category\n"
        "/addproduct - Add product\n"
        "/addstock - Add stock\n"
        "/viewstock - View stock\n"
        "/setoffer - Set mega offer\n"
        "/addtutorial - Add tutorial\n"
        "/removetutorial - Remove tutorial\n"
        "/genaretcupun - Generate coupon\n"
        "/offbot - Turn OFF bot\n"
        "/onbot - Turn ON bot"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["pendingorders"])
def cmd_pendingorders(message: Message):
    if not is_admin(message.from_user.id):
        return
    orders = get_pending_orders()
    if not orders:
        bot.send_message(message.chat.id, "⚠️ No pending orders.")
        return
    lines = ["⏳ PENDING ORDERS:\n"]
    for o in orders:
        p = get_product(o["product_id"])
        lines.append(
            f"ID: {o['id']} | {config.ORDER_PREFIX}{o['order_code']} | {p['name']} | ৳{o['final_price']}"
        )
    bot.send_message(message.chat.id, "\n".join(lines))


@bot.message_handler(commands=["userscount"])
def cmd_userscount(message: Message):
    if not is_admin(message.from_user.id):
        return
    n = users_count()
    bot.send_message(message.chat.id, f"👥 TOTAL USERS: {n}")


@bot.message_handler(commands=["offbot"])
def cmd_offbot(message: Message):
    if not is_admin(message.from_user.id):
        return
    set_bot_on(False)
    bot.send_message(message.chat.id, "⚠️ Bot turned OFF.")


@bot.message_handler(commands=["onbot"])
def cmd_onbot(message: Message):
    if not is_admin(message.from_user.id):
        return
    set_bot_on(True)
    bot.send_message(message.chat.id, "✨ Bot is now LIVE again!")


# ---- Add category / product / stock ----

@bot.message_handler(commands=["addcategory"])
def cmd_addcategory(message: Message):
    if not is_admin(message.from_user.id):
        return
    msg = bot.send_message(message.chat.id, "Send new category name:")
    bot.register_next_step_handler(msg, handle_addcategory_name)


def handle_addcategory_name(message: Message):
    name = message.text.strip()
    cid = add_category(name)
    bot.send_message(message.chat.id, f"✅ Category added with ID {cid}")


@bot.message_handler(commands=["addproduct"])
def cmd_addproduct(message: Message):
    if not is_admin(message.from_user.id):
        return
    cats = get_categories()
    if not cats:
        bot.send_message(message.chat.id, "No categories. Use /addcategory first.")
        return
    lines = ["Send product in this format:", "category_id | name | duration | price", "", "Available categories:"]
    for c in cats:
        lines.append(f"{c['id']} - {c['name']}")
    bot.send_message(message.chat.id, "\n".join(lines))
    bot.register_next_step_handler(message, handle_addproduct_data)


def handle_addproduct_data(message: Message):
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) != 4 or not parts[0].isdigit() or not parts[3].isdigit():
        bot.send_message(message.chat.id, "Invalid format.")
        return
    cid = int(parts[0])
    name = parts[1]
    duration = parts[2]
    price = int(parts[3])
    pid = add_product(cid, name, duration, price)
    bot.send_message(message.chat.id, f"✅ Product added with ID {pid}")


@bot.message_handler(commands=["addstock"])
def cmd_addstock(message: Message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "Send stock in this format:\nproduct_id | email | password\n(one account per message)",
    )
    bot.register_next_step_handler(message, handle_addstock_data)


def handle_addstock_data(message: Message):
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) != 3 or not parts[0].isdigit():
        bot.send_message(message.chat.id, "Invalid format.")
        return
    pid = int(parts[0])
    email = parts[1]
    password = parts[2]
    add_stock(pid, email, password)
    bot.send_message(message.chat.id, "✅ Stock added.")


@bot.message_handler(commands=["viewstock"])
def cmd_viewstock(message: Message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(message.chat.id, "Send product_id to view stock:")
    bot.register_next_step_handler(message, handle_viewstock_pid)


def handle_viewstock_pid(message: Message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Invalid ID.")
        return
    pid = int(message.text)
    from db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM stock WHERE product_id = ? AND used = 0", (pid,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        bot.send_message(message.chat.id, "📛 No stock available.")
        return
    lines = [f"Available stock for product {pid}:\n"]
    for r in rows:
        lines.append(f"{r['id']} | {r['email']} | {r['password']}")
    bot.send_message(message.chat.id, "\n".join(lines))


# ---- Offer / Tutorial / Coupon (simple) ----

@bot.message_handler(commands=["setoffer"])
def cmd_setoffer(message: Message):
    if not is_admin(message.from_user.id):
        return
    msg = bot.send_message(message.chat.id, "Send new Mega Offer text (or 'none' to clear):")
    bot.register_next_step_handler(msg, handle_setoffer)


def handle_setoffer(message: Message):
    if message.text.lower().strip() == "none":
        set_mega_offer(None)
        bot.send_message(message.chat.id, "Offer cleared.")
    else:
        set_mega_offer(message.text)
        bot.send_message(message.chat.id, "🎁 Mega Offer updated!")


@bot.message_handler(commands=["addtutorial"])
def cmd_addtutorial(message: Message):
    if not is_admin(message.from_user.id):
        return
    msg = bot.send_message(message.chat.id, "Send tutorial text or video link:")
    bot.register_next_step_handler(msg, handle_addtutorial)


def handle_addtutorial(message: Message):
    set_tutorial(message.text)
    bot.send_message(message.chat.id, "📚 Tutorial added!")


@bot.message_handler(commands=["removetutorial"])
def cmd_removetutorial(message: Message):
    if not is_admin(message.from_user.id):
        return
    set_tutorial(None)
    bot.send_message(message.chat.id, "❌ Tutorial removed.")


@bot.message_handler(commands=["genaretcupun"])
def cmd_generate_coupon(message: Message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(
        message.chat.id,
        "Send coupon info in format:\n"
        "discount | DD-MM-YYYY HH:MM AM/PM\n\n"
        "Example:\n150 | 30-12-2025 11:59 PM\n\n"
        "This will create an ALL PRODUCT coupon (one-time use).",
    )
    bot.register_next_step_handler(message, handle_generate_coupon)


def handle_generate_coupon(message: Message):
    from db import create_coupon
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) != 2 or not parts[0].isdigit():
        bot.send_message(message.chat.id, "Invalid format.")
        return
    discount = int(parts[0])
    expiry = parts[1]
    # Simple random code
    import random
    code = f"POWER-{random.randint(100,999)}-POINT{random.randint(1000,9999)}-BREAK"
    create_coupon(code, discount, expiry, product_id=None, max_uses=1)
    bot.send_message(
        message.chat.id,
        f"🎟 Coupon generated:\n{code}\nDiscount: ৳{discount}\nExpiry: {expiry}",
    )


# ---------- FALLBACK ----------

@bot.message_handler(func=lambda m: True)
def fallback(message: Message):
    bot.send_message(message.chat.id, "Use /start or /openstore to begin.", reply_markup=main_menu_kb())


print("Bot is running...")
bot.infinity_polling()
