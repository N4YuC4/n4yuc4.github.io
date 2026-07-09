# mT5 Çift Yönlü EN-TR Yapay Çeviri (ONNX INT8 & ORT Mobile)

Bu proje, çift yönlü İngilizce-Türkçe Yapay Çeviri (EN<->TR) için `google/mt5-small` modelinin 8-bit LoRA (Low-Rank Adaptation) tekniği kullanılarak ince ayarlanmasını (fine-tune) ve ardından mobil ortamlarda (örneğin Flutter uygulamalarında) verimli çalıştırılması amacıyla modelin ONNX INT8 biçimine optimize edilip kuantize edilmesini içermektedir.

## Temel Özellikler & İş Akışı

1. **Çift Yönlü Çeviri:** Model, dinamik olarak her iki yönde de (İngilizce'den Türkçe'ye ve Türkçe'den İngilizce'ye) simetrik olarak çeviri yapacak şekilde eğitilmiştir.
2. **Model İnce Ayarlama:** `google/mt5-small` modeli, özel bir EN-TR veri kümesi (Lainchan-HPLT) üzerinde eğitildi. Eğitim sırasında GPU belleği (VRAM) kullanımını optimize etmek için model `BitsAndBytes` ile 8-bit olarak yüklendi ve LoRA uygulamak için `PEFT` kütüphanesi kullanıldı.
3. **Sözlük Budama (Vocabulary Pruning):** Orijinal mT5 sözlüğü, veri kümesi belirteçleri analiz edilerek agresif bir şekilde budandı. Sözlük boyutu %67 oranında azaltılarak gömme (embedding) katmanının boyutu önemli ölçüde düşürüldü ve model uç cihazlar için çok daha hafif hale getirildi.
4. **ONNX ve INT8 Kuantizasyonu:** Eğitilen LoRA ağırlıkları temel modelle birleştirildikten sonra, Hugging Face `optimum` kütüphanesi kullanılarak ONNX formatına aktarıldı. Düşük gecikmeli mobil çıkarım ve azaltılmış depolama alanı için ONNX modeli **INT8** seviyesine kuantize edildi ve son derece optimize edilmiş ORT Mobile biçimine dönüştürüldü.
5. **Performans Değerlendirmesi:** Nihai kuantize edilmiş ONNX modeli, doğrulama seti üzerinde değerlendirildi ve `0.6245` gibi başarılı bir METEOR skoru elde edildi.

## Kullanılan Teknolojiler

- **Derin Öğrenme Kütüphaneleri:** PyTorch, PyTorch Lightning, Transformers, PEFT (LoRA), BitsAndBytes
- **Optimizasyon & Çıkarım (Inference):** ONNX, ONNX Runtime, Hugging Face Optimum
- **Veri İşleme & Metrikler:** Pandas, PyArrow, Evaluate (METEOR Skoru)
