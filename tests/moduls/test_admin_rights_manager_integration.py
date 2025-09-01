import asyncio
import time
from datetime import datetime
from bot.loader import AM
from bot.data.config import ADMIN

def test_admins_manager_complete():
    """
    AdminsManager klassining to'liq funksionalligini test qilish
    """
    print("=== AdminsManager Test Boshlandi ===\n")
    
    # Test ma'lumotlari
    SUPER_ADMIN_ID = ADMIN
    TEST_ADMIN_1 = 987654321    # Test admin 1
    TEST_ADMIN_2 = 111222333    # Test admin 2
    TEST_USER = 444555666       # Oddiy user (admin emas)
    
    try:
        print("1. DASTLABKI HOLATNI TEKSHIRISH")
        print("-" * 40)
        
        # Avval barcha test ma'lumotlarini tozalash
        print("Test ma'lumotlarini tozalash...")
        
        # MySQL dan tozalash
        AM.db.cursor.execute("DELETE FROM admin_rights WHERE admin_id IN (SELECT id FROM admins WHERE user_id IN (%s, %s, %s))", 
                           (TEST_ADMIN_1, TEST_ADMIN_2, TEST_USER))
        AM.db.cursor.execute("DELETE FROM admins WHERE user_id IN (%s, %s, %s)", 
                           (TEST_ADMIN_1, TEST_ADMIN_2, TEST_USER))
        AM.db.cursor.execute("DELETE FROM rights WHERE `key` IN ('test_feature', 'add_admin', 'delete_admin', 'edit_rights', 'add_rights')")
        
        # Redis dan tozalash
        redis_keys = AM.redis.keys(f"{AM.ns}:*")
        if redis_keys:
            AM.redis.delete(*redis_keys)
        
        print("✓ Test ma'lumotlari tozalandi")
        
        print("\n2. SUPER ADMIN TEKSHIRISH")
        print("-" * 40)
        
        # Super admin qo'shish (bu odatda dastur boshida amalga oshiriladi)
        AM.add(SUPER_ADMIN_ID, SUPER_ADMIN_ID, 'admin')
        
        # Super admin ekanligini tekshirish
        is_admin, initiator, role, created_at = AM[SUPER_ADMIN_ID]
        print(f"Super admin tekshiruvi: is_admin={is_admin}, role={role}")
        assert is_admin == True, "Super admin qo'shilmadi"
        print("✓ Super admin muvaffaqiyatli qo'shildi")
        
        print("\n3. FEATURES (HUQUQLAR) YARATISH")
        print("-" * 40)
        
        # Asosiy huquqlarni yaratish
        features_to_create = [
            ('add_admin', 'Admin qo\'shish huquqi', 'Yangi adminlar qo\'shish imkoniyati'),
            ('delete_admin', 'Admin o\'chirish huquqi', 'Adminlarni o\'chirish imkoniyati'),
            ('edit_rights', 'Huquqlarni tahrirlash', 'Admin huquqlarini o\'zgartirish'),
            ('add_rights', 'Yangi huquq qo\'shish', 'Yangi huquqlar yaratish'),
            ('test_feature', 'Test huquq', 'Test uchun yaratilgan huquq')
        ]
        
        for key, name, description in features_to_create:
            AM.update_features(key, SUPER_ADMIN_ID, name, description, True)
            print(f"✓ '{key}' huquqi yaratildi")
        
        # Huquqlar ro'yxatini tekshirish
        features_list = AM.list_features()
        print(f"Jami huquqlar soni: {len(features_list)}")
        assert len(features_list) >= 5, "Huquqlar to'liq yaratilmadi"
        
        print("\n4. SUPER ADMIN HUQUQLARINI BERISH")
        print("-" * 40)
        
        # Super admin ga barcha huquqlarni berish
        for key, _, _ in features_to_create:
            AM.update(SUPER_ADMIN_ID, key, True, SUPER_ADMIN_ID)
            print(f"✓ Super admin ga '{key}' huquqi berildi")
        
        # Huquqlarni tekshirish
        can_add_admin = AM(SUPER_ADMIN_ID, 'add_admin')
        can_delete_admin = AM(SUPER_ADMIN_ID, 'delete_admin')
        can_edit_rights = AM(SUPER_ADMIN_ID, 'edit_rights')
        
        print(f"Super admin huquqlari: add_admin={can_add_admin}, delete_admin={can_delete_admin}, edit_rights={can_edit_rights}")
        assert all([can_add_admin, can_delete_admin, can_edit_rights]), "Super admin huquqlari noto'g'ri"
        
        print("\n5. YANGI ADMINLAR QO'SHISH")
        print("-" * 40)
        
        # Birinchi admin qo'shish
        AM.add(TEST_ADMIN_1, SUPER_ADMIN_ID, 'admin')
        is_admin_1, initiator_1, role_1, created_1 = AM[TEST_ADMIN_1]
        print(f"Admin 1 qo'shildi: is_admin={is_admin_1}, initiator={initiator_1}, role={role_1}")
        assert is_admin_1 == True, "Test admin 1 qo'shilmadi"
        assert initiator_1 == SUPER_ADMIN_ID, "Initiator noto'g'ri"
        
        # Ikkinchi admin qo'shish
        AM.add(TEST_ADMIN_2, SUPER_ADMIN_ID, 'moderator')
        is_admin_2, initiator_2, role_2, created_2 = AM[TEST_ADMIN_2]
        print(f"Admin 2 qo'shildi: is_admin={is_admin_2}, initiator={initiator_2}, role={role_2}")
        assert is_admin_2 == True, "Test admin 2 qo'shilmadi"
        assert role_2 == 'moderator', "Role noto'g'ri"
        
        print("✓ Yangi adminlar muvaffaqiyatli qo'shildi")
        
        print("\n6. ADMIN HUQUQLARINI BERISH")
        print("-" * 40)
        
        # Admin 1 ga ba'zi huquqlarni berish
        AM.update(TEST_ADMIN_1, 'add_admin', True, SUPER_ADMIN_ID)
        AM.update(TEST_ADMIN_1, 'edit_rights', True, SUPER_ADMIN_ID)
        AM.update(TEST_ADMIN_1, 'test_feature', False, SUPER_ADMIN_ID)  # False qiymat
        
        # Admin 2 ga boshqa huquqlarni berish
        AM.update(TEST_ADMIN_2, 'delete_admin', True, SUPER_ADMIN_ID)
        AM.update(TEST_ADMIN_2, 'test_feature', True, SUPER_ADMIN_ID)
        
        print("✓ Admin huquqlari berildi")
        
        print("\n7. HUQUQLARNI TEKSHIRISH")
        print("-" * 40)
        
        # Admin 1 huquqlarini tekshirish
        admin1_add_admin = AM(TEST_ADMIN_1, 'add_admin')
        admin1_edit_rights = AM(TEST_ADMIN_1, 'edit_rights')
        admin1_test_feature = AM(TEST_ADMIN_1, 'test_feature')
        admin1_delete_admin = AM(TEST_ADMIN_1, 'delete_admin')  # Bu huquq berilmagan
        
        print(f"Admin 1 huquqlari:")
        print(f"  add_admin: {admin1_add_admin}")
        print(f"  edit_rights: {admin1_edit_rights}")
        print(f"  test_feature: {admin1_test_feature}")
        print(f"  delete_admin: {admin1_delete_admin}")
        
        assert admin1_add_admin == True, "Admin 1 add_admin huquqi noto'g'ri"
        assert admin1_edit_rights == True, "Admin 1 edit_rights huquqi noto'g'ri"
        assert admin1_test_feature == False, "Admin 1 test_feature huquqi noto'g'ri"
        assert admin1_delete_admin == False, "Admin 1 delete_admin huquqi noto'g'ri"
        
        # Admin 2 huquqlarini tekshirish
        admin2_delete_admin = AM(TEST_ADMIN_2, 'delete_admin')
        admin2_test_feature = AM(TEST_ADMIN_2, 'test_feature')
        admin2_add_admin = AM(TEST_ADMIN_2, 'add_admin')  # Bu huquq berilmagan
        
        print(f"Admin 2 huquqlari:")
        print(f"  delete_admin: {admin2_delete_admin}")
        print(f"  test_feature: {admin2_test_feature}")
        print(f"  add_admin: {admin2_add_admin}")
        
        assert admin2_delete_admin == True, "Admin 2 delete_admin huquqi noto'g'ri"
        assert admin2_test_feature == True, "Admin 2 test_feature huquqi noto'g'ri"
        assert admin2_add_admin == False, "Admin 2 add_admin huquqi noto'g'ri"
        
        print("✓ Huquqlar to'g'ri ishlayapti")
        
        print("\n8. RETURN_INITIATOR FUNKSIYASINI TEKSHIRISH")
        print("-" * 40)
        
        # Initiator ma'lumotini olish
        can_add, initiator_id = AM(TEST_ADMIN_1, 'add_admin', return_initiator=True)
        print(f"Admin 1 add_admin huquqi: {can_add}, initiator: {initiator_id}")
        assert can_add == True, "return_initiator value noto'g'ri"
        assert initiator_id == SUPER_ADMIN_ID, "return_initiator initiator_id noto'g'ri"
        
        print("✓ return_initiator funksiyasi to'g'ri ishlayapti")
        
        print("\n9. REDIS CACHE TEKSHIRISH")
        print("-" * 40)
        
        # Redis cache tozalash
        redis_keys = AM.redis.keys(f"{AM.ns}:*")
        if redis_keys:
            AM.redis.delete(*redis_keys)
        print("Redis cache tozalandi")
        
        # Birinchi marta so'rov (MySQL dan)
        start_time = time.time()
        result1 = AM(TEST_ADMIN_1, 'add_admin')
        mysql_time = time.time() - start_time
        
        # Ikkinchi marta so'rov (Redis dan)
        start_time = time.time()
        result2 = AM(TEST_ADMIN_1, 'add_admin')
        redis_time = time.time() - start_time
        
        print(f"MySQL so'rov vaqti: {mysql_time:.4f}s")
        print(f"Redis so'rov vaqti: {redis_time:.4f}s")
        print(f"Natijalar: MySQL={result1}, Redis={result2}")
        
        assert result1 == result2, "Cache natijalar mos kelmayapti"
        print("✓ Redis cache to'g'ri ishlayapti")
        
        print("\n10. ADMIN TOMONIDAN YANGI ADMIN QO'SHISH")
        print("-" * 40)
        
        # Admin 1 tomonidan yangi admin qo'shish
        AM.add(TEST_USER, TEST_ADMIN_1, 'admin')
        is_new_admin, new_initiator, new_role, new_created = AM[TEST_USER]
        
        print(f"Yangi admin qo'shildi: is_admin={is_new_admin}, initiator={new_initiator}")
        assert is_new_admin == True, "Yangi admin qo'shilmadi"
        assert new_initiator == TEST_ADMIN_1, "Yangi admin initiator noto'g'ri"
        
        print("✓ Admin tomonidan yangi admin qo'shish muvaffaqiyatli")
        
        print("\n11. MY_ADMINS FUNKSIYASINI TEKSHIRISH")
        print("-" * 40)
        
        # Super admin uchun barcha adminlar
        super_admin_list = AM.my_admins(SUPER_ADMIN_ID)
        print(f"Super admin ro'yxatida adminlar soni: {len(super_admin_list)}")
        assert len(super_admin_list) >= 3, "Super admin ro'yxati noto'g'ri"
        
        # Admin 1 tomonidan qo'shilgan adminlar
        admin1_list = AM.my_admins(TEST_ADMIN_1)
        print(f"Admin 1 ro'yxatida adminlar soni: {len(admin1_list)}")
        assert len(admin1_list) == 1, "Admin 1 ro'yxati noto'g'ri"
        assert admin1_list[0]['user_id'] == TEST_USER, "Admin 1 ro'yxatidagi admin noto'g'ri"
        
        print("✓ my_admins funksiyasi to'g'ri ishlayapti")
        
        print("\n12. ADMIN O'CHIRISH")
        print("-" * 40)
        
        # Admin 1 tomonidan o'z qo'shgan adminni o'chirish
        AM.remove(TEST_USER, TEST_ADMIN_1)
        is_removed_admin, _, _, _ = AM[TEST_USER]
        print(f"O'chirilgan admin holati: is_admin={is_removed_admin}")
        assert is_removed_admin == False, "Admin o'chirilmadi"
        
        # Super admin tomonidan admin o'chirish
        AM.remove(TEST_ADMIN_2, SUPER_ADMIN_ID)
        is_removed_admin2, _, _, _ = AM[TEST_ADMIN_2]
        print(f"Super admin tomonidan o'chirilgan admin: is_admin={is_removed_admin2}")
        assert is_removed_admin2 == False, "Admin 2 o'chirilmadi"
        
        print("✓ Admin o'chirish funksiyasi to'g'ri ishlayapti")
        
        print("\n13. XATO HOLATLARNI TEKSHIRISH")
        print("-" * 40)
        
        # Admin bo'lmagan user tomonidan huquq tekshirish
        non_admin_right = AM(999888777, 'add_admin')
        print(f"Admin bo'lmagan user huquqi: {non_admin_right}")
        assert non_admin_right == False, "Admin bo'lmagan user huquqi noto'g'ri"
        
        # Mavjud bo'lmagan huquqni tekshirish
        fake_right = AM(SUPER_ADMIN_ID, 'fake_feature')
        print(f"Mavjud bo'lmagan huquq: {fake_right}")
        assert fake_right in [None, False], "Mavjud bo'lmagan huquq noto'g'ri"
        
        # Admin bo'lmagan user ga huquq berish
        try:
            AM.update(999888777, 'add_admin', True, SUPER_ADMIN_ID)
            print("Admin bo'lmagan user ga huquq berish - kutilganidek xato yuz bermadi")
        except Exception as e:
            print(f"Admin bo'lmagan user ga huquq berish xatosi: {e}")
        
        print("✓ Xato holatlar to'g'ri qayta ishlanyapti")
        
        print("\n14. HUQUQ YANGILASH")
        print("-" * 40)
        
        # Mavjud huquqni yangilash
        AM.update(TEST_ADMIN_1, 'test_feature', True, SUPER_ADMIN_ID)  # False dan True ga
        updated_right = AM(TEST_ADMIN_1, 'test_feature')
        print(f"Yangilangan huquq: {updated_right}")
        assert updated_right == True, "Huquq yangilanmadi"
        
        print("✓ Huquq yangilash to'g'ri ishlayapti")
        
        print("\n15. FEATURE FAOLLIGINI TEKSHIRISH")
        print("-" * 40)
        
        # Feature ni faol emas qilish
        AM.update_features('test_feature', SUPER_ADMIN_ID, 'Test Feature', 'Test description', False)
        
        # Faol bo'lmagan feature huquqini tekshirish
        inactive_feature_right = AM(TEST_ADMIN_1, 'test_feature')
        print(f"Faol bo'lmagan feature huquqi: {inactive_feature_right}")
        assert inactive_feature_right is None, "Faol bo'lmagan feature huquqi noto'g'ri"
        
        # Feature ni qayta faollashtirish
        AM.update_features('test_feature', SUPER_ADMIN_ID, 'Test Feature', 'Test description', True)
        
        print("✓ Feature faollik tekshirish to'g'ri ishlayapti")
        
        print("\n16. YAKUNIY STATISTIKA")
        print("-" * 40)
        
        # Yakuniy holatni ko'rsatish
        all_features = AM.list_features()
        all_admins = AM.my_admins(SUPER_ADMIN_ID)
        
        print(f"Jami yaratilgan features: {len(all_features)}")
        print(f"Jami adminlar soni: {len(all_admins)}")
        
        # Faol adminlar soni
        active_admins = [admin for admin in all_admins if admin['is_active']]
        print(f"Faol adminlar soni: {len(active_admins)}")
        
        print("\n=== BARCHA TESTLAR MUVAFFAQIYATLI O'TDI! ===")
        print("AdminsManager klassi to'liq ishga yaraydi va barcha funksiyalar to'g'ri ishlayapti.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST XATOSI: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Test ma'lumotlarini tozalash
        try:
            print("\nTest ma'lumotlarini tozalash...")
            AM.db.cursor.execute("DELETE FROM admin_rights WHERE admin_id IN (SELECT id FROM admins WHERE user_id IN (%s, %s, %s, %s))", 
                               (SUPER_ADMIN_ID, TEST_ADMIN_1, TEST_ADMIN_2, TEST_USER))
            AM.db.cursor.execute("DELETE FROM admins WHERE user_id IN (%s, %s, %s, %s)", 
                               (SUPER_ADMIN_ID, TEST_ADMIN_1, TEST_ADMIN_2, TEST_USER))
            AM.db.cursor.execute("DELETE FROM rights WHERE `key` IN ('test_feature', 'add_admin', 'delete_admin', 'edit_rights', 'add_rights')")
            
            redis_keys = AM.redis.keys(f"{AM.ns}:*")
            if redis_keys:
                AM.redis.delete(*redis_keys)
            
            print("✓ Test ma'lumotlari tozalandi")
        except Exception as e:
            print(f"Tozalashda xatolik: {e}")


if __name__ == "__main__":
    print("AdminsManager test ishga tushirilmoqda...")
    success = test_admins_manager_complete()
    
    if success:
        print("\n🎉 Barcha testlar muvaffaqiyatli!")
    else:
        print("\n💥 Ba'zi testlar muvaffaqiyatsiz!")
    
    print("\nTest yakunlandi.")