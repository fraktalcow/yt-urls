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

// Modal Management
const modal = document.getElementById('channelModal');
const manageChannelsBtn = document.querySelector('.manage-channels-btn');
const closeModalBtn = document.querySelector('.close-modal');

function openModal() {
    modal.classList.add('active');
    loadCategories();
}

function closeModal() {
    modal.classList.remove('active');
}

manageChannelsBtn.addEventListener('click', openModal);
closeModalBtn.addEventListener('click', closeModal);
modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
});

// Category Management
async function loadCategories() {
    const response = await fetch('/api/videos');
    const data = await response.json();
    renderCategoriesManager(data);
}

function renderCategoriesManager(data) {
    const categoriesList = document.getElementById('categoriesList');
    categoriesList.innerHTML = Object.entries(data)
        .map(([category, channels]) => createCategoryManagerItem(category, channels))
        .join('');

    // Add event listeners for new channel inputs
    document.querySelectorAll('.add-channel-form').forEach(form => {
        form.addEventListener('submit', handleAddChannel);
    });
}

function createCategoryManagerItem(category, videos) {
    const channels = [...new Set(videos.map(video => video.channel))];
    return `
        <div class="category-item">
            <div class="category-header">
                <h3 class="category-name">${category}</h3>
            </div>
            <div class="category-channels">
                ${channels.map(channel => `
                    <div class="channel-tag">
                        ${channel}
                        <button class="remove-channel" onclick="removeChannel('${channel}', '${category}')">&times;</button>
                    </div>
                `).join('')}
            </div>
            <form class="add-channel-input add-channel-form" data-category="${category}">
                <input type="text" placeholder="Add new channel" required>
                <button type="submit">Add</button>
            </form>
        </div>
    `;
}

// Channel Management
async function handleAddChannel(e) {
    e.preventDefault();
    const form = e.target;
    const category = form.dataset.category;
    const input = form.querySelector('input');
    const channelName = input.value.trim();

    if (channelName) {
        const success = await addChannel(channelName, category);
        if (success) {
            input.value = '';
            await loadCategories();
        }
    }
}

async function addChannel(channelName, categoryName) {
    try {
        const formData = new FormData();
        formData.append('channel_name', channelName);
        formData.append('category_name', categoryName);
        
        const response = await fetch('/api/channels', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add channel');
        }
        
        await loadVideos();
        return true;
    } catch (error) {
        console.error('Error adding channel:', error);
        alert(error.message);
        return false;
    }
}

async function removeChannel(channelName) {
    try {
        const response = await fetch(`/api/channels/${encodeURIComponent(channelName)}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to remove channel');
        }
        
        await loadVideos();
        return true;
    } catch (error) {
        console.error('Error removing channel:', error);
        alert(error.message);
        return false;
    }
}

// Add Category
document.getElementById('addCategoryBtn').addEventListener('click', async () => {
    const input = document.getElementById('newCategoryInput');
    const categoryName = input.value.trim();
    
    if (categoryName) {
        const success = await addCategory(categoryName);
        if (success) {
            input.value = '';
            await loadCategories();
        }
    }
});

async function addCategory(categoryName) {
    try {
        const response = await fetch(`/api/categories/${encodeURIComponent(categoryName)}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add category');
        }
        
        await loadVideos();
        return true;
    } catch (error) {
        console.error('Error adding category:', error);
        alert(error.message);
        return false;
    }
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
        renderDashboard(data);
    } catch (error) {
        console.error('Error refreshing videos:', error);
        alert('Failed to refresh videos. Please try again.');
    }
}

// Add refresh button event listener
document.getElementById('refreshBtn').addEventListener('click', refreshVideos);

// Initialize
document.addEventListener('DOMContentLoaded', loadVideos);
