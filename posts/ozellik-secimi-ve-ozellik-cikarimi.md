## **Veri Biliminde Boyutluluk: Özellik Seçimi ve Özellik Çıkarımı Arasındaki Kritik Fark**

Veri bilimiyle ilgilenen herkesin bildiği temel bir prensip vardır: "Garbage in, garbage out" (Çöp giren, çöp çıkar). Bir makine öğrenimi modelinin performansı, ona sunduğumuz verinin kalitesiyle doğrudan orantılıdır.

Modern veri setleri, genellikle "yüksek boyutluluk laneti" (curse of dimensionality) olarak bilinen bir zorlukla birlikte gelir: Binlerce özellik, hesaplama maliyetini artırır ve modelin ilgisiz "gürültü" üzerinde aşırı öğrenmesine neden olabilir.

Bu zorlukların üstesinden gelmek için **Özellik Mühendisliği (Feature Engineering)** kritik bir rol oynar. Bu disiplinin iki temel yaklaşımı olan **Özellik Seçimi (Feature Selection)** ve **Özellik Çıkarımı (Feature Extraction)**, sıklıkla birbirine karıştırılsa da, temelde farklı felsefelere dayanır.

Bu yazıda, bu iki temel tekniği, uygulamalarını ve aralarındaki stratejik farkları inceleyeceğiz.

-----

### Özellik Seçimi (Feature Selection) 🎯

Özellik Seçimi, modelin hedef değişkenini açıklama gücü en yüksek olan **orijinal özelliklerin bir alt kümesini belirleme** sürecidir. Esasen, gereksiz ve ilgisiz veriyi filtreleyerek sinyali gürültüden ayırmayı amaçlar.

Örneğin, bir konut fiyatı regresyon modelini ele alalım. 'Metrekare', 'oda sayısı' ve 'konum' gibi özellikler hedef değişkenle yüksek korelasyona sahipken; 'kapı zili markası' gibi özellikler muhtemelen ilgisizdir. Özellik seçimi, bu ilgisiz özellikleri sistematik olarak eler.

![Özellik Seçimi](../images/blog-images/ozellik-secimi.png)

Bu yöntemin birincil hedefleri:

1.  Modelin karmaşıklığını azaltmak ve hesaplama verimliliğini artırmak.
2.  Aşırı öğrenme riskini minimize etmek.
3.  Modelin yorumlanabilirliğini korumak veya artırmak.

Python'daki `scikit-learn` kütüphanesi, bu işlem için çeşitli mekanizmalar sunar. Örneğin `SelectKBest` sınıfı, ANOVA F-testi gibi istatistiksel yöntemler kullanarak en yüksek puana sahip 'k' adet özelliği filtreler:

```python
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.datasets import load_iris

# Iris veri setini yükleyelim
X, y = load_iris(return_X_y=True, as_frame=True)
print(f"Orijinal özellik sayısı ({X.shape[1]} adet): {list(X.columns)}")

# İstatistiksel olarak en iyi 2 özelliği seçmeyi hedefleyelim
selector = SelectKBest(score_func=f_classif, k=2)
X_new = selector.fit_transform(X, y)

# Seçilen özelliklerin isimlerini alalım
selected_features = selector.get_feature_names_out()
print(f"Seçilen en iyi 2 özellik: {list(selected_features)}")
```

**Çıktı:**
```
Orijinal özellik sayısı (4 adet): ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
Seçilen en iyi 2 özellik: ['petal length (cm)', 'petal width (cm)']
```

Görüldüğü üzere, 4 orijinal özellikten, hedef değişkeni (çiçek türü) açıklamada en başarılı olan 2 tanesi korunmuş, diğerleri elenmiştir.

-----

### Özellik Çıkarımı (Feature Extraction) ✨

Özellik Çıkarımı, mevcut özellik uzayını **matematiksel olarak dönüştürerek** daha düşük boyutlu yeni bir uzay yaratan bir tekniktir. Bu yeni özellikler, orijinal verinin birer *kombinasyonudur*.

Buradaki amaç, orijinal verideki varyansın veya bilginin büyük bir kısmını, daha az sayıda *yeni* özelliğe 'yoğunlaştırmaktır'.

Görüntü işleme buna klasik bir örnektir. 1000x1000 piksellik bir görüntü, 1 milyon özellik anlamına gelir. Bu yüksek boyutlulukla çalışmak verimsizdir. Özellik çıkarımı, bu 1 milyon pikseli, verinin yapısını temsil eden 100-200 adet "bileşene" dönüştürebilir.

![Özellik Çıkarımı](../images/blog-images/ozellik-cikarimi.png)

En yaygın tekniklerden biri olan **PCA (Principal Component Analysis - Temel Bileşen Analizi)**, verideki maksimum varyansı açıklayan yeni, ortogonal (birbirine dik) eksenler (bileşenler) bulur. Aynı Iris verisi üzerinde uygulayalım:

```python
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True, as_frame=True)
print(f"Orijinal özellik sayısı: {X.shape[1]}")

# Orijinal 4 özelliği 2 yeni bileşene dönüştürelim
pca = PCA(n_components=2)
X_new_pca = pca.fit_transform(X)

# Yeni bileşenleri DataFrame olarak görelim
pca_df = pd.DataFrame(data=X_new_pca, columns=['Bileşen 1', 'Bileşen 2'])

print(f"Yeni özellik sayısı: {pca_df.shape[1]}")
print("Dönüşüm sonrası yeni özellikler (ilk 5 satır):")
print(pca_df.head())
```

**Çıktı:**

```
Orijinal özellik sayısı: 4
Yeni özellik sayısı: 2
Dönüşüm sonrası yeni özellikler (ilk 5 satır):
   Bileşen 1  Bileşen 2
0  -2.684126   0.319397
1  -2.714142  -0.177001
2  -2.888991  -0.144949
3  -2.745343  -0.318299
4  -2.728717   0.326755
```

Dikkat edilirse, "Bileşen 1" ve "Bileşen 2" olarak adlandırılan yeni özellikler, orijinal "çanak yaprak uzunluğu" gibi doğrudan yorumlanabilir özelliklerin yerini almıştır.

-----

### Temel Farklılıklar ve Stratejik Seçim

İki yaklaşım arasındaki farkları ve kullanım senaryolarını netleştirelim.

| Kriter | Özellik Seçimi (Feature Selection) | Özellik Çıkarımı (Feature Extraction) |
| :--- | :--- | :--- |
| **Temel Felsefe** | Orijinal özelliklerin bir **alt kümesini seçer**. | Orijinal özelliklerden **yeni özellikler türetir**. |
| **Veri** | Özellikler korunur (Dönüşüm yoktur). | Özellikler dönüştürülür (Orijinaller kaybolur). |
| **Yorumlanabilirlik** | **Yüksektir.** (Hangi özelliğin önemli olduğu bilinir). | **Düşüktür.** (Yeni bileşenlerin anlamı karmaşıktır). |
| **Başlıca Amaç** | Aşırı öğrenmeyi önlemek, yorumlanabilirliği artırmak. | Yüksek boyutluluğu (örn. \>1000 özellik) yönetmek. |
| **Popüler Yöntemler** | Filtre (örn. Chi2, ANOVA), Sarma (RFE), Gömülü (Lasso) | PCA, LDA, t-SNE, Autoencoder'lar |

**Bir Metafor Kullanmak Gerekirse:**

  * **Özellik Seçimi:** 20 kitaplık bir kütüphaneden, projenizle en ilgili 5 kitabı *seçip* rafa koymaktır. Raftaki kitaplar hala orijinal kitaplardır.
  * **Özellik Çıkarımı:** Bu 20 kitabın tamamını okuyup, içerdikleri ana fikirleri 3 sayfalık bir *özet* (sentez) halinde yeniden yazmaktır. Elinizdeki artık orijinal kitaplar değil, onların yoğunlaştırılmış bir temsilidir.

-----

### Sonuç: Hangi Yaklaşım Ne Zaman Tercih Edilmeli?

Özellik Seçimi ve Özellik Çıkarımı arasında mutlak bir "kazanan" yoktur; yalnızca projenin gereksinimlerine göre optimize edilmesi gereken **stratejik bir tercih** mevcuttur.

1.  Eğer projenizin önceliği **yorumlabilirlik** ise (örneğin, tıbbi bir teşhis, finansal risk veya kredi skoru modellemesi gibi kararların "neden" alındığının açıklanması gereken durumlar), orijinal özellikleri koruyan **Özellik Seçimi** tercih edilmelidir.
2.  Eğer öncelik, yüksek boyutlu verilerde (görüntü, ses, yapılandırılmamış metin) **tahmin doğruluğunu maksimize etmekse** ve yorumlanabilirlik ikinci plandaysa, **Özellik Çıkarımı** (PCA gibi) genellikle daha üstün performans sağlar.

Her iki teknik de, daha verimli, daha hızlı ve daha doğru makine öğrenimi modelleri oluşturmak için vazgeçilmez araçlardır.