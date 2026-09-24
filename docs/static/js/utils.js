// utils.js - Genel yardımcı fonksiyonlar

/**
 * Mobil menüyü açar (Popover API veya fallback).
 */
export function openMobileMenu(mobileMenuOverlay, bodyElement) {
    if (mobileMenuOverlay && mobileMenuOverlay.showPopover) {
        try {
            mobileMenuOverlay.showPopover();
            return;
        } catch (e) {
            // Devam et fallback
        }
    }
    if (mobileMenuOverlay) mobileMenuOverlay.classList.add('open');
    if (bodyElement) bodyElement.classList.add('no-scroll');
}

/**
 * Mobil menüyü kapatır (Popover API veya fallback).
 */
export function closeMobileMenu(mobileMenuOverlay, bodyElement) {
    if (mobileMenuOverlay && mobileMenuOverlay.hidePopover) {
        try {
            mobileMenuOverlay.hidePopover();
        } catch (e) {
            // Ignored
        }
    }
    if (mobileMenuOverlay) mobileMenuOverlay.classList.remove('open');
    if (bodyElement) bodyElement.classList.remove('no-scroll');
}

/**
 * Portföy teknoloji etiket filtreleme mantığını başlatır.
 */
export function initPortfolioFilter() {
    const filterBar = document.getElementById('portfolio-filter-bar');
    if (!filterBar) return;

    const buttons = filterBar.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.portfolio-card');

    buttons.forEach((btn) => {
        btn.addEventListener('click', () => {
            buttons.forEach((b) => b.classList.remove('active'));
            btn.classList.add('active');

            const selectedTag = btn.getAttribute('data-tag');

            cards.forEach((card) => {
                if (selectedTag === 'all') {
                    card.classList.remove('filtered-out');
                    card.style.opacity = '1';
                    card.style.transform = 'scale(1)';
                } else {
                    const cardTags = (card.getAttribute('data-tags') || '')
                        .split(',')
                        .map((t) => t.trim());

                    if (cardTags.includes(selectedTag)) {
                        card.classList.remove('filtered-out');
                        card.style.opacity = '1';
                        card.style.transform = 'scale(1)';
                    } else {
                        card.style.opacity = '0';
                        card.style.transform = 'scale(0.96)';
                        card.classList.add('filtered-out');
                    }
                }
            });
        });
    });
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
                copyBtn.style.color = '#00d4ff'; // Neon mavi

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

/**
 * Mevcut sayfaya göre navigasyon linklerini vurgular.
 */
export function highlightActiveLink() {
    const path = window.location.pathname;
    
    // Normalize Turkish paths (e.g., /tr/about.html -> /about.html)
    let normalizedPath = path;
    if (path.startsWith('/tr/')) {
        normalizedPath = path.substring(3);
    } else if (path === '/tr') {
        normalizedPath = '/';
    }
    
    // Link ID'lerini ve yollarını eşleştir
    const navMap = {
        '/index.html': 'home',
        '/': 'home',
        '/blog.html': 'blog',
        '/portfolio.html': 'portfolio',
        '/publications.html': 'publications',
        '/about.html': 'about',
        '/contact.html': 'contact'
    };

    // Alt sayfalar için kontrol (örn: /portfolio/proje.html)
    let activeKey = navMap[normalizedPath];
    if (!activeKey) {
        if (normalizedPath.includes('/portfolio/')) activeKey = 'portfolio';
    }

    if (activeKey) {
        // Desktop linkini vurgula
        const desktopLink = document.getElementById(`nav-${activeKey}`);
        if (desktopLink) {
            desktopLink.classList.add('active');
        }

        // Mobil linkini vurgula
        const mobileLink = document.getElementById(`mobile-nav-${activeKey}`);
        if (mobileLink) {
            mobileLink.classList.add('active');
        }
    }
}