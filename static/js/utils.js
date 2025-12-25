// utils.js - Genel yardımcı fonksiyonlar

/**
 * 404 (Sayfa Bulunamadı) sayfasını render eder.
 * @param {HTMLElement} contentArea - İçeriğin render edileceği DOM elemanı
 */
export function renderNotFoundPage(contentArea) {
    contentArea.innerHTML = `
        <div class="max-w-3xl mx-auto text-center py-10">
            <h2 class="text-4xl font-bold text-red-600 mb-4">404 - Yazı Bulunamadı</h2>
            <p class="text-lg text-gray-700">Aradığınız sayfa mevcut değil veya yanlış bir URL kullandınız.</p>
            <a href="#/" class="mt-6 inline-block text-white py-3 px-6 rounded-full hover:bg-purple-700 transition duration-300 font-semibold modern-button
                    bg-gradient-to-r from-purple-500 to-purple-600 shadow-lg">Ana Sayfaya Dön</a>
        </div>
    `;
    contentArea.classList.remove('grid-container');
    document.title = "404 - Sayfa Bulunamadı";
    // Canonical ve Open Graph URL'leri 404 sayfasına göre güncelle
    const blogDomain = 'https://n4yuc4.netlify.app/'; // Bu domain'i dinamik olarak alabilir veya sabit tutabilirsiniz
    document.querySelector('link[rel="canonical"]').setAttribute('href', `${blogDomain}#/404`);
    document.querySelector('meta[property="og:url"]').setAttribute('content', `${blogDomain}#/404`);
}

/**
 * Mobil menüyü açar.
 * @param {HTMLElement} mobileMenuOverlay - Mobil menü overlay elemanı
 * @param {HTMLElement} bodyElement - Body elemanı (kaydırmayı engellemek için)
 */
export function openMobileMenu(mobileMenuOverlay, bodyElement) {
    mobileMenuOverlay.classList.add('open');
    bodyElement.classList.add('no-scroll'); // Sayfa kaydırmayı engelle
}

/**
 * Mobil menüyü kapatır.
 * @param {HTMLElement} mobileMenuOverlay - Mobil menü overlay elemanı
 * @param {HTMLElement} bodyElement - Body elemanı (kaydırmayı etkinleştirmek için)
 */
export function closeMobileMenu(mobileMenuOverlay, bodyElement) {
    mobileMenuOverlay.classList.remove('open');
    bodyElement.classList.remove('no-scroll'); // Sayfa kaydırmayı etkinleştir
}

/**
 * Başlık küçültme efektini başlatır.
 * @param {HTMLElement} mainHeader - Ana başlık elemanı
 */
export function initHeaderShrink(mainHeader) {
    const SCROLL_THRESHOLD = 80; // Başlığın küçülmeden önceki kaydırma mesafesi

    window.addEventListener('scroll', () => {
        if (window.scrollY > SCROLL_THRESHOLD) {
            mainHeader.classList.add('shrunk');
        } else {
            mainHeader.classList.remove('shrunk');
        }
    });
}


