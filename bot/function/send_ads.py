import asyncio
import logging
import time
from aiogram.types import Message
from loader import db, bot

def init_broadcast_settings(total, admin_id, broadcast_type):
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
        db.insert_settings(admin_id, "broadcast_status", "active")
    except Exception:
        db.update_settings_key(admin_id, "broadcast_status", "active")
    try:
        db.insert_settings(admin_id, "broadcast_start_id", "0")
    except Exception:
        db.update_settings_key(admin_id, "broadcast_start_id", "0")
    try:
        db.insert_settings(admin_id, "broadcast_admin_id", str(admin_id))
    except Exception:
        db.update_settings_key(admin_id, "broadcast_admin_id", str(admin_id))
    try:
        db.insert_settings(admin_id, "broadcast_type", str(broadcast_type))
    except Exception:
        db.update_settings_key(admin_id, "broadcast_type", str(broadcast_type))


async def send_ads_to_all(message: Message):
    try:
        broadcast_start_id = int(db.select_setting("broadcast_start_id"))
        broadcast_total = int(db.select_setting("broadcast_total"))
        broadcast_sent = int(db.select_setting("broadcast_sent"))
        broadcast_fail = int(db.select_setting("broadcast_fail"))
        broadcast_start_time = float(db.select_setting("broadcast_start_time"))
        broadcast_status = db.select_setting("broadcast_status")
        broadcast_admin_id = int(db.select_setting("broadcast_admin_id"))
        broadcast_type = db.select_setting("broadcast_type")
        
        while broadcast_status == "active":
            broadcast_status = db.select_setting("broadcast_status")
            if broadcast_status == "inactive":
                break

            if broadcast_sent + broadcast_fail >= broadcast_total:
                db.update_settings_key(broadcast_admin_id, "broadcast_status", "stop")
                break

            broadcast_end_id = broadcast_start_id + 100

            if broadcast_type == 'users':
                users_data = db.select_users_by_id(start_id=broadcast_start_id, end_id=broadcast_end_id)
            elif broadcast_type == 'admin':
                users_data = db.select_admins_by_id(start_id=broadcast_start_id, end_id=broadcast_end_id)
            else:
                logging.error("Noma'lum broadcast_type: %s", broadcast_type)
                break

            batch_start_time = time.time()
            
            for user in users_data:
                try:
                    await bot.copy_message(
                        chat_id=user['user_id'],
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                    broadcast_sent += 1
                except Exception as e:
                    logging.error("Xabar yuborishda xato, user %s: %s", user['user_id'], e)
                    broadcast_fail += 1

            db.update_settings_key(broadcast_admin_id, "broadcast_sent", str(broadcast_sent))
            db.update_settings_key(broadcast_admin_id, "broadcast_fail", str(broadcast_fail))
            db.update_settings_key(broadcast_admin_id, "broadcast_start_id", str(broadcast_end_id))
            
            batch_duration = time.time() - batch_start_time
            logging.info("Batch davomiyligi: %.2f soniya", batch_duration)
            
            await asyncio.sleep(max(5, 60 - batch_duration))
            
            broadcast_status = db.select_setting("broadcast_status")
        
        total_time = time.time() - broadcast_start_time
        report_text = (
            f"📊 Broadcast yakunlandi.\n"
            f"Send: {broadcast_sent} ({broadcast_sent / broadcast_total * 100:.2f}%)\n"
            f"Fail: {broadcast_fail} ({broadcast_fail / broadcast_total * 100:.2f}%)\n"
            f"Jami foydalanuvchilar: {broadcast_total}\n"
            f"Umumiy vaqt: {total_time:.2f} soniya\n"
        )
        try:
            await bot.send_message(chat_id=broadcast_admin_id, text=report_text)
        except Exception as e:
            logging.error("Hisobot yuborishda xato: %s", e)
            
    except Exception as e:
        logging.error("send_ads_to_all funksiyasida xato: %s", e)
