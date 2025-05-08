function getTimeAgo(dateString) {
    const now = new Date();
    const past = new Date(dateString);
    const diffInHours = Math.floor((now - past) / (1000 * 60 * 60));

    if (diffInHours < 24) return `${diffInHours}h`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d`;
    const diffInWeeks = Math.floor(diffInDays / 7);
    if (diffInWeeks < 4) return `${diffInWeeks}w`;
    const diffInMonths = Math.floor(diffInDays / 30);
    return `${diffInMonths}mo`;
}

// Video Display
function createVideoCard(video) {
    return `
        <article class="video-card">
            <a href="${video.url}" class="video-title" target="_blank">
                ${video.title}
            </a>
            <div class="video-info">
                <span class="video-time">${getTimeAgo(video.publishedAt)}</span>
                <span class="video-channel">${video.channel}</span>
            </div>
        </article>
    `;
}

function createCategorySection(categoryName, videos) {
    return `
        <section class="category">
            <div class="category-header">
                <h2 class="category-title">${categoryName}</h2>
            </div>
            <div class="video-list">
                ${videos.length > 0
                    ? videos.map(video => createVideoCard(video)).join('')
                    : '<div class="empty-category">No videos available</div>'
                }
            </div>
        </section>
    `;
}

function renderDashboard(data) {
    const container = document.getElementById('categories-container');
    
    if (!data || Object.keys(data).length === 0) {
        container.innerHTML = '<div class="empty-category">No content available</div>';
        return;
    }

    const categoriesHtml = Object.entries(data)
        .map(([category, videos]) => createCategorySection(category, videos))
        .join('');

    container.innerHTML = categoriesHtml;
}

// Loading and Refresh
function showLoading() {
    const container = document.getElementById('categories-container');
    container.innerHTML = '<div class="loading">Loading videos...</div>';
}

async function loadVideos() {
    showLoading();
    try {
        const response = await fetch('/videos.json');
        if (!response.ok) {
            throw new Error('Failed to load videos.json');
        }
        const data = await response.json();
        renderDashboard(data);
    } catch (error) {
        console.error('Error loading videos:', error);
        alert('Failed to load videos. Please try again.');
    }
}

async function refreshVideos() {
    showLoading();
    try {
        const response = await fetch('/api/refresh');
        if (!response.ok) {
            throw new Error('Failed to refresh videos');
        }
        const data = await response.json();
        window.location.reload();
    } catch (error) {
        console.error('Error refreshing videos:', error);
        alert('Failed to refresh videos. Please try again.');
    }
}

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadVideos();
    document.getElementById('refreshBtn').addEventListener('click', refreshVideos);
});
