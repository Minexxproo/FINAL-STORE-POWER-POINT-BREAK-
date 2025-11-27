import os

# এখানে সরাসরি token দিতে পারো,
# বা hosting app এ ENV variable হিসেবেও সেট করতে পারো।
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# Admin / super admin settings
SUPER_ADMINS = {123456789}  # your own Telegram ID here
ADMINS = {123456789}        # normal admins (SUPER_ADMINS এর বাইরেও হতে পারে)

# Admin order notification group/channel ID (minus সহ)
ADMIN_ORDER_CHAT_ID = -1001234567890  # change this

# Branding / text
STORE_NAME = "POWER POINT BREAK PREMIUM STORE"
HOSTED_BY = "@PowerPointBreak"
SUPPORT_USERNAME = "@YourSupportUsername"
ADMIN_SUPPORT_USERNAME = "@MinexxProo"

# Order ID prefix
ORDER_PREFIX = "CG-"

# bKash number
BKASH_NUMBER = "01877576843"

# Crypto info (simple text)
CRYPTO_TEXT = (
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
    f"📩 Crypto Payment Please Contact Admin: 👉 {ADMIN_SUPPORT_USERNAME}"
)
