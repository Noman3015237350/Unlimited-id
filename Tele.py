‎‎import os
‎import sys
‎from pathlib import Path
‎import telebot
‎
‎# ----------------- Configuration -----------------
‎# Set your Telegram bot token here
‎TOKEN = os.getenv("8114485296:AAGDPMLUltxX9nOUGvHxNtgkpgKOJW2lh1E") or "YOUR_BOT_TOKEN_HERE"
‎
‎# Initialize bot
‎bot = telebot.TeleBot(TOKEN)
‎
‎# Add current directory to Python path
‎current_dir = Path(__file__).parent
‎sys.path.insert(0, str(current_dir))
‎
‎# ----------------- Load fchk Module -----------------
‎try:
‎    import fchk
‎except ImportError as e:
‎    print(f"Error importing fchk module: {e}")
‎    sys.exit(1)
‎
‎# Utility to list callable functions
‎def get_fchk_functions():
‎    return [x for x in dir(fchk) if callable(getattr(fchk, x)) and not x.startswith("_")]
‎
‎# ----------------- Bot Handlers -----------------
‎@bot.message_handler(commands=['start'])
‎def start(message):
‎    funcs = get_fchk_functions()
‎    response = "🤖 fchk Bot Ready!\nAvailable commands from fchk module:\n"
‎    for f in funcs:
‎        response += f"- /{f}\n"
‎    bot.reply_to(message, response)
‎
‎# Dynamically create handlers for each function
‎for func_name in get_fchk_functions():
‎    def make_handler(name):
‎        def handler(message):
‎            try:
‎                func = getattr(fchk, name)
‎                # Note: Assuming fchk functions take no arguments for simplicity.
‎                # If they require args, this part needs modification.
‎                result = func() 
‎                bot.reply_to(message, f"✅ Function '{name}' executed!\nResult:\n{result}")
‎            except Exception as e:
‎                bot.reply_to(message, f"❌ Error executing '{name}': {e}")
‎        return handler
‎    # Register the handler function to the command (e.g., /check_facebook_account)
‎    bot.message_handler(commands=[func_name])(make_handler(func_name))
‎
‎# Catch-all for unknown commands
‎@bot.message_handler(func=lambda m: True)
‎def unknown(message):
‎    bot.reply_to(message, "❌ Unknown command. Type /start to see available commands.")
‎
‎# ----------------- Start Bot -----------------
‎if __name__ == "__main__":
‎    print("🤖 fchk Telegram Bot running...")
‎    bot.infinity_polling()
