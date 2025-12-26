import os
import shutil
import json
import datetime
from app import app

# Çıktı klasörü
BUILD_DIR = 'docs'
SITE_URL = 'https://n4yuc4.github.io'

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
    pages = [
        ('/', 'index.html'),
        ('/blog.html', 'blog.html'),
        ('/about.html', 'about.html'),
        ('/contact.html', 'contact.html'),
        ('/portfolio.html', 'portfolio.html'),
        ('/privacy.html', 'privacy.html'),
        ('/terms.html', 'terms.html'),
    ]

    # Blog yazılarını metadata dosyasından oku
    try:
        with open('data/blogPostsMetadata.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
            for post in posts:
                pages.append((f"/posts/{post['slug']}.html", f"posts/{post['slug']}.html"))
    except Exception as e:
        print(f"Blog metadataları okunamadı: {e}")

    # Portfolyo detaylarını metadata dosyasından oku
    try:
        with open('data/portfolioItems.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
            for item in items:
                pages.append((f"/portfolio/{item['slug']}.html", f"portfolio/{item['slug']}.html"))
    except Exception as e:
        print(f"Portfolyo metadataları okunamadı: {e}")

    print(f"Toplam {len(pages)} sayfa oluşturuluyor ve Sitemap hazırlanıyor...")

    # Flask test client kullanarak sayfaları render et
    with app.test_client() as client:
        for route, output_path in pages:
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
            
            # Localhost adreslerini gerçek site adresiyle değiştir (SEO için)
            html_content = html_content.replace('http://localhost/', f'{SITE_URL}/')
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

    # Sitemap oluştur
    generate_sitemap(pages)

    print("\nİşlem Başarıyla Tamamlandı!")
    print(f"Statik site '{BUILD_DIR}' klasörüne oluşturuldu.")

def generate_sitemap(pages):
    print("Sitemap.xml oluşturuluyor...")
    
    sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">')
    
    today = datetime.date.today().isoformat()
    
    for route, output_path in pages:
        if route == '/' or output_path == 'index.html':
            url = f"{SITE_URL}/"
            priority = '1.0'
        else:
            url = f"{SITE_URL}/{output_path}"
            priority = '0.8'
            
        sitemap_content.append('  <url>')
        sitemap_content.append(f'    <loc>{url}</loc>')
        sitemap_content.append(f'    <lastmod>{today}</lastmod>')
        sitemap_content.append('    <changefreq>weekly</changefreq>')
        sitemap_content.append(f'    <priority>{priority}</priority>')
        sitemap_content.append('  </url>')
        
    sitemap_content.append('</urlset>')
    
    with open(os.path.join(BUILD_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sitemap_content))

if __name__ == "__main__":
    build()