import asyncio
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.exceptions import TelegramAPIError
from db.database import Database
from data.config import *


db = Database(host=HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)

# Token va admin identifikatori
API_TOKEN = "1430978281:AAFbdRkUFtw3fVLqbU8_L9KJ-wy_9mwwNS4"
ADMIN_ID = 835558445  # O'zingizning admin ID raqamingiz

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Foydalanuvchilar ro'yxatini oddiy to'plamda saqlaymiz (amaldagi loyihada ma'lumotlar bazasi orqali olib borish tavsiya etiladi)
registered_users = set()

# Avvalgi keltirilgan Database modulidan db obyektini import qiling
# from your_database_module import db
# Misolda biz oldindan yaratilgan `db` obyektidan foydalanamiz

# Broadcast jarayoni uchun 'settings' jadvalidagi kalitlar:
# "broadcast_total", "broadcast_sent", "broadcast_fail", "broadcast_start_time", "broadcast_stop"
# Ushbu funksiyalar orqali settings jadvaliga yozamiz:
def init_broadcast_settings(total, admin_id):
    try:
        db.insert_settings(admin_id, "broadcast_total", str(total))
    except Exception:
        db.update_settings_key(admin_id, "broadcast_total", str(total))
    try:
        db.insert_settings(admin_id, "broadcast_sent", "0")
    except Exception:
        db.update_settings_key(admin_id, "broadcast_sent", "0")
    try:
        db.insert_settings(admin_id, "broadcast_fail", "0")
    except Exception:
        db.update_settings_key(admin_id, "broadcast_fail", "0")
    try:
        db.insert_settings(admin_id, "broadcast_start_time", str(time.time()))
    except Exception:
        db.update_settings_key(admin_id, "broadcast_start_time", str(time.time()))
    try:
        db.insert_settings(admin_id, "broadcast_stop", "0")
    except Exception:
        db.update_settings_key(admin_id, "broadcast_stop", "0")

def update_broadcast_setting(key, value, admin_id=ADMIN_ID):
    try:
        db.update_settings_key(admin_id, key, str(value))
    except Exception as e:
        print("DB update error:", e)

def get_broadcast_setting(key):
    value = db.select_setting(key)
    return value

# /start handler – foydalanuvchini ro'yxatga qo'shish
@dp.message(Command("start"))
async def on_start(message: types.Message):
    registered_users.add(message.from_user.id)
    await message.answer("Botga xush kelibsiz! Siz ro'yxatga olindingiz.")

# Global o'zgaruvchi: broadcasting jarayonining task obyektini saqlash
broadcast_task = None

# /send komandasi – adminning broadcasting jarayonini ishga tushiradi
@dp.message(Command("send"))
async def broadcast_handler(message: types.Message):
    global broadcast_task
    if message.from_user.id != ADMIN_ID:
        return  # Faqat admin uchun
    if not registered_users:
        await message.answer("Hozircha foydalanuvchilar ro'yxati bo'sh.")
        return
    total_users = len(registered_users)
    init_broadcast_settings(total_users, ADMIN_ID)
    await message.answer("✅ Reklama jo'natish boshlandi.")
    broadcast_task = asyncio.create_task(send_ads_to_all(message))

# /status komandasi – adminga real vaqt progressini ko'rsatadi
@dp.message(Command("status"))
async def status_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        total = int(get_broadcast_setting("broadcast_total") or "0")
        sent = int(get_broadcast_setting("broadcast_sent") or "0")
        fail = int(get_broadcast_setting("broadcast_fail") or "0")
        start_time = float(get_broadcast_setting("broadcast_start_time") or time.time())
        current_time = time.time()
        elapsed = current_time - start_time
        processed = sent + fail
        remaining = total - processed
        avg_time = elapsed / processed if processed > 0 else 0
        estimated_remaining = avg_time * remaining
        status_text = (
            f"📊 Broadcast Status:\n"
            f"Jami foydalanuvchilar: {total}\n"
            f"Jo'natilgan: {sent}\n"
            f"Xatoliklar: {fail}\n"
            f"Qayta ishlangan: {processed}\n"
            f"O'tgan vaqt: {int(elapsed)} soniya\n"
            f"Taxminiy qolgan vaqt: {int(estimated_remaining)} soniya"
        )
        await message.answer(status_text)
    except Exception as err:
        await message.answer(err)

# /stop komandasi – admin broadcasting jarayonini to'xtatadi
@dp.message(Command("stop"))
async def stop_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    update_broadcast_setting("broadcast_stop", "1")
    await message.answer("🚫 Broadcast to'xtatildi. Jarayon keyingi iteratsiyada to'xtaydi.")

# Fon vazifasi: barcha foydalanuvchilarga xabar (adminning xabari)ni yuborish
async def send_ads_to_all(admin_message: types.Message):
    total_users = len(registered_users)
    sent_count = 0
    fail_count = 0
    start_time = time.time()
    update_broadcast_setting("broadcast_start_time", start_time)
    # Ro'yxat bo'ylab aylanamiz
    for idx, user_id in enumerate(registered_users, start=1):
        # Agar /stop komandasi orqali broadcast_stop 1 ga o'zgarsa, to'xtatamiz
        if get_broadcast_setting("broadcast_stop") == "1":
            break
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=admin_message.chat.id,
                message_id=admin_message.message_id
            )
            sent_count += 1
        except Exception as err:
            fail_count += 1
        time.sleep(1000000000)
        # Har bir xabar yuborilgandan so'ng progressni yangilaymiz
        update_broadcast_setting("broadcast_sent", sent_count)
        update_broadcast_setting("broadcast_fail", fail_count)
        # Har 100 ta xabardan keyin 60 soniya kutish (daqiqasiga 100 ta tezlik)
        if idx % 100 == 0:
            await asyncio.sleep(60)
    # Yakuniy hisobotni yangilaymiz va adminga jo'natamiz
    update_broadcast_setting("broadcast_sent", sent_count)
    update_broadcast_setting("broadcast_fail", fail_count)
    report_text = (
        f"📊 Broadcast yakunlandi.\n"
        f"Jo'natilgan: {sent_count}\n"
        f"Xatoliklar: {fail_count}\n"
        f"Jami foydalanuvchilar: {total_users}"
    )
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=report_text)
    except Exception:
        pass

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
