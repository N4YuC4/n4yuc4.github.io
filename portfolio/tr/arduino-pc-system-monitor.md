# TinyML ile Arduino PC Sistem Monitörü

Bu proje, bilgisayar kaynaklarını (CPU, RAM, GPU, VRAM) takip eden ve PC'nin güç modunu otomatik olarak ayarlayan donanım tabanlı bir sistem monitörüdür. Mevcut iş yükünü tahmin etmek ve güç profillerini buna göre değiştirmek için bir Arduino Leonardo üzerinde çalışan TinyML (Destek Vektör Makinesi - SVM) sınıflandırma modeli kullanır.

## Temel Özellikler

* **Gerçek Zamanlı Donanım İzleme:** CPU, RAM, GPU ve VRAM kullanım metriklerini toplar ve işler.
* **TinyML Sınıflandırması:** Tamamen Arduino mikrodenetleyicisi üzerinde çalışmak üzere scikit-learn ile eğitilmiş ve `micromlgen` aracılığıyla dışa aktarılmış hafif bir SVM modeli kullanır.
* **Dinamik Güç Yönetimi:** Tahmin edilen sistem yüküne bağlı olarak otomatik olarak `power-saver` (güç tasarrufu), `balanced` (dengeli) ve `performance` (performans) modları arasında geçiş yapmak için Linux'un `powerprofilesctl` aracı ile etkileşime girer.
* **Seri İletişim:** Python ana bilgisayar (host) betiği ile Arduino Leonardo arasında güvenilir iki yönlü iletişim.
* **Özel Veri Kümesi Toplama:** Verileri manuel olarak etiketlemek (Boşta, Günlük Kullanım, Ağır Yük) ve özelleştirilmiş bir eğitim veri kümesi oluşturmak için yerleşik bir günlükçü (logger) içerir.

## Kullanılan Teknolojiler

* **Donanım:** Arduino Leonardo
* **Diller:** Python, C++
* **Makine Öğrenimi:** scikit-learn, SVM, TinyML
* **Araçlar ve Kütüphaneler:** PlatformIO, `micromlgen`, `psutil`, `pyserial`, `nvidia-ml-py`
