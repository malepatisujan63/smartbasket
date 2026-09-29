document.addEventListener('DOMContentLoaded', () => {
    const cartList = document.getElementById('cart-list');
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');

    const renderCart = () => {
        // Update count label
        const countEl = document.getElementById('cart-item-count');
        const totalQty = cart.reduce((s, i) => s + i.quantity, 0);
        if (countEl) countEl.textContent = totalQty;

        cartList.innerHTML = '';

        if (cart.length === 0) {
            cartList.innerHTML = `
                <div class="empty-cart">
                    <h2>Your cart is empty</h2>
                    <p style="margin-bottom:24px;">Looks like you haven't added anything yet.</p>
                    <button class="btn btn-primary" onclick="window.location.href='/home'" style="width:auto; padding:12px 28px;">
                        Start Shopping →
                    </button>
                </div>`;
            const btn = document.getElementById('btn-checkout');
            if (btn) { btn.disabled = true; btn.style.opacity = '0.4'; }
        } else {
            const btn = document.getElementById('btn-checkout');
            if (btn) { btn.disabled = false; btn.style.opacity = '1'; }

            cart.forEach((item, index) => {
                const div = document.createElement('div');
                div.className = 'cart-item';
                div.innerHTML = `
                    <img src="${item.imgUrl}" alt="${item.title}" class="item-img"
                         onerror="this.src='https://via.placeholder.com/90?text=No+Image'">
                    <div class="item-details">
                        <div class="item-title">${item.title}</div>
                        <div class="item-price">₹${(parseFloat(item.price) * 83).toFixed(0)}</div>
                        <div class="qty-controls">
                            <button class="qty-btn" onclick="updateQty(${index}, -1)">−</button>
                            <span class="qty-num">${item.quantity}</span>
                            <button class="qty-btn" onclick="updateQty(${index}, 1)">+</button>
                            <span class="item-remove" onclick="removeItem(${index})">Remove</span>
                        </div>
                    </div>
                    <div class="item-total">₹${(parseFloat(item.price) * item.quantity * 83).toFixed(0)}</div>
                `;
                cartList.appendChild(div);
            });
        }
        updateTotals();
    };

    window.updateQty = (index, delta) => {
        cart[index].quantity += delta;
        if (cart[index].quantity <= 0) cart.splice(index, 1);
        localStorage.setItem('cart', JSON.stringify(cart)); if(window.syncCartToDB) window.syncCartToDB();
        renderCart();
    };

    window.removeItem = (index) => {
        cart.splice(index, 1);
        localStorage.setItem('cart', JSON.stringify(cart)); if(window.syncCartToDB) window.syncCartToDB();
        renderCart();
    };

    const updateTotals = () => {
        const qty      = cart.reduce((s, i) => s + i.quantity, 0);
        const subtotal = cart.reduce((s, i) => s + (i.price * i.quantity), 0);
        const tax      = subtotal * 0.08;
        const total    = subtotal + tax;

        document.getElementById('sum-qty').textContent      = qty;
        document.getElementById('sum-subtotal').textContent = `₹${(subtotal * 83).toFixed(0)}`;
        document.getElementById('sum-tax').textContent      = `₹${(tax * 83).toFixed(0)}`;
        document.getElementById('sum-total').textContent    = `₹${(total * 83).toFixed(0)}`;
    };

    document.getElementById('btn-checkout').addEventListener('click', () => {
        window.location.href = '/checkout';
    });

    renderCart();
});
