# Elma Tespit ve Kalite Analizi Sistemi

Bu proje, endüstriyel konveyör bantları üzerindeki elmaları YOLOv8 tabanlı segmentasyon kullanarak tespit eden, fiziksel boyutlarını ölçen ve CIEDE2000 renk analizi yöntemiyle kalitelerini sınıflandıran profesyonel bir endüstriyel masaüstü uygulamasıdır.

Stajım sırasında ekip çalışmasıyla geliştirilmiştir. Benim temel sorumluluklarım modern kullanıcı arayüzünü tasarlamak ve sistemin temel mimarisini oluşturmak iken, ekip arkadaşlarım yapay zeka modelinin eğitimi ve matematiksel renk analizi üzerine odaklandı. Onların makine öğrenimi modellerini ve algoritmalarını PyQt5 kullanarak entegre ettim ve tek bir asenkron, yüksek performanslı masaüstü uygulaması haline getirdim.

## Genel Sistem Arayüzü & Mimarisi

Uygulama özellikle fabrika ortamları için tasarlanmıştır. Hibrit mimari, Derin Öğrenme algoritmalarını duyarlı (responsive) bir Kontrol Paneli ile sorunsuz bir şekilde harmanlamaktadır. GPU hızlandırma görevlerinin arayüzü engellemesini (donmasını) önlemek için asenkron Çoklu İş Parçacığı (Multithreading) uyguladım.

![Yapay Zeka Destekli Elma Kalite Analiz Paneli](/static/images/portfolio-images/elma-tespit-figures/genel_gorunum.png)

## Temel Özellikler & Arayüzler

### 1. Donanım Entegrasyonu ve Yapılandırma
Sistem iki kademeli bir yapılandırma mekanizmasına sahiptir. Endüstriyel kameralar üzerinde doğrudan sensör seviyesinde kontrol sağlamak amacıyla HikRobot MVS SDK entegrasyonunu gerçekleştirdim.

![Donanım Seviyesi Kontrol Paneli](/static/images/portfolio-images/elma-tespit-figures/kamera_renk_ayarlari.png)
*Pozlama (Exposure), Kazanç (Gain) ve Beyaz Dengesi (White Balance) gibi sensör seviyesi donanım kontrolleri.*

### 2. Gerçek Zamanlı Segmentasyon ve ROI Katmanı
Sistemin merkezinde etkileşimli kanvas yer alır. YOLOv8-seg tarafından tahmin edilen segmentler piksel hassasiyetiyle çizilir. Her segmentlere ayrılmış elma, etkileşimli bir ROI (İlgi Alanı) olarak işlev görür. Operatör bunlara tıklayarak renk karşılaştırmaları için temel teşkil eden bir \"Referans Havuzuna\" ekleyebilir.

![Gerçek Zamanlı Segmentasyon ve ROI Katmanları](/static/images/portfolio-images/elma-tespit-figures/merkezi_kanvas.png)

### 3. Endüstriyel Veri Merkezi ve Metrikler
Arayüzün sağ paneli, yazılımın analitik kalbi olarak işlev görür ve elmaların piyasa değerini belirleyen temel bilimsel metrikleri raporlar:
- **Renk Sapması (Delta E00):** Referans havuzuna kıyasla algısal renk farkı.
- **Sınıf İçi Sapma (σ - Sigma):** Paketleme partisinin kararlılığını ve homojenliğini temsil eder.
- **Homojenlik Endeksi (%):** Yüksek kalite için %90+ oranının hedeflendiği görsel tekdüzelik skoru.

![Endüstriyel Veri Analiz Paneli](/static/images/portfolio-images/elma-tespit-figures/sag_analiz_paneli.png)

### 4. Akıllı Renk Kalibrasyonu
Değişen endüstriyel aydınlatma koşullarını telafi etmek için sistem, hatalı bir beyaz dengesinden bilimsel analize uygun doğal renklere geçişi sağlayan bir \"Otomatik Renk Ayarı\" modülü içerir.

![Otomatik Kalibrasyon](/static/images/portfolio-images/elma-tespit-figures/renk_sonrasi.png)

### 5. Asenkron Toplu İşleme
Dosyalardan veya canlı kameralardan gelen işleme akışları bir kuyruk yapısında yönetilir. Dinamik bir alt galeri, işlenen kareleri takip eder.

![Toplu İşleme Küçük Resim Galerisi](/static/images/portfolio-images/elma-tespit-figures/alt_galeri.png)

## Kullanılan Teknolojiler

- **Kullanıcı Arayüzü Çerçevesi & Mimari:** PyQt5, Asenkron Çoklu İş Parçacığı (Benim katkım)
- **Bilgisayarlı Görü & İşleme:** OpenCV 4.x (Benim katkım)
- **Derin Öğrenme:** YOLOv8-seg (Ekip katkısı)
- **Matematiksel Analiz:** CIEDE2000 Renk Mesafesi (Ekip katkısı)
- **Donanım Entegrasyonu:** HikRobot MVS SDK
- **Veri Kalıcılığı:** YAML Konfigürasyonları, CSV Günlükleme
