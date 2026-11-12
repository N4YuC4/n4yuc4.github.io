# DocNeedle: Şema Tabanlı Belge Veri Çıkarma Sistemi

Kurumsal belgelerden—taranmış faturalar, çok sayfalı sözleşmeler, finansal tablolar veya el yazılı makbuzlar—yapılandırılmış veri çekmek geleneksel yöntemlerle ciddi bir mühendislik açmazıdır. Klasik optik karakter tanıma (OCR) motorları soluk taramalarda ve karmaşık tablolarda harf hataları yaparak bağlamı bozar; popüler bulut modelleri hassas ticari sırların ve kişisel verilerin dışarı sızmasına yol açar; devasa genel dil modelleri ise belge boyutu 50 sayfayı aştığında dikkat kaybı yaşayarak halüsinasyon üretir.

**DocNeedle**, bu tıkanıklıkları aşmak için geliştirilmiş, **%100 yerel ve gizlilik odaklı bir yapılandırılmış bilgi çıkarma (Information Extraction) motoru ve mikroservis platformudur**.

Sisteme yüklenen belgelerden kullanıcı tarafından belirlenen JSON şemasına uygun alanları ayıklar; her veriyi doğrulanabilir sayfa referansı, kaynak metin alıntısı ve istatistiksel güven skoruyla birlikte sunar. Veriler hiçbir zaman kalıcı diske yazılmaz ve harici bulut API'lerine tek bir bayt veri dahi gönderilmez.

![DocNeedle Etkileşimli Arayüz](/static/images/portfolio-images/docneedle/dashboard_preview.png)

---

## Sistem Mimarisi ve İşlem Akışı

DocNeedle; doküman ayrıştırma, çok modlu vektörleştirme, hibrit arama ve yerel model çıkarımını tek bir uçucu bellek oturumunda birleştirir:

```
[Yüklenen Belge & JSON Şeması]
               │
               ▼
┌────────────────────────────────────────────────────────┐
│ Uçucu Bellek-İçi İşlem Hattı (PR_SET_DUMPABLE = 0)     │
│                                                        │
│  Docling Ayrıştırıcı (io.BytesIO) ──► AcroForm Analizi │
│         │                                              │
│         ▼                                              │
│  SessionVectorStore (Bellek-İçi RRF Hibrit İndeks)     │
│         │                                              │
│         ▼                                              │
│  Yerel Çok Modlu Model (Qwen3.5-4B + mmproj)           │
│         │                                              │
│         ▼                                              │
│  Uzamsal Çakışma Çözücü ve Güven Doğrulayıcı          │
└────────────────────────────────────────────────────────┘
               │
               ▼
[Sayfa Referanslı Yapılandırılmış JSON Çıktısı]
               │
               ▼
    finally: store.clear() (RAM anında tahliye edilir)
```

Modüler kod mimarisi, çekirdek güvenliğinden C++ çıkarım katmanına kadar katı bir sorumluluk ayrımı sunar:

```
DocNeedle/
├── .github/
│   └── workflows/
│       └── ci.yml                # CI: Lint, 159 hermetik test, konteyner ve fail-fast denetimi
├── assets/
│   ├── logo.svg / logo.png       # Vektör ve raster marka logoları
│   ├── favicon.svg               # Uygulama favicon ikonu
│   ├── demo.gif                  # Canlı veri çıkarma animasyonu
│   ├── dashboard_preview.png     # Web arayüzü önizleme görseli
│   └── examples/                 # Örnek belgeler (fatura, kira sözleşmesi, makbuz)
├── app.py                        # Port 7860 üzerinde birleşik Gradio 6 ve FastAPI girişi
├── config.toml                   # Uygulama, model, donanım ve çıkarım ayarları
├── pyproject.toml / requirements.txt
├── Dockerfile                    # Multi-stage Python 3.14-slim üretim ve test imajı
├── docker-compose.yml            # Birleşik `gpu` ve `cpu` donanım profilleri
├── scripts/
│   ├── download_models.py        # Doğrulamalı kuantize GGUF model indirme aracı
│   ├── benchmark_extractbench.py # ExtractBench değerlendirme ve raporlama betiği
│   └── deploy_space.sh           # Hugging Face Spaces (ZeroGPU) tek tıkla dağıtım
├── models/
│   ├── embedding/                # EmbeddingGemma-2 GGUF + SigLIP mmproj-F16 projektörü
│   ├── llm/                      # Qwen3.5-4B-Q4_K_M GGUF + mmproj-Qwen3.5-4B-F16
│   └── reranker/                 # Qwen3-Reranker-0.6B.Q4_K_M GGUF
├── src/docneedle/
│   ├── main.py                   # FastAPI uygulama fabrikası, CORS ve /healthz tanı ucu
│   ├── config.py                 # Pydantic BaseSettings (TOML + ortam değişkenleri)
│   ├── hardening.py              # Linux çekirdeği PR_SET_DUMPABLE bellek koruması
│   ├── cuda_compat.py            # ZeroGPU önyükleyicileri ve dinamik CUDA yönetimi
│   ├── api/
│   │   ├── routes_extract.py     # POST /v1/extract (senkron veri çıkarma)
│   │   ├── routes_jobs.py        # POST /v1/jobs, GET /v1/jobs/{id}, SSE /events
│   │   └── validation.py         # Özyinelemeli $ref çözücü ve yük sınırı denetimi
│   ├── jobs/
│   │   ├── models.py             # JobStatus, JobProgress ve yanıt sözleşmeleri
│   │   └── manager.py            # Bellek-içi iş kaydı, SSE yayın kuyrukları ve TTL
│   ├── ingest/
│   │   ├── parser.py             # Bellek-içi Docling + pypdfium2 ayrıştırma (sıfır-disk)
│   │   ├── chunker.py            # Başlık ve görsel ekleme destekli DoclingChunker
│   │   ├── acroform.py           # Etkileşimli PDF AcroForm form alanı çıkarıcısı
│   │   ├── cache.py              # İş parçacığı güvenli bellek-içi LRU doküman önbelleği
│   │   ├── service.py            # IngestionService orkestratörü
│   │   └── models.py             # Doküman ve parça (chunk) veri modelleri
│   ├── retrieval/
│   │   ├── embedder.py           # Yerel libdocneedle_embed.so için ctypes bağlayıcısı
│   │   ├── docneedle_embed.cpp   # Yerel C++ çapraz modlu vektörleştirme çekirdeği
│   │   ├── worker.py             # Yalıtılmış alt süreç gömme sunucusu (RTLD_DEEPBIND)
│   │   ├── bm25.py               # Okapi BM25 sözcüksel arama motoru
│   │   ├── reranker.py           # Qwen3-Reranker cross-encoder logit puanlayıcısı
│   │   ├── store.py              # SessionVectorStore (bellek-içi RRF ve çeşitlilik)
│   │   └── models.py             # SearchResult arama sonucu modeli
│   ├── extraction/
│   │   ├── service.py            # Arama sorgu sentezi ve LLM orkestrasyonu
│   │   ├── verifier.py           # ConfidenceCalculator ve tip doğrulama
│   │   ├── matcher.py            # Birebir/yaklaşık metin ve sayfa kanıtı eşleştirici
│   │   ├── collision.py          # Mükerrer değerler için SpatialCollisionResolver
│   │   └── schemas.py            # İstek/yanıt Pydantic veri modelleri
│   └── llm/
│       ├── local_engine.py       # LocalLLMEngine (Qwen3.5-4B GGUF + mmproj görsel çıkarım)
│       ├── client.py             # LLMClient arayüzü
│       ├── handlers.py           # Çok modlu sohbet tamamlama yöneticileri
│       ├── parsing.py            # Çıktı temizleme, JSON ayıklama ve unicode onarımı
│       ├── prompts.py            # Şema kısıtlı prompt inşa edici
│       └── speculative.py        # Prompt Lookup Decoding spekülatif hızlandırıcı
└── tests/
    ├── test_zero_disk.py         # Çekirdek PR_SET_DUMPABLE ve sıfır-disk testleri
    ├── test_clean_modules.py     # Ayrıştırma, doğrulayıcı, eşleyici birim testleri
    ├── test_collision*.py        # Uzamsal çakışma çözümü testleri (EN ve TR)
    ├── test_acroform.py          # Etkileşimli PDF AcroForm form çıkarma testleri
    ├── test_ocr_grounding.py     # Çok modlu görsel kanıt ve alıntı testleri
    ├── test_ui_schema_sync.py    # Gradio 6 şema oluşturucu senkronizasyon testleri
    ├── test_health.py            # /healthz tanı ucu ve donanım testleri
    └── test_extraction.py        # Uçtan uca veri çıkarma entegrasyon testleri
```

---

## Temel Mühendislik Çözümleri

### 1. Sıfır-Disk Bellek Mimarisi ve Çekirdek Güvenliği

Finansal raporlar, hasta verileri veya ticari sözleşmeler gibi belgelerin gizliliği yalnızca yazılım seviyesinde geçici dosyalar silinerek garanti edilemez. DocNeedle bu güvenceyi işletim sistemi çekirdeği düzeyinde sağlar:

* **Sadece Uçucu Bellek (RAM-Only):** Sisteme gelen dosyalar doğrudan bayt akışı (`io.BytesIO`) olarak karşılanır; parçalama, gömme vektörleri ve arama indeksleri yalnızca `SessionVectorStore` içinde tutulur. İstek tamamlandığı an `finally: store.clear()` tetiklenerek ayrılan bellek blokları işletim sistemine geri verilir.
* **Bellek Dökümü Engelleme (Anti-Dumping):** `src/docneedle/hardening.py` modülü, Linux çekirdeğinin `prctl(PR_SET_DUMPABLE, 0)` bayrağını etkinleştirir. Süreç çalışırken yetkisiz bellek dökümü (core dump) alınması veya harici araçların `ptrace` ile sürece bağlanıp belleği okuması çekirdek düzeyinde engellenir.
* **Sertleştirilmiş Konteyner & CI Doğrulaması:** Üretim ortamında salt okunur kök dosya sistemi (`read_only: true`), RAM tabanlı geçici alan (`tmpfs`, 1 GB, `nosuid`), sıfırlanmış core dump limiti ve çevrimdışı Hugging Face kipi (`HF_HUB_OFFLINE=1`) zorunlu tutulur. GitHub Actions CI boru hattı; her derlemede `PR_SET_DUMPABLE=0` çekirdek logunu, salt okunur dosya sisteminde sağlık ucunu ve geçersiz dosya formatlarında fail-fast (HTTP 415) yanıtını otomatik olarak denetler.

### 2. OCR Bağımsız Görsel RAG ve Yerel C++ Vektörleştirme

Klasik iş akışları belgeleri önce bir OCR motoruna sokar; okunamayan harfler veya bozulan tablo dizilimleri dil modeline aktarıldığında çıkarım baştan çöker. DocNeedle dokümanları çift kanaldan işler:

* **Dijital PDF'ler:** Seçilebilir metin içeren belgeler Docling Core ile başlık hiyerarşisi ve tablo yapıları kayıpsız korunarak Markdown parçalarına ayrılır.
* **Taranmış Sayfalar ve Görseller:** Taranmış sözleşmeler, el yazılı makbuzlar ve resimler (PNG, JPG, TIFF, WEBP), `pypdfium2` ile 108 DPI çözünürlükte işlenerek doğrudan görsel parça olarak sisteme alınır.
* **Doğrudan Görsel Çıkarım:** Sayfa görselleri SigLIP projeksiyonu üzerinden çok modlu Qwen3.5-4B modeline yüksek çözünürlüklü görsel belirteçler olarak iletilir. Model sayfayı bir insanın gördüğü gibi doğrudan görsel olarak inceler; metne dönüştürme hataları tamamen elenir.
* **Yerel C++ Gömme Çekirdeği (`libdocneedle_embed.so`):** Python-C++ arasındaki serileştirme yükünü ortadan kaldırmak için C++ ile bağımsız bir gömme motoru geliştirilmiştir. EmbeddingGemma-2 ile metin sorgularını ve görsel parçaları 768 boyutlu ortak bir L2 uzayında buluşturur. Modern NVIDIA mimarilerini (`sm_80` Ampere, `sm_86`, `sm_89` Ada Lovelace ve `sm_120a` Blackwell) dahili CUDA çekirdekleriyle destekler ve `RTLD_LOCAL | RTLD_DEEPBIND` bayraklarıyla sembol çakışmalarına karşı izole edilir.

### 3. AcroForm Ayrıştırma ve Uzamsal Çakışma Çözümü (Spatial Collision Resolution)

Resmi vergi beyannameleri veya sigorta formları işlenirken genel amaçlı modeller genellikle iki kritik yanılsamaya düşer: işaretlenmemiş kutucukları dolu varsaymak ve belgedeki tek bir baskın tutarı boş kalan diğer alanlara kopyalamak.

* **AcroForm Doğrudan Ayrıştırma:** DocNeedle, PDF nesne akışlarını doğrudan `pypdfium2` arayüzü (`FPDFPage_GetAnnot`, `FPDFAnnot_GetFormFieldType`) üzerinden okur. Form alan adları, ipuçları, onay kutusu durumları ve kullanıcı girdileri UTF-16LE akışından sıfır yanılsamayla çekilerek tablo formatında bağlama eklenir.
* **Uzamsal Çakışma Çözücü (`collision.py`):** Model, belgedeki tek bir belirgin tutarı (örneğin fatura toplamı) şemadaki birden fazla alana atadığında devreye girer. Değerin ilgili sayfada fiziksel olarak kaç kez geçtiği doğrulanır. Eğer sayfada tek bir kez geçiyorsa, alan tanımlarıyla değerin etrafındaki metin bağlamı arasındaki alaka puanlanır. Değer en yüksek ilgi skoruna sahip alana atanırken, mükerrer atanan diğer alanlar güvenle `found: False, value: None` durumuna getirilir.

### 4. VRAM Ayak İzi, Geniş Bağlam ve Çıkarım Optimizasyonları

Geniş belge koleksiyonlarında modelin 32.768 token bağlamında belleği tüketmeden çalışması dikkatle dengelenmiştir:

* **Gerçek Donanım VRAM Ölçümü:** Üç nöral modelin tümü (Qwen3.5-4B LLM, EmbeddingGemma-2 gömme ve Qwen3-Reranker) GPU'ya aktarıldığında ölçülen tepe VRAM tüketimi **7.286 MiB / 8.188 MiB** seviyesindedir (~7.3 GB - RTX 4060 Laptop). Sistem 8 GB ekran kartlarında bile tam kapasite çalışır; modeller ilk istekte tembel yükleme (lazy-loading) ile belleğe alınır (~10 sn soğuk, ~2.3 sn sıcak istek).
* **Flash Attention ve Sıkıştırılmış KV Önbellek:** 32K token tam bağlam penceresinde GPU belleğinin şişmesini (OOM) önlemek için `llama.cpp` Flash Attention çekirdekleriyle çalıştırılır. Key tensörleri FP16 hassasiyetinde tutulurken, Value tensörleri 8-bit (Q8_0) seviyesinde kuantize edilerek önbellek boyutu yarı yarıya indirilir.
* **RRF Hibrit Arama & Reranker:** EmbeddingGemma-2 yoğun vektörleri ile Okapi BM25 anahtar kelime eşleşmeleri, sayfa çeşitliliği dengesi gözetilerek (k = 60 sabitiyle) Reciprocal Rank Fusion üzerinden harmanlanır. Kritik sorgularda aday parçalar **Qwen3-Reranker-0.6B** cross-encoder modeline aktarılarak logit puan farkıyla elenir.
* **Spekülatif Kod Çözme (Prompt Lookup Decoding):** Şema tabanlı JSON üretiminde hız kazanmak için n-gram eşleşmelerine dayalı dahili `LlamaPromptLookupDecoding` (`max_ngram_size=2`) mekanizması desteklenir.

### 5. Birleşik Port 7860, Dağıtım ve Asenkron İş Akışı

* **Tek Portta Birleşik Hizmet (7860):** Gradio 6 web arayüzü ve FastAPI REST API uçları tek bir port (`7860`) üzerinden birlikte sunulur.
* **Konteyner Donanım Profilleri:** `docker-compose.yml` modern profil mimarisini destekler: NVIDIA GPU hızlandırmalı üretim için `docker compose --profile gpu up -d`, geliştirme ve CI doğrulaması için `docker compose --profile cpu up -d`.
* **Hugging Face Spaces (ZeroGPU):** `bash scripts/deploy_space.sh` komutu ile dinamik NVIDIA A100/A10G GPU dilimlerine sahip Hugging Face Spaces ortamına tek adımda kurulur.
* **Dinamik Şema ve Canlı SSE Akışı:** Çok belgeli toplu işler (`POST /v1/jobs`), Server-Sent Events (`GET /v1/jobs/{id}/events`) üzerinden anlık ilerleme yüzdesiyle canlı takip edilir; form alanları arayüzden seçilebilir veya iç içe `$ref` işaretçilerini çözebilen çift yönlü senkronize ham JSON şema editörü kullanılabilir.

---

## ExtractBench Kıyaslama ve Liderlik Tablosu

DocNeedle; faturalar, resmi sözleşmeler, finansal tablolar ve el yazılı makbuzlardan oluşan **370 belge**, **4.869 sayfa** ve **13.577 etiketli alan** içeren **[ExtractBench](https://www.extractbench.ai/)** (LlamaIndex, [arXiv:2607.29677](https://arxiv.org/abs/2607.29677)) kurumsal veri setinde test edilmiştir.

Resmi ExtractBench liderlik tablosu (`leaderboard.csv`) karşılaştırması:

| Sistem / Model | Sağlayıcı / Kategori | Mimari ve Boyut | Genel F1 | Kısa (≤10s) | Orta (11-50s) | Uzun (>50s) | Sayfa Konumu | Sayfa Başı Maliyet | Gizlilik ve Depolama |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **LlamaExtract Agentic Plus** | LlamaIndex | Bulut Ajan İş Hattı | **96.17%** | 97.02% | 94.30% | 94.65% | 88.26% | $0.0750 | Bulut API (Harici) |
| **Codex (GPT-6.1 Sol Evidence)** | OpenAI / Codex | Frontier Kodlama Ajanı | **95.31%** | 97.01% | 92.96% | 85.46% | 89.37% | $0.0713 | Bulut API (Harici) |
| **Claude Code (Sonnet 5.5 Evidence)** | Anthropic | Frontier Kodlama Ajanı | **94.68%** | 96.22% | 92.97% | 83.69% | 75.99% | $0.0569 | Bulut API (Harici) |
| **OpenAI GPT-6 Astra** | OpenAI | Ticari Büyük VLM | **91.91%** | 97.22% | 90.56% | 31.70% | 0.00% *(Yok)* | $0.1109 | Bulut API (Harici) |
| **Qwen3.5 4B (Yalın Temel Model)** | Alibaba / OSS | Bağımsız Temel Model | **82.43%** | 89.06% | 76.64% | 27.31% | 0.00% *(Yok)* | Ücretsiz (yerel) | Yerel / Self-Hosted |
| **Google Gemini 3.8 Flash** | Google | Ticari Hızlı VLM | **80.71%** | 88.14% | 72.23% | 28.70% | 0.00% *(Yok)* | $0.0043 | Bulut API (Harici) |
| **DocNeedle (Süreç İçi)** | **DocNeedle** | **Qwen3.5-4B + Gemma2-RAG** | **75.71%** | **77.16%** | **69.70%** | **71.43%** | **80.95%** | **$0.00 (yerel)** | **Sıfır-Disk RAM / Hava Boşluklu** |

### Öne Çıkan Bulgular ve Mühendislik Çıkarımları

* **Uzun Belgelerde Üstün Dayanıklılık (Temel Modele Göre +44.12 Puan):** 50 sayfayı aşan belgelerde RAG desteği olmayan büyük modeller dikkat dağınıklığı yaşayarak çökerken (yalın Qwen3.5 4B %27.31'e, GPT-6 Astra %31.70'e düşer), DocNeedle görsel ve metinsel parçaları akıllıca yönlendirerek **%71.43 F1** başarısını korur (2.6 kat dayanıklılık artışı).
* **Denetlenebilir Sayfa Konumlandırması (%90.67 Kısa, %80.95 Genel):** Ticari büyük modeller kaynak gösteriminde %0.00 alırken, DocNeedle çıkarılan her veri için doğrulanmış sayfa numarası ve doğrudan alıntı metni sunar.
* **Modelden Bağımsız Ölçeklenebilirlik:** Yayımlanan bu sonuçlar (**%75.71 Genel F1**, **%90.67 Kısa Sayfa Doğrulaması**), sistemin tüketici sınıfı donanımlarda (asgari 8 GB VRAM) çalışabildiğini kanıtlamak için kompakt bir **4B model** (`Qwen3.5-4B-Q4_K_M`) ve **0.6B gömme modeli** ile elde edilmiştir. Doküman ayrıştırma, AcroForm çıkarma ve hibrit RAG mimarisi modelden tamamen bağımsız olduğundan; daha büyük model ağırlıklarıyla (örneğin **Qwen3.5-9B** veya **35B**) sıfır-disk gizlilik garantisi korunarak **%88–95+ F1** seviyelerine doğrudan ölçeklenebilir.
* **Sıfır Marjinal Maliyet ve Hava Boşluklu Güvenlik:** Sayfa başına $0.00 maliyetle çalışırken, uçucu RAM garantileriyle kurumsal veri sızıntılarını tamamen engeller.

### Segment Bazlı Ayrıntılı Sonuçlar

`scripts/benchmark_extractbench.py` ile yürütülen 370 belgelik testin segment dökümü:

| Metrik | Kısa (≤10s) | Orta (11-50s) | Uzun (>50s) | Genel (370 Belge) |
| :--- | :---: | :---: | :---: | :---: |
| **Belge Sayısı** | 252 | 98 | 20 | **370** |
| **Hedef Alan Sayısı** | 10.676 | 2.808 | 93 | **13.577** |
| **Birebir Eşleşen Alanlar** | 8.759 | 2.153 | 60 | **10.972** |
| **Birleşik Değer F1** | **77.16%** | **69.70%** | **71.43%** | **75.71%** |
| **Değer Kesinliği (Precision)** | **81.00%** | **79.43%** | **80.88%** | **80.73%** |
| **Değer Duyarlılığı (Recall)** | **73.66%** | **62.10%** | **63.95%** | **71.27%** |
| **Sayfa Konumlandırma** | **90.67%** | **62.14%** | **50.58%** | **80.95%** |
| **Eksik Alan Doğruluğu (Strict Null)** | **81.92%** | **84.62%** | **27.78%** | **82.35%** |

---

## Kullanılan Teknolojiler

* **Çalışma Zamanı ve Servis Mimarisi:** Python 3.14+, FastAPI 0.115+, Pydantic v2, Uvicorn, Server-Sent Events (SSE)
* **Kullanıcı Arayüzü:** Gradio 6+ (Koyu Tema, Dinamik Şema Editörü, Canlı İlerleme Göstergeleri)
* **Süreç-İçi Model Çıkarımı:** `llama-cpp-python` (CUDA/cuBLAS & Flash Attention), Qwen3.5-4B GGUF Çok Modlu Model, SigLIP Görsel Projektör
* **Vektör Gömme ve Yerel Çekirdek:** C++ (`docneedle_embed.cpp`, `libdocneedle_embed.so`), EmbeddingGemma-2 GGUF, `ctypes` süreç izolasyonu
* **Belge Ayrıştırma ve İşleme:** Docling Core 2.15+, `pypdfium2` (AcroForm ayrıştırıcı ve 108 DPI rasterizer), `python-docx`, `openpyxl`, Pillow
* **Arama ve Yeniden Sıralama:** Okapi BM25 (`rank-bm25`), Reciprocal Rank Fusion (RRF), Qwen3-Reranker-0.6B GGUF
* **Güvenlik ve Konteyner:** Linux `prctl(PR_SET_DUMPABLE, 0)`, Docker, Docker Compose (GPU/CPU donanım profilleri), Hugging Face Spaces (ZeroGPU)
* **Test ve Kalite:** Pytest (159 hermetik birim testi), Ruff, Sıfır-Disk CI doğrulaması
