import os, re
js_dir = r'd:\3rd sem created files\AIML PROJECT\ecommerce_app\static\js'

for f in os.listdir(js_dir):
    if not f.endswith('.js'): continue
    path = os.path.join(js_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Let's restore the template variables that were wiped out
    # 1. <div class="product-price">$$₹</div> -> <div class="product-price">₹${(parseFloat(price) * 83).toFixed(0)}</div>
    content = content.replace('<div class="product-price">$$₹</div>', '<div class="product-price">₹${(parseFloat(price) * 83).toFixed(0)}</div>')
    content = content.replace('<div class="product-price">$$?</div>', '<div class="product-price">₹${(parseFloat(price) * 83).toFixed(0)}</div>')
    
    # 2. <div class="item-price">$$₹</div> -> <div class="item-price">₹${(parseFloat(item.price) * 83).toFixed(0)}</div>
    content = content.replace('<div class="item-price">$$₹</div>', '<div class="item-price">₹${(parseFloat(item.price) * 83).toFixed(0)}</div>')
    content = content.replace('<div class="item-price">$$?</div>', '<div class="item-price">₹${(parseFloat(item.price) * 83).toFixed(0)}</div>')
    
    # 3. <div class="item-total">$$₹</div> -> <div class="item-total">₹${(parseFloat(item.price) * item.quantity * 83).toFixed(0)}</div>
    content = content.replace('<div class="item-total">$$₹</div>', '<div class="item-total">₹${(parseFloat(item.price) * item.quantity * 83).toFixed(0)}</div>')
    content = content.replace('<div class="item-total">$$?</div>', '<div class="item-total">₹${(parseFloat(item.price) * item.quantity * 83).toFixed(0)}</div>')
    
    # 4. sum-subtotal, sum-tax, sum-total
    content = content.replace('`$$₹`', '`₹${(subtotal * 83).toFixed(0)}`', 1) if 'sum-subtotal' in content else content
    content = content.replace('`$$?`', '`₹${(subtotal * 83).toFixed(0)}`', 1) if 'sum-subtotal' in content else content
    
    content = content.replace('`$$₹`', '`₹${(tax * 83).toFixed(0)}`', 1) if 'sum-tax' in content else content
    content = content.replace('`$$?`', '`₹${(tax * 83).toFixed(0)}`', 1) if 'sum-tax' in content else content
    
    content = content.replace('`$$₹`', '`₹${(total * 83).toFixed(0)}`', 1) if 'sum-total' in content else content
    content = content.replace('`$$?`', '`₹${(total * 83).toFixed(0)}`', 1) if 'sum-total' in content else content
    
    # checkout.js
    content = content.replace('<span style="font-weight: 500;">$$₹</span>', '<span style="font-weight: 500;">₹${(parseFloat(item.price) * item.quantity * 83).toFixed(0)}</span>')
    content = content.replace('<span style="font-weight: 500;">$$?</span>', '<span style="font-weight: 500;">₹${(parseFloat(item.price) * item.quantity * 83).toFixed(0)}</span>')
    
    if 'chk-subtotal' in content:
        content = content.replace('`$$₹`', '`₹${(subtotal * 83).toFixed(0)}`', 1)
        content = content.replace('`$$?`', '`₹${(subtotal * 83).toFixed(0)}`', 1)
        
    if 'chk-tax' in content:
        content = content.replace('`$$₹`', '`₹${(tax * 83).toFixed(0)}`', 1)
        content = content.replace('`$$?`', '`₹${(tax * 83).toFixed(0)}`', 1)
        
    if 'chk-total' in content:
        content = content.replace('`$$₹`', '`₹${(total * 83).toFixed(0)}`', 1)
        content = content.replace('`$$?`', '`₹${(total * 83).toFixed(0)}`', 1)
        
    # product.js
    content = content.replace('document.getElementById(\'p-price\').textContent = `₹`;', 'document.getElementById(\'p-price\').textContent = `₹${p.price ? (parseFloat(p.price) * 83).toFixed(0) : \'0\'}`;')
    content = content.replace('document.getElementById(\'p-price\').textContent = `?`;', 'document.getElementById(\'p-price\').textContent = `₹${p.price ? (parseFloat(p.price) * 83).toFixed(0) : \'0\'}`;')
    
    # And to be completely safe against anything else:
    # Look for any untouched USD:
    content = content.replace(r'$${price}', r'₹${(parseFloat(price) * 83).toFixed(0)}')
    content = content.replace(r'$${item.price.toFixed(2)}', r'₹${(parseFloat(item.price) * 83).toFixed(0)}')
    content = content.replace(r'$${(item.price * item.quantity).toFixed(2)}', r'₹${(parseFloat(item.price) * item.quantity * 83).toFixed(0)}')
    content = content.replace(r'$${subtotal.toFixed(2)}', r'₹${(subtotal * 83).toFixed(0)}')
    content = content.replace(r'$${tax.toFixed(2)}', r'₹${(tax * 83).toFixed(0)}')
    content = content.replace(r'$${total.toFixed(2)}', r'₹${(total * 83).toFixed(0)}')
    content = content.replace(r'$${p.price ? parseFloat(p.price).toFixed(2) : \'0.00\'}', r'₹${p.price ? (parseFloat(p.price) * 83).toFixed(0) : \'0\'}')

    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

print("JS fixes applied.")
