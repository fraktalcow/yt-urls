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
        const timestamp = new Date().getTime();
        const response = await fetch(`/videos.json?t=${timestamp}`);
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

// Channel Management
function createChannelTag(channelName, categoryName) {
    return `
        <div class="channel-tag">
            ${channelName}
            <button class="remove-channel" data-channel="${channelName}" data-category="${categoryName}">&times;</button>
        </div>
    `;
}

function createCategoryItem(categoryName, channels) {
    return `
        <div class="category-item">
            <div class="category-header">
                <span class="category-name">${categoryName}</span>
                <div class="category-actions">
                    <button class="category-action delete-category" data-category="${categoryName}">Delete</button>
                </div>
            </div>
            <div class="category-channels">
                ${channels.map(channel => createChannelTag(channel, categoryName)).join('')}
            </div>
            <div class="add-channel-input">
                <input type="text" placeholder="Add channel" data-category="${categoryName}">
                <button class="add-channel-btn" data-category="${categoryName}">Add</button>
            </div>
        </div>
    `;
}

function renderCategoriesManager(categories) {
    const container = document.getElementById('categoriesList');
    const categoriesHtml = Object.entries(categories)
        .map(([category, channels]) => createCategoryItem(category, channels))
        .join('');
    container.innerHTML = categoriesHtml;
}

async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        if (!response.ok) throw new Error('Failed to load categories');
        const preferences = await response.json();
        renderCategoriesManager(preferences);
    } catch (error) {
        console.error('Error loading categories:', error);
        alert('Failed to load categories. Please try again.');
    }
}

async function addCategory(categoryName) {
    try {
        const response = await fetch('/api/categories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: categoryName })
        });
        if (!response.ok) throw new Error('Failed to add category');
        await loadCategories();
        // Just update the channel management UI, videos will be fetched on refresh
    } catch (error) {
        console.error('Error adding category:', error);
        alert('Failed to add category. Please try again.');
    }
}

async function deleteCategory(categoryName) {
    try {
        const response = await fetch(`/api/categories/${encodeURIComponent(categoryName)}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete category');
        await loadCategories();
        // Just update the channel management UI, videos will be fetched on refresh
    } catch (error) {
        console.error('Error deleting category:', error);
        alert('Failed to delete category. Please try again.');
    }
}

async function addChannel(channelName, categoryName) {
    try {
        const response = await fetch('/api/channels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ channel: channelName, category: categoryName })
        });
        if (!response.ok) throw new Error('Failed to add channel');
        await loadCategories();
        // Just update the channel management UI, videos will be fetched on refresh
    } catch (error) {
        console.error('Error adding channel:', error);
        alert('Failed to add channel. Please try again.');
    }
}

async function removeChannel(channelName, categoryName) {
    try {
        const response = await fetch(`/api/channels/${encodeURIComponent(channelName)}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: categoryName })
        });
        if (!response.ok) throw new Error('Failed to remove channel');
        await loadCategories();
        // Just update the channel management UI, videos will be fetched on refresh
    } catch (error) {
        console.error('Error removing channel:', error);
        alert('Failed to remove channel. Please try again.');
    }
}

// Modal Management
function showModal() {
    document.getElementById('channelModal').classList.add('active');
    loadCategories();
}

function hideModal() {
    document.getElementById('channelModal').classList.remove('active');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadVideos();
    document.getElementById('refreshBtn').addEventListener('click', refreshVideos);
    document.getElementById('manageChannelsBtn').addEventListener('click', showModal);
    document.querySelector('.close-modal').addEventListener('click', hideModal);

    // Close modal when clicking outside
    document.getElementById('channelModal').addEventListener('click', (e) => {
        if (e.target.id === 'channelModal') hideModal();
    });

    // Add category
    document.getElementById('addCategoryBtn').addEventListener('click', () => {
        const input = document.getElementById('newCategoryInput');
        const categoryName = input.value.trim();
        if (categoryName) {
            addCategory(categoryName);
            input.value = '';
        }
    });

    // Add channel
    document.getElementById('categoriesList').addEventListener('click', (e) => {
        if (e.target.classList.contains('add-channel-btn')) {
            const categoryName = e.target.dataset.category;
            const input = e.target.previousElementSibling;
            const channelName = input.value.trim();
            if (channelName) {
                addChannel(channelName, categoryName);
                input.value = '';
            }
        }
    });

    // Remove channel
    document.getElementById('categoriesList').addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-channel')) {
            const channelName = e.target.dataset.channel;
            const categoryName = e.target.dataset.category;
            removeChannel(channelName, categoryName);
        }
    });

    // Delete category
    document.getElementById('categoriesList').addEventListener('click', (e) => {
        if (e.target.classList.contains('delete-category')) {
            const categoryName = e.target.dataset.category;
            deleteCategory(categoryName);
        }
    });
});
