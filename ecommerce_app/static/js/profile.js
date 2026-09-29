document.addEventListener('DOMContentLoaded', async () => {
    const userId = localStorage.getItem('user_id');
    const username = localStorage.getItem('username');
    
    if (!userId || userId === '0') {
        window.location.href = '/';
        return;
    }
    
    document.getElementById('user-display').textContent = `Hi, ${username}`;
    document.getElementById('profile-greeting').textContent = `Hi, ${username}`;
    
    // Cart setup
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    const counterEl = document.getElementById('cart-counter');
    counterEl.textContent = count;
    if (count > 0) counterEl.style.display = 'flex';
    
    // Search form handler
    document.getElementById('search-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const q = document.getElementById('search-input').value.trim();
        if (q) window.location.href = `/home?q=${encodeURIComponent(q)}`;
    });

    try {
        const res = await fetch(`/api/profile/${userId}`);
        const data = await res.json();
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('profile-content').style.display = 'block';
        
        // Render Most Viewed
        if (data.most_viewed && data.most_viewed.length > 0) {
            document.getElementById('most-viewed-section').style.display = 'block';
            document.getElementById('most-viewed-carousel').innerHTML = data.most_viewed.map(p => createProductCardHTML(p, p.views + ' views')).join('');
        }
        
        // Render Past Viewed
        if (data.past_viewed && data.past_viewed.length > 0) {
            document.getElementById('past-viewed-section').style.display = 'block';
            document.getElementById('past-viewed-carousel').innerHTML = data.past_viewed.map(p => createProductCardHTML(p, 'Last viewed ' + new Date(p.last_viewed).toLocaleDateString())).join('');
        }
        
        // Render Orders
        if (data.orders && data.orders.length > 0) {
            document.getElementById('orders-section').style.display = 'block';
            document.getElementById('orders-list').innerHTML = data.orders.map(o => `
                <div style="display:flex; align-items:center; gap:20px; padding:20px; border:1px solid var(--border); border-radius:var(--radius-md); background:var(--white);">
                    <img src="${o.imgUrl}" onerror="this.src='https://via.placeholder.com/100x100?text=No+Image'" style="width:80px; height:80px; object-fit:contain; padding:8px;">
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <div style="font-size:14px; font-weight:600; color:var(--dark);">${o.title}</div>
                            ${o.order_id ? `<span style="background:var(--bg); border:1px solid var(--border); border-radius:var(--radius-pill); font-size:11px; font-weight:700; padding:2px 8px;">Order #${o.order_id}</span>` : ''}
                        </div>
                        <div style="font-size:13px; color:var(--mid);">Ordered on: ${new Date(o.timestamp || o.created_at).toLocaleString()} ${o.quantity > 1 ? `· Qty: ${o.quantity}` : ''}</div>
                        <div style="font-size:16px; font-weight:700; margin-top:8px;">₹${(parseFloat(o.price || o.price_at_purchase || 0) * (o.quantity || 1) * 83).toFixed(0)}</div>
                    </div>
                </div>
            `).join('');
        } else {
            document.getElementById('orders-section').style.display = 'block';
            document.getElementById('orders-list').innerHTML = '<p style="color:var(--mid);">You have no past orders.</p>';
        }

    } catch (err) {
        document.getElementById('loading').innerHTML = '<p style="color:red;">Error loading profile data.</p>';
        console.error(err);
    }
    
    function createProductCardHTML(p, subtitle) {
        const price = p.price ? parseFloat(p.price).toFixed(2) : '0.00';
        const imgUrl = p.imgUrl || 'https://via.placeholder.com/300x300?text=No+Image';
        
        return `
            <div class="product-card" onclick="window.location.href='/product?asin=${p.asin}'">
                <div class="product-image-wrap">
                    <img src="${imgUrl}" alt="${p.title}" class="product-image" onerror="this.src='https://via.placeholder.com/300x300?text=No+Image'">
                </div>
                <div class="product-card-body">
                    <div class="product-brand" style="color:var(--google-blue);">${subtitle}</div>
                    <div class="product-title">${p.title}</div>
                    <div class="product-price">₹${(parseFloat(price) * 83).toFixed(0)}</div>
                </div>
            </div>
        `;
    }
});
