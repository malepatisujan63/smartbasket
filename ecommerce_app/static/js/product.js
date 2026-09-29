document.addEventListener('DOMContentLoaded', () => {
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

    const urlParams = new URLSearchParams(window.location.search);
    const asin = urlParams.get('asin');
    const userId = localStorage.getItem('user_id');

    if (!asin) {
        window.location.href = '/home';
        return;
    }

    const logAction = (action) => {
        const payload = {
            user_id: parseInt(userId),
            asin: asin,
            action: action,
            search_query: '',
            view_duration: Math.floor(Math.random() * 120)
        };

        fetch('/api/log_action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            keepalive: true
        }).catch(e => console.error(e));
    };

    const loadRealReviews = async (productStars) => {
        const listEl = document.getElementById('real-reviews-list');
        const countBadge = document.getElementById('reviews-count-badge');
        try {
            const res = await fetch(`/api/reviews/${asin}`);
            const data = await res.json();
            const reviews = data.reviews || [];

            if (countBadge) {
                countBadge.textContent = `${reviews.length} ${reviews.length === 1 ? 'review' : 'reviews'}`;
            }

            if (reviews.length === 0) {
                listEl.innerHTML = `
                    <div style="padding:20px; text-align:center; color:var(--mid); background:var(--bg); border-radius:var(--radius-sm);">
                        No written reviews yet. Be the first to share your thoughts!
                    </div>
                `;
                return;
            }

            let html = '';
            reviews.forEach(r => {
                const rating = Math.round(parseFloat(r.rating) || 5);
                const starStr = '★'.repeat(rating) + '☆'.repeat(5 - rating);
                const dateStr = r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Recent';
                const uname = r.username || 'Verified Shopper';

                html += `
                    <div class="review-card" style="border-bottom:1px solid var(--border); padding:16px 0;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                            <div class="review-stars" style="color:#f59e0b; font-size:14px;">${starStr}</div>
                            <span style="font-size:12px; color:var(--light);">${dateStr}</span>
                        </div>
                        <div class="review-author" style="font-size:13px; font-weight:700; color:var(--dark); margin-bottom:4px;">${uname}</div>
                        <div class="review-text" style="font-size:13px; color:var(--mid); line-height:1.6;">${r.comment}</div>
                    </div>
                `;
            });
            listEl.innerHTML = html;
        } catch (err) {
            console.error("Failed to load reviews:", err);
            listEl.innerHTML = '<p style="color:red; font-size:12px;">Failed to load reviews.</p>';
        }
    };

    // Review Submission
    const submitReviewBtn = document.getElementById('btn-submit-review');
    if (submitReviewBtn) {
        submitReviewBtn.addEventListener('click', async () => {
            const commentInput = document.getElementById('review-comment-input');
            const ratingSelect = document.getElementById('review-rating-select');
            const comment = (commentInput ? commentInput.value : '').trim();
            const rating = parseFloat(ratingSelect ? ratingSelect.value : '5');

            if (!comment) {
                if (window.showToast) window.showToast('Please enter a review comment.', 'error');
                return;
            }

            if (!userId || userId === '0') {
                if (window.showToast) window.showToast('Please sign in to post a review.', 'error');
                return;
            }

            submitReviewBtn.disabled = true;
            submitReviewBtn.textContent = 'Submitting…';

            try {
                const res = await fetch('/api/reviews', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: parseInt(userId),
                        asin: asin,
                        rating: rating,
                        comment: comment
                    })
                });

                const data = await res.json();
                if (res.ok && data.status === 'success') {
                    if (window.showToast) window.showToast('Review submitted!', 'success');
                    if (commentInput) commentInput.value = '';
                    await loadRealReviews(5);
                } else {
                    if (window.showToast) window.showToast(data.detail || 'Could not save review.', 'error');
                }
            } catch (err) {
                console.error(err);
                if (window.showToast) window.showToast('Network error submitting review.', 'error');
            } finally {
                submitReviewBtn.disabled = false;
                submitReviewBtn.textContent = 'Submit Review';
            }
        });
    }

    loadRealReviews(p.stars);

    document.getElementById('loading').style.display = 'none';
    document.getElementById('product-container').style.display = 'flex';
                
                // Log view
                logAction('view');

                document.getElementById('btn-add-cart').onclick = (e) => {
                    logAction('cart');
                    let cart = getCart();
                    const existing = cart.find(i => i.asin === p.asin);
                    if (existing) {
                        existing.quantity++;
                    } else {
                        cart.push({ asin: p.asin, title: p.title, price: p.price, imgUrl: p.imgUrl, quantity: 1 });
                    }
                    localStorage.setItem('cart', JSON.stringify(cart));
                    if (window.syncCartToDB) window.syncCartToDB();
                    updateCartCounter();
                    e.target.textContent = 'Added to Cart ✓';
                    e.target.style.background = 'white';
                    e.target.style.color = 'var(--google-blue)';
                    e.target.style.border = '1px solid var(--google-blue)';
                    if (window.showToast) window.showToast('Item added to cart!', 'success');
                };
                
                document.getElementById('btn-buy-now').onclick = () => {
                    logAction('cart');
                    let cart = getCart();
                    const existing = cart.find(i => i.asin === p.asin);
                    if (existing) {
                        existing.quantity++;
                    } else {
                        cart.push({ asin: p.asin, title: p.title, price: p.price, imgUrl: p.imgUrl, quantity: 1 });
                    }
                    localStorage.setItem('cart', JSON.stringify(cart));
                    if (window.syncCartToDB) window.syncCartToDB();
                    window.location.href = '/checkout';
                };

            } else {
                if (window.showToast) window.showToast('Product not found', 'error');
                setTimeout(() => window.location.href = '/home', 1500);
            }
        } catch (err) {
            console.error(err);
            if (window.showToast) window.showToast('Error loading product', 'error');
        }
    };
    
    const loadRecommendations = async () => {
        try {
            const res = await fetch(`/api/recommendations/${asin}?user_id=${userId || 0}`);
            const data = await res.json();
            if (data.recommendations && data.recommendations.length > 0) {
                const grid = document.getElementById('recs-grid');
                document.getElementById('recommendations-container').style.display = 'block';
                let html = '';
                data.recommendations.forEach(r => {
                    const price = r.price ? parseFloat(r.price).toFixed(2) : '0.00';
                    html += `
                        <div class="product-card" onclick="window.location.href='/product?asin=${r.asin}'" style="cursor:pointer;">
                            <div class="product-image-wrap">
                                <img src="${r.imgUrl}" onerror="this.src='https://via.placeholder.com/300?text=No+Image'" class="product-image">
                            </div>
                            <div class="product-card-body">
                                <div class="product-title">${r.title}</div>
                                <div class="product-price">₹${(parseFloat(price) * 83).toFixed(0)}</div>
                            </div>
                        </div>
                    `;
                });
                grid.innerHTML = html;
            }
        } catch (err) {
            console.error('Failed to load recommendations', err);
        }
    };

    loadProduct().then(loadRecommendations);
});
