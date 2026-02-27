// utils.js - Genel yardımcı fonksiyonlar

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
        
        // Header HTML content
        header.innerHTML = `
            <div class="window-dots">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
            </div>
            <div class="language-label">${language}</div>
            <button class="copy-btn" title="Copy Code">
                <i class="far fa-copy"></i>
                <span>Copy</span>
            </button>
        `;

        // Add event listener to button
        const copyBtn = header.querySelector('.copy-btn');
        copyBtn.addEventListener('click', () => {
            const codeText = codeBlock.innerText; // Get only text
            
            navigator.clipboard.writeText(codeText).then(() => {
                // Successful copy effect
                const icon = copyBtn.querySelector('i');
                const text = copyBtn.querySelector('span');
                
                icon.className = 'fas fa-check';
                text.innerText = 'Copied!';
                copyBtn.style.color = '#27c93f'; // Green

                setTimeout(() => {
                    icon.className = 'far fa-copy';
                    text.innerText = 'Copy';
                    copyBtn.style.color = '';
                }, 2000);
            }).catch(err => {
                console.error('Copy error:', err);
                alert('Copy failed.');
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