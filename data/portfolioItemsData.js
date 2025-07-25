// portfolioItemsData.js - Portfolyo elemanlarını JSON dosyasından çeker
export async function fetchPortfolioItems() {
    const response = await fetch('/data/portfolioItems.json');
    if (!response.ok) throw new Error('Portfolyo verisi yüklenemedi');
    return await response.json();
}
