#!/usr/bin/env python3
import os
import shutil
import glob
import tempfile
import platform
from pathlib import Path
import time

class SystemCleaner:
    def __init__(self):
        self.system = platform.system().lower()
        self.total_cleaned = 0
        self.files_deleted = 0
        
    def get_size_format(self, bytes_size):
        """แปลงไบต์เป็นหน่วยที่อ่านง่าย"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def get_folder_size(self, folder_path):
        """คำนวณขนาดโฟลเดอร์"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    try:
                        file_path = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, PermissionError):
            pass
        return total_size
    
    def clean_temp_files(self):
        """ลบไฟล์ temporary"""
        print("🗑️  กำลังลบไฟล์ temporary...")
        temp_paths = []
        
        # ตำแหน่ง temp files ตามระบบปฏิบัติการ
        if self.system == "windows":
            temp_paths = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp'),
                'C:\\Windows\\Temp'
            ]
        else:  # Linux/macOS
            temp_paths = [
                '/tmp',
                '/var/tmp',
                os.path.join(os.path.expanduser('~'), '.cache'),
                tempfile.gettempdir()
            ]
        
        cleaned_size = 0
        cleaned_files = 0
        
        for temp_path in temp_paths:
            if temp_path and os.path.exists(temp_path):
                try:
                    for item in os.listdir(temp_path):
                        item_path = os.path.join(temp_path, item)
                        try:
                            if os.path.isfile(item_path):
                                size = os.path.getsize(item_path)
                                os.remove(item_path)
                                cleaned_size += size
                                cleaned_files += 1
                            elif os.path.isdir(item_path):
                                size = self.get_folder_size(item_path)
                                shutil.rmtree(item_path)
                                cleaned_size += size
                                cleaned_files += 1
                        except (PermissionError, OSError, FileNotFoundError):
                            continue
                except (PermissionError, OSError):
                    continue
        
        self.total_cleaned += cleaned_size
        self.files_deleted += cleaned_files
        print(f"   ✅ ลบไฟล์ temporary: {cleaned_files} ไฟล์, {self.get_size_format(cleaned_size)}")
    
    def clean_browser_cache(self):
        """ลบ cache ของเบราว์เซอร์"""
        print("🌐 กำลังลบ browser cache...")
        cache_paths = []
        
        if self.system == "windows":
            user_profile = os.environ.get('USERPROFILE', '')
            cache_paths = [
                os.path.join(user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
                os.path.join(user_profile, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
                os.path.join(user_profile, 'AppData', 'Local', 'Mozilla', 'Firefox', 'Profiles', '*', 'cache2'),
            ]
        elif self.system == "darwin":  # macOS
            home = os.path.expanduser('~')
            cache_paths = [
                f"{home}/Library/Caches/Google/Chrome/Default/Cache",
                f"{home}/Library/Caches/com.apple.Safari",
                f"{home}/Library/Caches/Firefox/Profiles/*/cache2",
            ]
        else:  # Linux
            home = os.path.expanduser('~')
            cache_paths = [
                f"{home}/.cache/google-chrome/Default/Cache",
                f"{home}/.cache/mozilla/firefox/*/cache2",
                f"{home}/.cache/chromium/Default/Cache",
            ]
        
        cleaned_size = 0
        cleaned_files = 0
        
        for cache_path in cache_paths:
            if '*' in cache_path:
                # ใช้ glob สำหรับ wildcard
                for path in glob.glob(cache_path):
                    if os.path.exists(path):
                        try:
                            size = self.get_folder_size(path)
                            shutil.rmtree(path)
                            cleaned_size += size
                            cleaned_files += 1
                        except (PermissionError, OSError):
                            continue
            else:
                if os.path.exists(cache_path):
                    try:
                        size = self.get_folder_size(cache_path)
                        shutil.rmtree(cache_path)
                        cleaned_size += size
                        cleaned_files += 1
                    except (PermissionError, OSError):
                        continue
        
        self.total_cleaned += cleaned_size
        self.files_deleted += cleaned_files
        print(f"   ✅ ลบ browser cache: {cleaned_files} โฟลเดอร์, {self.get_size_format(cleaned_size)}")
    
    def clean_logs(self):
        """ลบ log files เก่า"""
        print("📝 กำลังลบ log files เก่า...")
        log_paths = []
        
        if self.system == "windows":
            log_paths = [
                'C:\\Windows\\Logs',
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Logs'),
            ]
        else:  # Linux/macOS
            log_paths = [
                '/var/log',
                f"{os.path.expanduser('~')}/.local/share/logs",
            ]
        
        cleaned_size = 0
        cleaned_files = 0
        
        for log_path in log_paths:
            if os.path.exists(log_path):
                try:
                    for root, dirs, files in os.walk(log_path):
                        for file in files:
                            if file.endswith(('.log', '.LOG', '.txt')) and 'old' in file.lower():
                                file_path = os.path.join(root, file)
                                try:
                                    # ลบไฟล์ log ที่เก่ากว่า 7 วัน
                                    file_age = time.time() - os.path.getmtime(file_path)
                                    if file_age > 7 * 24 * 3600:  # 7 วัน
                                        size = os.path.getsize(file_path)
                                        os.remove(file_path)
                                        cleaned_size += size
                                        cleaned_files += 1
                                except (PermissionError, OSError, FileNotFoundError):
                                    continue
                except (PermissionError, OSError):
                    continue
        
        self.total_cleaned += cleaned_size
        self.files_deleted += cleaned_files
        print(f"   ✅ ลบ log files: {cleaned_files} ไฟล์, {self.get_size_format(cleaned_size)}")
    
    def clean_recycle_bin(self):
        """ลบไฟล์ในถังขยะ"""
        print("🗑️  กำลังล้างถังขยะ...")
        
        if self.system == "windows":
            # Windows Recycle Bin
            try:
                import winshell
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
                print("   ✅ ล้างถังขยะ Windows เรียบร้อย")
            except ImportError:
                print("   ⚠️  ต้องติดตั้ง winshell: pip install winshell")
            except:
                print("   ⚠️  ไม่สามารถล้างถังขยะได้")
        elif self.system == "darwin":  # macOS
            trash_path = os.path.expanduser('~/.Trash')
            if os.path.exists(trash_path):
                try:
                    size = self.get_folder_size(trash_path)
                    shutil.rmtree(trash_path)
                    os.makedirs(trash_path)
                    self.total_cleaned += size
                    print(f"   ✅ ล้างถังขยะ macOS: {self.get_size_format(size)}")
                except (PermissionError, OSError):
                    print("   ⚠️  ไม่สามารถล้างถังขยะได้")
        else:  # Linux
            trash_path = os.path.expanduser('~/.local/share/Trash')
            if os.path.exists(trash_path):
                try:
                    size = self.get_folder_size(trash_path)
                    shutil.rmtree(trash_path)
                    os.makedirs(trash_path)
                    os.makedirs(os.path.join(trash_path, 'files'))
                    os.makedirs(os.path.join(trash_path, 'info'))
                    self.total_cleaned += size
                    print(f"   ✅ ล้างถังขยะ Linux: {self.get_size_format(size)}")
                except (PermissionError, OSError):
                    print("   ⚠️  ไม่สามารถล้างถังขยะได้")
    
    def clean_downloads(self):
        """ลบไฟล์ใน Downloads ที่เก่ากว่า 30 วัน"""
        print("📥 กำลังตรวจสอบโฟลเดอร์ Downloads...")
        
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(downloads_path):
            print("   ⚠️  ไม่พบโฟลเดอร์ Downloads")
            return
        
        cleaned_size = 0
        cleaned_files = 0
        cutoff_time = time.time() - (30 * 24 * 3600)  # 30 วัน
        
        try:
            for file in os.listdir(downloads_path):
                file_path = os.path.join(downloads_path, file)
                try:
                    if os.path.isfile(file_path):
                        # ลบไฟล์ที่เก่ากว่า 30 วัน
                        if os.path.getmtime(file_path) < cutoff_time:
                            size = os.path.getsize(file_path)
                            os.remove(file_path)
                            cleaned_size += size
                            cleaned_files += 1
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError):
            print("   ⚠️  ไม่สามารถเข้าถึงโฟลเดอร์ Downloads ได้")
            return
        
        self.total_cleaned += cleaned_size
        self.files_deleted += cleaned_files
        print(f"   ✅ ลบไฟล์ Downloads เก่า: {cleaned_files} ไฟล์, {self.get_size_format(cleaned_size)}")
    
    def run_cleanup(self, options=None):
        """เรียกใช้การทำความสะอาด"""
        if options is None:
            options = ['temp', 'browser', 'logs', 'trash', 'downloads']
        
        print("🧹 System Cleaner เริ่มทำงาน...")
        print("=" * 50)
        print(f"ระบบปฏิบัติการ: {platform.system()} {platform.release()}")
        print("-" * 50)
        
        start_time = time.time()
        
        if 'temp' in options:
            self.clean_temp_files()
        
        if 'browser' in options:
            self.clean_browser_cache()
        
        if 'logs' in options:
            self.clean_logs()
        
        if 'trash' in options:
            self.clean_recycle_bin()
        
        if 'downloads' in options:
            self.clean_downloads()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("-" * 50)
        print("🎉 การทำความสะอาดเสร็จสิ้น!")
        print(f"📊 สรุป:")
        print(f"   • ไฟล์ที่ลบ: {self.files_deleted:,} ไฟล์")
        print(f"   • พื้นที่ที่ว่าง: {self.get_size_format(self.total_cleaned)}")
        print(f"   • เวลาที่ใช้: {duration:.2f} วินาที")
        print("=" * 50)

def main():
    cleaner = SystemCleaner()
    
    print("🧹 System Cleaner")
    print("=" * 30)
    print("เลือกสิ่งที่ต้องการทำความสะอาด:")
    print("1. Temporary files")
    print("2. Browser cache")  
    print("3. Log files")
    print("4. Recycle bin/Trash")
    print("5. Old downloads (30+ days)")
    print("6. ทั้งหมด")
    print("0. ยกเลิก")
    
    try:
        choice = input("\nเลือก (1-6, หรือใส่หลายตัวเลข เช่น 1,2,3): ").strip()
        
        if choice == '0':
            print("👋 ยกเลิกการทำงาน")
            return
        
        if choice == '6':
            options = ['temp', 'browser', 'logs', 'trash', 'downloads']
        else:
            choice_map = {
                '1': 'temp',
                '2': 'browser', 
                '3': 'logs',
                '4': 'trash',
                '5': 'downloads'
            }
            
            selected = [c.strip() for c in choice.split(',')]
            options = [choice_map[c] for c in selected if c in choice_map]
            
            if not options:
                print("❌ ตัวเลือกไม่ถูกต้อง")
                return
        
        print(f"\n⚠️  คำเตือน: การดำเนินการนี้จะลบไฟล์ถาวร!")
        confirm = input("ต้องการดำเนินการต่อ? (y/n): ").strip().lower()
        
        if confirm == 'y':
            cleaner.run_cleanup(options)
        else:
            print("👋 ยกเลิกการทำงาน")
            
    except KeyboardInterrupt:
        print("\n👋 ยกเลิกการทำงาน")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()
