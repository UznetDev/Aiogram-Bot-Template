import json
import logging
from redis import Redis
from datetime import datetime
from typing import Tuple, Optional, List, Dict, Any


from bot.db.database import Database
from bot.data.config import ADMIN


class AdminsManager:
    
    def __init__(self, db: Database, 
                 redis_client: Redis, 
                 root_logger: logging.Logger, 
                 redis_namespace: str = "admin_setting"):
        self.db = db
        self.redis = redis_client
        self.logger = root_logger
        self.ns = redis_namespace
        self.now = datetime.now()
        
        self._create_tables()
    
    def _create_tables(self):
        tables = [
            """
            CREATE TABLE IF NOT EXISTS `admins` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `user_id` BIGINT NOT NULL,
                `initiator_user_id` BIGINT,
                `updater_user_id` BIGINT,
                `role` ENUM('admin','moderator') DEFAULT 'admin',
                `is_active` BOOLEAN DEFAULT TRUE,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                `deleted_at` TIMESTAMP NULL,
                KEY `idx_user_id`(`user_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS `rights` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `name` VARCHAR(100),
                `key` VARCHAR(100) NOT NULL,
                `description` TEXT,
                `is_active` BOOLEAN DEFAULT TRUE,
                `initiator_user_id` BIGINT,
                `updater_user_id` BIGINT,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `deleted_at` TIMESTAMP NULL,
                KEY `idx_key`(`key`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            """
            CREATE TABLE IF NOT EXISTS admin_rights (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `admin_id` INT NOT NULL,
                `rights_id` INT NOT NULL,
                `value` BOOLEAN NOT NULL,
                `description` TEXT,
                `initiator_user_id` BIGINT,
                `updater_user_id` BIGINT,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                `deleted_at` TIMESTAMP NULL,
                UNIQUE KEY uq_admin_right (`admin_id`, `rights_id`),
                CONSTRAINT fk_admin_rights_admin
                    FOREIGN KEY (`admin_id`) REFERENCES `admins`(id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                CONSTRAINT fk_admin_rights_right
                    FOREIGN KEY (`rights_id`) REFERENCES `rights`(id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        ]
        
        try:
            for table_sql in tables:
                self.db.cursor.execute(table_sql)
        except Exception as e:
            self.logger.error(f"Jadvallarni yaratishda xatolik: {e}")
    
    def __call__(self, user_id: int, feature: str, return_initiator: bool = False) -> Tuple[Optional[bool], Optional[int]]:
        """
        Admin huquqini tekshirish
        
        Args:
            user_id: Admin telegram user ID
            feature: Xususiyat nomi
            return_initiator: Initiator ID qaytarish kerakmi
            
        Returns:
            (is_active, initiator_user_id) yoki (is_active,) yoki (None, None)
        """
        try:

            if not isinstance(user_id, int) or not isinstance(feature, str) :
                return None, None if return_initiator else None
             
            if user_id == ADMIN:
                return True, None if return_initiator else True
            
            feature_active_key = f"{self.ns}:rights:{feature}:is_active"
            feature_active = self.redis.get(feature_active_key)
            
            if feature_active is None:
                # MySQL dan feature faolligini tekshirish
                query = "SELECT is_active FROM rights WHERE `key` = %s AND deleted_at IS NULL"
                self.db.cursor.execute(query, (feature,))
                result = self.db.cursor.fetchone()
                
                if not result:
                    return None, None if return_initiator else None
                
                feature_active = result['is_active']
                self.redis.set(feature_active_key, str(int(feature_active)))
            else:
                feature_active = bool(int(feature_active))
            
            if not feature_active:
                return None, None if return_initiator else None

            redis_key = f"{self.ns}:admin_rights:{user_id}:{feature}"
            cached_data = self.redis.get(redis_key)
            
            if cached_data:
                data = json.loads(cached_data)

                
                if return_initiator:
                    return data.get('value', False), data.get('initiator_user_id')

                return data.get('value', False)
            
            query = """
                SELECT ar.value, ar.initiator_user_id 
                FROM admin_rights ar
                JOIN admins a ON ar.admin_id = a.id
                JOIN rights r ON ar.rights_id = r.id
                WHERE a.user_id = %s AND r.key = %s 
                AND a.is_active = TRUE AND a.deleted_at IS NULL
                AND r.is_active = TRUE AND r.deleted_at IS NULL
                AND ar.deleted_at IS NULL
            """
            
            self.db.cursor.execute(query, (user_id, feature))
            result = self.db.cursor.fetchone()
            
            if result:
                cache_data = {
                    'value': result['value'],
                    'initiator_user_id': result['initiator_user_id']
                }
                self.redis.set(redis_key, json.dumps(cache_data))
                
                if return_initiator:
                    return result['value'], result['initiator_user_id']
                return result['value']
            
            return False, None if return_initiator else False
            
        except Exception as e:
            self.logger.error(f"Huquq tekshirishda xatolik: {e}")
            return (None, None) if return_initiator else None

    def __getitem__(self, user_id: int) -> Tuple[Optional[bool], Optional[int], Optional[str], Optional[datetime]]:
        """
        Admin ekanligini tekshirish
        
        Args:
            user_id: Tekshirilayotgan admin telegram ID
            
        Returns:
            (is_admin, initiator_user_id, role, created_at)
        """
        try:
            if user_id == ADMIN:
                return True, None, 'super_admin', None
            
            redis_key = f"{self.ns}:admins:{user_id}"
            cached_data = self.redis.get(redis_key)
            
            if cached_data:
                data = json.loads(cached_data)
                created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
                return data.get('is_active'), data.get('initiator_user_id'), data.get('role'), created_at
            
            # MySQL dan qidirish
            query = """
                SELECT is_active, initiator_user_id, role, created_at 
                FROM admins 
                WHERE user_id = %s AND deleted_at IS NULL
            """
            
            self.db.cursor.execute(query, (user_id,))
            result = self.db.cursor.fetchone()
            
            if result:
                # Redis ga saqlash
                cache_data = {
                    'is_active': result['is_active'],
                    'initiator_user_id': result['initiator_user_id'],
                    'role': result['role'],
                    'created_at': result['created_at'].isoformat() if result['created_at'] else None
                }
                self.redis.set(redis_key, json.dumps(cache_data))
                
                return result['is_active'], result['initiator_user_id'], result['role'], result['created_at']
            
            return None, None, None, None
            
        except Exception as e:
            self.logger.error(f"Admin tekshirishda xatolik: {e}")
            return None, None, None, None
    
    def update(self, user_id: int, feature: str, value: bool, initiator_user_id: int) -> None:
        try:
            is_admin, _, _, _ = self.__getitem__(user_id)
            if not is_admin:
                self.logger.warning(f"User {user_id} admin emas")
                return
            rights_query = "SELECT id FROM rights WHERE `key` = %s AND is_active = TRUE AND deleted_at IS NULL"
            self.db.cursor.execute(rights_query, (feature,))
            right_result = self.db.cursor.fetchone()
            
            if not right_result:
                # self.logger.warning(f"Feature '{feature}' mavjud emas yoki faol emas")
                return
            
            rights_id = right_result['id']
            
            # Admin ID olish
            admin_query = "SELECT id FROM admins WHERE user_id = %s AND deleted_at IS NULL"
            self.db.cursor.execute(admin_query, (user_id,))
            admin_result = self.db.cursor.fetchone()
            
            if not admin_result:
                self.logger.warning(f"Admin {user_id} topilmadi")
                return
            
            admin_id = admin_result['id']
            
            # Admin_rights da mavjudligini tekshirish
            check_query = "SELECT id FROM admin_rights WHERE admin_id = %s AND rights_id = %s AND deleted_at IS NULL"
            self.db.cursor.execute(check_query, (admin_id, rights_id))
            existing = self.db.cursor.fetchone()
            
            current_time = datetime.now()
            
            if existing:
                # Yangilash
                update_query = """
                    UPDATE admin_rights 
                    SET value = %s, updater_user_id = %s, updated_at = %s 
                    WHERE id = %s
                """
                self.db.cursor.execute(update_query, (value, initiator_user_id, current_time, existing['id']))
            else:
                # Yaratish
                insert_query = """
                    INSERT INTO admin_rights (admin_id, rights_id, value, initiator_user_id, updater_user_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.db.cursor.execute(insert_query, (admin_id, rights_id, value, initiator_user_id, initiator_user_id, current_time, current_time))
            
            # Redis dan o'chirish (keyingi so'rovda yangilanadi)
            redis_key = f"{self.ns}:admin_rights:{user_id}:{feature}"
            self.redis.delete(redis_key)
            
            # self.logger.info(f"Admin {user_id} uchun {feature} huquqi {value} ga o'zgartirildi")
            
        except Exception as e:
            self.logger.error(f"Huquq yangilashda xatolik: {e}")
    
    def add(self, user_id: int, initiator_user_id: int, role: str = 'admin') -> None:
        """
        Yangi admin qo'shish
        
        Args:
            user_id: Qo'shilayotgan admin telegram ID
            initiator_user_id: Qo'shayotgan admin ID
            role: Admin roli
        """
        try:
            # Allaqachon admin emasligini tekshirish
            is_admin, _, _, _ = self.__getitem__(user_id)
            if is_admin:
                self.logger.warning(f"User {user_id} allaqachon admin")
                return
            
            # Initiator admin ekanligini va add_admin huquqini tekshirish
            if initiator_user_id != ADMIN:
                initiator_is_admin, _, _, _ = self.__getitem__(initiator_user_id)
                if not initiator_is_admin:
                    self.logger.warning(f"Initiator {initiator_user_id} admin emas")
                    return
                
                can_add_admin = self.__call__(initiator_user_id, 'add_admin')
                if not can_add_admin:
                    self.logger.warning(f"Initiator {initiator_user_id} da add_admin huquqi yo'q")
                    return
            
            # Yangi admin qo'shish
            current_time = datetime.now()
            insert_query = """
                INSERT INTO admins (user_id, initiator_user_id, updater_user_id, role, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.db.cursor.execute(insert_query, (user_id, initiator_user_id, initiator_user_id, role, True, current_time, current_time))
            
            # Redis dan o'chirish
            redis_key = f"{self.ns}:admins:{user_id}"
            cache_data = {
                "is_active": True,
                "initiator_user_id": initiator_user_id,
                "role": role,
                "created_at": current_time.isoformat()
            }
            self.redis.set(redis_key, json.dumps(cache_data))

            
            self.logger.info(f"Yangi admin qo'shildi: {user_id}, initiator: {initiator_user_id}")
            
        except Exception as e:
            self.logger.error(f"Admin qo'shishda xatolik: {e}")
    
    def remove(self, user_id: int, initiator_user_id: int) -> None:
        """
        Admin faolligini o'chirish
        
        Args:
            user_id: O'chiriladigan admin telegram ID
            initiator_user_id: O'chirmoqchi bo'lgan admin ID
        """
        try:
            # Admin ma'lumotlarini olish
            is_admin, admin_initiator_id, _, _ = self.__getitem__(user_id)
            if not is_admin:
                self.logger.warning(f"User {user_id} admin emas")
                return
            
            # Huquqni tekshirish: faqat shu adminni qo'shgan yoki super admin o'chira oladi
            if initiator_user_id != ADMIN and initiator_user_id != admin_initiator_id:
                self.logger.warning(f"Initiator {initiator_user_id} admin {user_id} ni o'chira olmaydi")
                return
            
            # Admin faolligini o'chirish
            current_time = datetime.now()
            update_query = """
                UPDATE admins 
                SET is_active = FALSE, updater_user_id = %s, updated_at = %s 
                WHERE user_id = %s AND deleted_at IS NULL
            """
            self.db.cursor.execute(update_query, (initiator_user_id, current_time, user_id))
            
            # Redis dan o'chirish
            redis_key = f"{self.ns}:admins:{user_id}"
            self.redis.delete(redis_key)
            
            # Admin huquqlarini ham Redis dan o'chirish
            redis_pattern = f"{self.ns}:admin_rights:{user_id}:*"
            keys = self.redis.keys(redis_pattern)
            if keys:
                self.redis.delete(*keys)
            
            self.logger.info(f"Admin {user_id} o'chirildi, initiator: {initiator_user_id}")
            
        except Exception as e:
            self.logger.error(f"Admin o'chirishda xatolik: {e}")
    
    def list_features(self) -> List[Dict[str, Any]]:
        """
        Barcha xususiyatlarni ro'yxat shaklida qaytarish
        
        Returns:
            Xususiyatlar ro'yxati
        """
        try:
            query = "SELECT * FROM rights WHERE deleted_at IS NULL ORDER BY created_at DESC"
            self.db.cursor.execute(query)
            return self.db.cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Xususiyatlar ro'yxatini olishda xatolik: {e}")
            return []
    
    def update_features(self, key: str, initiator_user_id: int, name: str = None, 
                       description: str = None, is_active: bool = False) -> None:
        """
        Yangi feature qo'shish yoki yangilash
        
        Args:
            key: Huquq kaliti
            initiator_user_id: Qo'shayotgan admin telegram ID
            name: Huquq nomi
            description: Huquq haqida ma'lumot
            is_active: Feature faolligi
        """
        try:
            # add_rights maxsus huquq uchun faqat super admin
            if key == 'add_rights':
                if initiator_user_id != ADMIN:
                    self.logger.warning(f"add_rights huquqini faqat super admin o'zgartira oladi")
                    return
            else:
                # Boshqa huquqlar uchun add_rights huquqini tekshirish
                if initiator_user_id != ADMIN:
                    initiator_is_admin, _, _, _ = self.__getitem__(initiator_user_id)
                    if not initiator_is_admin:
                        self.logger.warning(f"Initiator {initiator_user_id} admin emas")
                        return
                    
                    can_add_rights = self.__call__(initiator_user_id, 'add_rights')
                    if not can_add_rights:
                        self.logger.warning(f"Initiator {initiator_user_id} da add_rights huquqi yo'q")
                        return
            
            # Mavjudligini tekshirish
            check_query = "SELECT id FROM rights WHERE `key` = %s AND deleted_at IS NULL"
            self.db.cursor.execute(check_query, (key,))
            existing = self.db.cursor.fetchone()
            
            current_time = datetime.now()
            
            if existing:
                # Yangilash
                update_query = """
                    UPDATE rights 
                    SET name = %s, description = %s, is_active = %s, updater_user_id = %s, updated_at = %s 
                    WHERE id = %s
                """
                self.db.cursor.execute(update_query, (name, description, is_active, initiator_user_id, current_time, existing['id']))
            else:
                # Yaratish
                insert_query = """
                    INSERT INTO rights (name, `key`, description, is_active, initiator_user_id, updater_user_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.cursor.execute(insert_query, (name, key, description, is_active, initiator_user_id, initiator_user_id, current_time, current_time))
            
            # Redis dan feature faolligini yangilash
            feature_active_key = f"{self.ns}:rights:{key}:is_active"
            self.redis.set(feature_active_key, str(int(is_active)))
            
            # self.logger.info(f"Feature '{key}' yangilandi/yaratildi, initiator: {initiator_user_id}")
            
        except Exception as e:
            self.logger.error(f"Feature yangilashda xatolik: {e}")
    
    def my_admins(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Berilgan user_id uchun qo'shgan adminlar ro'yxati
        
        Args:
            user_id: Tekshirilayotgan admin telegram ID
            
        Returns:
            Adminlar ro'yxati
        """
        try:
            # Super admin uchun barcha adminlar
            if user_id == ADMIN:
                query = "SELECT * FROM admins WHERE deleted_at IS NULL ORDER BY created_at DESC"
                self.db.cursor.execute(query)
                return self.db.cursor.fetchall()
            
            # Oddiy admin uchun tekshirish
            is_admin, _, _, _ = self.__getitem__(user_id)
            if not is_admin:
                self.logger.warning(f"User {user_id} admin emas")
                return []
            
            can_add_admin = self.__call__(user_id, 'add_admin')
            if not can_add_admin:
                self.logger.warning(f"User {user_id} da add_admin huquqi yo'q")
                return []
            
            # Shu user tomonidan qo'shilgan adminlar
            query = "SELECT * FROM admins WHERE initiator_user_id = %s AND deleted_at IS NULL ORDER BY created_at DESC"
            self.db.cursor.execute(query, (user_id,))
            return self.db.cursor.fetchall()
            
        except Exception as e:
            self.logger.error(f"Adminlar ro'yxatini olishda xatolik: {e}")
            return []