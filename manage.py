import os
import json
import datetime
import unicodedata
import re
import sys
import subprocess
import readline  # For better input handling

# --- Configuration ---
BLOG_METADATA_FILE = 'data/blogPostsMetadata.json'
PORTFOLIO_METADATA_FILE = 'data/portfolioItems.json'
POSTS_DIR = 'posts'
PORTFOLIO_DIR = 'portfolio'

# --- Helpers ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def slugify(text):
    text = text.lower()
    replacements = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        ' ': '-', '.': '', ',': '', '!': '', '?': '', ':': '', ';': '',
        '\'': '', '"': '', '(': '', ')': '', '[': '', ']': ''
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[-\s]+', '-', text).strip('-_')
    return text

def load_json(filepath):
    try:
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Colors.FAIL}Error loading JSON {filepath}: {e}{Colors.ENDC}")
        return []

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"{Colors.FAIL}Error saving JSON {filepath}: {e}{Colors.ENDC}")
        return False

def get_input(prompt_text, default=None):
    """Gets input with an optional default value."""
    if default:
        user_input = input(f"{Colors.BLUE}{prompt_text} [{default}]: {Colors.ENDC}")
        return user_input.strip() if user_input.strip() else default
    else:
        return input(f"{Colors.BLUE}{prompt_text}: {Colors.ENDC}").strip()

def confirm_action(prompt_text):
    response = input(f"{Colors.WARNING}{prompt_text} (y/n): {Colors.ENDC}").lower()
    return response == 'y'

# --- Base Manager ---
class ContentManager:
    def __init__(self, metadata_file, content_dir, item_type):
        self.metadata_file = metadata_file
        self.content_dir = content_dir
        self.item_type = item_type  # 'post' or 'portfolio'
        self.data = load_json(self.metadata_file)

    def reload_data(self):
        self.data = load_json(self.metadata_file)

    def list_items(self):
        self.reload_data()
        print(f"\n{Colors.HEADER}--- {self.item_type.upper()} LISTESİ ---{Colors.ENDC}")
        if not self.data:
            print("Kayıt bulunamadı.")
            return

        for idx, item in enumerate(self.data):
            print(f"{Colors.BOLD}{idx + 1}.{Colors.ENDC} {item.get('title', 'Başlıksız')} ({item.get('slug', 'no-slug')})")

    def select_item(self):
        self.list_items()
        if not self.data:
            return None
        
        try:
            choice = int(input(f"\n{Colors.BLUE}Seçiminiz (Numara): {Colors.ENDC}"))
            if 1 <= choice <= len(self.data):
                return choice - 1
            else:
                print(f"{Colors.FAIL}Geçersiz numara.{Colors.ENDC}")
                return None
        except ValueError:
            print(f"{Colors.FAIL}Lütfen bir sayı girin.{Colors.ENDC}")
            return None

    def delete_item(self):
        idx = self.select_item()
        if idx is None: return

        item = self.data[idx]
        print(f"\n{Colors.WARNING}SİLİNECEK: {item.get('title')}{Colors.ENDC}")
        
        if not confirm_action("Bu öğeyi ve ilgili dosyasını silmek istediğinize emin misiniz?"):
            print("İşlem iptal edildi.")
            return

        # Delete content file
        file_key = 'contentFile' if self.item_type == 'post' else 'detailFile'
        file_path = item.get(file_key)
        
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"{Colors.GREEN}✓ Dosya silindi: {file_path}{Colors.ENDC}")
            except OSError as e:
                print(f"{Colors.FAIL}Dosya silinemedi: {e}{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}Dosya bulunamadı veya zaten silinmiş: {file_path}{Colors.ENDC}")

        # Delete from JSON
        del self.data[idx]
        if save_json(self.metadata_file, self.data):
            print(f"{Colors.GREEN}✓ Kayıt JSON'dan silindi.{Colors.ENDC}")

    def create_content_file(self, filename, title, extra_content=""):
        try:
            content = f"# {title}\n\n{extra_content}"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"{Colors.GREEN}✓ Dosya oluşturuldu: {filename}{Colors.ENDC}")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}Hata (Dosya Oluşturma): {e}{Colors.ENDC}")
            return False

# --- Blog Manager ---
class BlogManager(ContentManager):
    def __init__(self):
        super().__init__(BLOG_METADATA_FILE, POSTS_DIR, 'post')

    def create(self):
        print(f"\n{Colors.HEADER}--- YENİ BLOG YAZISI ---{Colors.ENDC}")
        title = get_input("Başlık")
        if not title: return
        
        excerpt = get_input("Kısa Özet")
        slug = slugify(title)
        
        # Date handling
        now = datetime.datetime.now()
        months = {
            "January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", 
            "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", 
            "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"
        }
        date_str = now.strftime("%d %B %Y")
        for eng, tr in months.items():
            date_str = date_str.replace(eng, tr)
            
        date_input = get_input("Tarih", default=date_str)
        image_url = get_input("Görsel Yolu", default="images/blog-images/black-box.jpg")

        filename = os.path.join(self.content_dir, f"{slug}.md")
        
        new_entry = {
            "imageUrl": image_url,
            "title": title,
            "date": date_input,
            "excerpt": excerpt,
            "slug": slug,
            "contentFile": filename
        }

        self.data.insert(0, new_entry)
        if save_json(self.metadata_file, self.data):
            self.create_content_file(filename, title, "Buraya yazınızı yazmaya başlayın...")
            print(f"{Colors.GREEN}✓ Blog yazısı başarıyla oluşturuldu.{Colors.ENDC}")

    def update(self):
        idx = self.select_item()
        if idx is None: return
        
        item = self.data[idx]
        print(f"\n{Colors.HEADER}--- DÜZENLE: {item['title']} ---{Colors.ENDC}")
        
        item['title'] = get_input("Başlık", item['title'])
        item['excerpt'] = get_input("Özet", item.get('excerpt', ''))
        item['date'] = get_input("Tarih", item['date'])
        item['imageUrl'] = get_input("Görsel Yolu", item['imageUrl'])
        
        # Slug update logic could be complex (requires file rename), skipping for safety unless explicitly requested.
        # But we update the JSON.
        
        if save_json(self.metadata_file, self.data):
             print(f"{Colors.GREEN}✓ Kayıt güncellendi.{Colors.ENDC}")
             print(f"{Colors.BLUE}İçerik dosyasını düzenlemek için: {item['contentFile']}{Colors.ENDC}")

# --- Portfolio Manager ---
class PortfolioManager(ContentManager):
    def __init__(self):
        super().__init__(PORTFOLIO_METADATA_FILE, PORTFOLIO_DIR, 'portfolio')

    def create(self):
        print(f"\n{Colors.HEADER}--- YENİ PORTFOLYO ÖĞESİ ---{Colors.ENDC}")
        title = get_input("Proje Adı")
        if not title: return

        description = get_input("Kısa Açıklama")
        slug = slugify(title)
        image_url = get_input("Görsel Yolu", default="images/icon.png")
        
        filename = os.path.join(self.content_dir, f"{slug}.md")

        new_entry = {
            "title": title,
            "imageUrl": image_url,
            "description": description,
            "detailFile": filename,
            "slug": slug
        }

        self.data.insert(0, new_entry)
        if save_json(self.metadata_file, self.data):
            self.create_content_file(filename, title, "Proje detaylarını buraya yazın...")
            print(f"{Colors.GREEN}✓ Portfolyo öğesi başarıyla oluşturuldu.{Colors.ENDC}")

    def update(self):
        idx = self.select_item()
        if idx is None: return
        
        item = self.data[idx]
        print(f"\n{Colors.HEADER}--- DÜZENLE: {item['title']} ---{Colors.ENDC}")
        
        item['title'] = get_input("Proje Adı", item['title'])
        item['description'] = get_input("Açıklama", item.get('description', ''))
        item['imageUrl'] = get_input("Görsel Yolu", item['imageUrl'])

        if save_json(self.metadata_file, self.data):
             print(f"{Colors.GREEN}✓ Kayıt güncellendi.{Colors.ENDC}")
             print(f"{Colors.BLUE}Detay dosyasını düzenlemek için: {item['detailFile']}{Colors.ENDC}")

# --- Main Application ---
def build_site():
    print(f"\n{Colors.HEADER}--- SİTE DERLENİYOR (BUILD) ---{Colors.ENDC}")
    subprocess.run([sys.executable, "build.py"])
    subprocess.run(["touch", "docs/.nojekyll"])

def main_menu():
    blog_mgr = BlogManager()
    portfolio_mgr = PortfolioManager()

    while True:
        # clear_screen() # Optional: keep history visible
        print(f"\n{Colors.BOLD}{Colors.HEADER}=== N4YuC4 Blog Yönetim Paneli ==={Colors.ENDC}")
        print("1. Blog Yazıları")
        print("2. Portfolyo Öğeleri")
        print("3. Siteyi Derle (Build)")
        print("4. Çıkış")
        
        choice = input(f"\n{Colors.BLUE}Seçiminiz: {Colors.ENDC}").strip()
        
        if choice == '1':
            sub_menu(blog_mgr, "Blog")
        elif choice == '2':
            sub_menu(portfolio_mgr, "Portfolyo")
        elif choice == '3':
            build_site()
        elif choice == '4':
            print("Güle güle!")
            break
        else:
            print("Geçersiz seçim.")

def sub_menu(manager, name):
    while True:
        print(f"\n{Colors.BOLD}--- {name} Yönetimi ---{Colors.ENDC}")
        print("1. Listele")
        print("2. Yeni Ekle")
        print("3. Düzenle (Metadata)")
        print("4. Sil")
        print("5. Ana Menüye Dön")
        
        choice = input(f"\n{Colors.BLUE}Seçiminiz: {Colors.ENDC}").strip()
        
        if choice == '1':
            manager.list_items()
        elif choice == '2':
            manager.create()
        elif choice == '3':
            manager.update()
        elif choice == '4':
            manager.delete_item()
        elif choice == '5':
            break
        else:
            print("Geçersiz seçim.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nÇıkış yapılıyor...")