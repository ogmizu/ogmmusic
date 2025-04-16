import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

# 🔐 токены
TELEGRAM_TOKEN = '7686855161:AAGbqBExB0RxCDOmDWRDN2UxsrEOLpFNO3U'
SPOTIFY_CLIENT_ID = 'cb965f1eaae44f73aed751f3cd56b1da'
SPOTIFY_CLIENT_SECRET = '51e42de85525450aa620ddc35f8e63a0'

# 🎵 подключение к Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# 🤖 инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 🎛️ клавиатура снизу
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🎧 Рандом"), KeyboardButton("🔥 Зарубежный рэп"))
    markup.row(KeyboardButton("😌 Спокойное"), KeyboardButton("💔 Грустное"))
    markup.row(KeyboardButton("СНГ рэп"))
    return markup

# 🔍 получить рандомный трек
def get_random_track(search_query, sent_tracks):
    results = sp.search(q=search_query, type='track', limit=50)
    tracks = results.get('tracks', {}).get('items', [])

    if not tracks:
        return None

    # фильтруем по дате релиза если возможно
    tracks = sorted(tracks, key=lambda x: x['album']['release_date'], reverse=True)

    # ищем трек, который еще не был отправлен
    new_tracks = [track for track in tracks if track['id'] not in sent_tracks]

    if not new_tracks:
        return None

    track = random.choice(new_tracks[:20])  # выбираем из топ-20 свежих
    name = track['name']
    artists = ', '.join([artist['name'] for artist in track['artists']])
    url = track['external_urls']['spotify']
    image = track['album']['images'][0]['url'] if track['album']['images'] else None

    # добавляем трек в список отправленных
    sent_tracks.add(track['id'])

    return f"*{name}* — _{artists}_\n[Слушать в Spotify]({url})", image

# 🔘 соответствие кнопок и запросов
query_map = {
    "🎧 Рандом": "us rap 2025 playlist",
    "😌 Спокойное": "chill lofi",
    "🔥 Зарубежный рэп": "travis scott,playboi carti,lil tecca,ken karson",
    "СНГ рэп": "трэп новые 2025, популярный реп 2025",
    "💔 Грустное": "sad songs"
}


# 🟢 старт
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "привет! я бот, который подбирает музыку под настроение 🎵\n\nвыбери один из жанров или настроений ниже 👇",
        reply_markup=main_menu()
    )

# 📩 любое сообщение
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_input = message.text.strip()

    if user_input not in query_map:
        bot.send_message(message.chat.id, "нажми одну из кнопок снизу", reply_markup=main_menu())
        return

    search_query = query_map[user_input]
    bot.send_message(message.chat.id, "вот тебе пара песен под настроение 🎶")

    # создаем множество для отправленных треков
    if not hasattr(handle_text, "sent_tracks"):
        handle_text.sent_tracks = set()

    track_info = get_random_track(search_query, handle_text.sent_tracks)
    if track_info:
        text, img_url = track_info
        if img_url:
            bot.send_photo(message.chat.id, img_url, caption=text, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "не удалось найти новый трек 😿")

# 🚀 запуск
bot.polling(none_stop=True)