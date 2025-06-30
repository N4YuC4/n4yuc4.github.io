# Python ile SOLID Prensipleri: Yazılım Geliştirmede Temel Taşlar

SOLID prensipleri, **nesne yönelimli programlamada (OOP)** daha sağlam, **bakımı kolay** ve **esnek** yazılımlar tasarlamak için kullanılan **beş temel prensibin** kısaltmasıdır. Bu prensipler, yazılım tasarımını ve mimarisini iyileştirerek, zamanla değişen gereksinimlere daha kolay adapte olabilen sistemler oluşturmanıza yardımcı olur.

SOLID, her bir harfin bir prensibi temsil ettiği bir akronimdir:

-   **S** - Single Responsibility Principle (**Tek Sorumluluk Prensibi**)
    
-   **O** - Open/Closed Principle (**Açık/Kapalı Prensibi**)
    
-   **L** - Liskov's Substitution Principle (**Liskov Yerine Geçme Prensibi**)
    
-   **I** - Interface Segregation Principle (**Arayüz Ayrımı Prensibi**)
    
-   **D** - Dependency Inversion Principle (**Bağımlılık Tersine Çevirme Prensibi**)
    

# SOLID Prensiplerinin Önemi: Neden İhtiyacımız Var?

Yazılım projeleri büyüdükçe ve geliştikçe, kod tabanının karmaşıklığı artar. Bu karmaşıklık, yazılımın bakımı, yeni özellik eklenmesi ve test edilmesi süreçlerini zorlaştırabilir. SOLID prensipleri, bu zorlukları aşmak için bir yol haritası sunar:

-   **Bakım Kolaylığı**: Kodun daha **modüler ve anlaşılır** olmasını sağlar. Bir hata veya değişiklik, sadece ilgili küçük bir bölümü etkiler, tüm sistemi riske atmaz. Bu, hataları bulmayı ve düzeltmeyi hızlandırır.
    
-   **Genişletilebilirlik**: Yeni özellikler eklemek, **mevcut kodu değiştirmek yerine genellikle yeni kod ekleyerek** yapılır. Bu, "çalışan koda dokunmama" ilkesini destekler ve mevcut fonksiyonelliğin bozulma riskini azaltır.
    
-   **Test Edilebilirlik**: Her bir sınıfın veya modülün **net bir sorumluluğu** olduğu için, bağımsız **birim testleri** yazmak çok daha kolaydır. Bu, yazılımın güvenilirliğini artırır.
    
-   **Yeniden Kullanılabilirlik**: İyi tasarlanmış, tek sorumluluklu bileşenler, farklı projelerde veya sistemin farklı yerlerinde **tekrar tekrar kullanılabilir**. Bu, geliştirme süresini kısaltır ve maliyetleri düşürür.
    
-   **Ekip Çalışması**: Kodun daha organize ve mantıksal olarak ayrılmış olması, birden fazla geliştiricinin aynı proje üzerinde **paralel olarak çalışmasını** kolaylaştırır, çakışmaları azaltır.
    

Şimdi her bir prensibi daha detaylı inceleyelim:

# SOLID'in Özellikleri ve Detaylı Açıklamalar

## 1. Single Responsibility Principle (SRP - Tek Sorumluluk Prensibi)

### Nedir?

Bir sınıfın veya modülün yalnızca **bir ve tek bir** sorumluluğu olmalıdır. Basitçe söylemek gerekirse, bir sınıfın **değişmesi için sadece tek bir nedeni** olmalıdır.

### Neden Önemli?

-   **Anlaşılırlık**: Sınıfın ne iş yaptığını anlamak kolaylaşır.
    
-   **Bakım**: Bir değişiklik gerektiğinde, yalnızca **ilgili sınıfa** odaklanmanız yeterlidir, diğer fonksiyonellikleri etkileme riski azalır.
    
-   **Test Edilebilirlik**: Sınıfın tek bir görevi olduğu için, test senaryoları daha **basit ve odaklı** olur.
    

### Yanlış Örnek: "Her Şeyi Yapan" Bir Öğrenci Sınıfı

Bu örnekte, `Ogrenci` sınıfı hem **öğrenci bilgilerini yönetiyor**, hem **not ortalamasını hesaplıyor** hem de **öğrenci bilgilerini bir dosyaya kaydediyor**. Bu durum, sınıfın **üç farklı değişim nedeni** olduğunu gösterir: öğrenci bilgilerinin yapısı değişirse, not ortalaması hesaplama mantığı değişirse veya veri kaydetme mekanizması (dosya yerine veritabanı gibi) değişirse sınıfı güncellemeniz gerekir. Bu durum **SRP'ye aykırıdır**.

```Python
class Ogrenci:
    def __init__(self, ad, soyad, numara):
        self.ad = ad
        self.soyad = soyad
        self.numara = numara

    def tam_ad_getir(self):
        # Bu kısım öğrencinin kimlik bilgisini yönetiyor.
        return f"{self.ad} {self.soyad}"

    def ortalama_hesapla(self, notlar):
        # Bu kısım not hesaplama mantığını yönetiyor.
        toplam = sum(notlar)
        ortalama = toplam / len(notlar)
        return ortalama

    def bilgileri_kaydet(self, dosya_adi="ogrenci.txt"):
        # Bu kısım öğrenci bilgilerini kaydetme sorumluluğunu üstleniyor.
        with open(dosya_adi, "a") as f:
            f.write(f"Ad: {self.ad}, Soyad: {self.soyad}, Numara: {self.numara}\n")
        print(f"Öğrenci bilgileri {dosya_adi} dosyasına kaydedildi.")

# Kullanım
ogrenci1 = Ogrenci("Ahmet", "Yılmaz", 123)
notlar = [80, 90, 75]
ortalama = ogrenci1.ortalama_hesapla(notlar)
print(f"{ogrenci1.tam_ad_getir()} öğrencisinin ortalaması: {ortalama}")
ogrenci1.bilgileri_kaydet()

```

### Doğru Örnek: Sorumlulukları Ayırma

Burada, **sorumlulukları üç farklı sınıfa ayırdık**: `Ogrenci` sınıfı **sadece öğrencinin kimlik ve temel bilgilerini yönetir**. `NotHesaplayici` sınıfı **sadece not ortalaması hesaplama** sorumluluğunu üstlenir. `OgrenciKaydedici` sınıfı ise **öğrenci bilgilerini kalıcı hale getirme (kaydetme)** sorumluluğunu üstlenir. Böylece **her sınıfın tek bir değişim nedeni** olur ve daha **modüler, anlaşılır** bir yapıya sahip oluruz.

```Python
class Ogrenci:
    def __init__(self, ad, soyad, numara):
        self.ad = ad
        self.soyad = soyad
        self.numara = numara

    def tam_ad_getir(self):
        return f"{self.ad} {self.soyad}"

class NotHesaplayici:
    def hesapla(self, notlar):
        if not notlar:
            return 0.0
        toplam = sum(notlar)
        ortalama = toplam / len(notlar)
        return ortalama

class OgrenciKaydedici:
    def kaydet(self, ogrenci: Ogrenci, dosya_adi="ogrenci.txt"):
        # Sadece öğrenci bilgilerini kaydetme sorumluluğu.
        with open(dosya_adi, "a") as f:
            f.write(f"Ad: {ogrenci.ad}, Soyad: {ogrenci.soyad}, Numara: {ogrenci.numara}\n")
        print(f"Öğrenci bilgileri {dosya_adi} dosyasına kaydedildi.")

# Kullanım
ogrenci1 = Ogrenci("Ahmet", "Yılmaz", 123)
notlar = [80, 90, 75]

hesaplayici = NotHesaplayici()
ortalama = hesaplayici.hesapla(notlar)
print(f"{ogrenci1.tam_ad_getir()} öğrencisinin ortalaması: {ortalama}")

kaydedici = OgrenciKaydedici()
kaydedici.kaydet(ogrenci1)

```

-   `Ogrenci` sınıfı artık **sadece öğrenci bilgilerini tutmakla sorumludur**.
    
-   `NotHesaplayici` sınıfı ise **sadece notları hesaplamakla sorumludur**.
    
-   `OgrenciKaydedici` sınıfı ise **öğrenci bilgilerini kaydetmekla sorumludur**. Her sınıfın değişmesi için artık sadece tek bir nedeni var.
    

## 2. Open/Closed Principle (OCP - Açık/Kapalı Prensibi)

### Nedir?

Yazılım varlıkları (sınıflar, modüller, fonksiyonlar vb.) **genişlemeye açık, ancak değişikliğe kapalı** olmalıdır. Yani, yeni bir özellik eklemek istediğinizde **mevcut, çalışan kodunuzu değiştirmemelisiniz**; bunun yerine **yeni kod eklemelisiniz**.

### Neden Önemli?

-   **Kararlılık**: Mevcut ve iyi test edilmiş kodun **bozulma riskini azaltır**.
    
-   **Esneklik**: Sistemin yeni gereksinimlere veya değişikliklere daha **kolay adapte** olmasını sağlar.
    
-   **Daha Az Hata**: Mevcut kodu değiştirmek yerine yeni kod eklemek, genellikle **daha az yeni hataya** yol açar.
    

### Yanlış Örnek: `if-elif` Cehennemi

Bu `Sekil` sınıfı, yeni bir şekil tipi (örneğin, `Üçgen` veya `Elips`) eklendiğinde `alan_hesapla` metodu içindeki **`if-elif` bloğunun değiştirilmesini gerektirir**. Bu, sınıfın "**değişikliğe kapalı**" olmadığını gösterir. Her yeni şekil için bu sınıfı tekrar açıp düzenlemeniz gerekir, bu da **kodun karmaşıklaşmasına ve gelecekte hatalara yol açabilir**.

```Python
class Sekil:
    def __init__(self, sekil_tipi):
        self.sekil_tipi = sekil_tipi

    def alan_hesapla(self, uzunluk, genislik=0, yaricap=0):
        if self.sekil_tipi == "kare":
            return uzunluk * uzunluk
        elif self.sekil_tipi == "dikdörtgen":
            return uzunluk * genislik
        elif self.sekil_tipi == "daire":
            import math
            return math.pi * yaricap * yaricap
        else:
            raise ValueError("Geçersiz şekil tipi")

# Kullanım
sekil1 = Sekil("kare")
print(f"Kare alanı: {sekil1.alan_hesapla(5)}")

sekil2 = Sekil("dikdörtgen")
print(f"Dikdörtgen alanı: {sekil2.alan_hesapla(4, 6)}")

sekil3 = Sekil("daire")
print(f"Daire alanı: {sekil3.alan_hesapla(0, 0, 3)}")

```

### Doğru Örnek: Soyutlama ve Polimorfizm Kullanımı

Bu yaklaşımda, `Sekil` adında **soyut bir temel sınıf** (veya Python'da `abc` modülü ile soyut sınıf) tanımlıyoruz. Bu soyut sınıf, tüm şekillerin sahip olması gereken ortak davranışı (`alan_hesapla` metodu) tanımlar. Daha sonra, her yeni şekil tipi için bu soyut sınıfı miras alan **yeni bir somut sınıf** oluştururuz. Bu, **mevcut `Sekil` sınıfını değiştirmeden** sisteme yeni şekiller eklememizi sağlar; yani "**genişlemeye açık, değişikliğe kapalı**"dır.

```Python
from abc import ABC, abstractmethod
import math

# Soyut Temel Sınıf
class Sekil(ABC):
    @abstractmethod
    def alan_hesapla(self) -> float:
        """Her türemiş sınıf kendi alanını hesaplama sorumluluğunu üstlenir."""
        pass

# Somut Sınıflar (genişlemeye açık)
class Kare(Sekil):
    def __init__(self, kenar):
        self.kenar = kenar

    def alan_hesapla(self) -> float:
        return self.kenar * self.kenar

class Dikdortgen(Sekil):
    def __init__(self, uzunluk, genislik):
        self.uzunluk = uzunluk
        self.genislik = genislik

    def alan_hesapla(self) -> float:
        return self.uzunluk * self.genislik

class Daire(Sekil):
    def __init__(self, yaricap):
        self.yaricap = yaricap

    def alan_hesapla(self) -> float:
        return math.pi * self.yaricap * self.yaricap

class Ucgen(Sekil):
    def __init__(self, taban, yukseklik):
        self.taban = taban
        self.yukseklik = yukseklik

    def alan_hesapla(self) -> float:
        return 0.5 * self.taban * self.yukseklik

# Kullanım (Şekil sınıfını değiştirmeden yeni şekiller ekleyebiliriz)
kare = Kare(5)
dikdortgen = Dikdortgen(4, 6)
daire = Daire(3)
ucgen = Ucgen(4, 3)

sekiller = [kare, dikdortgen, daire, ucgen]
for sekil in sekiller:
    print(f"Şekil Alanı: {sekil.alan_hesapla()}")

```

-   Soyut bir sınıf (`Sekil`): Tüm şekillerin ortak özelliklerini (alan hesaplama) tanımlar.
    
-   Somut sınıflar (`Kare`, `Dikdortgen`, `Daire`, `Ucgen`): Soyut sınıfı miras alır ve kendi alan hesaplama metotlarını uygular.
    
-   **Genişletilebilirlik**: Yeni bir şekil (örneğin `Ucgen` sınıfı) eklemek için **mevcut `Sekil` sınıfını değiştirmeye gerek yoktur**; sadece yeni bir sınıf türetmek yeterlidir.
    

## 3. Liskov's Substitution Principle (LSP - Liskov Yerine Geçme Prensibi)

### Nedir?

"Bir programdaki nesneler, **alt tiplerinin örnekleriyle (subtypes) değiştirilebilmelidir**, böylece programın doğruluğu etkilenmez." Kısacası, bir **alt sınıfın nesneleri, türediği üst sınıfın nesneleri gibi davranabilmelidir**. Eğer bir kod parçası bir üst sınıf türünde bir nesne bekliyorsa, o üst sınıfın herhangi bir alt sınıfının nesnesini de aynı kod parçasına güvenle verebilmelisiniz ve kodun doğru çalışmaya devam etmesi gerekir.

### Neden Önemli?

-   **Güvenilirlik**: Kodun **beklenmedik davranışlar** sergilemesini engeller.
    
-   **Doğru Polimorfizm**: **Çok biçimliliğin (polymorphism)** doğru ve güvenli bir şekilde kullanılmasını sağlar.
    
-   **Kod Tutarlılığı**: Üst sınıfı kullanan bir kod parçasının, alt sınıfları kullandığında da **aynı şekilde çalışacağını garanti** eder.
    

### Yanlış Örnek: Kare'nin Dikdörtgen Gibi Davranmaması

Matematiksel olarak bir kare özel bir dikdörtgen olsa da, nesne yönelimli tasarımda `Kare`'yi `Dikdortgen`'den türetmek **LSP ihlaline** yol açabilir. Çünkü bir `Dikdortgen`'in genişliği ve uzunluğu bağımsız olarak değiştirilebilirken, bir `Kare`'nin tüm kenarları her zaman eşit olmalıdır. `Dikdortgen` sınıfının davranışlarını `Kare` sınıfına uyguladığımızda **beklenmedik sonuçlar** ortaya çıkar. Aşağıdaki `alan_test_et` fonksiyonu bir `Dikdortgen` bekler ve onun davranışlarını değiştirmeye çalışır; ancak bir `Kare` nesnesiyle çağrıldığında **beklenen sonucu vermez**, bu da bir LSP ihlalidir.

```Python
class Dikdortgen:
    def __init__(self, uzunluk, genislik):
        self._boy = uzunluk
        self._en = genislik

    def uzunluk_ayarla(self, uzunluk):
        self._boy = uzunluk

    def genislik_ayarla(self, genislik):
        self._en = genislik

    def alan_hesapla(self):
        return self._boy * self._en

class Kare(Dikdortgen):
    def __init__(self, kenar):
        super().__init__(kenar, kenar)

    # Kare'nin kenarları her zaman eşit olmalı. Bu metotlar Dikdörtgen'in davranışını bozuyor.
    def uzunluk_ayarla(self, uzunluk):
        self._boy = uzunluk
        self._en = uzunluk
    
    def genislik_ayarla(self, genislik):
        self._boy = genislik
        self._en = genislik

# Kullanım örneği (LSP ihlali gösterimi)
def alan_test_et(dikdortgen_nesnesi: Dikdortgen):
    print(f"Başlangıç uzunluk: {dikdortgen_nesnesi._boy}, genişlik: {dikdortgen_nesnesi._en}")
    dikdortgen_nesnesi.uzunluk_ayarla(5)
    dikdortgen_nesnesi.genislik_ayarla(4)
    print(f"Yeni uzunluk: {dikdortgen_nesnesi._boy}, yeni genişlik: {dikdortgen_nesnesi._en}")
    print(f"Beklenen Alan: 20 (Dikdörtgen için), Gerçekleşen Alan: {dikdortgen_nesnesi.alan_hesapla()}")

dikdortgen = Dikdortgen(2, 3)
kare = Kare(3)

print("--- Dikdörtgen için test ---")
alan_test_et(dikdortgen)

print("\n--- Kare için test (LSP ihlali) ---")
alan_test_et(kare)

```

### Doğru Örnek: Ortak Bir Soyutlamadan Türetme

LSP'yi doğru uygulamak için, `Kare` ve `Dikdortgen` gibi birbirine benzer ama davranışsal olarak farklı olan sınıfları **ortak bir soyut sınıftan** (örneğin `Sekil`) türetmeliyiz. Her bir sınıf kendi özelliklerini ve alan hesaplama mantığını bağımsız olarak uygular. Böylece, `Sekil` bekleyen herhangi bir kod, `Kare` veya `Dikdortgen` nesneleriyle **güvenle çalışabilir**, çünkü her ikisi de `Sekil`'in **sözleşmesine uygun** davranır.

```Python
from abc import ABC, abstractmethod

class Sekil(ABC):
    @abstractmethod
    def alan_hesapla(self) -> float:
        """Soyut alan hesaplama metodu."""
        pass

class Dikdortgen(Sekil):
    def __init__(self, uzunluk, genislik):
        self.uzunluk = uzunluk
        self.genislik = genislik

    def alan_hesapla(self) -> float:
        return self.uzunluk * self.genislik

class Kare(Sekil):
    def __init__(self, kenar):
        self.kenar = kenar

    def alan_hesapla(self) -> float:
        return self.kenar * self.kenar

# Kullanım (LSP'ye uygun)
def sekil_alani_yazdir(sekil_nesnesi: Sekil):
    # Bu fonksiyon Sekil türünde bir nesne bekler ve sadece alan_hesapla metodunu çağırır.
    # Kare veya Dikdortgen nesnesi geldiğinde beklenmedik bir durum olmaz.
    print(f"Şekil Alanı: {sekil_nesnesi.alan_hesapla()}")

dikdortgen_nesnesi = Dikdortgen(4, 6)
kare_nesnesi = Kare(5)

sekil_alani_yazdir(dikdortgen_nesnesi)
sekil_alani_yazdir(kare_nesnesi)

# Her iki nesne de Sekil türünde bir değişkene atanabilir ve
# alan_hesapla metodunu kendi doğal davranışlarına göre çağırabilirler.

```

-   `Kare` ve `Dikdortgen` sınıfları **ortak bir temel sınıf** olan `Sekil` sınıfından türetilir.
    
-   Her iki sınıf da `alan_hesapla` metotlarını kendi özelliklerine göre hesaplar.
    
-   Bu sayede, bir `Kare` nesnesi veya bir `Dikdortgen` nesnesi, `Sekil` türünde bir değişkene atanabilir ve **polimorfik olarak aynı şekilde kullanılabilir**, **beklenmedik davranışlara yol açmaz**.
    

## 4. Interface Segregation Principle (ISP - Arayüz Ayrımı Prensibi)

### Nedir?

"Bir istemci, **kullanmadığı metotları içeren bir arayüze bağımlı olmamalıdır**." Kısacası, büyük, genel arayüzler yerine, **küçük ve spesifik arayüzler** kullanılmalıdır. Bu prensip, sınıfların sadece ihtiyaç duydukları fonksiyonellikleri implemente etmelerini teşvik eder.

### Neden Önemli?

-   **Esneklik**: Sınıfların sadece **ihtiyaç duydukları arayüzleri** uygulamasına olanak tanır.
    
-   **Gereksiz Bağımlılıkları Azaltır**: Bir sınıfın, aslında hiç kullanmayacağı metotları implemente etme zorunluluğunu ortadan kaldırır. Bu, **kod karmaşıklığını ve bakım yükünü azaltır**.
    
-   **Kodun Yeniden Kullanılabilirliği**: Daha küçük arayüzler, farklı senaryolarda daha **kolay birleştirilebilir ve yeniden kullanılabilir**.
    

### Yanlış Örnek: "Dev" Bir Yazıcı Arayüzü

`IYaziciOrtak` arayüzü, yazdırma, tarama, faks ve fotokopi gibi **tüm olası yazıcı işlevlerini içeriyor**. Ancak, gerçek dünyada tüm yazıcılar bu işlevlerin hepsini sunmaz. Örneğin, basit bir lazer yazıcı tarama, faks veya fotokopi özelliğine sahip olmayabilir. Bu durumda, `LazerYazici` sınıfı, **aslında yapmadığı bu metotları zorunlu olarak implemente etmek zorunda kalır** (boş veya hata fırlatan implementasyonlarla). Bu durum **ISP'yi ihlal eder**.

```Python
class IYaziciOrtak:
    def belge_yazdir(self):
        pass
    def belge_tara(self):
        pass
    def faks_gonder(self):
        pass
    def fotokopi_cek(self):
        pass

class LazerYazici(IYaziciOrtak):
    def belge_yazdir(self):
        print("Lazer yazıcı ile belge yazdırılıyor...")

    def belge_tara(self):
        # Lazer yazıcı genellikle tarama yapmaz.
        raise NotImplementedError("Bu lazer yazıcı tarama yapamaz.")

    def faks_gonder(self):
        # Lazer yazıcı genellikle faks göndermez.
        raise NotImplementedError("Bu lazer yazıcı faks gönderemez.")

    def fotokopi_cek(self):
        # Lazer yazıcı genellikle fotokopi çekmez.
        raise NotImplementedError("Bu lazer yazıcı fotokopi çekemez.")

class OfisCokIslevliYazici(IYaziciOrtak):
    def belge_yazdir(self):
        print("Çok işlevli yazıcı ile belge yazdırılıyor...")
    def belge_tara(self):
        print("Çok işlevli yazıcı ile belge taranıyor...")
    def faks_gonder(self):
        print("Çok işlevli yazıcı ile faks gönderiliyor...")
    def fotokopi_cek(self):
        print("Çok işlevli yazıcı ile fotokopi çekiliyor...")

# Kullanım
lazer_yazici = LazerYazici()
lazer_yazici.belge_yazdir()
try:
    lazer_yazici.belge_tara()
except NotImplementedError as e:
    print(f"Hata: {e}")

```

### Doğru Örnek: Arayüzleri Ayırma

Burada, genel `IYaziciOrtak` arayüzünü **daha küçük ve spesifik arayüzlere ayırıyoruz**: `IYazici`, `ITarayici`, `IFaks` ve `IFotokopici`. Artık sınıflar, **sadece gerçekten ihtiyaç duydukları arayüzleri implemente edebilir**. Bu sayede, `LazerYazici` sadece `IYazici` arayüzünü implemente ederken, çok işlevli bir yazıcı birden fazla arayüzü implemente edebilir.

```Python
class IYazici:
    def yazdir(self):
        pass

class ITarayici:
    def tara(self):
        pass

class IFaks:
    def faks_gonder(self):
        pass

class IFotokopici:
    def fotokopi_cek(self):
        pass

class LazerYazici(IYazici):
    def yazdir(self):
        print("Lazer yazıcı ile yazdırılıyor...")

class CokIslevliAgYazicisi(IYazici, ITarayici, IFaks, IFotokopici):
    def yazdir(self):
        print("Ağ yazıcısı ile yazdırılıyor...")
    
    def tara(self):
        print("Ağ üzerinden tarama yapılıyor...")
    
    def faks_gonder(self):
        print("Ağ üzerinden faks gönderiliyor...")

    def fotokopi_cek(self):
        print("Ağ üzerinden fotokopi çekiliyor...")

# Kullanım
lazer_yazici = LazerYazici()
lazer_yazici.yazdir()

cok_islevli_yazici = CokIslevliAgYazicisi()
cok_islevli_yazici.yazdir()
cok_islevli_yazici.tara()
cok_islevli_yazici.faks_gonder()
cok_islevli_yazici.fotokopi_cek()

```

-   **Farklı işlemler için farklı arayüzler tanımlanmıştır**.
    
-   Bir sınıf **sadece ihtiyaç duyduğu metotları implemente etmek** zorundadır.
    
-   `CokIslevliAgYazicisi` sınıfı hem yazdırabilir hem de tarayabilir, faks gönderebilir ve fotokopi çekebilir, ancak `LazerYazici` sınıfı sadece yazdırabilir. Bu, sınıfların **gereksiz bağımlılıklardan kurtulmasını** sağlar.
    

## 5. Dependency Inversion Principle (DIP - Bağımlılık Tersine Çevirme Prensibi)

### Nedir?

1.  **Yüksek seviyeli modüller, düşük seviyeli modüllere bağımlı olmamalıdır.** Her ikisi de **soyutlamalara (abstraction)** bağımlı olmalıdır.
    
2.  **Soyutlamalar detaylara bağımlı olmamalıdır.** Detaylar (somut implementasyonlar) **soyutlamalara bağımlı** olmalıdır.
    

Basitçe, kodunuzdaki belirli (**somut**) implementasyonlara doğrudan bağlı kalmak yerine, **soyut arayüzlere veya soyut sınıflara bağlı olun**. Bu, sisteminizin daha **esnek ve test edilebilir** olmasını sağlar. Bu prensip genellikle **Bağımlılık Enjeksiyonu (Dependency Injection)** ile birlikte uygulanır.

### Neden Önemli?

-   **Esneklik**: Bir bileşenin iç implementasyonunu değiştirdiğinizde, ona bağımlı olan diğer bileşenleri etkilemezsiniz.
    
-   **Test Edilebilirlik**: Bağımlılıkları **kolayca değiştirilebildiği (inject edilebildiği)** için birim testleri yazmak çok daha kolaydır.
    
-   **Yeniden Kullanılabilirlik**: Modüllerin farklı ortamlarda veya farklı implementasyonlarla **yeniden kullanılmasını** teşvik eder.
    

### Yanlış Örnek: Yüksek Seviyeli Modülün Düşük Seviyeli Detaya Bağımlılığı

`Uygulamam` (**yüksek seviyeli modül**), doğrudan **somut bir sınıf** olan `DosyaKayitci`'ya (**düşük seviyeli detay**) bağımlıdır. `Uygulamam` sınıfının yapıcı metodu içinde **doğrudan `DosyaKayitci` nesnesini yaratması**, bu **sıkı bağımlılığın** temel nedenidir. Eğer kayitlama işlemini farklı bir şekilde (örneğin, veritabanına kayitlamak veya bulut servisine göndermek) yapmak istersek, `Uygulamam` sınıfında **değişiklik yapmamız gerekir**. Bu, yüksek seviyeli modülün detaya bağımlı olduğunu ve **DIP'yi ihlal ettiğini** gösterir.

```Python
class DosyaKayitci:
    def log(self, mesaj):
        with open("uygulama.log", "a") as f:
            f.write(f"Dosya Kaydı: {mesaj}\n")
        print(f"Dosyaya kayitlandı: {mesaj}")

class Uygulamam:
    def __init__(self):
        # Doğrudan DosyaKayitci'ya bağımlılık - Yanlış!
        # Bu satır, Uygulamam'ın DosyaKayitci'ya sıkıca bağlanmasına neden olur.
        self.kayitci = DosyaKayitci()

    def calistir(self):
        print("Uygulama çalıştırılıyor...")
        self.kayitci.log("Uygulama başarıyla başlatıldı.")
        print("Uygulama kapatılıyor...")
        self.kayitci.log("Uygulama kapatıldı.")

# Kullanım
uygulama = Uygulamam()
uygulama.calistir()

```

### Doğru Örnek: Soyutlama ve Bağımlılık Enjeksiyonu (Dependency Injection)

Burada, `IKayitci` adında **soyut bir arayüz** (veya soyut sınıf) tanımlıyoruz. Hem `DosyaKayitci`, `VeritabaniKayitci` hem de yeni eklenen `KonsolKayitci` bu arayüzü implemente eder. `Uygulamam` sınıfı ise **somut bir `Kayitci` nesnesi almak yerine, `IKayitci` arayüzü tipinde bir nesne bekler**. Bu nesne dışarıdan (`__init__` metodu aracılığıyla) **enjekte edilir (Bağımlılık Enjeksiyonu)**.

Böylece:

-   `Uygulamam` (yüksek seviyeli modül) artık somut `DosyaKayitci`'ya bağımlı değil, **`IKayitci` soyutlamasına bağımlı**.
    
-   `DosyaKayitci`, `VeritabaniKayitci` ve `KonsolKayitci` (düşük seviyeli detaylar) da **`IKayitci` soyutlamasına bağımlı**.
    
-   Hem yüksek seviyeli hem de düşük seviyeli modüller **soyutlamalara bağımlıdır**. Bu, **bağımlılıkların tersine çevrilmesidir**.
    

```Python
from abc import ABC, abstractmethod

class IKayitci(ABC):
    @abstractmethod
    def log(self, mesaj):
        pass

class DosyaKayitci(IKayitci):
    def log(self, mesaj):
        with open("uygulama.log", "a") as f:
            f.write(f"Dosya Kaydı: {mesaj}\n")
        print(f"Dosyaya kayitlandı: {mesaj}")

class VeritabaniKayitci(IKayitci):
    def log(self, mesaj):
        # Veritabanına kayitlama işlemi simülasyonu
        print(f"Veritabanına kayitlandı: {mesaj}")

class KonsolKayitci(IKayitci):
    def log(self, mesaj):
        print(f"Konsol Kaydı: {mesaj}")

class Uygulamam:
    def __init__(self, kayitci: IKayitci):
        self.kayitci = kayitci

    def calistir(self):
        print("Uygulama çalıştırılıyor...")
        self.kayitci.log("Uygulama başarıyla başlatıldı.")
        print("Uygulama kapatılıyor...")
        self.kayitci.log("Uygulama kapatıldı.")

# Kullanım: Hangi kayitlayıcının kullanılacağını dışarıdan belirliyoruz.

print("--- Dosya Kayitci ile Uygulama ---")
dosya_kayitci = DosyaKayitci()
dosya_kayitci_ile_uygulama = Uygulamam(dosya_kayitci)
dosya_kayitci_ile_uygulama.calistir()

print("\n--- Veritabanı Kayitci ile Uygulama ---")
veritabani_kayitci = VeritabaniKayitci()
veritabani_kayitci_ile_uygulama = Uygulamam(veritabani_kayitci)
veritabani_kayitci_ile_uygulama.calistir()

print("\n--- Konsol Kayitci ile Uygulama ---")
konsol_kayitci = KonsolKayitci()
konsol_kayitci_ile_uygulama = Uygulamam(konsol_kayitci)
konsol_kayitci_ile_uygulama.calistir()

# İstediğimiz zaman başka bir kayitlama implementasyonu ekleyebiliriz
# ve Uygulamam sınıfını değiştirmeden kullanabiliriz.

```

-   `IKayitci` arayüzü, kayitlama işlemi için bir **soyutlama** sağlar.
    
-   `DosyaKayitci`, `VeritabaniKayitci` ve `KonsolKayitci` sınıfları, `IKayitci` arayüzünü **implemente eder**.
    
-   `Uygulamam` sınıfı, `IKayitci` türünde bir nesne alır (**Bağımlılık Enjeksiyonu**). Bu sayede, hangi kayitlama mekanizmasının kullanılacağı dışarıdan belirlenir ve `Uygulamam` sınıfı **somut bir implementasyona bağımlı kalmaz**.
    

## Sonuç

SOLID prensipleri, başlangıçta ekstra çaba gerektirebilir gibi görünse de, uzun vadede yazılım projelerinin **sağlığını ve sürdürülebilirliğini artıran güçlü araçlardır**. Bu prensipleri uygulayarak:

-   Daha **kolay bakımı yapılan**,
    
-   Yeni özelliklere daha **hızlı adapte olabilen**,
    
-   Daha **az hata içeren**,
    
-   Ve farklı ekiplerin üzerinde daha **verimli çalışabileceği** yazılımlar geliştirebilirsiniz.
    

SOLID, sadece bir dizi kural değil, aynı zamanda daha iyi yazılım mühendisliği uygulamaları için bir **düşünce biçimidir**.
