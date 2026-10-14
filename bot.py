import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- CONFIGURATION ---
BOT_TOKEN = "8924381339:AAHVou8YI6_emA5VjktlXkEJzIX3oP6zrtI"
ADMIN_USERNAME = "kikolxd"
ADMIN_CHAT_ID = None  # Populated when admin first clicks /start

# Minimal Database Simulation
users_db = {}  # { user_id: {"main_balance": 0.0, "bonus_balance": 10.0, "username": "@..."} }

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user.username == ADMIN_USERNAME:
        global ADMIN_CHAT_ID
        ADMIN_CHAT_ID = user_id

    # Onboarding & Welcome Bonus (10 ETB)
    if user_id not in users_db:
        users_db[user_id] = {
            "main_balance": 0.0,
            "bonus_balance": 10.0, # 10 ETB Sign-up bonus
            "username": f"@{user.username}" if user.username else user.first_name
        }

    keyboard = [
        [InlineKeyboardButton("🎮 የመወራረጃ ክፍሎች (Stakes)", callback_data="btn_stakes")],
        [InlineKeyboardButton("💳 ተቀማጭ (Deposit)", callback_data="btn_deposit"), InlineKeyboardButton("🏧 ወጪ ማድረግ (Withdraw)", callback_data="btn_withdraw")],
        [InlineKeyboardButton("👥 ጋብዘው ያትርፉ (15% Referral)", callback_data="btn_referral"), InlineKeyboardButton("🎧 Support", url="https://t.me/cherekabingosupport")]
    ]

    welcome_text = (
        f"🌕 **እንኳን ወደ ቸረቃ ቢንጎ በደህና መጡ!** 🌕\n\n"
        f"🎁 **የ 10 ETB የእንኳን ደህና መጡ ቦነስ ተሰጥቶዎታል!**\n\n"
        f"💵 Main Balance: `{users_db[user_id]['main_balance']:.2f} ETB`\n"
        f"🎁 Bonus Balance: `{users_db[user_id]['bonus_balance']:.2f} ETB`\n\n"
        f"እባክዎን ከታች ካሉት አማራጮች አንዱን ይምረጡ:"
    )

    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "btn_stakes":
        text = (
            "🎰 **የመወራረጃ ክፍሎች (Stake Rooms)**\n\n"
            "1️⃣ **5 ETB Room** (Prize: 70% Pool)\n"
            "2️⃣ **10 ETB Room** (Prize: 70% Pool)\n"
            "3️⃣ **20 ETB Room** (Prize: 70% Pool)\n"
            "4️⃣ **50 ETB Room** (Prize: 70% Pool)\n"
        )
        await query.message.edit_text(text, parse_mode="Markdown")

    elif query.data == "btn_deposit":
        dep_text = (
            "💳 **ገንዘብ ለማስገባት (Deposit)**\n\n"
            "📌 **የከፋይ ስም:** Serkalem Araya\n"
            "📱 **Telebirr:** `0953431916`\n"
            "🏦 **CBE:** `1000127511447`\n\n"
            "⚠️ አነስተኛ ተቀማጭ: **10 ETB** (🎁 50% First Deposit Bonus!)\n\n"
            "ከከፈሉ በኋላ የደረሰኝ ፎቶ ወይም የግብይት ቁጥር (Transaction ID) እዚህ ይላኩ!"
        )
        await query.message.edit_text(dep_text, parse_mode="Markdown")

    elif query.data == "btn_withdraw":
        user_bal = users_db[user_id]["main_balance"]
        if user_bal < 100:
            await query.message.edit_text(
                f"❌ **ተቀማጭ ገንዘብዎ በቂ አይደለም!**\n\n"
                f"💵 በአካውንትዎ ላይ ያለው: `{user_bal:.2f} ETB`\n"
                f"⚠️ አነስተኛ የክፍያ ጥያቄ (Minimum Withdrawal) **100 ETB** ነው!",
                parse_mode="Markdown"
            )
        else:
            await query.message.edit_text("🏧 እባክዎን የወጪ ማድረግ የክፍያ ቁጥርዎን እና ስምዎን ያስገቡ:")

# Admin Bonus Command: /addbonus <user_id> <amount>
async def add_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        await update.message.reply_text("❌ Unauthorized.")
        return

    try:
        target_id = int(context.args[0])
        amount = float(context.args[1])
        
        if target_id in users_db:
            users_db[target_id]["main_balance"] += amount
            await update.message.reply_text(f"✅ Added {amount} ETB to {target_id}!")
            await context.bot.send_message(chat_id=target_id, text=f"🎉 Congratulations! You received a bonus of `{amount:.2f} ETB`!", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ User ID not found in database.")
    except Exception:
        await update.message.reply_text("Usage: `/addbonus <user_id> <amount>`", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addbonus", add_bonus))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is live and running...")
    app.run_polling()

if __name__ == "__main__":
    main()
