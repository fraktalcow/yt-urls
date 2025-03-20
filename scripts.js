function getTimeAgo(dateString) {
    const now = new Date();
    const past = new Date(dateString);
    const diffInHours = Math.floor((now - past) / (1000 * 60 * 60));

    if (diffInHours < 24) {
        return `${diffInHours}h`;
    }
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) {
        return `${diffInDays}d`;
    }
    const diffInWeeks = Math.floor(diffInDays / 7);
    if (diffInWeeks < 4) {
        return `${diffInWeeks}w`;
    }
    const diffInMonths = Math.floor(diffInDays / 30);
    return `${diffInMonths}mo`;
}

function createVideoCard(video) {
    return `
        <article class="video-card">
            <span class="video-time">${getTimeAgo(video.publishedAt)}</span>
            <a href="${video.url}" class="video-title" target="_blank">
                ${video.title}
            </a>
            <span class="video-channel">— ${video.channel}</span>
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

    if (Object.keys(data).length === 0) {
        container.innerHTML = '<div class="empty-category">No content available</div>';
        return;
    }

    const categoriesHtml = Object.entries(data)
        .map(([category, videos]) => createCategorySection(category, videos))
        .join('');

    container.innerHTML = categoriesHtml;
}

// Determine which API endpoint to use
const isUsingFastAPI = window.location.port === '8000';
const apiUrl = isUsingFastAPI ? '/videos.json' : 'videos.json';

// Add a refresh button if we're using FastAPI
if (isUsingFastAPI) {
    const header = document.querySelector('header');
    if (header) {
        const refreshButton = document.createElement('button');
        refreshButton.className = 'refresh-button';
        refreshButton.textContent = 'Refresh Videos';
        refreshButton.onclick = function() {
            this.disabled = true;
            this.textContent = 'Refreshing...';
            
            fetch('/api/refresh')
                .then(response => response.json())
                .then(data => {
                    this.textContent = `Refreshed (${data.count} videos)`;
                    // Reload the data
                    loadVideos();
                    // Reset button after 3 seconds
                    setTimeout(() => {
                        this.textContent = 'Refresh Videos';
                        this.disabled = false;
                    }, 3000);
                })
                .catch(error => {
                    this.textContent = 'Refresh Failed';
                    this.disabled = false;
                    console.error('Error refreshing videos:', error);
                });
        };
        header.appendChild(refreshButton);
    }
}

function loadVideos() {
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => renderDashboard(data))
        .catch(error => {
            console.error('Error loading the data:', error);
            document.getElementById('categories-container').innerHTML = `
                <div class="error-message">
                    <h2>Error Loading Content</h2>
                    <p>There was an error loading the content.</p>
                    <code>${error.message}</code>
                    <button onclick="loadVideos()">Retry</button>
                </div>
            `;
        });
}

// Initial load
loadVideos();
