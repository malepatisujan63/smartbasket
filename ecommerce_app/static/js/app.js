
window.syncCartToDB = function() {
    const userId = localStorage.getItem('user_id');
    if (!userId || userId == 0) return;
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    fetch('/api/cart_sync/' + userId, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ cart: cart.map(item => ({asin: item.asin, quantity: item.quantity})) })
    }).catch(e => console.error('Cart sync failed', e));
};

document.addEventListener('DOMContentLoaded', () => {
    // --- Utility: Toast Notifications ---
    window.showToast = (message, type = 'success') => {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        // Icon logic
        let icon = '✓';
        if (type === 'error') icon = '✕';
        else if (type === 'info') icon = 'ℹ';
        
        toast.innerHTML = `<div style="font-size: 1.2rem; font-weight: bold;">${icon}</div><div>${message}</div>`;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    };

    // --- Utility: Cart Logic ---
    const getCart = () => {
        return JSON.parse(localStorage.getItem('cart') || '[]');
    };
    const updateCartCounter = () => {
        const counter = document.getElementById('cart-counter');
        const cart = getCart();
        if (counter) counter.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);
    };
    updateCartCounter();

    // Go to cart page on click
    document.querySelectorAll('.cart-icon').forEach(icon => {
        icon.style.cursor = 'pointer';
        icon.addEventListener('click', () => window.location.href = '/cart');
    });

    // --- Login Page Logic ---
    const loginForm = document.getElementById('auth-form');
    if (loginForm) {
        const btnLogin    = document.getElementById('btn-login');
        const btnRegister = document.getElementById('btn-register');
        const errorMsg    = document.getElementById('error-msg');

        const showError = (msg) => {
            errorMsg.textContent = msg;
            errorMsg.style.display = 'block';
            errorMsg.style.color = '#c44444';
            errorMsg.style.fontSize = '13px';
            errorMsg.style.marginTop = '12px';
            errorMsg.style.fontWeight = '500';
        };

        const handleAuth = async (endpoint) => {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;

            if (!username) { showError('Please enter a username.'); return; }
            if (!password) { showError('Please enter a password.'); return; }

            // Disable buttons during request
            btnLogin.disabled = true;
            btnRegister.disabled = true;
            btnLogin.textContent = 'Please wait...';

            try {
                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();

                if (data.status === 'success') {
                    localStorage.setItem('user_id', data.user_id);
                    localStorage.setItem('username', data.username);
                    if (data.is_admin === 1 || data.is_admin === true) {
                        window.location.href = '/admin';
                    } else {
                        window.location.href = '/home';
                    }
                } else {
                    // FastAPI error: {detail: "..."}  or our: {message: "..."}
                    showError(data.detail || data.message || 'Authentication failed.');
                    btnLogin.disabled = false;
                    btnRegister.disabled = false;
                    btnLogin.textContent = 'Sign In';
                }
            } catch (err) {
                console.error('Auth error:', err);
                showError('Network error — please try again.');
                btnLogin.disabled = false;
                btnRegister.disabled = false;
                btnLogin.textContent = 'Sign In';
            }
        };

        // Form submit (Enter key) → always login
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleAuth('/api/login');
        });

        // Register button (explicit click only)
        btnRegister.addEventListener('click', (e) => {
            e.preventDefault();
            handleAuth('/api/register');
        });
    }

    // --- Home Page Logic ---
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        const userId = localStorage.getItem('user_id');
        const username = localStorage.getItem('username');
        
        if (!userId) {
            window.location.href = '/';
            return;
        }

        document.getElementById('user-display').textContent = `Hi, ${username}`;

        let currentSearchQuery = '';

        const logAction = (asin, action) => {
            // Cart/purchase: fire immediately (important user action)
            if (action !== 'view') {
                fetch('/api/log_action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: parseInt(userId), asin, action,
                        search_query: currentSearchQuery,
                        view_duration: Math.floor(Math.random() * 60) }),
                    keepalive: true
                }).catch(() => {});
                return;
            }
            // View: batch and send max once per 3 seconds
            if (!logAction._queue) logAction._queue = [];
            if (!logAction._queue.includes(asin)) logAction._queue.push(asin);
            clearTimeout(logAction._timer);
            logAction._timer = setTimeout(() => {
                const batch = logAction._queue.splice(0);
                batch.forEach(a => {
                    fetch('/api/log_action', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: parseInt(userId), asin: a, action: 'view',
                            search_query: currentSearchQuery, view_duration: 5 }),
                        keepalive: true
                    }).catch(() => {});
                });
            }, 3000);
        };

        // No category dropdown exists on the home page — removed fetchCategories() to avoid null ref.

        // --- Render Product Card (reference theme: circular image + qty + ADD TO CART pill) ---
        const createProductCard = (p, delayIndex=0) => {
            const card = document.createElement('div');
            card.className = 'product-card fade-in-up';
            card.style.animationDelay = `${delayIndex * 0.05}s`;

            const price  = p.price  ? parseFloat(p.price).toFixed(2)  : '0.00';
            const stars  = p.stars  ? parseFloat(p.stars).toFixed(1)  : '0.0';
            const mlBadge = p.ml_score !== undefined
                ? `<span class="ml-score-badge">ML ${(p.ml_score*100).toFixed(0)}%</span>`
                : '';

            // Circular image wrapper
            card.innerHTML = `
                <div class="product-image-wrap" data-goto="${p.asin}">
                    <img src="${p.imgUrl}" alt="${p.title}" class="product-image"
                         onerror="this.src='https://via.placeholder.com/300x300?text=No+Image'">
                </div>
                <div class="product-card-body">
                    <div class="product-brand">★ ${stars}</div>
                    <div class="product-title" data-goto="${p.asin}">${p.title}</div>
                    <div class="product-price">₹${(parseFloat(price) * 83).toFixed(0)}</div>
                    ${mlBadge}
                    <div class="card-actions">
                        <div class="qty-wrap">
                            <button class="qty-btn" data-action="dec">−</button>
                            <span class="qty-num">1</span>
                            <button class="qty-btn" data-action="inc">+</button>
                        </div>
                        <button class="btn-cart">Add to Cart</button>
                    </div>
                </div>
            `;

            // Log view in batched mode (fires once per 3s max)
            logAction(p.asin, 'view');

            // Qty controls
            let qty = 1;
            const qtyEl  = card.querySelector('.qty-num');
            card.querySelector('[data-action="inc"]').addEventListener('click', (e) => {
                e.stopPropagation(); qty++; qtyEl.textContent = qty;
            });
            card.querySelector('[data-action="dec"]').addEventListener('click', (e) => {
                e.stopPropagation(); if (qty > 1) { qty--; qtyEl.textContent = qty; }
            });

            // Add to Cart
            card.querySelector('.btn-cart').addEventListener('click', (e) => {
                e.stopPropagation();
                logAction(p.asin, 'cart');
                let cartData = getCart();
                const existing = cartData.find(i => i.asin === p.asin);
                if (existing) {
                    existing.quantity += qty;
                } else {
                    cartData.push({ asin: p.asin, title: p.title, price: parseFloat(p.price) || 0, imgUrl: p.imgUrl, quantity: qty });
                }
                localStorage.setItem('cart', JSON.stringify(cartData)); window.syncCartToDB();
                updateCartCounter();
                e.target.textContent = 'Added ✓';
                setTimeout(() => { e.target.textContent = 'Add to Cart'; }, 1800);
                if (window.showToast) window.showToast(`${qty > 1 ? qty + 'x ' : ''}Added to cart!`, 'success');
            });

            // Click image/title → go to product page
            card.querySelectorAll('[data-goto]').forEach(el => {
                el.addEventListener('click', () => {
                    window.location.href = `/product?asin=${p.asin}`;
                });
                el.style.cursor = 'pointer';
            });

            return card;
        };

        // --- Load Home Feed ---
        const loadHomeFeed = async () => {
            const container = document.getElementById('dynamic-content');
            // Show Skeleton Loaders
            container.innerHTML = `
                <div class="feed-section">
                    <h3 class="feed-title skeleton skeleton-title"></h3>
                    <div class="product-carousel">
                        <div class="skeleton skeleton-card"></div>
                        <div class="skeleton skeleton-card"></div>
                        <div class="skeleton skeleton-card"></div>
                        <div class="skeleton skeleton-card"></div>
                    </div>
                </div>
            `;
            
            try {
                const res = await fetch(`/api/home_feed?user_id=${userId}`);
                const data = await res.json();
                
                container.innerHTML = ''; // Clear skeletons
                
                data.sections.forEach((section, index) => {
                    if(section.products.length === 0) return;
                    
                    const sectionDiv = document.createElement('div');
                    sectionDiv.className = 'feed-section';
                    
                    const title = document.createElement('h3');
                    title.className = 'feed-title';
                    title.textContent = section.title;
                    if(section.title.includes("Top Picks")) {
                        title.innerHTML = `✨ ${section.title} <span style="font-size:12px; color:var(--google-green); font-weight:normal;">(Powered by your ML Model)</span>`;
                    }
                    
                    const carouselContainer = document.createElement('div');
                    carouselContainer.className = 'carousel-container';
                    
                    const prevBtn = document.createElement('div');
                    prevBtn.className = 'carousel-btn prev';
                    prevBtn.innerHTML = '❮';
                    
                    const nextBtn = document.createElement('div');
                    nextBtn.className = 'carousel-btn next';
                    nextBtn.innerHTML = '❯';
                    
                    const carousel = document.createElement('div');
                    carousel.className = 'product-carousel';
                    carousel.id = `carousel-${index}`;
                    
                    section.products.forEach((p, pIndex) => {
                        carousel.appendChild(createProductCard(p, pIndex));
                    });
                    
                    // Scrolling logic
                    prevBtn.onclick = () => carousel.scrollBy({left: -600, behavior: 'smooth'});
                    nextBtn.onclick = () => carousel.scrollBy({left: 600, behavior: 'smooth'});
                    
                    carouselContainer.appendChild(prevBtn);
                    carouselContainer.appendChild(carousel);
                    carouselContainer.appendChild(nextBtn);
                    
                    sectionDiv.appendChild(title);
                    sectionDiv.appendChild(carouselContainer);
                    container.appendChild(sectionDiv);
                });
            } catch (err) {
                console.error(err);
                window.showToast('Failed to load personalized feed', 'error');
            }
        };

        // --- Load Search Results ---
        const doSearch = async (query) => {
            currentSearchQuery = query;
            const isSmart = document.getElementById('smart-toggle').checked;
            
            const container = document.getElementById('dynamic-content');
            document.getElementById('hero-banner').style.display = 'none'; // Hide hero on search
            
            // Show skeletons
            container.innerHTML = `
                <div class="feed-section">
                    <h3 class="feed-title">Searching...</h3>
                    <div class="product-grid">
                        <div class="skeleton skeleton-card"></div>
                        <div class="skeleton skeleton-card"></div>
                        <div class="skeleton skeleton-card"></div>
                    </div>
                </div>
            `;
            
            try {
                // Determine API endpoint based on Smart Toggle
                let endpoint = `/api/search?q=${encodeURIComponent(query)}&user_id=${userId}&smart_recommendation=false`;
                if (isSmart) {
                    endpoint = `/api/semantic_search?q=${encodeURIComponent(query)}`;
                }
                
                const res = await fetch(endpoint);
                const data = await res.json();
                
                container.innerHTML = '<div class="feed-section"><h3 class="feed-title">Search Results</h3><div class="product-grid" id="search-grid"></div></div>';
                const grid = document.getElementById('search-grid');
                
                if (!data.results || data.results.length === 0) {
                    grid.innerHTML = '<h3 style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No products found.</h3>';
                    return;
                }

                data.results.forEach((p, index) => {
                    grid.appendChild(createProductCard(p, index));
                });
            } catch (err) {
                console.error(err);
                window.showToast('Search failed.', 'error');
            }
        };

        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const q = document.getElementById('search-input').value.trim();
            if (q) {
                doSearch(q);
            } else {
                // Reset: show hero banner and home feed
                const heroBanner = document.getElementById('hero-banner');
                if (heroBanner) heroBanner.style.display = 'grid';
                loadHomeFeed();
            }
        });

        document.getElementById('smart-toggle').addEventListener('change', () => {
            const q = document.getElementById('search-input').value;
            if (q) doSearch(q);
        });

        // Initialize Home Feed or auto-trigger search from URL ?q= param
        const urlParams = new URLSearchParams(window.location.search);
        const urlQuery = urlParams.get('q');
        if (urlQuery) {
            document.getElementById('search-input').value = urlQuery;
            document.getElementById('hero-banner').style.display = 'none';
            doSearch(urlQuery);
        } else {
            loadHomeFeed();
        }
    }
});
