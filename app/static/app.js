// ============= Глобальное состояние =============
const state = {
    initData: null,
    currentUser: null,
    myGifts: [],
    myFriends: [],
    friendRequests: [],
    selectedFriend: null,
    selectedFriendGifts: [],
    myGiftsSortBy: 'date', // date, price, wish_rate
    friendGiftsSortBy: 'date'
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
            'X-Telegram-Init-Data': state.initData,
            ...options.headers
        },
        ...options
    };

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
    return await apiRequest(`/users/me/friend-requests/${receiverId}`, {
        method: 'POST'
    });
}

async function getPendingRequests() {
    return await apiRequest('/users/me/friend-requests');
}

async function acceptFriendRequest(senderId) {
    return await apiRequest(`/users/me/friend-requests/${senderId}/accept`, {
        method: 'POST'
    });
}

async function rejectFriendRequest(senderId) {
    return await apiRequest(`/users/me/friend-requests/${senderId}/reject`, {
        method: 'POST'
    });
}

async function deleteFriend(friendId) {
    return await apiRequest(`/users/me/friends/${friendId}`, {
        method: 'DELETE'
    });
}

async function getUserById(userId) {
    return await apiRequest(`/users/${userId}`);
}

async function getUserGifts(userId) {
    return await apiRequest(`/users/${userId}/gifts`);
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
        case 'date':
            // Сортировка по дате (новые первыми)
            sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            break;
        case 'price':
            // Сортировка по цене (дорогие первыми, null в конце)
            sorted.sort((a, b) => {
                if (a.price === null) return 1;
                if (b.price === null) return -1;
                return b.price - a.price;
            });
            break;
        case 'wish_rate':
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

// обработчики изменения сортировки
function changeMyGiftsSort(sortBy) {
    state.myGiftsSortBy = sortBy;
    renderMyGifts();
}

function changeFriendGiftsSort(sortBy) {
    state.friendGiftsSortBy = sortBy;
    renderFriendGifts();
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
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        showTab(tabName);
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

    // кнопка слева, ID по центру
    const idElement = document.getElementById('my-id');
    idElement.innerHTML = `
        <button class="copy-id-btn" onclick="copyIdToClipboard()" title="Скопировать ID">
            📋
        </button>
        <span class="id-text">ID: ${user.tg_id}</span>
    `;

    renderMyGifts();
}

function renderMyGifts() {
    const container = document.getElementById('my-gifts-container');
    const gifts = state.currentUser.gifts || [];

    if (gifts.length === 0) {
        container.innerHTML = `
            <div class="sort-controls">
                <label class="sort-label">Сортировать:</label>
                <select class="sort-select" onchange="changeMyGiftsSort(this.value)">
                    <option value="date" ${state.myGiftsSortBy === 'date' ? 'selected' : ''}>По дате</option>
                    <option value="price" ${state.myGiftsSortBy === 'price' ? 'selected' : ''}>По цене</option>
                    <option value="wish_rate" ${state.myGiftsSortBy === 'wish_rate' ? 'selected' : ''}>По рейтингу</option>
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
                <option value="date" ${state.myGiftsSortBy === 'date' ? 'selected' : ''}>По дате</option>
                <option value="price" ${state.myGiftsSortBy === 'price' ? 'selected' : ''}>По цене</option>
                <option value="wish_rate" ${state.myGiftsSortBy === 'wish_rate' ? 'selected' : ''}>По рейтингу</option>
            </select>
        </div>
        <div class="gifts-grid">
            ${sortedGifts.map(gift => `
                <div class="gift-card own">
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
                </div>
            `).join('')}
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
    document.getElementById('friend-id').textContent = `ID: ${friend.tg_id}`;

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
                    <option value="date" ${state.friendGiftsSortBy === 'date' ? 'selected' : ''}>По дате</option>
                    <option value="price" ${state.friendGiftsSortBy === 'price' ? 'selected' : ''}>По цене</option>
                    <option value="wish_rate" ${state.friendGiftsSortBy === 'wish_rate' ? 'selected' : ''}>По рейтингу</option>
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
                <option value="date" ${state.friendGiftsSortBy === 'date' ? 'selected' : ''}>По дате</option>
                <option value="price" ${state.friendGiftsSortBy === 'price' ? 'selected' : ''}>По цене</option>
                <option value="wish_rate" ${state.friendGiftsSortBy === 'wish_rate' ? 'selected' : ''}>По рейтингу</option>
            </select>
        </div>
        <div class="gifts-grid">
            ${sortedGifts.map(gift => `
                <div class="gift-card">
                    <div class="gift-header">
                        <div class="gift-name">${escapeHtml(gift.name)}</div>
                        ${gift.wish_rate ? `<div class="gift-wish-rate">⭐ ${gift.wish_rate}/10</div>` : ''}
                    </div>
                    ${gift.url ? `<a href="${escapeHtml(gift.url)}" class="gift-url" target="_blank">🔗 Ссылка</a>` : ''}
                    ${gift.price ? `<div class="gift-price">💰 ${formatPrice(gift.price)} ₽</div>` : ''}
                    ${gift.note ? `<div class="gift-note">📝 ${escapeHtml(gift.note)}</div>` : ''}
                    <div class="gift-date">Добавлен: ${new Date(gift.created_at).toLocaleDateString('ru-RU')}</div>
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
        user_id: state.currentUser.tg_id,
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
        state.currentUser = await getCurrentUser();
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
                state.currentUser = await getCurrentUser();
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

// ============= Инициализация приложения =============
async function initApp() {
    try {
        if (!state.initData) {
            throw new Error('Откройте приложение из Telegram');
        }

        // Сначала делаем авторизацию через /users/auth/telegram
        // Этот эндпоинт создаст пользователя если его нет
        state.currentUser = await apiRequest('/users/auth/telegram', {
            method: 'POST',
            body: JSON.stringify({
                init_data: state.initData
            })
        });

        console.log('User authenticated:', state.currentUser);

        // Загружаем друзей и заявки
        state.myFriends = await getMyFriends();
        state.friendRequests = await getPendingRequests();

        // Отображаем интерфейс
        document.getElementById('loading').style.display = 'none';
        document.getElementById('main-app').style.display = 'block';

        // Рендерим профиль, друзей и заявки
        renderMyProfile();
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
