import os
import json
import datetime
import unicodedata
import re
import sys
import subprocess

# Renkli çıktılar için
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def slugify(text):
    """Metni URL dostu hale getirir (Türkçe karakterleri düzeltir)."""
    text = text.lower()
    replacements = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        ' ': '-', '.': '', ',': '', '!': '', '?': '', ':': '', ';': ''
    }
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    
    # ASCII olmayan karakterleri temizle
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[-\s]+', '-', text).strip('-_')
    return text

def create_blog_post():
    print(f"\n{Colors.HEADER}--- YENİ BLOG YAZISI OLUŞTUR ---{Colors.ENDC}")
    title = input(f"{Colors.BLUE}Başlık: {Colors.ENDC}")
    excerpt = input(f"{Colors.BLUE}Kısa Özet (Ana sayfada görünecek): {Colors.ENDC}")
    
    slug = slugify(title)
    date_str = datetime.datetime.now().strftime("%d %B %Y")
    
    # Türkçe ay isimleri düzeltmesi (Basitçe)
    months = {
        "January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", 
        "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", 
        "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"
    }
    for eng, tr in months.items():
        if eng in date_str:
            date_str = date_str.replace(eng, tr)

    # Dosya Yolu
    filename = f"posts/{slug}.md"
    
    # JSON Verisi Hazırla
    new_entry = {
        "imageUrl": "images/blog-images/black-box.jpg",  # Varsayılan resim
        "title": title,
        "date": date_str,
        "excerpt": excerpt,
        "slug": slug,
        "contentFile": filename
    }
    
    # JSON Dosyasını Güncelle
    try:
        with open('data/blogPostsMetadata.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # En başa ekle
        data.insert(0, new_entry)
        
        with open('data/blogPostsMetadata.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"{Colors.GREEN}✓ Metadata JSON güncellendi.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Hata (JSON): {e}{Colors.ENDC}")
        return

    # Markdown Dosyası Oluştur
    try:
        content = f"# {title}\n\nBuraya yazınızı yazmaya başlayın..."
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"{Colors.GREEN}✓ Dosya oluşturuldu: {filename}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}Hata (Dosya): {e}{Colors.ENDC}")

    print(f"\n{Colors.WARNING}HATIRLATMA: 'static/images/blog-images/' klasörüne bir resim eklemeyi ve JSON dosyasındaki 'imageUrl' alanını güncellemeyi unutmayın!{Colors.ENDC}")

def create_portfolio_item():
    print(f"\n{Colors.HEADER}--- YENİ PORTFOLYO ÖĞESİ OLUŞTUR ---{Colors.ENDC}")
    title = input(f"{Colors.BLUE}Proje Adı: {Colors.ENDC}")
    description = input(f"{Colors.BLUE}Kısa Açıklama: {Colors.ENDC}")
    
    slug = slugify(title)
    filename = f"portfolio/{slug}.md"
    
    new_entry = {
        "title": title,
        "imageUrl": "images/icon.png", # Varsayılan
        "description": description,
        "detailFile": filename,
        "slug": slug
    }
    
    try:
        with open('data/portfolioItems.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        data.insert(0, new_entry)
        
        with open('data/portfolioItems.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"{Colors.GREEN}✓ Metadata JSON güncellendi.{Colors.ENDC}")
        
        content = f"# {title}\n\nProje detaylarını buraya yazın..."
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"{Colors.GREEN}✓ Dosya oluşturuldu: {filename}{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}Hata: {e}{Colors.ENDC}")

def build_site():
    print(f"\n{Colors.HEADER}--- SİTE DERLENİYOR (BUILD) ---{Colors.ENDC}")
    subprocess.run(["python3", "build.py"])
    subprocess.run(["touch", "docs/.nojekyll"])

def main():
    while True:
        print(f"\n{Colors.BOLD}--- N4YuC4 Blog Yönetim Paneli ---{Colors.ENDC}")
        print("1. Yeni Blog Yazısı Ekle")
        print("2. Yeni Portfolyo Öğesi Ekle")
        print("3. Siteyi Derle (Build)")
        print("4. Çıkış")
        
        choice = input(f"\n{Colors.BLUE}Seçiminiz (1-4): {Colors.ENDC}")
        
        if choice == '1':
            create_blog_post()
        elif choice == '2':
            create_portfolio_item()
        elif choice == '3':
            build_site()
        elif choice == '4':
            print("Güle güle!")
            break
        else:
            print("Geçersiz seçim.")

if __name__ == "__main__":
    main()
