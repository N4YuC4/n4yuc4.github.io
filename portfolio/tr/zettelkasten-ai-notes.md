# Zettelkasten Yapay Zeka Notları

**Zettelkasten** metodolojisini masaüstüne taşıyan, **Python** ve Python'un modern UI kütüphanesi **Flet** ile geliştirilmiş gizlilik odaklı bir kişisel bilgi yönetimi sistemi. İlk olarak **Pupilica Yapay Zeka Hackathonu'nda İlk 10 Finalist** arasına girerek ödüllendirilen proje; daha sonra modüler mimariye, yüksek performanslı yerel çıkarım yeteneklerine ve zengin bir görselleştirme ortamına sahip tam teşekküllü bir masaüstü uygulamasına dönüştürülmüştür.

Uygulama, hem Google Gemini bulut API'sini hem de donanım hızlandırmalı Vulkan GPU desteğiyle çalışan %100 çevrimdışı yerel GGUF modellerini bünyesinde birleştiren bir **Çift Yapay Zeka Motoru (Dual AI Engine)**, etkileşimli kanvas zihin haritası, LaTeX matematik destekli canlı Markdown editörü ve çift yönlü [[WikiLink]] altyapısı sunar.

---

## Mimari ve Temel Yetenekler

### 1. Çift Yapay Zeka Çıkarım Motoru (Bulut & Çevrimdışı Yerel)
Zettelkasten AI Notes, yoğun PDF belgelerini işleyerek anlamlı atomik fikirler çıkarır ve aralarında anlamsal bağlantılar kurar:

* **Bulut Yapay Zeka (Google Gemini API):** Güncel resmi `google-genai` SDK'sı üzerinden API anahtarı ile çalışan hızlı ve yüksek verimli çıkarım katmanı.
* **Çevrimdışı Yerel Yapay Zeka (Vulkan GPU ile GGUF):** `llama-cpp-python` kütüphanesi ve platform bağımsız **Vulkan GPU hızlandırması** (NVIDIA, AMD, Intel ve Apple Silicon uyumlu) sayesinde internet bağlantısı gerektirmeyen, tamamen gizlilik odaklı yerel LLM çıkarımı.
* **Süreç İzolasyonlu Çalışma Mantığı (`multiprocessing`):** Yerel model çıkarımları bağımsız bir Python alt sürecinde yürütülür. Bu sayede Linux/Wayland ortamlarında arayüz donmaları ve Vulkan sunum kilitlenmeleri engellenir, arayüz akıcılığı korunur ve işlem tamamlandığında veya iptal edildiğinde kullanılan RAM/VRAM anında sisteme iade edilir.
* **Akıllı Yanıt Ayrıştırıcı (`AiResponseParser`):** Akademik atıf kalıntılarını (`[1]`, `[Smith vd.]`) temizleyen, yapısal başlıkları (Şekil, Tablo, Bölüm) filtreleyen ve bozuk JSON çıktılarını onararak tutarlı grafik kenarlarına dönüştüren çok aşamalı ayrıştırma altyapısı.

### 2. Dahili Model Yöneticisi ve İndirici
Kullanıcıların harici sunucular kurmasına ya da terminal komutlarıyla uğraşmasına gerek kalmadan yerel modelleri yönetmesini sağlar:

* **Seçilmiş Yerel Model Kataloğu:** Farklı donanım seviyeleri için optimize edilmiş **Gemma 4 ailesi** (128K bağlam pencereli 3.2 GB hafif E2B, 6.2 GB dengeli 12B ve 13.1 GB amiral gemisi 26B MoE).
* **Parçalı HTTP İndirme Yöneticisi:** Hugging Face üzerinden modelleri doğrudan arayüz içerisinden indiren; anlık hız, tahmini süre (ETA), ilerleme çubuğu ve duraklatma/iptal desteği sunan arka plan indiricisi.

### 3. Donanım Kaynak Denetleyicisi ve OOM Koruması
* **Otomatik Donanım Tespiti:** Sistem RAM'i, CPU çekirdekleri, GPU aygıtları ve kullanılabilir VRAM miktarını proaktif olarak denetler.
* **Bellek Aşımı (OOM) Koruması:** Modeller belleğe alınmadan veya indirilmeden önce sistem kapasitesini doğrulayarak çökmeleri önler.
* **Dinamik Katman Paylaştırma:** Mevcut donanım gücüne göre GPU'ya devredilecek en uygun katman sayısını (`n_gpu_layers`) dinamik olarak belirler.

### 4. Gelişmiş Canlı Markdown Çalışma Alanı
* **Kaynak ve Okuma Modları:** `Ctrl+E` kısayolu veya başlık çubuğundaki düğmeyle ham Markdown düzenleme ile biçimlendirilmiş okuma modu arasında anında geçiş.
* **Zengin Biçimlendirme Araç Çubuğu:** Başlıklar (H1–H4), kalın (`Ctrl+B`), eğik (`Ctrl+I`), üstü çizili, sözdizimi vurgulamalı kod blokları, alıntılar, listeler, tablolar ve yatay ayırıcılar için tek tıkla kısayollar.
* **Etkileşimli Görev Listeleri:** Hem düzenleme hem de okuma modunda tıklanarak işaretlenebilen `- [ ]` ve `- [x]` onay kutuları.
* **LaTeX Matematik Normalizasyonu:** Satır içi (`$ ... $`, `\( ... \)`) ve blok (`$$ ... $$`, `\[ ... \]`) matematik formüllerinin Flet arayüzünde kod bloklarını bozmadan temiz şekilde işlenmesi.
* **Belge İstatistikleri:** Kelime, karakter, satır sayısı ve tahmini okuma süresini gösteren gerçek zamanlı sayaçlar.
* **Otomatik Kaydetme:** Arka planda çalışan ve kaydedilmemiş değişiklikleri (`*`) gösteren güvenli otomatik kayıt mimarisi.

### 5. Çift Yönlü [[WikiLink]] Sistemi
* **WikiLink Sözdizimi:** Düşünceler `[[Not Başlığı]]` veya `[[Hedef Not|Özel İsim]]` biçiminde kolayca birbirine bağlanır.
* **Etkileşimli Gezinme ve Otomatik Oluşturma:** Herhangi bir bağlantıya tıklandığında hedef nota doğrudan geçilir. Hedef not henüz mevcut değilse tek tıkla oluşturulup bağlanır.
* **Hızlı Bağlantı Seçici (`Ctrl+K`):** Notlar arasında hızlıca tek veya çift yönlü bağlantılar kurmayı sağlayan arama penceresi.

### 6. Etkileşimli Kanvas Zihin Haritası ve Bilgi Grafiği
* **Kanvas Çizimi:** `flet.canvas` kullanılarak GPU ivmeli dinamik grafik çizimi ve `PyGraphviz` ile otomatik düğüm konumlandırma.
* **Kaydırma ve Yakınlaştırma:** `InteractiveViewer` kontrolleriyle akıcı pan ve zoom özellikleri.
* **Doğrudan Odaklanma:** Grafikteki herhangi bir düğüme tıklandığında o notun düzenleme alanında anında açılması.

### 7. Modüler 3 Bölmeli Esnek Arayüz
* **Sol Kenar Çubuğu:** Koleksiyon filtreleme, anlık arama, not sayısı göstergeleri ve ayarlar paneli.
* **Merkezi Çalışma Alanı:** Markdown editörü, canlı önizleme ve not eylem butonları.
* **Sağ Panel:** Etkileşimli zihin haritası kanvası ve bağlı notlar listesi.
* **Daraltılabilir İnce Raylar:** Yazı alanını genişletmek için sol kenar çubuğunu (`Ctrl+[`) veya sağ paneli (`Ctrl+]`) 50 piksellik kompakt simge raylarına dönüştürebilme.
* **Sürüklenebilir Ayırıcılar:** Bölme genişliklerini fareyle serbestçe ayarlama imkanı.

### 8. Güçlü SQLite Kalıcılık Katmanı
* **Write-Ahead Logging (WAL):** Eşzamanlı okuma ve yazma işlemlerinde performansı artıran WAL modu yapılandırması.
* **İş Parçacığı Güvenliği:** Thread-local bağlantılar sayesinde iş parçacıkları arasında güvenli veritabanı iletişimi.
* **İlişkisel Bütünlük:** Basamaklı silmeler (cascading deletes) ve yabancı anahtar kısıtlamaları (`PRAGMA foreign_keys = ON`).

---

## Kullanılan Teknolojiler

* **Masaüstü Framework:** Python, Flet
* **Yapay Zeka ve Çıkarım:** `llama-cpp-python` (Vulkan GPU hızlandırması), Google Gemini API (`google-genai`)
* **Belge ve Grafik İşleme:** `pypdf`, `pygraphviz`, `markdown`
* **Depolama ve Sistem:** SQLite (WAL modu), `psutil`, `requests`
