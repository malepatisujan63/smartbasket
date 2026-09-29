document.addEventListener('DOMContentLoaded', () => {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const userId = localStorage.getItem('user_id');

    if (cart.length === 0) {
        window.location.href = '/cart';
        return;
    }

    const itemsList = document.getElementById('checkout-items-list');
    
    let subtotal = 0;
    cart.forEach(item => {
        subtotal += (item.price * item.quantity);
        const div = document.createElement('div');
        div.className = 'checkout-item';
        div.innerHTML = `
            <span style="flex: 2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 10px;">${item.quantity}x ${item.title}</span>
            <span style="font-weight: 500;">₹${(parseFloat(item.price) * item.quantity * 83).toFixed(0)}</span>
        `;
        itemsList.appendChild(div);
    });

    const tax = subtotal * 0.08;
    const total = subtotal + tax;

    document.getElementById('chk-subtotal').textContent = `₹${(subtotal * 83).toFixed(0)}`;
    document.getElementById('chk-tax').textContent = `₹${(tax * 83).toFixed(0)}`;
    document.getElementById('chk-total').textContent = `₹${(total * 83).toFixed(0)}`;

    const logPurchase = async (asin) => {
        const payload = {
            user_id: parseInt(userId),
            asin: asin,
            action: 'purchase',
            search_query: '',
            view_duration: 0
        };

        return fetch('/api/log_action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).catch(e => console.error(e));
    };

    document.getElementById('checkout-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing Order…';
        }

        const payload = {
            user_id: parseInt(userId || '0'),
            full_name: document.getElementById('ship-name').value.trim(),
            address: document.getElementById('ship-address').value.trim(),
            city: document.getElementById('ship-city').value.trim(),
            zip_code: document.getElementById('ship-zip').value.trim(),
            items: cart.map(item => ({ asin: item.asin, quantity: item.quantity }))
        };

        try {
            const res = await fetch('/api/checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok && data.status === 'success') {
                // Set Order ID in modal
                const orderIdEl = document.getElementById('order-id-display');
                if (orderIdEl) orderIdEl.textContent = `Order #${data.order_id} (Total: ₹${(data.total_amount * 83).toFixed(0)})`;

                // Clear Cart in localStorage and Database
                localStorage.removeItem('cart');
                if (window.syncCartToDB) window.syncCartToDB();

                // Show Success Modal
                document.getElementById('success-modal').style.display = 'flex';
            } else {
                alert(data.detail || 'Could not process order. Please try again.');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Place Order';
                }
            }
        } catch (err) {
            console.error('Checkout error:', err);
            alert('Network error placing order.');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Place Order';
            }
        }
    });
});
