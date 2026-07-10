# Web Sitesi ve CV Düzenleme Rehberi

Bu rehber, kişisel web sitenizdeki ve CV'nizdeki içerikleri (projeler, iş deneyimleri, eğitimler, sosyal medya hesapları vb.) nasıl kolayca düzenleyebileceğinizi açıklamaktadır.

İçerikleri güncellemek için **iki farklı yöntem** kullanabilirsiniz:

---

## 1. Yöntem: Yönetim Paneli (CLI) ile Düzenleme (Tavsiye Edilen)

Terminal üzerinden çalışan interaktif bir arayüz yardımıyla hiçbir kod veya JSON dosyasına dokunmadan verilerinizi güvenli bir şekilde güncelleyebilirsiniz.

### Çalıştırma:
Terminali açın ve proje dizininde şu komutu çalıştırın:
```bash
.venv/bin/python admin_panel.py
```

### Sunulan Seçenekler:
Komutu çalıştırdığınızda karşınıza aşağıdaki gibi bir ana menü çıkacaktır:
* **1. Portfolyo Öğelerini Yönet:** Yeni proje ekleme, mevcut projelerin başlık/açıklama/link bilgilerini düzenleme veya silme.
* **2. CV Bilgilerini Düzenle:** İngilizce veya Türkçe CV'nizi seçerek; Kişisel Bilgiler, Kariyer Özeti, Yetenek Kategorileri, İş Deneyimleri, Eğitim Geçmişi, Diller ve Referansları düzenleme.
* **3. Hakkımda Sayfasını Güncelle:** Sayfa başlığı, profil resmi ve biyografi yazısını düzenleme.
* **4. İletişim Sayfasını Güncelle:** Başlık ve form/iletişim giriş metinlerini düzenleme.
* **5. Sosyal Medya & İletişim Linklerini Yönet:** E-posta, web sitesi ve sosyal profil (GitHub, LinkedIn vb.) linklerini/ikonlarını düzenleme.
* **6. Akademik Yayın Bağlantılarını Yönet:** Sitede otomatik olarak Crossref/arXiv üzerinden başlık ve özet bilgileri çekilen akademik yayınların DOI/arXiv linklerini ekleme veya çıkarma.
* **7. Web Sitesini Derle (Build):** Sitenin statik dosyalarını ve CV PDF'lerini yeniden üretme.
* **8. Geliştirici Sunucusunu Çalıştır (Flask):** Sitenin son halini yerel sunucuda test etme.

> [!TIP]
> CLI aracılığıyla bir veriyi güncellediğinizde, araç size değişikliklerin yayına girmesi için siteyi otomatik olarak derlemek (build) isteyip istemediğinizi soracaktır. `e` (evet) diyerek tek adımda sitenizi güncelleyebilirsiniz.

---

## 2. Yöntem: JSON Dosyalarını Doğrudan Düzenleme

Eğer verileri doğrudan dosyalardan el ile değiştirmek isterseniz, eklenen **JSON Şemaları** sayesinde VS Code (veya uyumlu bir editör) size tam destek sunacaktır.

### Düzenlenebilir Dosyalar:
* **CV Verileri (İngilizce):** `data/cvData.json`
* **CV Verileri (Türkçe):** `data/tr/cvData.json`
* **Projeler (İngilizce):** `data/portfolioItems.json`
* **Projeler (Türkçe):** `data/tr/portfolioItems.json`
* **Sosyal Hesaplar & İletişim:** `data/socialLinks.json`
* **Hakkımda Sayfası:** `data/aboutPageData.json` (veya `data/tr/aboutPageData.json`)

### JSON Şeması (JSON Schema) Güvenliği:
JSON dosyalarının başında bulunan `"$schema"` tanımları sayesinde VS Code'da şu özellikler aktif olur:
1. **Otomatik Tamamlama (Autocomplete):** Yeni bir satır açıp `"` yazdığınızda ekleyebileceğiniz alanlar listelenir.
2. **Açıklamalar (Tooltips):** Fareyi bir anahtar kelimenin üzerine getirdiğinizde, o alanın ne işe yaradığına dair açıklamaları görebilirsiniz.
3. **Anlık Hata Denetimi (Validation):** Yanlışlıkla hatalı bir veri tipi girerseniz (örneğin liste olması gereken yere düz metin yazmak) editör altını kırmızı çizerek sizi uyarır.

### Değişiklikleri Derleme (Build):
JSON dosyalarını el ile düzenledikten sonra sitenizin ve CV PDF'lerinin güncellenmesi için şu komutla derleme işlemini tetiklemelisiniz:
```bash
.venv/bin/python build.py
```

---

## Yeni Bir Portfolyo Projesi Ekleme Süreci

Sitenize yeni bir proje eklemek için en pratik iş akışı şöyledir:

1. **Projeyi Tanımlayın:**
   `admin_panel.py` aracını çalıştırın ve `1` (Portfolyo) -> `2` (Yeni Ekle) adımlarını izleyin. Proje başlığını, kısa açıklamasını ve teknolojilerini girin.
   * Bu işlem otomatik olarak `portfolio/proje-slug.md` adında boş bir markdown dosyası oluşturacaktır.
2. **Detayları Yazın:**
   Oluşturulan `portfolio/proje-slug.md` (veya Türkçe için `portfolio/tr/proje-slug.md`) dosyasını bir editörle açın. Projenizin detaylarını, görsellerini ve teknik ayrıntılarını standart **Markdown** formatında yazıp kaydedin.
3. **Derleyin ve İnceleyin:**
   `admin_panel.py` üzerinden `7` (Build) seçeneğiyle sitenizi derleyin.

---

## Değişiklikleri Yerel Ortamda Test Etme

Yaptığınız değişikliklerin tarayıcıda nasıl göründüğünü kontrol etmek için yerel sunucuyu başlatabilirsiniz:

1. `admin_panel.py` içerisinden `8` (Flask Sunucusu) seçeneğini seçin veya doğrudan terminalde çalıştırın:
   ```bash
   .venv/bin/python app.py
   ```
2. Tarayıcınızda **[http://localhost:5000](http://localhost:5000)** adresine gidin.
3. İncelemeniz bittiğinde terminalde `CTRL + C` tuş kombinasyonunu kullanarak sunucuyu durdurabilirsiniz.
