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
}

/**
 * Mobil menüyü açar.
 */
export function openMobileMenu(mobileMenuOverlay, bodyElement) {
    mobileMenuOverlay.classList.add('open');
    bodyElement.classList.add('no-scroll');
}

/**
 * Mobil menüyü kapatır.
 */
export function closeMobileMenu(mobileMenuOverlay, bodyElement) {
    mobileMenuOverlay.classList.remove('open');
    bodyElement.classList.remove('no-scroll');
}

/**
 * Başlık küçültme efektini başlatır.
 */
export function initHeaderShrink(mainHeader) {
    const SCROLL_THRESHOLD = 80;
    window.addEventListener('scroll', () => {
        if (window.scrollY > SCROLL_THRESHOLD) {
            mainHeader.classList.add('shrunk');
        } else {
            mainHeader.classList.remove('shrunk');
        }
    });
}

/**
 * Kod bloklarını Mac tarzı pencereye dönüştürür ve kopyala butonu ekler.
 */
export function setupCodeBlocks() {
    // Tüm highlight edilmiş kod bloklarını bul
    document.querySelectorAll('pre code').forEach((codeBlock) => {
        const pre = codeBlock.parentElement;
        
        // Zaten işlenmişse atla
        if (pre.parentElement.classList.contains('code-wrapper')) return;

        // Dil sınıfını bul (language-python gibi)
        let language = 'KOD';
        codeBlock.classList.forEach(cls => {
            if (cls.startsWith('language-')) {
                language = cls.replace('language-', '').toUpperCase();
            }
        });

        // Wrapper oluştur
        const wrapper = document.createElement('div');
        wrapper.className = 'code-wrapper';

        // Header oluştur
        const header = document.createElement('div');
        header.className = 'code-header';
        
        // Header HTML içeriği
        header.innerHTML = `
            <div class="window-dots">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
            </div>
            <div class="language-label">${language}</div>
            <button class="copy-btn" title="Kodu Kopyala">
                <i class="far fa-copy"></i>
                <span>Kopyala</span>
            </button>
        `;

        // Butona event listener ekle
        const copyBtn = header.querySelector('.copy-btn');
        copyBtn.addEventListener('click', () => {
            const codeText = codeBlock.innerText; // Sadece metni al
            
            navigator.clipboard.writeText(codeText).then(() => {
                // Başarılı kopyalama efekti
                const icon = copyBtn.querySelector('i');
                const text = copyBtn.querySelector('span');
                
                icon.className = 'fas fa-check';
                text.innerText = 'Kopyalandı!';
                copyBtn.style.color = '#27c93f'; // Yeşil

                setTimeout(() => {
                    icon.className = 'far fa-copy';
                    text.innerText = 'Kopyala';
                    copyBtn.style.color = '';
                }, 2000);
            }).catch(err => {
                console.error('Kopyalama hatası:', err);
                alert('Kopyalama başarısız oldu.');
            });
        });

        // DOM yapısını değiştir
        // pre elementinin olduğu yere wrapper'ı koy
        pre.parentNode.insertBefore(wrapper, pre);
        // header'ı wrapper'a ekle
        wrapper.appendChild(header);
        // pre elementini wrapper'ın içine taşı
        wrapper.appendChild(pre);

        // Highlight.js'i manuel tetikle (Eğer yüklüyse)
        if (window.hljs) {
            window.hljs.highlightElement(codeBlock);
        }
    });
}