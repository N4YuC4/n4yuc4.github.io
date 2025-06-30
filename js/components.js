// components.js - UI bileşenlerini oluşturan fonksiyonlar

/**
 * Blog yazısı özeti için HTML elemanı oluşturur.
 * @param {Object} post - Blog yazısı verisi (artık fullContent içermez, sadece metadata)
 * @returns {string} Blog yazısı özeti için HTML stringi
 */
export function createBlogPostSummaryElement(post) {
    // Okuma süresi hesaplamasını kaldırdık, çünkü fullContent artık burada mevcut değil.
    // fullContent yalnızca tek bir yazı sayfası yüklendiğinde fetch ediliyor.

    return `
        <article class="bg-white p-8 rounded-xl shadow-lg hover:shadow-2xl transition duration-500 transform hover:-translate-y-2 relative border border-gray-100">
            <img src="${post.imageUrl}" alt="${post.title} blog yazısı görseli" class="w-full h-52 object-cover rounded-lg mb-6 shadow-md">
            <h2 class="text-2xl font-bold text-gray-800 mb-3 leading-tight">${post.title}</h2>
            <p class="text-sm text-gray-500 mb-5">Yayınlanma Tarihi: ${post.date}</p>
            <p class="text-gray-700 leading-relaxed mb-6 excerpt">${post.excerpt}</p>
            <a href="#/posts/${post.slug}" class="read-more-btn inline-block py-3 px-6 rounded-full font-semibold shadow-lg transition duration-300">
                Devamını Oku
            </a>
        </article>
    `;
}
