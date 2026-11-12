# DocNeedle: Şema Tabanlı Belge Veri Çıkarma Sistemi

**DocNeedle**, karmaşık kurumsal dokümanlardan (PDF, taranmış faturalar, sözleşmeler, tablolar) belirlenen JSON şemasına uygun bilgileri doğrudan ayıklayan, her veri için doğrulanabilir sayfa referansı, kaynak alıntısı ve güven skoru üreten yerel bir **yapılandırılmış veri çıkarma (Information Extraction) motorudur**.

Harici bulut API'lerine bağımlı olan veya hata payı yüksek klasik optik karakter tanıma (OCR) motorlarıyla çalışan sistemlerin aksine DocNeedle; verileri üçüncü taraf sunuculara göndermeden, diske hiçbir kalıcı iz bırakmadan (sıfır-disk bellek garantisi) %100 yerel ortamda çalışır.

![DocNeedle Etkileşimli Arayüz](/static/images/portfolio-images/docneedle/dashboard_preview.png)

---

## Mimari ve Temel Bileşenler

```
DocNeedle/
├── assets/                       # Marka grafikleri ve SVG ikonlar
├── app.py                        # Birleşik Gradio 6 arayüzü + FastAPI kök bağlama ve ZeroGPU girişi
├── config.toml                   # Temel uygulama, model ve işlem hattı yapılandırması
├── src/docneedle/
│   ├── main.py                   # FastAPI servis fabrikası, CORS ve /healthz tanı uçları
│   ├── hardening.py              # Linux çekirdeği PR_SET_DUMPABLE bellek dökümü koruması
│   ├── cuda_compat.py            # ZeroGPU önyükleyicileri ve dinamik CUDA sembol yönetimi
│   ├── api/                      # Senkron (/v1/extract) ve asenkron iş uç noktaları
│   ├── jobs/                     # Bellek-içi asenkron iş kuyruğu ve anlık SSE akışı
│   ├── ingest/                   # Docling parçalama, pypdfium2 AcroForm çıkarımı ve görsel rasterizer
│   ├── retrieval/                # Yerel C++ gömme motoru, SessionVectorStore, BM25 ve Qwen3-Reranker
│   ├── extraction/               # Uzamsal çakışma çözümü, şema doğrulama ve güven puanlama
│   └── llm/                      # Qwen3.5-4B GGUF çok modlu çıkarım ve spekülatif kod çözme
└── tests/                        # Sıfır-disk doğrulamalı 159 hermetik birim testi
```

### 1. Sıfır-Disk Bellek Güvenliği ve Çekirdek Düzeyinde Koruma
Kişisel veri, finans veya ticari sır içeren belgelerin güvenliği için sistem seviyesinde katı gizlilik tedbirleri uygulanmıştır:
* **Yalnızca Uçucu Bellek (RAM-Only):** Sisteme yüklenen dosyalar, çıkarılan metin parçaları, vektör gömmeleri ve arama indeksleri yalnızca geçici bellekte (`SessionVectorStore`) tutulur. Her işlem tamamlandığında `finally: store.clear()` bloğu ile ayrılan tüm bellek blokları anında geri verilir.
* **Bellek Dökümü Engelleme:** Linux çekirdeğinin prctl arayüzü üzerinden (`prctl(PR_SET_DUMPABLE, 0)` - `src/docneedle/hardening.py`) sürecin belleği dışarıya kilitlenir; yetkisiz bellek dökümü (core dump) alınması ya da `ptrace` ile sürecin izlenmesi engellenir.
* **Sertleştirilmiş Konteyner Yapısı:** Üretim ortamında salt okunur kök dosya sistemi (`read_only: true`), RAM tabanlı `/tmp` dizini (`tmpfs`, 1 GB, `nosuid`), sıfırlanmış core dump limiti ve tamamen çevrimdışı Hugging Face kipi (`HF_HUB_OFFLINE=1`) ile çalıştırılır.

```
[Yüklenen Belge ve Şema]
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
│  Yerel Çok Modlu LLM (Qwen3.5-4B + mmproj)             │
│         │                                              │
│         ▼                                              │
│  Uzamsal Çakışma Çözücü ve Güven Doğrulayıcı          │
└────────────────────────────────────────────────────────┘
            │
            ▼
[Doğrulanmış Kaynak Alıntılarıyla Yapılandırılmış JSON]
            │
            ▼
  finally: store.clear() (RAM tamamen boşaltılır)
```

### 2. Klasik OCR'ı Devre Dışı Bırakan Görsel RAG Yaklaşımı
Geleneksel optik karakter tanıma (OCR) motorları; el yazılı notlar, kaşeler, soluk taranmış belgeler veya karmaşık tablo yapılarında harf ve biçim hataları yaparak çıkarım kalitesini düşürür. DocNeedle bu sorunu çift yönlü bir belge işleme hattıyla aşar:
* **Dijital Belgeler:** Seçilebilir metin içeren PDF'ler Docling Core ile hiyerarşik Markdown parçalarına ayrılarak başlık düzenleri ve tablo yapıları kayıpsız korunur.
* **Taranmış Dokümanlar ve Görseller:** Taranmış sayfalar ve görsel dosyaları (PNG, JPG, TIFF, WEBP), `pypdfium2` ile yüksek çözünürlükte (108 DPI) işlenip herhangi bir metin dönüşümüne zorlanmadan doğrudan görsel parça olarak sisteme alınır.
* **Görsel Bağlam ile Çıkarım:** Sayfa görselleri SigLIP projeksiyonu (`mmproj-F16.gguf`) üzerinden vektör uzayına taşınır ve çok modlu büyük dil modeline (Qwen3.5-4B) yüksek çözünürlüklü görsel belirteçler olarak iletilir. Model, sayfayı bir insanın gördüğü gibi doğrudan görsel olarak inceler.

### 3. Yerel C++ Çapraz Modlu Vektörleştirme Motoru
Geniş belge koleksiyonlarında arama gecikmesini sıfıra indirmek amacıyla C++ ile yazılmış bağımsız bir gömme motoru (`src/docneedle/retrieval/docneedle_embed.cpp`) paylaşımlı kütüphane (`libdocneedle_embed.so`) olarak derlenmiştir:
* **Ortak Vektör Uzayı:** Metin sorgularını (`task: search result | query: {text}`) ve sayfa görsellerini EmbeddingGemma-2 ile 768 boyutlu L2-normalleştirilmiş tek bir vektör uzayında buluşturur.
* **Hazır CUDA Desteği:** `libggml-cuda.so`, modern NVIDIA mimarilerini (`sm_80` Ampere, `sm_86`, `sm_89` Ada Lovelace ve `sm_120a` Blackwell) dahili çekirdekleriyle destekler; çalışma anında JIT derleme beklemeden doğrudan GPU gücünden faydalanır.
* **Dinamik Kütüphane İzolasyonu:** C++ motoru, Python `ctypes` üzerinden `RTLD_LOCAL | RTLD_DEEPBIND` bayraklarıyla yalıtılmış bir alt süreçte çalıştırılır. Böylece `llama-cpp-python` ile paylaşımlı sembol çakışmaları tamamen önlenir.

### 4. Etkileşimli PDF Formlarında (AcroForm) Doğrudan Ayrıştırma
Vergi beyannameleri, sigorta bildirimleri veya başvuru formları işlenirken dil modelleri genellikle işaretlenmemiş boş kutucukları dolu varsayabilir veya yan yana duran alan adlarını karıştırabilir.
* DocNeedle, `pypdfium2` arayüzü (`FPDFPage_GetAnnot`, `FPDFAnnot_GetFormFieldType`) üzerinden PDF nesne akışlarını doğrudan tarar.
* Form alanlarının adlarını, geliştirici ipuçlarını, onay kutusu durumlarını ve kullanıcı girdilerini UTF-16LE akışından hatasız okur.
* Çıkarılan form verilerini yapılandırılmış Markdown tablolarına dönüştürerek modelin bağlamına ekler; resmi formlarda sıfır yanılsamayla kesin sonuç verir.

### 5. Uzamsal Çakışma Çözücü (Spatial Collision Resolution)
Bir belgede tek bir belirgin tutar (örneğin fatura toplamı veya işlem tarihi) yer aldığında, dil modelleri genellikle bu tutarı belgede bulunmayan diğer boş alanlara da kopyalama eğilimi gösterir.
* `SpatialCollisionResolver` (`src/docneedle/extraction/collision.py`), çıkarım sonuçlarını inceleyerek farklı şema anahtarlarına aynı değerin atanıp atanmadığını tespit eder.
* Değerin ilgili sayfada fiziksel olarak kaç kez geçtiğini doğrular.
* Eğer değer sayfada tek bir kez geçiyorsa, şemadaki alan açıklamalarıyla değerin etrafındaki metin bağlamı arasındaki anlamsal ilgiyi puanlar.
* Değeri en yüksek ilgi skoruna sahip alana bırakır; mükerrer atanan diğer alanları ise güvenle `found: False, value: None` durumuna getirir.

### 6. Hibrit Arama (RRF) ve Cross-Encoder Yeniden Sıralama
* **Reciprocal Rank Fusion (RRF):** EmbeddingGemma-2 yoğun anlamsal vektörleri ile Okapi BM25 anahtar kelime eşleşmeleri, sayfa çeşitliliği dengesiyle ($k=60$) RRF algoritması üzerinden harmanlanır.
* **Yeniden Sıralama:** Yüksek hassasiyet gerektiren aramalarda aday parçalar **Qwen3-Reranker-0.6B** cross-encoder modeline aktarılarak logit puan farkı (`logit("yes") - logit("no")`) üzerinden elenir.

### 7. Spekülatif Kod Çözme ve Bellek Optimizasyonu
* **Flash Attention ve Kompakt KV Önbellek:** Flash Attention ile FP16 veya kuantize edilmiş KV önbellek (`model_kv_cache_type_k=1`, `model_kv_cache_type_v=8` [Q8_0]) mimarisi kullanılır; 32.768 token bağlam penceresi tüketici sınıfı donanımlarda bile rahatça çalışır.
* **Spekülatif Kod Çözme Hızlandırması:** Şema tabanlı JSON üretiminde hız kazanmak için dahili `LlamaPromptLookupDecoding` (`max_ngram_size=2`, `num_pred_tokens=5`) mekanizmasını destekler.

### 8. Web Arayüzü ve Asenkron Akış API'si
* **7860 Portunda Birleşik Hizmet:** Gradio 6 web arayüzü ve FastAPI REST API uçları tek bir port üzerinden birlikte sunulur.
* **Görsel ve Ham Şema Eşitleme:** Form alanları arayüzden kolayca eklenebilir veya iç içe `$ref` işaretçilerini 20 derinliğe kadar çözebilen çift yönlü senkronize ham JSON şema sekmesi kullanılabilir.
* **Canlı İlerleme Akışı:** Çok belgeli toplu işler (`POST /v1/jobs`), Server-Sent Events (`GET /v1/jobs/{id}/events`) üzerinden anlık ilerleme yüzdesi ve alan bazında çıkarım olaylarıyla canlı takip edilir.

---

## ExtractBench Kıyaslama ve Performans Değerlendirmesi

DocNeedle; faturalar, resmi sözleşmeler, finansal tablolar ve el yazılı makbuzlardan oluşan **370 belge**, **4.869 sayfa** ve **13.577 etiketli alan** içeren **ExtractBench** (LlamaIndex, arXiv:2607.29677) veri setinde test edilmiştir.

| Sistem / Model | Mimari ve Dağıtım | Genel Değer F1 | Kısa (≤10s) | Orta (11-50s) | Uzun (>50s) | Sayfa Konumu | Sayfa Başı Maliyet | Gizlilik ve Depolama |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **LlamaExtract Agentic Plus** | Bulut Ajan İş Hattı | **96.17%** | 97.02% | 94.30% | 94.65% | 88.26% | $0.0750 | Bulut API (Harici) |
| **Codex (GPT-6.1 Sol Evidence)** | Frontier Kodlama Ajanı | **95.31%** | 97.01% | 92.96% | 85.46% | 89.37% | $0.0713 | Bulut API (Harici) |
| **Claude Code (Sonnet 5.5 Evidence)**| Frontier Kodlama Ajanı | **94.68%** | 96.22% | 92.97% | 83.69% | 75.99% | $0.0569 | Bulut API (Harici) |
| **OpenAI GPT-6 Astra** | Ticari Büyük VLM | **91.91%** | 97.22% | 90.56% | 31.70% | 0.00% *(Yok)* | $0.1109 | Bulut API (Harici) |
| **Qwen3.5 4B (Yalın Temel Model)** | Bağımsız Temel Model | **82.43%** | 89.06% | 76.64% | 27.31% | 0.00% *(Yok)* | Ücretsiz (yerel) | Yerel / Self-Hosted |
| **Google Gemini 3.8 Flash** | Ticari Hızlı VLM | **80.71%** | 88.14% | 72.23% | 28.70% | 0.00% *(Yok)* | $0.0043 | Bulut API (Harici) |
| **DocNeedle (Süreç İçi)** | **Qwen3.5-4B + Gemma2-RAG** | **75.71%** | **77.16%** | **69.70%** | **71.43%** | **80.95%** | **$0.00 (yerel)** | **Sıfır-Disk RAM / Hava Boşluklu** |

### Öne Çıkan Bulgular
* **Uzun Belgelerde Üstün Dayanıklılık (Temel Modele Göre +44.12 Puan):** 50 sayfayı aşan belgelerde RAG desteği olmayan büyük modeller dikkat dağınıklığı yaşayarak çökerken (yalın Qwen3.5 4B %27.31'e, GPT-6 Astra %31.70'e düşer), DocNeedle görsel ve metinsel parçaları akıllıca yönlendirerek **%71.43 F1** başarısını korur.
* **Denetlenebilir Sayfa Konumlandırması (%90.67 Kısa, %80.95 Genel):** Ticari VLM'ler kaynak atfında %0.00 alırken, DocNeedle çıkarılan her veri için doğrulanmış sayfa numarası ve doğrudan alıntı metni sunar.
* **Ekonomik ve Güvenli:** Sayfa başına $0.00 marjinal maliyetle çalışırken, uçucu RAM garantileriyle kurumsal veri sızıntılarını tamamen engeller.

---

## Kullanılan Teknolojiler

* **Çalışma Zamanı ve Servis Mimarisi:** Python 3.14+, FastAPI 0.115+, Pydantic v2, Uvicorn, Server-Sent Events (SSE)
* **Kullanıcı Arayüzü:** Gradio 6+ (Koyu Tema, Dinamik Şema Editörü, Canlı İlerleme Göstergeleri)
* **Süreç-İçi Model Çıkarımı:** `llama-cpp-python` (CUDA/cuBLAS & Flash Attention), Qwen3.5-4B GGUF Çok Modlu Model, SigLIP Görsel Projektör
* **Vektör Gömme ve Yerel Çekirdek:** C++ (`docneedle_embed.cpp`, `libdocneedle_embed.so`), EmbeddingGemma-2 GGUF, `ctypes` süreç izolasyonu
* **Belge Ayrıştırma ve İşleme:** Docling Core 2.15+, `pypdfium2` (AcroForm ayrıştırıcı ve 108 DPI rasterizer), `python-docx`, `openpyxl`, Pillow
* **Arama ve Yeniden Sıralama:** Okapi BM25 (`rank-bm25`), Reciprocal Rank Fusion (RRF), Qwen3-Reranker-0.6B GGUF
* **Güvenlik ve Konteyner:** Linux `prctl(PR_SET_DUMPABLE, 0)`, Docker, Docker Compose, Hugging Face Spaces (ZeroGPU)
* **Test ve Kalite:** Pytest (159 otomatik birim testi), Ruff, Sıfır-Disk CI doğrulaması
