// blogPostsData.js - Blog yazısı metadata'sını JSON dosyasından çekme

/**
 * Harici bir JSON dosyasından blog yazısı metadata'sını çeker.
 * Tam içerik, ilgili Markdown dosyasından ayrı ayrı çekilmelidir.
 * @returns {Promise<Array>} Blog yazısı metadata nesnelerinin bir dizisini döndüren bir Promise.
 */
export async function fetchBlogPostsMetadata() { // Fonksiyon adını değiştirdik
    try {
        const response = await fetch('/data/blogPostsMetadata.json'); // Yeni dosya yolu
        if (!response.ok) {
            throw new Error(`HTTP hata kodu: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Blog yazısı metadata yüklenirken hata oluştu:', error);
        return [];
    }
}
