# --- Auto Library Installation ---
import sys
import subprocess
import os

required_libs = ['pyTelegramBotAPI', 'Pillow', 'exifread']
for lib in required_libs:
    try:
        __import__(lib if lib != 'pyTelegramBotAPI' else 'telebot')
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])

os.system('cls' if os.name == 'nt' else 'clear')
print("Script Is Running Successfully\n\nTool By Scorpion Hacking Group\nDeveloped by >>> Scorpion Yug & Zara")

# --- Telegram Bot Code ---
import telebot
from telebot import types
from PIL import Image
import exifread
from io import BytesIO

# --- Bot Token Input from Terminal with Validation ---
while True:
    BOT_TOKEN = input("🔑 Enter your Telegram Bot Token: ").strip()
    if BOT_TOKEN:
        try:
            bot = telebot.TeleBot(BOT_TOKEN)
            # Test token by calling get_me()
            bot.get_me()
            break
        except Exception as e:
            print("❌ Invalid Bot Token! Please try again.")
    else:
        print("❌ Token cannot be empty. Please enter a valid token.")

def create_welcome_buttons():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/ScorpionHackingGroup"),
        types.InlineKeyboardButton("💬 Join Chat", url="https://t.me/ScorpionHackingGroupChat")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        welcome_text = (
            "👋 <b>Welcome!</b>\n\n"
            "I'm <b>Photo Metadata Extractor</b> 🤖\n"
            "Send me a <b>photo as a file</b> (not compressed), and I'll show you its hidden metadata!\n\n"
            "🔗 <i>Join our community for more tools:</i>"
        )
        bot.send_message(
            message.chat.id,
            welcome_text,
            parse_mode='HTML',
            reply_markup=create_welcome_buttons()
        )
    except Exception as e:
        print(f"[ERROR] Failed to send welcome message: {e}")

@bot.message_handler(content_types=['photo', 'document'])
def handle_file(message):
    try:
        # --- File Type Handling ---
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            file_name = "photo.jpg"
        elif message.content_type == 'document':
            if not message.document.mime_type or not message.document.mime_type.startswith('image/'):
                bot.reply_to(message, "❌ Please send a valid <b>image file</b> (JPG, PNG, etc.).", parse_mode='HTML')
                return
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name or "image"
        else:
            bot.reply_to(message, "❌ Unsupported file type.", parse_mode='HTML')
            return

        # --- Download File ---
        try:
            downloaded_file = bot.download_file(file_info.file_path)
        except Exception:
            bot.reply_to(message, "🚫 <b>Failed to download file from Telegram servers.</b>", parse_mode='HTML')
            return

        # --- Verify Image ---
        try:
            img = Image.open(BytesIO(downloaded_file))
            img.verify()
        except Exception:
            bot.reply_to(message, "❌ The file is not a valid image. Please send a <b>JPG</b> or <b>PNG</b> as a file.", parse_mode='HTML')
            return

        # --- Prepare for EXIF Extraction ---
        image_stream = BytesIO(downloaded_file)
        image_stream.name = file_name

        # --- Extract EXIF Data ---
        try:
            exif_data = exifread.process_file(image_stream, details=True)
        except Exception:
            bot.reply_to(message, "🚫 <b>Failed to extract metadata from the image.</b>", parse_mode='HTML')
            return

        if exif_data:
            metadata = "📸 <b>Photo Metadata:</b>\n\n"
            for tag, value in exif_data.items():
                metadata += f"🔹 <b>{tag}</b>: {value}\n"
        else:
            metadata = (
                "⚠️ <b>No metadata found.</b>\n"
                "This usually happens because many social apps (like Telegram, WhatsApp, etc.) "
                "remove metadata from photos sent as compressed images.\n\n"
                "👉 <b>To extract metadata, please send the original photo as a <u>document</u> (not as a photo message).</b>"
            )

        bot.send_message(message.chat.id, metadata, parse_mode='HTML')
        bot.send_message(
            message.chat.id,
            "<b>Thanks to @ScorpionYug & Zara 💗</b>",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            "🚫 <b>Unexpected error processing file.</b> Please try again later.",
            parse_mode='HTML'
        )
        print(f"[ERROR] File handling failed: {e}")

@bot.message_handler(func=lambda message: True)
def fallback(message):
    try:
        bot.send_message(
            message.chat.id,
            "❓ <b>Send me a photo as a file</b> (not compressed) to extract its metadata.",
            parse_mode='HTML',
            reply_markup=create_welcome_buttons()
        )
    except Exception as e:
        print(f"[ERROR] Fallback message failed: {e}")

try:
    bot.infinity_polling()
except Exception as e:
    print(f"[FATAL ERROR] Bot polling crashed: {e}")
    
