import os
import shutil
import json
import datetime
from app import app

# Çıktı klasörü
BUILD_DIR = 'docs'
SITE_URL = 'https://n4yuc4.github.io'

def parse_turkish_date(date_str):
    """
    '27 Ekim 2025' formatındaki Türkçe tarihi '2025-10-27' (ISO) formatına çevirir.
    Hata olursa None döner.
    """
    if not date_str:
        return None
        
    months = {
        'Ocak': '01', 'Şubat': '02', 'Mart': '03', 'Nisan': '04', 'Mayıs': '05', 'Haziran': '06',
        'Temmuz': '07', 'Ağustos': '08', 'Eylül': '09', 'Ekim': '10', 'Kasım': '11', 'Aralık': '12'
    }
    
    try:
        parts = date_str.split()
        if len(parts) == 3:
            day = parts[0].zfill(2)
            month = months.get(parts[1])
            year = parts[2]
            if month:
                return f"{year}-{month}-{day}"
    except Exception as e:
        print(f"Tarih çevirme hatası ({date_str}): {e}")
    
    return None

def build():
    # Eski build klasörünü temizle
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)

    # .nojekyll dosyası oluştur (GitHub Pages için)
    with open(os.path.join(BUILD_DIR, '.nojekyll'), 'w') as f:
        pass

    # Static klasörünü kopyala
    print("Statik dosyalar kopyalanıyor...")
    
    # Hedef static klasörü (docs/static)
    dest_static = os.path.join(BUILD_DIR, 'static')
    os.makedirs(dest_static, exist_ok=True)

    if os.path.exists('static'):
        for item in os.listdir('static'):
            s = os.path.join('static', item)
            
            # Klasörleri (css, js, images) docs/static/ altına koy
            if os.path.isdir(s):
                d = os.path.join(dest_static, item)
                shutil.copytree(s, d)
            
            # Dosyaları (robots.txt vb.) docs/ altına koy (Kök dizine)
            else:
                # sitemap.xml hariç (dinamik oluşturulacak)
                if item == 'sitemap.xml':
                    continue
                d = os.path.join(BUILD_DIR, item)
                shutil.copy2(s, d)

    # Oluşturulacak sayfaları belirle 
    # Yapı: (route, output_path, source_file, explicit_date)
    pages = [
        ('/', 'index.html', 'templates/home.html', None),
        ('/blog.html', 'blog.html', 'templates/blog.html', None),
        ('/about.html', 'about.html', 'data/aboutPageData.json', None),
        ('/contact.html', 'contact.html', 'data/contactPageData.json', None),
        ('/portfolio.html', 'portfolio.html', 'data/portfolioItems.json', None),
        ('/privacy.html', 'privacy.html', 'data/privacy.md', None),
        ('/terms.html', 'terms.html', 'data/terms.md', None),
    ]

    # Blog yazılarını metadata dosyasından oku
    try:
        with open('data/blogPostsMetadata.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
            for post in posts:
                # JSON'dan tarihi al
                date_str = post.get('date')
                iso_date = parse_turkish_date(date_str)
                pages.append((f"/posts/{post['slug']}.html", f"posts/{post['slug']}.html", post['contentFile'], iso_date))
    except Exception as e:
        print(f"Blog metadataları okunamadı: {e}")

    # Portfolyo detaylarını metadata dosyasından oku
    try:
        with open('data/portfolioItems.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
            for item in items:
                # JSON'dan tarihi al
                date_str = item.get('date')
                iso_date = parse_turkish_date(date_str)
                pages.append((f"/portfolio/{item['slug']}.html", f"portfolio/{item['slug']}.html", item['detailFile'], iso_date))
    except Exception as e:
        print(f"Portfolyo metadataları okunamadı: {e}")

    print(f"Toplam {len(pages)} sayfa oluşturuluyor ve Sitemap hazırlanıyor...")

    # Flask test client kullanarak sayfaları render et
    with app.test_client() as client:
        for route, output_path, source_file, _ in pages:
            # print(f"İşleniyor: {route}")
            
            response = client.get(route)
            if response.status_code != 200:
                print(f"HATA: {route} alınamadı (Kod: {response.status_code})")
                continue

            # Dosya yolunu oluştur
            full_path = os.path.join(BUILD_DIR, output_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # HTML içeriğini yaz
            html_content = response.data.decode('utf-8')
            
            # Localhost adreslerini (portlu veya portsuz) gerçek site adresiyle değiştir
            html_content = html_content.replace('http://localhost:5000/', f'{SITE_URL}/')
            html_content = html_content.replace('http://localhost/', f'{SITE_URL}/')
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

    # Sitemap oluştur
    generate_sitemap(pages)

    print("\nİşlem Başarıyla Tamamlandı!")
    print(f"Statik site '{BUILD_DIR}' klasörüne oluşturuldu.")

def get_lastmod(file_path):
    """Dosyanın son değiştirilme tarihini ISO formatında döndürür."""
    if os.path.exists(file_path):
        mtime = os.path.getmtime(file_path)
        return datetime.datetime.fromtimestamp(mtime).date().isoformat()
    return datetime.date.today().isoformat()

def generate_sitemap(pages):
    print("Sitemap (XML ve TXT) oluşturuluyor...")
    
    # --- DÜZELTME BAŞLANGICI ---
    # XML Sitemap - Temiz ve Standart Başlık
    sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    # Sadece standart sitemap şemasını kullanıyoruz. Gereksiz video/news/image namespace'leri kaldırıldı.
    sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    # --- DÜZELTME BİTİŞİ ---
    
    # TXT Sitemap
    txt_content = []
    
    for route, output_path, source_file, explicit_date in pages:
        if route == '/' or output_path == 'index.html':
            url = f"{SITE_URL}/"
        else:
            # URL sonuna .html eklenmesi doğru (statik dosya yapısı için)
            url = f"{SITE_URL}/{output_path}"
        
        if explicit_date:
            lastmod = explicit_date
        else:
            lastmod = get_lastmod(source_file)
        
        # XML
        sitemap_content.append('  <url>')
        sitemap_content.append(f'    <loc>{url}</loc>')
        sitemap_content.append(f'    <lastmod>{lastmod}</lastmod>')
        sitemap_content.append('  </url>')
        
        # TXT
        txt_content.append(url)
        
    sitemap_content.append('</urlset>')
    
    with open(os.path.join(BUILD_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sitemap_content))
        
    with open(os.path.join(BUILD_DIR, 'sitemap.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(txt_content))

if __name__ == "__main__":
    build()