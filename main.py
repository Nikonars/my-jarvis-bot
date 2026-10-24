import os
import telebot
from telebot import types
from openai import OpenAI

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PROXY_API_KEY = os.environ.get("PROXY_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

ai_client = OpenAI(
    api_key=PROXY_API_KEY,
    base_url="https://proxyapi.ru"
)

MODELS = {
    "gemini": "gemini-1.5-flash",
    "deepseek": "deepseek-chat",
    "gpt": "gpt-4o-mini"
}

USER_SETTINGS = {}

SYSTEM_PROMPT = (
    "Ты — JARVIS, продвинутый текстовый ассистент Тони Старка. "
    "Твой стиль: лаконичный, с тонким ироничным юмором. "
    "К пользователю ВСЕГДА обращаешься 'сэр'. Отвечай емко, структура — списки."
)

def get_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🤖 Google Gemini Flash", callback_data="set_gemini")
    btn2 = types.InlineKeyboardButton("🧠 DeepSeek-V3", callback_data="set_deepseek")
    btn3 = types.InlineKeyboardButton("🟢 OpenAI GPT-4o Mini", callback_data="set_gpt")
    markup.add(btn1, btn2, btn3)
    return markup

@bot.message_handler(commands=['start', 'model'])
def send_welcome(message):
    current_model = USER_SETTINGS.get(message.chat.id, "gemini")
    bot.send_message(
        message.chat.id,
        f"Протокол JARVIS активен, сэр.\nИИ-ядро: **{current_model.upper()}**.",
        reply_markup=get_keyboard(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_"))
def handle_model_selection(call):
    model_key = call.data.split("_")[1]
    USER_SETTINGS[call.message.chat.id] = model_key
    bot.answer_callback_query(call.id, f"Ядро {model_key.upper()} подключено.")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Сэр, активный модуль мыслительных процессов: **{model_key.upper()}**.",
        reply_markup=get_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['text'])
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    user_choice = USER_SETTINGS.get(message.chat.id, "gemini")
    selected_model_string = MODELS[user_choice]
    
    try:
        completion = ai_client.chat.completions.create(
            model=selected_model_string,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, completion.choices.message.content, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Сэр, аппаратная ошибка: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()
