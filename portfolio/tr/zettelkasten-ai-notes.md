# Zettelkasten Yapay Zeka Notları

**Zettelkasten** metodolojisini masaüstüne taşıyan, **Python 3.13** ve Flutter tabanlı modern masaüstü UI framework'ü **Flet** ile geliştirilmiş gizlilik odaklı bir kişisel bilgi yönetimi sistemi. İlk olarak **Pupilica Yapay Zeka Hackathonu'nda İlk 10 Finalist** arasına girerek ödüllendirilen proje; daha sonra modüler mimariye, iki kademeli vektör RAG altyapısına, yüksek performanslı yerel çıkarım yeteneklerine ve zengin bir görselleştirme ortamına sahip tam teşekküllü bir masaüstü uygulamasına dönüştürülmüştür.

Uygulama, Google Gemini bulut API'sini ve donanım hızlandırmalı Vulkan GPU desteğiyle çalışan %100 çevrimdışı yerel GGUF modellerini bünyesinde birleştiren bir **Çift Yapay Zeka Motoru (Dual AI Engine)**, CPU üzerinde çalışan bağımsız gömme ve yeniden sıralama modelleriyle güçlendirilmiş **İki Kademeli Bellek-İçi Vektör RAG Havuzu**, etkileşimli kanvas zihin haritası, LaTeX matematik destekli canlı Markdown editörü ve çift yönlü [[WikiLink]] altyapısı sunar.

---

## Mimari ve Temel Yetenekler

### 1. Çift Yapay Zeka Çıkarım Motoru ve İki Kademeli Vektör RAG Havuzu
Zettelkasten AI Notes, yoğun PDF belgelerini işleyerek anlamlı atomik fikirler çıkarır, belge parçaları arasındaki kavram tekrarlarını engeller ve aralarında anlamsal bağlantılar kurar:

* **Bulut Yapay Zeka (Google Gemini API):** Güncel resmi `google-genai` SDK'sı (v2.22.0) ve özel sistem yönlendirmeleriyle (system prompt) yönetilen hızlı, yüksek verimli çıkarım katmanı.
* **Çevrimdışı Yerel Yapay Zeka (Vulkan GPU ile GGUF):** `llama-cpp-python` kütüphanesi ve platform bağımsız **Vulkan GPU hızlandırması** (NVIDIA, AMD, Intel ve Apple Silicon uyumlu) sayesinde internet bağlantısı gerektirmeyen, tamamen gizlilik odaklı yerel LLM çıkarımı.
* **İki Kademeli Bellek-İçi RAG Havuzu (`note_rag_pool.py`):** Çok parçalı PDF ve belge işleme sırasında parçalar arası kavram yinelemelerini ortadan kaldıran oturum tabanlı RAG havuzu:
  * **Kademe 1 (Global Konsept Haritası):** Birikmiş tüm notların kanonik ID'leri, başlıkları ve 1 cümlelik temel mekanizma özetleriyle kuşbakışı bir kavram dizini oluşturup üretim istemlerine enjekte eder.
  * **Kademe 2 (Odak Not Getirimi):** Bi-encoder vektör benzerliği ile cross-encoder yeniden sıralama puanlamasını birleştirerek bütçelenmiş odak notları isteme dinamik olarak ekler.
  * **Global Union-Find Küme Birleştirmesi:** Belge parçaları arasındaki geçişli kopya kavram kümelerini keşfeder ve bunları LLM veya algoritmik fazlalıksız sentezle birleştirir; wikilink'leri ve grafik kenarlarını temiz biçimde yeniden eşler.
* **Süreç İzolasyonlu Çalışma Mantığı (`multiprocessing`):** Yerel model çıkarımları bağımsız bir Python alt sürecinde yürütülür. Bu sayede Linux/Wayland ortamlarında arayüz donmaları ve Vulkan sunum kilitlenmeleri engellenir, arayüz akıcılığı korunur ve işlem tamamlandığında veya iptal edildiğinde kullanılan RAM/VRAM anında sisteme iade edilir.

### 2. Bağımsız CPU Yardımcı Çıkarım Modelleri (Gömme ve Yeniden Sıralama)
Üretim LLM'lerinin ihtiyaç duyduğu GPU bellek alanını tüketmemek ve VRAM çekişmesini sıfırlamak için yardımcı NLP modelleri tamamen CPU üzerinde çalışır:

* **Anlamsal Bellek Servisi (`semantic_memory_service.py`):** Vektör indeksleme, kosinüs benzerliği adayı keşfi ve anlamsal grafik bağlantıları için **Microsoft Harrier (0.6B)** (32K bağlam penceresi, 1024 boyutlu vektör uzayı) tabanlı yerel CPU gömme (embedding) çıkarımı.
* **Cross-Encoder Yeniden Sıralayıcı (`reranker_service.py`):** **Qwen3-Reranker (0.6B)** ile güçlendirilmiş yüksek hassasiyetli semantik alaka puanlama servisi. `(sorgu, not)` çiftlerini yönergeye duyarlı çapraz dikkat ve kalibre edilmiş sigmoid logit farkı (`logit("yes") - logit("no")`) ile değerlendirir.
* **Sıfır VRAM Rekabeti:** Yardımcı modeller kesinlikle CPU iş parçacıkları üzerinde (`n_threads=2`, `n_gpu_layers=0`) çalışarak GPU VRAM'inin %100'ünü ana metin üretim modellerine (Gemma 4 ailesi) bırakır.

### 3. Modüler Ayrıştırma, Kavram Eşleme ve Grafik Uzlaştırma Motorları
İşlem hattı esnek, birbirinden bağımsız etki alanı motorlarına ayrıştırılmıştır:

* **Çok Dilli Kavram Eşleyici (`concept_matcher.py`):** Karakter 4-gram örtüşmesi, dilden bağımsız token normalizasyonu ve kök bulma (stemming), niteleyici temizleme ve çok kademeli kopya kavram tespit motoru.
* **Dirençli JSON Onarım ve LaTeX Sanitizer (`json_repair_engine.py` & `ai_response_parser.py`):** Model bağlam limitlerinden kaynaklanan yarım kalmış dizgileri ve kapatılmamış parantezleri dengeleyen, akademik atıf kalıntılarını (`[1]`, `[Smith vd.]`) filtreleyen ve KaTeX uyumlu LaTeX kaçışlarını kod bloklarına zarar vermeden yürüten onarım motoru.
* **Döngü Korumalı Grafik Uzlaştırma (`graph_reconciliation.py`):** Kanonik yönsüz ikili sıralama (`canonical_pair`) uygulayan, döngüsel kilitlenmeleri engelleyen güvenli geçişli yönlendirmeler sunan ve heterojen tamsayı/UUID not kimliklerinde wikilink'leri yeniden eşleyen grafik araçları.
* **Evrensel Dinamik Semantik Parçalayıcı (`semantic_chunker.py`):** Uzun PDF metinlerini paragraf, cümle ve kelime sınırları boyunca adaptif token örtüşmesiyle (~4500 token) bölerek bağlam kaybını önleyen paylaşımlı parçalama motoru.
* **Arayüzü Kilitlemeyen PDF İşleme (`pdf_processor.py`):** Sayfa düzeni analizi ve tipografik normalizasyon (tire birleştirme, satır sonu temizleme) işlemlerini arka plan iş parçacığında yürüterek kullanıcı deneyimini kesintisiz tutar.

### 4. Dahili Model Yöneticisi ve İndirici
Kullanıcıların harici sunucular kurmasına ya da terminal komutlarıyla uğraşmasına gerek kalmadan yerel modelleri yönetmesini sağlar:

* **Seçilmiş Yerel Model Kataloğu (`local_models_catalog.py`):**
  * **Üretim Modelleri (Gemma 4 Ailesi):** 128K bağlam pencereli 3.2 GB hafif E2B, 6.2 GB dengeli 12B ve 13.1 GB amiral gemisi 26B MoE.
  * **Yardımcı Modeller:** Microsoft Harrier 0.6B (Gömme) ve Qwen3-Reranker 0.6B (Yeniden Sıralama).
* **Parçalı HTTP İndirme Yöneticisi (`model_downloader.py`):** Hugging Face üzerinden modelleri doğrudan arayüz içerisinden indiren; anlık hız, tahmini süre (ETA), ilerleme çubuğu ve iptal desteği sunan arka plan indiricisi. Modeller Git deposunu temiz tutmak adına işletim sistemi kullanıcı veri dizininde (`~/.local/share/zettelkasten_ai/models/`) depolanır.

### 5. Donanım Kaynak Denetleyicisi ve OOM Koruması (`hardware_checker.py`)
* **Otomatik Donanım Tespiti:** Sistem RAM'i, CPU çekirdekleri, GPU aygıtları ve kullanılabilir VRAM miktarını proaktif olarak denetler.
* **Bellek Aşımı (OOM) Koruması:** Modeller belleğe alınmadan veya indirilmeden önce sistem kapasitesini doğrulayarak çökmeleri önler.
* **Dinamik Katman Paylaştırma:** Mevcut donanım gücüne göre GPU'ya devredilecek en uygun katman sayısını (`n_gpu_layers`) dinamik olarak belirler.

### 6. Gelişmiş Canlı Markdown Çalışma Alanı (`markdown_editor_widget.py`)
* **Kaynak ve Okuma Modları:** `Ctrl+E` kısayolu veya başlık çubuğundaki düğmeyle ham Markdown düzenleme ile biçimlendirilmiş okuma modu arasında anında geçiş.
* **Zengin Biçimlendirme Araç Çubuğu:** Başlıklar (H1–H4), kalın (`Ctrl+B`), eğik (`Ctrl+I`), üstü çizili, sözdizimi vurgulamalı kod blokları, alıntılar, listeler, tablolar ve yatay ayırıcılar için tek tıkla kısayollar.
* **Etkileşimli Görev Listeleri:** Hem düzenleme hem de okuma modunda tıklanarak işaretlenebilen `- [ ]` ve `- [x]` onay kutuları.
* **LaTeX Matematik Normalizasyonu:** Satır içi (`$ ... $`, `\( ... \)`) ve blok (`$$ ... $$`, `\[ ... \]`) matematik formüllerinin Flutter KaTeX ile kod bloklarını bozmadan temiz şekilde işlenmesi.
* **Belge İstatistikleri:** Kelime, karakter, satır sayısı ve tahmini okuma süresini gösteren gerçek zamanlı sayaçlar.
* **Otomatik Kaydetme:** Arka planda çalışan ve kaydedilmemiş değişiklikleri (`*`) gösteren güvenli otomatik kayıt mimarisi.

### 7. Çift Yönlü [[WikiLink]] Sistemi
* **WikiLink Sözdizimi:** Düşünceler `[[Not Başlığı]]` veya `[[Hedef Not|Özel İsim]]` biçiminde kolayca birbirine bağlanır.
* **Etkileşimli Gezinme ve Otomatik Oluşturma:** Herhangi bir bağlantıya tıklandığında hedef nota doğrudan geçilir. Hedef not henüz mevcut değilse tek tıkla oluşturulup bağlanır.
* **Hızlı Bağlantı Seçici (`Ctrl+K`):** Notlar arasında hızlıca tek veya çift yönlü bağlantılar kurmayı sağlayan arama penceresi.
* **Kesin Anlamsal Kenar Çözümleme:** Tam başlıklar ve normalleştirilmiş küçük harf eşleşmeleriyle halüsinatif veya hatalı grafik bağlantılarını engeller.

### 8. Etkileşimli Kanvas Zihin Haritası ve Bilgi Grafiği (`mind_map_widget.py`)
* **Kanvas Çizimi:** `flet.canvas` kullanılarak GPU ivmeli dinamik grafik çizimi ve `PyGraphviz` ile otomatik düğüm konumlandırma.
* **Kaydırma ve Yakınlaştırma:** `InteractiveViewer` kontrolleriyle akıcı pan ve zoom özellikleri.
* **Doğrudan Odaklanma ve Odak Modu:** Grafikteki herhangi bir düğüme tıklandığında o notun düzenleme alanında anında açılması.

### 9. Modüler 3 Bölmeli Esnek Arayüz ve Ayar Mimarisi
* **Sol Kenar Çubuğu:** Koleksiyon filtreleme, anlık arama, not sayısı göstergeleri ve ayarlar paneli.
* **Merkezi Çalışma Alanı:** Markdown editörü, canlı önizleme, aktif not başlığı ve kategori rozeti içeren dinamik AppBar.
* **Sağ Panel:** Etkileşimli zihin haritası kanvası ve bağlı notlar listesi.
* **Daraltılabilir İnce Raylar:** Yazı alanını genişletmek için sol kenar çubuğunu (`Ctrl+[`) veya sağ paneli (`Ctrl+]`) 50 piksellik kompakt simge raylarına dönüştürebilme.
* **Sürüklenebilir Ayırıcılar:** Bölme genişliklerini fareyle serbestçe ayarlama imkanı.
* **Ayrılmış Ayarlar Deposu (`db/settings.db`):** İzole bağlantılarla yerel tercihleri ve API anahtarlarını yöneten, özel sistem yönlendirmeleri, canlı donanım tanıları ve fabrika ayarlarına sıfırlama desteği sunan 4 sekmeli (Genel, Yapay Zeka, Depolama, Sistem) modern ayar paneli.

### 10. Güçlü SQLite Kalıcılık Katmanı ve Gizlilik
* **Write-Ahead Logging (WAL):** `db/notes.db` ve `db/settings.db` veritabanlarında eşzamanlı okuma ve yazma işlemlerinde performansı artıran WAL modu yapılandırması.
* **İş Parçacığı Güvenliği:** Thread-local bağlantılar sayesinde iş parçacıkları arasında güvenli veritabanı iletişimi ve basamaklı yabancı anahtar bütünlüğü (`PRAGMA foreign_keys = ON`).
* **Özel Veritabanı Yolu Desteği (`CUSTOM_DB_PATH`):** Kullanıcının veritabanı dosyalarını dilediği dizinde konumlandırabilmesi.
* **Sıfır Veri Sızıntısı:** Tüm veritabanları ve günlük kayıtları yerel tutulur ve Git sürüm kontrolünden tamamen hariç tutulur.

### 11. Kapsamlı Otomasyon Test Paketi ve Mühendislik Disiplini
* **Genişletilmiş Test Kapsamı:** Domain modelleri, UI bileşenleri, yapay zeka ayrıştırıcıları, RAG vektör havuzu, cross-encoder yeniden sıralayıcı ve SQLite işlemlerini kapsayan 23 dosyada **291 başarılı otomatik birim test**.
* **Hızlı Yürütme:** Tüm test paketi yaklaşık 15-16 saniyede başarıyla tamamlanır.

---

## Kullanılan Teknolojiler

* **Masaüstü Framework:** Python 3.13, Flet (Flutter Masaüstü Katmanı)
* **Yapay Zeka ve Çıkarım:** `llama-cpp-python` (Vulkan GPU hızlandırması), Google Gemini API (`google-genai` SDK)
* **RAG ve NLP:** Microsoft Harrier 0.6B (Gömme), Qwen3-Reranker 0.6B (Cross-Encoder), NumPy
* **Belge ve Grafik İşleme:** PyPDF, PyGraphviz, Python-Markdown, KaTeX
* **Depolama ve Sistem:** SQLite (WAL modu, Thread-Local Bağlantılar), psutil, requests
* **Test:** Pytest (291 birim test)
