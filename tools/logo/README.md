# N4YuC4 — Logo Sistemi

Kişisel site (n4yuc4.github.io) için hazırlanmış minimal logo paketi.

## Konsept

İşaret, **4 düğümlü minimal bir sinir ağı grafiğidir ve "N" harfini çizer**:
N + 4 düğüm = **N4**. İki dikey kenar + bir çapraz kenar (ağ bağlantıları),
sağ alttaki cyan düğüm ise **ateşlenen nöronu** (aktivasyonu) temsil eder.
Çapraz kenardaki mavi→cyan degrade, sitenin mevcut aksan renkleriyle
(#007CF0 → #00D4FF) birebir uyumludur.

## Renkler

| Rol            | Değer     |
|----------------|-----------|
| Zemin (koyu)   | `#0D0D0D` |
| İşaret (koyu zeminde) | `#EDF2F7` |
| İşaret (açık zeminde) | `#0D0D0D` |
| Degrade başı   | `#007CF0` |
| Degrade sonu   | `#00D4FF` |

## Dosyalar

```
svg/
  logo-dark.svg    Birincil işaret, koyu zeminler için (şeffaf)
  logo-light.svg   Birincil işaret, açık zeminler için (şeffaf)
  icon.svg         Favicon: koyu yuvarlatılmış kare + işaret
  lockup-dark.svg  İşaret + "N4YuC4" yazısı (koyu zemin)
  lockup-light.svg İşaret + "N4YuC4" yazısı (açık zemin)
png/
  icon-16.png      Favicon (kalınlaştırılmış geometri)
  icon-32.png      Favicon (kalınlaştırılmış geometri)
  icon-180.png     apple-touch-icon
  icon-512.png     Genel amaçlı ikon / PWA
  logo-512-dark.png, logo-512-light.png, logo-1024-dark.png  Şeffaf raster
  og-cover.png     1200×630 Open Graph / sosyal paylaşım görseli
                   (alt başlık: "Software, Technology and AI")
preview.html       Tüm varyantların canlı önizlemesi
build_logo.py      SVG + PNG üretici betik
raster.py          PIL tabanlı rasterlayıcı (cairo gerektirmez)
```

## Siteye entegrasyon

1. `png/icon-*.png` ve `svg/icon.svg` dosyalarını sitendeki
   `static/images/` dizinine kopyala (mevcut `icon.png`, `icon-32.png`,
   `icon-16.png` yerine).
2. `index.html` / şablon `<head>` bölümüne ekle:

```html
<link rel="icon" type="image/svg+xml" href="/static/images/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/static/images/icon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/static/images/icon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/static/images/icon-180.png">
<meta property="og:image" content="https://n4yuc4.github.io/static/images/og-cover.png">
```

3. Header/nav logosu için (koyu tema):
   `<img src="/static/images/logo-dark.svg" alt="N4YuC4" height="40">`

## Yeniden üretme

```bash
python3 build_logo.py   # tüm SVG + PNG + preview.html çıktılarını yazar
```
