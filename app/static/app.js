// ============= Глобальное состояние =============
const state = {
    initData: null,
    currentUser: null,
    myGifts: [],
    myFriends: [],
    friendRequests: [],
    myReservations: [],
    selectedFriend: null,
    selectedFriendGifts: [],
    myGiftsSortBy: 'newest',
    friendGiftsSortBy: 'newest',
    myReservationsSortBy: 'owner-name'
};

// ============= Инициализация Telegram WebApp =============
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Применяем тему Telegram
if (tg.themeParams) {
    const root = document.documentElement;
    Object.entries(tg.themeParams).forEach(([key, value]) => {
        root.style.setProperty(`--tg-theme-${key.replace(/_/g, '-')}`, value);
    });
}

state.initData = tg.initData;

// ============= API запросы =============
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    // Для первого запроса авторизации используем X-Telegram-Init-Data header
    if (url === '/users/auth') {
        defaultOptions.headers['X-Telegram-Init-Data'] = state.initData;
    } else {
        // Для всех остальных запросов используем JWT token
        const token = localStorage.getItem('jwtToken');
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }
    }

    try {
        const response = await fetch(url, defaultOptions);

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        // Для DELETE запросов может не быть тела ответа
        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ============= API методы =============
async function getCurrentUser() {
    return await apiRequest('/users/me');
}

async function getMyFriends() {
    return await apiRequest('/users/me/friends');
}

async function sendFriendRequest(receiverId) {
    return await apiRequest(`/users/me/friends/${receiverId}/request`, {
        method: 'POST'
    });
}

async function getPendingRequests() {
    return await apiRequest('/users/me/friend-requests');
}

async function acceptFriendRequest(senderId) {
    return await apiRequest(`/users/me/friends/${senderId}/accept`, {
        method: 'PATCH'
    });
}

async function rejectFriendRequest(senderId) {
    return await apiRequest(`/users/me/friends/${senderId}/reject`, {
        method: 'PATCH'
    });
}

async function deleteFriend(friendId) {
    return await apiRequest(`/users/me/friends/${friendId}/delete`, {
        method: 'DELETE'
    });
}

async function getUserById(userId) {
    return await apiRequest(`/users/${userId}`);
}

async function getUserGifts(userId) {
    const result = await apiRequest(`/gifts/user/${userId}`);
    return result;
}

async function getMyReservations() {
    return await apiRequest('/gifts/my/reserve');
}

async function addGift(giftData) {
    return await apiRequest('/gifts', {
        method: 'POST',
        body: JSON.stringify(giftData)
    });
}

async function deleteGift(giftId) {
    return await apiRequest(`/gifts/${giftId}`, {
        method: 'DELETE'
    });
}

async function addReservation(giftId) {
    return await apiRequest(`/gifts/${giftId}/reserve`, {
        method: 'POST'
    });
}

async function deleteReservation(giftId) {
    return await apiRequest(`/gifts/${giftId}/reserve`, {
        method: 'DELETE'
    });
}

// ============= Утилиты =============
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU').format(price);
}

function getAvatarUrl(user) {
    if (user.avatar_url) {
        return user.avatar_url;
    }
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(user.first_name)}&size=200&background=0088cc&color=fff`;
}

// копирование ID в буфер обмена
async function copyIdToClipboard() {
    const userId = state.currentUser.tg_id;

    try {
        // Попытка использовать современный API
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(userId.toString());
        } else {
            // Fallback для старых браузеров или Telegram WebApp
            const textArea = document.createElement('textarea');
            textArea.value = userId.toString();
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            textArea.remove();
        }

        tg.showPopup({
            title: 'Скопировано!',
            message: `Ваш ID ${userId} скопирован в буфер обмена`,
            buttons: [{type: 'ok'}]
        });
    } catch (error) {
        console.error('Copy error:', error);
        tg.showPopup({
            title: 'ID',
            message: `Ваш ID: ${userId}`,
            buttons: [{type: 'ok'}]
        });
    }
}

// функция сортировки подарков
function sortGifts(gifts, sortBy) {
    const sorted = [...gifts]; // копируем массив

    switch(sortBy) {
        case 'newest':
            // Сортировка по дате (новые первыми)
            sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            break;
        case 'oldest':
            // Сортировка по дате (старые первыми)
            sorted.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
            break;
        case 'price-high':
            // Сортировка по цене (дорогие первыми, null в конце)
            sorted.sort((a, b) => {
                if (a.price === null) return 1;
                if (b.price === null) return -1;
                return b.price - a.price;
            });
            break;
        case 'price-low':
            // Сортировка по цене (дешёвые первыми, null в конце)
            sorted.sort((a, b) => {
                if (a.price === null) return 1;
                if (b.price === null) return -1;
                return a.price - b.price;
            });
            break;
        case 'wish-rate-high':
            // Сортировка по рейтингу (высокие первыми, null в конце)
            sorted.sort((a, b) => {
                if (a.wish_rate === null) return 1;
                if (b.wish_rate === null) return -1;
                return b.wish_rate - a.wish_rate;
            });
            break;
    }

    return sorted;
}

// функция обогащения резервирований данными о друзьях
function enrichReservationsWithFriendData(reservations, friends) {
    return reservations.map(gift => {
        const friend = friends.find(f => f.tg_id === gift.user_id);
        return {
            ...gift,
            friendData: friend || null
        };
    });
}

// специальная сортировка для "Мои брони"
function sortReservations(reservations, sortBy) {
    const sorted = [...reservations];

    switch(sortBy) {
        case 'owner-name':
            // Сортировка по имени друга (владельца подарка)
            sorted.sort((a, b) => {
                const nameA = a.friendData ? `${a.friendData.first_name} ${a.friendData.last_name || ''}` : '';
                const nameB = b.friendData ? `${b.friendData.first_name} ${b.friendData.last_name || ''}` : '';
                return nameA.localeCompare(nameB);
            });
            break;
        case 'price-low':
            // Сортировка по цене (дешёвые первыми)
            sorted.sort((a, b) => {
                if (a.price === null) return 1;
                if (b.price === null) return -1;
                return a.price - b.price;
            });
            break;
        case 'price-high':
            // Сортировка по цене (дорогие первыми)
            sorted.sort((a, b) => {
                if (a.price === null) return 1;
                if (b.price === null) return -1;
                return b.price - a.price;
            });
            break;
    }

    return sorted;
}

// обработчики изменения сортировки
function changeMyGiftsSort(sortBy) {
    state.myGiftsSortBy = sortBy;
    renderMyGifts();
}

function changeFriendGiftsSort(sortBy) {
    state.friendGiftsSortBy = sortBy;
    renderFriendGifts();
}

function changeMyReservationsSort(sortBy) {
    state.myReservationsSortBy = sortBy;
    renderMyReservations();
}

// ============= Навигация по табам =============
function showTab(tabName) {
    // Убираем активный класс со всех табов и контента
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Активируем нужный таб
    const tabButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (tabButton) {
        tabButton.classList.add('active');
    }

    const tabContent = document.getElementById(`tab-${tabName}`);
    if (tabContent) {
        tabContent.classList.add('active');
    }
}

// Обработчики кликов по табам
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            showTab(tabName);
        });
    });
});

// ============= Рендеринг =============
function renderMyProfile() {
    const user = state.currentUser;

    document.getElementById('my-avatar').src = getAvatarUrl(user);
    document.getElementById('my-name').textContent =
        `${user.first_name}${user.last_name ? ' ' + user.last_name : ''}`;
    document.getElementById('my-username').textContent =
        user.tg_username ? `@${user.tg_username}` : '';

    // ID справа от всего текста
    const idElement = document.getElementById('my-id');
    idElement.innerHTML = `
        <span class="id-text">ID: ${user.tg_id}</span>
        <button class="copy-id-btn" onclick="copyIdToClipboard()" title="Скопировать ID">
            📋
        </button>
    `;

    renderMyGifts();
}

function renderMyGifts() {
    const container = document.getElementById('my-gifts-container');
    const gifts = state.myGifts || [];

    if (gifts.length === 0) {
        container.innerHTML = `
            <div class="sort-controls">
                <label class="sort-label">Сортировать:</label>
                <select class="sort-select" onchange="changeMyGiftsSort(this.value)">
                    <option value="newest" ${state.myGiftsSortBy === 'newest' ? 'selected' : ''}>Сначала новые</option>
                    <option value="oldest" ${state.myGiftsSortBy === 'oldest' ? 'selected' : ''}>Сначала старые</option>
                    <option value="price-high" ${state.myGiftsSortBy === 'price-high' ? 'selected' : ''}>Сначала дороже</option>
                    <option value="price-low" ${state.myGiftsSortBy === 'price-low' ? 'selected' : ''}>Сначала дешевле</option>
                    <option value="wish-rate-high" ${state.myGiftsSortBy === 'wish-rate-high' ? 'selected' : ''}>Сначала самые желанные</option>
                </select>
            </div>
            <div class="section-empty">Пока нет подарков в списке желаний</div>
        `;
        return;
    }

    // сортируем подарки
    const sortedGifts = sortGifts(gifts, state.myGiftsSortBy);

    container.innerHTML = `
        <div class="sort-controls">
            <label class="sort-label">Сортировать:</label>
            <select class="sort-select" onchange="changeMyGiftsSort(this.value)">
                <option value="newest" ${state.myGiftsSortBy === 'newest' ? 'selected' : ''}>Сначала новые</option>
                <option value="oldest" ${state.myGiftsSortBy === 'oldest' ? 'selected' : ''}>Сначала старые</option>
                <option value="price-high" ${state.myGiftsSortBy === 'price-high' ? 'selected' : ''}>Сначала дороже</option>
                <option value="price-low" ${state.myGiftsSortBy === 'price-low' ? 'selected' : ''}>Сначала дешевле</option>
                <option value="wish-rate-high" ${state.myGiftsSortBy === 'wish-rate-high' ? 'selected' : ''}>Сначала самые желанные</option>
            </select>
        </div>
        <div class="gifts-grid">
            ${sortedGifts.map(gift => `
                <div class="gift-card own ${gift.is_reserved ? 'reserved' : ''}">
                    <button class="gift-delete-btn" onclick="confirmDeleteGift(${gift.id})" title="Удалить">
                        ×
                    </button>
                    <div class="gift-header">
                        <div class="gift-name">${escapeHtml(gift.name)}</div>
                        ${gift.wish_rate ? `<div class="gift-wish-rate">⭐ ${gift.wish_rate}/10</div>` : ''}
                    </div>
                    ${gift.url ? `<a href="${escapeHtml(gift.url)}" class="gift-url" target="_blank">🔗 Ссылка</a>` : ''}
                    ${gift.price ? `<div class="gift-price">💰 ${formatPrice(gift.price)} ₽</div>` : ''}
                    ${gift.note ? `<div class="gift-note">📝 ${escapeHtml(gift.note)}</div>` : ''}
                    <div class="gift-date">Добавлен: ${new Date(gift.created_at).toLocaleDateString('ru-RU')}</div>
                    ${gift.is_reserved
                        ? `<div class="gift-reservation-badge">🔒 Забронировано</div>
                           <button class="gift-reserve-btn unreserve" onclick="handleCancelReservation(${gift.id}, 'my-gifts')">Снять бронь</button>`
                        : `<button class="gift-reserve-btn reserve" onclick="handleReserveSelfGift(${gift.id})">🎁 Буду дарить</button>`
                    }
                </div>
            `).join('')}
        </div>
    `;
}

function renderMyReservations() {
    const container = document.getElementById('my-reservations-container');
    const reservations = state.myReservations || [];

    if (reservations.length === 0) {
        container.innerHTML = `
            <div class="sort-controls">
                <label class="sort-label">Сортировать:</label>
                <select class="sort-select" onchange="changeMyReservationsSort(this.value)">
                    <option value="owner-name" ${state.myReservationsSortBy === 'owner-name' ? 'selected' : ''}>По владельцу подарка (A-Z)</option>
                    <option value="price-low" ${state.myReservationsSortBy === 'price-low' ? 'selected' : ''}>По цене: дешевле</option>
                    <option value="price-high" ${state.myReservationsSortBy === 'price-high' ? 'selected' : ''}>По цене: дороже</option>
                </select>
            </div>
            <div class="section-empty">Ты пока ничего не забронировал 🎁</div>
        `;
        return;
    }

    // Обогащаем резервирования данными друзей или текущего пользователя
    const enrichedReservations = reservations.map(gift => {
        let friend = state.myFriends.find(f => f.tg_id === gift.user_id);
        // Если не в списке друзей и это твой подарок - используй текущего пользователя
        if (!friend && gift.user_id === state.currentUser.tg_id) {
            friend = state.currentUser;
        }
        return {
            ...gift,
            friendData: friend || null
        };
    });

    const sortedReservations = sortReservations(enrichedReservations, state.myReservationsSortBy);

    container.innerHTML = `
        <div class="sort-controls">
            <label class="sort-label">Сортировать:</label>
            <select class="sort-select" onchange="changeMyReservationsSort(this.value)">
                <option value="owner-name" ${state.myReservationsSortBy === 'owner-name' ? 'selected' : ''}>По владельцу подарка (A-Z)</option>
                <option value="price-low" ${state.myReservationsSortBy === 'price-low' ? 'selected' : ''}>По цене: дешевле</option>
                <option value="price-high" ${state.myReservationsSortBy === 'price-high' ? 'selected' : ''}>По цене: дороже</option>
            </select>
        </div>
        <div>
            ${sortedReservations.map(gift => {
                const friend = gift.friendData;
                const friendName = friend ? `${friend.first_name}${friend.last_name ? ' ' + friend.last_name : ''}` : 'Неизвестный';

                return `
                    <div class="reservation-card">
                        ${friend ? `
                            <img class="reservation-friend-avatar"
                                 src="${getAvatarUrl(friend)}"
                                 alt="Avatar"
                                 onclick="showFriendProfile(${friend.tg_id})"
                                 title="Перейти в профиль">
                        ` : ''}
                        <div class="reservation-content">
                            ${friend ? `
                                <a class="reservation-friend-name" onclick="showFriendProfile(${friend.tg_id})">
                                    ${escapeHtml(friendName)}
                                </a>
                            ` : `<div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">Неизвестный пользователь</div>`}
                            <div class="reservation-gift-name">${escapeHtml(gift.name)}</div>
                            <div class="reservation-gift-info">
                                ${gift.wish_rate ? `⭐ ${gift.wish_rate}/10 • ` : ''}
                                ${gift.price ? `💰 ${formatPrice(gift.price)} ₽ • ` : ''}
                                Зарезервировано: ${new Date(gift.created_at).toLocaleDateString('ru-RU')}
                            </div>
                            ${gift.note ? `<div class="reservation-gift-info">📝 ${escapeHtml(gift.note)}</div>` : ''}
                            <div class="reservation-actions">
                                <button class="reservation-cancel-btn" onclick="handleCancelReservation(${gift.id}, 'reservations')">
                                    ✕ Отменить бронь
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

    container.innerHTML = `
        <div class="sort-controls">
            <label class="sort-label">Сортировать:</label>
            <select class="sort-select" onchange="changeMyReservationsSort(this.value)">
                <option value="owner-name" ${state.myReservationsSortBy === 'owner-name' ? 'selected' : ''}>По владельцу подарка (A-Z)</option>
                <option value="price-low" ${state.myReservationsSortBy === 'price-low' ? 'selected' : ''}>По цене: дешевле</option>
                <option value="price-high" ${state.myReservationsSortBy === 'price-high' ? 'selected' : ''}>По цене: дороже</option>
            </select>
        </div>
        <div>
            ${sortedReservations.map(gift => {
                const friend = gift.friendData;
                const friendName = friend ? `${friend.first_name}${friend.last_name ? ' ' + friend.last_name : ''}` : 'Неизвестный';

                return `
                    <div class="reservation-card">
                        ${friend ? `
                            <img class="reservation-friend-avatar"
                                 src="${getAvatarUrl(friend)}"
                                 alt="Avatar"
                                 onclick="showFriendProfile(${friend.tg_id})"
                                 title="Перейти в профиль">
                        ` : ''}
                        <div class="reservation-content">
                            ${friend ? `
                                <a class="reservation-friend-name" onclick="showFriendProfile(${friend.tg_id})">
                                    ${escapeHtml(friendName)}
                                </a>
                            ` : `<div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">Неизвестный пользователь</div>`}
                            <div class="reservation-gift-name">${escapeHtml(gift.name)}</div>
                            <div class="reservation-gift-info">
                                ${gift.wish_rate ? `⭐ ${gift.wish_rate}/10 • ` : ''}
                                ${gift.price ? `💰 ${formatPrice(gift.price)} ₽ • ` : ''}
                                Зарезервировано: ${new Date(gift.created_at).toLocaleDateString('ru-RU')}
                            </div>
                            ${gift.note ? `<div class="reservation-gift-info">📝 ${escapeHtml(gift.note)}</div>` : ''}
                            <div class="reservation-actions">
                                <button class="reservation-cancel-btn" onclick="handleCancelReservation(${gift.id}, 'reservations')">
                                    ✕ Отменить бронь
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

function renderFriendRequests() {
    const container = document.getElementById('friend-requests-container');

    if (!state.friendRequests || state.friendRequests.length === 0) {
        container.innerHTML = '<div class="section-empty">Нет входящих заявок</div>';
        return;
    }

    container.innerHTML = `
        <div class="friend-requests-list">
            ${state.friendRequests.map(request => `
                <div class="friend-request-card">
                    <div class="request-user-info">
                        <div class="friend-name">${escapeHtml(request.sender_name || 'Пользователь')}</div>
                        <div class="friend-username">
                            ${request.sender_username ? '@' + escapeHtml(request.sender_username) : 'ID: ' + request.sender_tg_id}
                        </div>
                    </div>
                    <div class="request-actions">
                        <button class="btn btn-primary btn-small"
                                onclick="handleAcceptRequest(${request.sender_tg_id})">
                            ✓ Принять
                        </button>
                        <button class="btn btn-small"
                                onclick="handleRejectRequest(${request.sender_tg_id})">
                            ✗ Отклонить
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderFriends() {
    const container = document.getElementById('friends-container');
    const friends = state.myFriends;

    if (friends.length === 0) {
        container.innerHTML = '<div class="section-empty">Пока нет друзей</div>';
        return;
    }

    container.innerHTML = `
        <div class="friends-grid">
            ${friends.map(friend => `
                <div class="friend-card" onclick="showFriendProfile(${friend.tg_id})">
                    <button class="friend-delete-btn" onclick="event.stopPropagation(); confirmDeleteFriend(${friend.tg_id})" title="Удалить">
                        ×
                    </button>
                    <img class="friend-avatar" src="${getAvatarUrl(friend)}" alt="Avatar">
                    <div class="friend-info">
                        <div class="friend-name">${escapeHtml(friend.first_name)}${friend.last_name ? ' ' + escapeHtml(friend.last_name) : ''}</div>
                        <div class="friend-username">${friend.tg_username ? '@' + escapeHtml(friend.tg_username) : 'ID: ' + friend.tg_id}</div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderFriendProfile() {
    const friend = state.selectedFriend;

    document.getElementById('friend-avatar').src = getAvatarUrl(friend);
    document.getElementById('friend-name').textContent =
        `${friend.first_name}${friend.last_name ? ' ' + friend.last_name : ''}`;
    document.getElementById('friend-username').textContent =
        friend.tg_username ? `@${friend.tg_username}` : '';

    // ID справа от всего текста
    const idElement = document.getElementById('friend-id');
    idElement.innerHTML = `
        <span class="id-text">ID: ${friend.tg_id}</span>
    `;

    renderFriendGifts();
}

function renderFriendGifts() {
    const container = document.getElementById('friend-gifts-container');
    const gifts = state.selectedFriendGifts;

    if (gifts.length === 0) {
        container.innerHTML = `
            <div class="sort-controls">
                <label class="sort-label">Сортировать:</label>
                <select class="sort-select" onchange="changeFriendGiftsSort(this.value)">
                    <option value="newest" ${state.friendGiftsSortBy === 'newest' ? 'selected' : ''}>Сначала новые</option>
                    <option value="oldest" ${state.friendGiftsSortBy === 'oldest' ? 'selected' : ''}>Сначала старые</option>
                    <option value="price-high" ${state.friendGiftsSortBy === 'price-high' ? 'selected' : ''}>Сначала дороже</option>
                    <option value="price-low" ${state.friendGiftsSortBy === 'price-low' ? 'selected' : ''}>Сначала дешевле</option>
                    <option value="wish-rate-high" ${state.friendGiftsSortBy === 'wish-rate-high' ? 'selected' : ''}>Сначала самые желанные</option>
                </select>
            </div>
            <div class="section-empty">У друга пока нет подарков в вишлисте</div>
        `;
        return;
    }

    // сортируем подарки
    const sortedGifts = sortGifts(gifts, state.friendGiftsSortBy);

    container.innerHTML = `
        <div class="sort-controls">
            <label class="sort-label">Сортировать:</label>
            <select class="sort-select" onchange="changeFriendGiftsSort(this.value)">
                <option value="newest" ${state.friendGiftsSortBy === 'newest' ? 'selected' : ''}>Сначала новые</option>
                <option value="oldest" ${state.friendGiftsSortBy === 'oldest' ? 'selected' : ''}>Сначала старые</option>
                <option value="price-high" ${state.friendGiftsSortBy === 'price-high' ? 'selected' : ''}>Сначала дороже</option>
                <option value="price-low" ${state.friendGiftsSortBy === 'price-low' ? 'selected' : ''}>Сначала дешевле</option>
                <option value="wish-rate-high" ${state.friendGiftsSortBy === 'wish-rate-high' ? 'selected' : ''}>Сначала самые желанные</option>
            </select>
        </div>
        <div class="gifts-grid">
            ${sortedGifts.map(gift => `
                <div class="gift-card ${gift.is_reserved ? 'reserved' : ''}">
                    <div class="gift-header">
                        <div class="gift-name">${escapeHtml(gift.name)}</div>
                        ${gift.wish_rate ? `<div class="gift-wish-rate">⭐ ${gift.wish_rate}/10</div>` : ''}
                    </div>
                    ${gift.url ? `<a href="${escapeHtml(gift.url)}" class="gift-url" target="_blank">🔗 Ссылка</a>` : ''}
                    ${gift.price ? `<div class="gift-price">💰 ${formatPrice(gift.price)} ₽</div>` : ''}
                    ${gift.note ? `<div class="gift-note">📝 ${escapeHtml(gift.note)}</div>` : ''}
                    <div class="gift-date">Добавлен: ${new Date(gift.created_at).toLocaleDateString('ru-RU')}</div>
                    ${gift.is_reserved && gift.reserved_by === state.currentUser.tg_id
                        ? `<div class="gift-reservation-badge">🔒 Забронировано тобой</div>
                           <button class="gift-reserve-btn unreserve" onclick="handleCancelReservation(${gift.id}, 'friend-profile')">Снять бронь</button>`
                        : gift.is_reserved
                            ? `<div class="gift-reservation-badge">🔒 Забронировано</div>`
                            : `<button class="gift-reserve-btn reserve" onclick="handleReserve(${gift.id})">🎁 Буду дарить</button>`
                    }
                </div>
            `).join('')}
        </div>
    `;
}

// ============= Действия с подарками =============
function openAddGiftModal() {
    document.getElementById('modal-add-gift').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    // Очищаем форму
    const form = document.querySelector(`#${modalId} form`);
    if (form) form.reset();
}

async function handleAddGift(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const giftData = {
        name: formData.get('name'),
        url: formData.get('url') || null,
        wish_rate: formData.get('wish_rate') ? parseInt(formData.get('wish_rate')) : null,
        price: formData.get('price') ? parseInt(formData.get('price')) : null,
        note: formData.get('note') || null
    };

    try {
        await addGift(giftData);
        closeModal('modal-add-gift');

        // Обновляем данные
        state.myGifts = await getUserGifts(state.currentUser.tg_id);
        renderMyGifts();

        tg.showPopup({
            title: 'Успех',
            message: 'Подарок добавлен в вишлист!',
            buttons: [{type: 'ok'}]
        });
    } catch (error) {
        tg.showPopup({
            title: 'Ошибка',
            message: error.message,
            buttons: [{type: 'ok'}]
        });
    }
}

function confirmDeleteGift(giftId) {
    tg.showPopup({
        title: 'Удалить подарок?',
        message: 'Вы уверены, что хотите удалить этот подарок из вишлиста?',
        buttons: [
            {id: 'cancel', type: 'cancel'},
            {id: 'delete', type: 'destructive', text: 'Удалить'}
        ]
    }, async (buttonId) => {
        if (buttonId === 'delete') {
            try {
                await deleteGift(giftId);

                // Обновляем данные
                state.myGifts = await getUserGifts(state.currentUser.tg_id);
                renderMyGifts();

                tg.showPopup({
                    title: 'Успех',
                    message: 'Подарок удалён',
                    buttons: [{type: 'ok'}]
                });
            } catch (error) {
                tg.showPopup({
                    title: 'Ошибка',
                    message: error.message,
                    buttons: [{type: 'ok'}]
                });
            }
        }
    });
}

// ============= Действия с друзьями =============
function openAddFriendModal() {
    document.getElementById('modal-add-friend').classList.add('active');
}

async function handleAddFriend(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const friendId = parseInt(formData.get('friend_id'));

    if (friendId === state.currentUser.tg_id) {
        tg.showPopup({
            title: 'Ошибка',
            message: 'Нельзя добавить самого себя в друзья',
            buttons: [{type: 'ok'}]
        });
        return;
    }

    try {
        await sendFriendRequest(friendId);
        closeModal('modal-add-friend');

        tg.showPopup({
            title: 'Успех',
            message: 'Заявка в друзья отправлена!',
            buttons: [{type: 'ok'}]
        });
    } catch (error) {
        tg.showPopup({
            title: 'Ошибка',
            message: error.message,
            buttons: [{type: 'ok'}]
        });
    }
}

async function handleAcceptRequest(senderId) {
    try {
        await acceptFriendRequest(senderId);

        // Обновляем данные
        state.friendRequests = await getPendingRequests();
        state.myFriends = await getMyFriends();

        renderFriendRequests();
        renderFriends();

        tg.showPopup({
            title: 'Успех',
            message: 'Заявка принята! Пользователь добавлен в друзья',
            buttons: [{type: 'ok'}]
        });
    } catch (error) {
        tg.showPopup({
            title: 'Ошибка',
            message: error.message,
            buttons: [{type: 'ok'}]
        });
    }
}

async function handleRejectRequest(senderId) {
    try {
        await rejectFriendRequest(senderId);

        state.friendRequests = await getPendingRequests();
        renderFriendRequests();

        tg.showPopup({
            title: 'Успех',
            message: 'Заявка отклонена',
            buttons: [{type: 'ok'}]
        });
    } catch (error) {
        tg.showPopup({
            title: 'Ошибка',
            message: error.message,
            buttons: [{type: 'ok'}]
        });
    }
}

function confirmDeleteFriend(friendId) {
    tg.showPopup({
        title: 'Удалить из друзей?',
        message: 'Вы уверены, что хотите удалить этого пользователя из друзей?',
        buttons: [
            {id: 'cancel', type: 'cancel'},
            {id: 'delete', type: 'destructive', text: 'Удалить'}
        ]
    }, async (buttonId) => {
        if (buttonId === 'delete') {
            try {
                await deleteFriend(friendId);

                // Обновляем список друзей
                state.myFriends = await getMyFriends();
                renderFriends();

                tg.showPopup({
                    title: 'Успех',
                    message: 'Пользователь удален из друзей',
                    buttons: [{type: 'ok'}]
                });
            } catch (error) {
                tg.showPopup({
                    title: 'Ошибка',
                    message: error.message,
                    buttons: [{type: 'ok'}]
                });
            }
        }
    });
}

async function showFriendProfile(friendId) {
    try {
        // Загружаем данные друга и его подарки
        state.selectedFriend = await getUserById(friendId);
        state.selectedFriendGifts = await getUserGifts(friendId);

        // Отображаем профиль друга
        renderFriendProfile();
        showTab('friend-profile');
    } catch (error) {
        tg.showPopup({
            title: 'Ошибка',
            message: 'Не удалось загрузить профиль друга',
            buttons: [{type: 'ok'}]
        });
    }
}

// ============= Действия с бронью =============
async function handleReserveSelfGift(giftId) {
    try {
        await addReservation(giftId);
        state.myGifts = await getUserGifts(state.currentUser.tg_id);
        state.myReservations = await getMyReservations();
        renderMyGifts();
        renderMyReservations();
    } catch (error) {
        tg.showPopup({
            title: 'Ошибка',
            message: error.message,
            buttons: [{type: 'ok'}]
        });
    }
}

async function handleReserve(giftId) {
    try {
        await addReservation(giftId);
        state.selectedFriendGifts = await getUserGifts(state.selectedFriend.tg_id);
        state.myReservations = await getMyReservations();
        renderFriendGifts();
        renderMyReservations();  // ← ДОБАВИТЬ ЭТО для обновления вкладки "Мои брони"
    } catch (error) {
        tg.showPopup({
            title: 'Ошибка',
            message: error.message,
            buttons: [{type: 'ok'}]
        });
    }
}

// Отмена брони (универсальная функция)
async function handleCancelReservation(giftId, sourceTab) {
    try {
        await deleteReservation(giftId);

        // Обновляем данные в зависимости от того, где произошло удаление
        if (sourceTab === 'my-gifts') {
            state.myGifts = await getUserGifts(state.currentUser.tg_id);
            state.myReservations = await getMyReservations();
            renderMyGifts();
            renderMyReservations();
        } else if (sourceTab === 'friend-profile') {
            state.selectedFriendGifts = await getUserGifts(state.selectedFriend.tg_id);
            state.myReservations = await getMyReservations();
            renderFriendGifts();
            renderMyReservations();
        } else if (sourceTab === 'reservations') {
            state.myReservations = await getMyReservations();
            renderMyReservations();
        }

        tg.showPopup({
            title: 'Успех',
            message: 'Бронь отменена',
            buttons: [{type: 'ok'}]
        });
    } catch (error) {
        tg.showPopup({
            title: 'Ошибка',
            message: error.message,
            buttons: [{type: 'ok'}]
        });
    }
}

// ============= Инициализация приложения =============
async function initApp() {
    try {
        if (!state.initData) {
            throw new Error('Откройте приложение из Telegram');
        }

        // Авторизация через /users/auth
        // Отправляем X-Telegram-Init-Data header, получаем TokenOut
        const authResponse = await apiRequest('/users/auth', {
            method: 'POST'
        });

        // Сохраняем access_token из TokenOut
        if (authResponse.access_token) {
            localStorage.setItem('jwtToken', authResponse.access_token);
        } else {
            throw new Error('Не получен access_token от сервера');
        }

        // Загружаем текущего пользователя
        state.currentUser = await getCurrentUser();

        // Загружаем друзей, заявки, подарки и резервирования
        state.myFriends = await getMyFriends();
        state.friendRequests = await getPendingRequests();
        state.myGifts = await getUserGifts(state.currentUser.tg_id);
        state.myReservations = await getMyReservations();

        // Отображаем интерфейс
        document.getElementById('loading').style.display = 'none';
        document.getElementById('main-app').style.display = 'block';

        // Рендерим профиль, друзей, заявки и резервирования
        renderMyProfile();
        renderMyReservations();
        renderFriends();
        renderFriendRequests();

    } catch (error) {
        console.error('Init error:', error);
        document.getElementById('loading').innerHTML = `
            <div class="status error">
                ❌ Ошибка: ${error.message}
            </div>
        `;
    }
}

// Запускаем приложение
initApp();
