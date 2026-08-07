# Zettelkasten Yapay Zeka Notları

Zettelkasten yöntemini kullanarak verimli bilgi yönetimi sağlamak amacıyla `Flet` (Flutter tabanlı Python UI framework'ü) ile geliştirilmiş bir masaüstü uygulamasıdır. Kullanıcıların notlar oluşturmasına, düzenlemesine ve bunları birbirine bağlamasına olanak tanır. Zengin içerik için `Markdown` formatını destekler ve gerçek zamanlı önizleme sunar. Tüm verileri yerel bir `SQLite` veritabanında saklar. Uygulamanın en önemli özelliği, PDF belgelerinden (`pypdf`) Zettelkasten tarzı notlar üretmek ve bunlar arasında otomatik olarak ilgili bağlantılar önermek için `Google Gemini AI` (`google-genai` SDK) kullanmasıdır.

## Temel Özellikler

* **Modern Kullanıcı Arayüzü:** Akıcı, responsive ve platformlar arası masaüstü deneyimi sunan `Flet` ile inşa edilmiş temiz arayüz.
* **Not Oluşturma ve Yönetimi:** Notları kolayca oluşturun, kaydedin, yeniden adlandırın ve silin.
* **Canlı Önizlemeli Markdown Desteği:** Notlarınızı `Markdown` biçiminde yazın ve biçimlendirilmiş çıktıyı gerçek zamanlı olarak görün.
* **Kategorizasyon:** Daha iyi filtreleme ve gezinme için notları özel kategoriler halinde düzenleyin.
* **PDF'den Yapay Zeka Destekli Not Üretimi:** `pypdf` ile PDF belgelerinden metin çıkarın ve güncel `google-genai` SDK'sı üzerinden `Google Gemini AI` kullanarak önerilen bağlantılarla birlikte otomatik Zettelkasten tarzı notlar oluşturun.
* **Flet Canvas Zihin Haritası Görselleştirme:** Notlarınızı ve bağlantılarını `flet.canvas` destekli etkileşimli bir zihin haritası olarak görüntüleyin. Fikirleriniz arasındaki ilişkileri görselleştirerek bilgi tabanınızda daha etkili bir şekilde gezinin.
* **Akıllı Not Bağlama:** Bilgileriniz arasında zengin, birbirine bağlı bir grafik oluşturmak için notlar arasında açık bağlantılar kurun.
* **Tema Desteği:** Uygulamanın görünümünü özelleştirmek için açık ve karanlık temalar arasında seçim yapın.
* **SQLite Veritabanı:** Tüm notlarınız ve bunların ilişkileri için sağlam ve güvenilir yerel depolama.
* **Kapsamlı Test Paketi:** Temel veritabanı işlemleri, başlık temizleme (sanitization) ve not mantığı için otomatik birim testleri (unit tests).
