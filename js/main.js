// main.js - Uygulamanın ana mantığı, rota işleme ve olay dinleyicileri

// Veri Modüllerini İçe Aktar
// blogPosts artık bir Promise döndürüyor, bu yüzden doğrudan içe aktarmıyoruz
import { fetchBlogPostsMetadata } from '../data/blogPostsData.js'; // metadata çeken fonksiyonu import ettik
import { aboutPageData } from '../data/aboutPageData.js';
import { privacyPolicyData } from '../data/privacyPolicyData.js';
import { termsOfUseData } from '../data/termsOfUseData.js';
import { contactPageData } from '../data/contactPageData.js';

// Bileşen ve Yardımcı Fonksiyon Modüllerini İçe Aktar
import { createBlogPostSummaryElement } from './components.js';
import {
    renderNotFoundPage,
    openMobileMenu,
    closeMobileMenu,
    initHeaderShrink
} from './utils.js';

// Rastgele arka plan görseli seçimi
const backgrounds = [
    'images/bg/bg_1.gif',
    'images/bg/bg_2.gif',
    'images/bg/bg_3.gif',
    'images/bg/bg_4.gif',
    'images/bg/bg_5.gif',
];
const randomBg = backgrounds[Math.floor(Math.random() * backgrounds.length)];
document.body.style.backgroundImage = `url('${randomBg}')`;

document.addEventListener('DOMContentLoaded', async () => {
    // Blog sitesinin ana alan adını burada tanımlayın
    const blogDomain = 'https://n4yuc4.neocities.com/';

    // DOM elemanlarına referanslar
    const contentArea = document.getElementById('content-area');
    const loadingMessage = document.getElementById('loading-message');
    const errorMessage = document.getElementById('error-message');
    const hamburgerButton = document.getElementById('hamburger-button');
    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    const closeMobileMenuButton = document.getElementById('close-mobile-menu');
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');

    // Başlangıçta canonical linkleri ve Open Graph URL'yi ayarla
    document.querySelector('link[rel="canonical"]').setAttribute('href', blogDomain);
    document.querySelector('meta[property="og:url"]').setAttribute('content', blogDomain);

    let blogPostsMetadata = []; // Blog yazı metadata'sını tutacak değişken

    // JSON verilerini çekme ve hata kontrolü
    try {
        // Blog yazı metadata'sını fetchBlogPostsMetadata fonksiyonundan çekiyoruz
        blogPostsMetadata = await fetchBlogPostsMetadata(); // await ile Promise'in çözülmesini bekliyoruz

        // Diğer sabit veriler doğrudan JS'den geliyor, burada değişim yok:
        // aboutPageData, privacyPolicyData, termsOfUseData, contactPageData

        loadingMessage.classList.add('hidden'); // Yükleme mesajını gizle
    } catch (error) {
        console.error('Veri yüklenirken hata oluştu:', error);
        loadingMessage.classList.add('hidden');
        errorMessage.classList.remove('hidden');
        errorMessage.textContent = 'Sayfa verileri yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.';
        return;
    }

    /**
     * Blog yazı listesini ana içerik alanına render eder.
     */
    function renderPostsList() {
        contentArea.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
                ${blogPostsMetadata.map(post => createBlogPostSummaryElement(post)).join('')}
            </div>
        `;
        contentArea.classList.add('grid-container'); // Izgara düzeni için sınıf ekle
        document.title = "N4YuC4_Blog - Veri Bilimi, Makine Öğrenmesi, Derin Öğrenme";
        // Ana sayfa için canonical URL'yi güncelle
        document.querySelector('link[rel="canonical"]').setAttribute('href', blogDomain);
        document.querySelector('meta[property="og:url"]').setAttribute('content', blogDomain);
    }

    /**
     * Tek bir blog yazısını ana içerik alanına render eder.
     * @param {string} slug - Görüntülenecek blog yazısının slug'ı (benzersiz kimliği)
     */
    async function renderSinglePost(slug) { // async anahtar kelimesini ekledik
        const post = blogPostsMetadata.find(p => p.slug === slug);
        if (!post) {
            renderNotFoundPage(contentArea); // Yardımcı fonksiyona contentArea'yı geç
            return;
        }

        // Sayfa başlığını ve canonical URL'yi gönderiyle eşleşecek şekilde güncelle
        document.title = `${post.title} - N4YuC4_Blog`;
        document.querySelector('link[rel="canonical"]').setAttribute('href', `${blogDomain}#/posts/${post.slug}`);
        document.querySelector('meta[property="og:url"]').setAttribute('content', `${blogDomain}#/posts/${post.slug}`);

        // Blog yazısının tam içeriğini Markdown dosyasından çek
        let fullMarkdownContent = '';
        try {
            const response = await fetch(`/${post.contentFile}`); // Markdown dosyasının yolunu kullanıyoruz
            if (!response.ok) {
                throw new Error(`HTTP hata kodu: ${response.status}`);
            }
            fullMarkdownContent = await response.text(); // Metin olarak çekiyoruz
        } catch (error) {
            console.error(`Markdown içeriği yüklenirken hata oluştu: ${post.contentFile}`, error);
            fullMarkdownContent = 'Yazı içeriği yüklenemedi.'; // Hata durumunda mesaj göster
        }

        // Yazı içeriğini Markdown'dan HTML'e dönüştürerek render et
        contentArea.innerHTML = `
            <article class="bg-white p-8 rounded-xl shadow-lg relative border border-gray-100 max-w-3xl mx-auto">
                <a href="#/" class="back-to-home-button inline-block text-purple-600 hover:text-purple-800 transition duration-300 font-semibold mb-6 flex items-center">
                    <i class="fas fa-arrow-left mr-2"></i> Tüm Yazılara Dön
                </a>
                <img src="${post.imageUrl}" alt="${post.title} blog yazısı görseli" class="w-full h-auto object-cover rounded-lg mb-6 shadow-md">
                <h1 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4 leading-tight">${post.title}</h1>
                <p class="text-sm text-gray-500 mb-6">Yayınlanma Tarihi: ${post.date}</p>
                <div class="text-gray-700 leading-relaxed text-lg content-area">
                    ${marked.parse(fullMarkdownContent)}
                </div>
            </article>
        `;
        contentArea.classList.remove('grid-container'); // Izgara düzenini kaldır

        // İçerik render edildikten sonra söz dizimi vurgulamasını uygula
        if (typeof hljs !== 'undefined') {
            hljs.highlightAll();
        }
    }

    /**
     * Hakkımda sayfasını JSON verisinden alarak render eder.
     */
    function renderAboutPage() {
        document.title = `${aboutPageData.title} - N4YuC4_Blog`;
        document.querySelector('link[rel="canonical"]').setAttribute('href', `${blogDomain}#/about`);
        document.querySelector('meta[property="og:url"]').setAttribute('content', `${blogDomain}#/about`);

        // Sosyal medya ikonlarını dinamik olarak oluşturma
        const socialMediaIconsHtml = aboutPageData.socialMediaLinks.map(link => {
            return `
                <a href="${link.url}" class="text-gray-500 hover:text-purple-600 transition duration-300 text-2xl" aria-label="${link.platform} Profili">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        ${link.svgCircle ? `<circle cx="4" cy="4" r="2" stroke="currentColor" stroke-width="0" fill="currentColor"></circle>` : ''}
                        <path ${link.svgCircle ? '' : 'fill-rule="evenodd"'} d="${link.svgPath}"></path>
                    </svg>
                </a>
            `;
        }).join('');

        contentArea.innerHTML = `
            <section id="about-section" class="container mx-auto p-8 bg-white rounded-xl shadow-lg flex-grow">
                <div class="max-w-3xl mx-auto text-center">
                    <img src="${aboutPageData.profileImageUrl}" alt="Kullanıcının profil resmi" class="rounded-full w-40 h-40 object-cover mx-auto mb-6 shadow-md border-4 border-purple-300">
                    <h2 class="text-4xl font-bold text-gray-800 mb-4">${aboutPageData.title}</h2>
                    <div class="text-lg text-gray-700 leading-relaxed content-area-text">
                        ${marked.parse(aboutPageData.content)}
                    </div>
                    <div class="mt-8 flex justify-center space-x-6">
                        ${socialMediaIconsHtml}
                    </div>
                </div>
            </section>
        `;
        contentArea.classList.remove('grid-container');
        if (typeof hljs !== 'undefined') {
            hljs.highlightAll();
        }
    }

    /**
     * İletişim sayfasını JSON verisinden alarak render eder.
     */
    function renderContactPage() {
        document.title = `${contactPageData.title} - N4YuC4_Blog`;
        document.querySelector('link[rel="canonical"]').setAttribute('href', `${blogDomain}#/contact`);
        document.querySelector('meta[property="og:url"]').setAttribute('content', `${blogDomain}#/contact`);

        // Sosyal medya ikonlarını dinamik olarak oluşturma
        const socialMediaIconsHtml = contactPageData.socialMediaLinks.map(link => {
            return `
                <a href="${link.url}" class="text-gray-500 hover:text-purple-600 transition duration-300 text-2xl" aria-label="${link.platform} Profili">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                        ${link.svgCircle ? `<circle cx="4" cy="4" r="2" stroke="currentColor" stroke-width="0" fill="currentColor"></circle>` : ''}
                        <path ${link.svgCircle ? '' : 'fill-rule="evenodd"'} d="${link.svgPath}"></path>
                    </svg>
                </a>
            `;
        }).join('');

        contentArea.innerHTML = `
            <section id="contact-section" class="container mx-auto p-8 bg-white rounded-xl shadow-lg flex-grow">
                <div class="max-w-3xl mx-auto text-center">
                    <h2 class="text-4xl font-bold text-gray-800 mb-6">${contactPageData.title}</h2>
                    <p class="text-lg text-gray-700 leading-relaxed mb-8">
                        ${contactPageData.introText}
                    </p>

                    <div class="mt-8">
                        <h3 class="text-2xl font-bold text-gray-800 mb-4">${contactPageData.otherContactMethodsTitle}</h3>
                        <p class="text-lg text-gray-700 mb-2">
                            E-posta: <a href="mailto:${contactPageData.email}" target="_blank" class="text-blue-600 hover:underline">${contactPageData.email}</a>
                        </p>
                        ${contactPageData.phone ? `<p class="text-lg text-gray-700 mb-2">Telefon: <a href="tel:${contactPageData.phone.replace(/\s/g, '')}" class="text-blue-600 hover:underline">${contactPageData.phone}</a></p>` : ''}
                        <div class="mt-6 flex justify-center space-x-6">
                            ${socialMediaIconsHtml}
                        </div>
                    </div>
                </div>
            </section>
        `;
        contentArea.classList.remove('grid-container');
    }

    /**
     * Gizlilik Politikası sayfasını JSON verisinden alarak render eder.
     */
    function renderPrivacyPage() {
        document.title = `${privacyPolicyData.title} - N4YuC4_Blog`;
        document.querySelector('link[rel="canonical"]').setAttribute('href', `${blogDomain}#/privacy`);
        document.querySelector('meta[property="og:url"]').setAttribute('content', `${blogDomain}#/privacy`);

        contentArea.innerHTML = `
            <section id="privacy-policy-section" class="container mx-auto p-8 bg-white rounded-xl shadow-lg flex-grow">
                <div class="max-w-3xl mx-auto">
                    <h2 class="text-4xl font-bold text-gray-800 mb-6 text-center">${privacyPolicyData.title}</h2>
                    <div class="text-lg text-gray-700 leading-relaxed content-area-text">
                        ${marked.parse(privacyPolicyData.content)}
                    </div>
                </div>
            </section>
        `;
        contentArea.classList.remove('grid-container');
        if (typeof hljs !== 'undefined') {
            hljs.highlightAll();
        }
    }

    /**
     * Kullanım Koşulları sayfasını JSON verisinden alarak render eder.
     */
    function renderTermsPage() {
        document.title = `${termsOfUseData.title} - N4YuC4_Blog`;
        document.querySelector('link[rel="canonical"]').setAttribute('href', `${blogDomain}#/terms`);
        document.querySelector('meta[property="og:url"]').setAttribute('content', `${blogDomain}#/terms`);

        contentArea.innerHTML = `
            <section id="terms-of-use-section" class="container mx-auto p-8 bg-white rounded-xl shadow-lg flex-grow">
                <div class="max-w-3xl mx-auto">
                    <h2 class="text-4xl font-bold text-gray-800 mb-6 text-center">${termsOfUseData.title}</h2>
                    <div class="text-lg text-gray-700 leading-relaxed content-area-text">
                        ${marked.parse(termsOfUseData.content)}
                    </div>
                </div>
            </section>
        `;
        contentArea.classList.remove('grid-container');
        if (typeof hljs !== 'undefined') {
            hljs.highlightAll();
        }
    }

    /**
     * URL hash'ine göre sayfayı yönlendirir ve içeriği render eder.
     */
    async function handleRoute() { // async anahtar kelimesini ekledik
        const hash = window.location.hash;
        loadingMessage.classList.add('hidden'); // Yükleme mesajını gizle
        errorMessage.classList.add('hidden'); // Hata mesajını gizla

        contentArea.innerHTML = ''; // Mevcut tüm içeriği temizle

        if (hash.startsWith('#/posts/')) {
            const slug = hash.substring('#/posts/'.length);
            await renderSinglePost(slug); // await ile bekle
        } else if (hash === '#/about') {
            renderAboutPage();
        } else if (hash === '#/contact') {
            renderContactPage();
        } else if (hash === '#/privacy') {
            renderPrivacyPage();
        } else if (hash === '#/terms') {
            renderTermsPage();
        } else {
            renderPostsList(); // Varsayılan olarak blog yazısı listesini göster
        }
        // Rota değişiminde mobil menüyü kapat
        closeMobileMenu(mobileMenuOverlay, document.body);
    }

    // Hash değişikliklerini (navigasyon için) ve popstate'i (geri/ileri butonları için) dinle
    window.addEventListener('hashchange', handleRoute);
    window.addEventListener('popstate', handleRoute);

    // Sayfa yüklendiğinde ilk rota işleme
    handleRoute();

    // Kaydırma ile başlık küçültme efekti
    initHeaderShrink(document.getElementById('main-header'));

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

    // Header başlık animasyonu (_ karakteri kadar boşluk bırak)
    const headerTitleText = document.getElementById('header-title-text');
    if (headerTitleText) {
        let toggle = false;
        setInterval(() => {
            if (toggle) {
                headerTitleText.innerHTML = "N4YuC4_Blog";
            } else {
                // "_" karakteri yerine aynı uzunlukta boşluk bırak
                headerTitleText.innerHTML = "N4YuC4&nbsp;&nbsp;&nbsp;&nbsp;Blog";
            }
            toggle = !toggle;
        }, 1000);
    }
});
