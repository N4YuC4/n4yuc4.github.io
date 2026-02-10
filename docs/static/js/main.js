// main.js - Uygulamanın ana mantığı, rota işleme ve olay dinleyicileri

// Yardımcı Fonksiyon Modüllerini İçe Aktar
import {
    openMobileMenu,
    closeMobileMenu,
    initHeaderShrink,
    setupCodeBlocks
} from './utils.js';

document.addEventListener('DOMContentLoaded', async () => {
    // DOM elemanlarına referanslar
    const hamburgerButton = document.getElementById('hamburger-button');
    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    const closeMobileMenuButton = document.getElementById('close-mobile-menu');
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');

    // Kaydırma ile başlık küçültme efekti
    initHeaderShrink(document.getElementById('main-header'));

    // Kod bloklarını geliştir (Mac penceresi, Kopyala butonu)
    // Highlight.js zaten base.html'de çalışıyor, bu fonksiyon üzerine ekleme yapar.
    setupCodeBlocks();

    // Mobil menü olay dinleyicileri
    hamburgerButton.addEventListener('click', () => openMobileMenu(mobileMenuOverlay, document.body));
    closeMobileMenuButton.addEventListener('click', () => closeMobileMenu(mobileMenuOverlay, document.body));

    // Mobil menü içindeki linklere tıklanınca menüyü kapat
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => closeMobileMenu(mobileMenuOverlay, document.body));
    });

    // Pencere boyutu değiştiğinde mobil menüyü kapat (tablet ve üstü için)
    window.addEventListener('resize', () => {
        if (window.innerWidth >= 768) {
            closeMobileMenu(mobileMenuOverlay, document.body);
        }
    });
});
