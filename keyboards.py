from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from db import get_categories, get_products_by_category
import config


def main_menu_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🛒 All Categories", "🪪 My Profile")
    kb.row("🛍 Active Orders", "📦 My Orders")
    kb.row("⏳ Pending Orders", "🆘 Help Center")
    kb.row("📚 Tutorial", "🎁 Mega Offer")
    return kb


def categories_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    cats = get_categories()
    for c in cats:
        kb.row(f"{c['id']}. {c['name']}")
    kb.row("⬅ Back")
    return kb


def products_inline_kb(category_id: int):
    markup = InlineKeyboardMarkup()
    products = get_products_by_category(category_id)
    for p in products:
        text = f"{p['name']}"
        markup.add(InlineKeyboardButton(text, callback_data=f"product:{p['id']}"))
    markup.add(InlineKeyboardButton("⬅ Back", callback_data=f"back:categories"))
    return markup


def product_detail_kb(product_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🛒 Buy Now", callback_data=f"buy:{product_id}"))
    markup.add(InlineKeyboardButton("🎟 Apply Coupon", callback_data=f"coupon:{product_id}"))
    markup.add(InlineKeyboardButton("⬅ Back", callback_data=f"back:products:{product_id}"))
    return markup


def payment_method_kb(order_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🟣 bKash", callback_data=f"pay:{order_id}:bkash"))
    markup.add(InlineKeyboardButton("🟡 Nagad", callback_data=f"pay:{order_id}:nagad"))
    markup.add(InlineKeyboardButton("🟠 Upay", callback_data=f"pay:{order_id}:upay"))
    markup.add(InlineKeyboardButton("🔵 Rocket", callback_data=f"pay:{order_id}:rocket"))
    markup.add(InlineKeyboardButton("🪙 Crypto (USDT)", callback_data=f"pay:{order_id}:crypto"))
    markup.add(InlineKeyboardButton("⬅ Back", callback_data=f"back:product_from_order:{order_id}"))
    return markup


def admin_order_kb(order_id: int):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve:{order_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject:{order_id}"),
    )
    return markup
