import random
import datetime
import time
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from models.models import (
    User, Retailer, Category, Brand, Product, Inventory, Order, OrderItem,
    Cart, Wishlist, Review, Coupon, Address, SalesHistory,
    Recommendation, CustomerAnalytics, Notification, AnalyticsEvent
)
from utils.security import get_password_hash

def run_production_seed_factory(db: Session):
    """
    Massive Enterprise Production Database Seed Factory for Amazon-AI.
    Generates:
    - 20 Major Categories (1,000 products per category = 20,000+ total products)
    - 400+ Unique Brands
    - 400+ Retailers (each managing approx 50 products)
    - 50,000+ Customers
    - 250,000+ Product Reviews
    - 1,000,000+ Order Records & Order Items
    - 2,000,000+ Analytics Events
    """
    start_time = time.time()
    print("\n" + "="*80)
    print(" [AMAZON-AI ENTERPRISE FACTORY] BOOTSTRAPPING MASSIVE PRODUCTION DATABASE")
    print("Scale: 20,000+ Products | 400+ Brands | 400+ Retailers | 50,000+ Customers")
    print("       250,000+ Reviews | 1,000,000+ Orders | 2,000,000+ Analytics Events")
    print("="*80 + "\n")

    # 1. CATEGORIES (20 Major Categories)
    print(" [1/8] Generating 20 Major Product Categories & Subcategories...")
    categories_data = [
        {"name": "Electronics", "slug": "electronics", "icon": "Laptop", "description": "Laptops, Tablets, Monitors, Hubs & Office Tech"},
        {"name": "Laptops & Ultrabooks", "slug": "laptops", "icon": "Laptop", "description": "High-Performance AI Workstations, Ultrabooks & Business Books"},
        {"name": "Mobiles & 5G Smartphones", "slug": "mobiles", "icon": "Smartphone", "description": "Flagship 5G Phones, Foldables, Cases & MagSafe Power Banks"},
        {"name": "Smart Watches & Wearables", "slug": "smart-watches", "icon": "Watch", "description": "GPS Fitness Trackers, Health Monitors & Luxury Smartbands"},
        {"name": "Gaming Consoles & VR", "slug": "gaming", "icon": "Gamepad2", "description": "Next-Gen Consoles, VR Headsets, Mechanical Keyboards & Mice"},
        {"name": "Audio & Headphones", "slug": "audio", "icon": "Headphones", "description": "Noise-Cancelling Headphones, Audiophile Earbuds & Soundbars"},
        {"name": "Televisions & Home Theater", "slug": "televisions", "icon": "Tv", "description": "4K/8K OLED TVs, Laser Projectors & Dolby Atmos Systems"},
        {"name": "Home Appliances", "slug": "home-appliances", "icon": "Home", "description": "Smart Vacuums, Air Purifiers, Washers & Robot Sweepers"},
        {"name": "Modern Furniture & Decor", "slug": "furniture", "icon": "Armchair", "description": "Ergonomic Office Chairs, Standing Desks & Minimalist Sofas"},
        {"name": "Kitchen & Dining", "slug": "kitchen", "icon": "Utensils", "description": "Pro Air Fryers, Espresso Machines, Blender Stations & Cookware"},
        {"name": "Fashion & Luxury Apparel", "slug": "fashion", "icon": "Shirt", "description": "Designer Coats, Cashmere Sweaters, Watches & Tailored Suits"},
        {"name": "Shoes & Footwear", "slug": "shoes", "icon": "Footprints", "description": "Carbon-Plated Running Shoes, Sneakers, Boots & Formal Footwear"},
        {"name": "Sports & Outdoors", "slug": "sports", "icon": "Dumbbell", "description": "Camping Tents, Kayaks, Golf Clubs & Cycling Gear"},
        {"name": "Fitness & Training", "slug": "fitness", "icon": "Activity", "description": "Smart Treadmills, Adjustable Dumbbells, Resistance Bands & Yoga"},
        {"name": "Books & Audible", "slug": "books", "icon": "BookOpen", "description": "Tech Bestsellers, AI Treatises, Sci-Fi Epics & Audiobooks"},
        {"name": "Office & Workplace Tech", "slug": "office", "icon": "Briefcase", "description": "4K Webcams, Studio Mics, Ergonomic Mice & Desk Organizers"},
        {"name": "Beauty & Personal Care", "slug": "beauty", "icon": "Sparkles", "description": "Skincare Serums, Sonic Toothbrushes, Fragrances & Hair styling"},
        {"name": "Health & Wellness", "slug": "health", "icon": "HeartPulse", "description": "Smart Scales, Massage Guns, Vitamins & Sleep Trackers"},
        {"name": "Automotive & EV Tech", "slug": "automotive", "icon": "Car", "description": "EV Chargers, 4K Dash Cams, Tire Inflators & Car Diagnostics"},
        {"name": "Toys & STEM Robotics", "slug": "toys", "icon": "Bot", "description": "Programmable STEM Robots, Drone Kits, Lego Sets & Board Games"}
    ]
    
    cat_objs = []
    for c in categories_data:
        cat = Category(**c)
        db.add(cat)
        cat_objs.append(cat)
    db.flush()

    # 2. BRANDS (400+ Unique Brands)
    print("  [2/8] Generating 400+ Unique Global Brands...")
    base_brands = [
        "Apple", "Samsung", "Sony", "Bose", "Nike", "Adidas", "Dyson", "Dell", "Asus", "Lenovo",
        "HP", "LG", "Microsoft", "Google", "OnePlus", "Xiaomi", "Garmin", "Razer", "Corsair", "Logitech",
        "Canon", "Nikon", "GoPro", "DJI", "Philips", "KitchenAid", "Ninja", "Breville", "Ikea", "Herman Miller",
        "Steelcase", "Zara", "H&M", "Levi's", "Under Armour", "Puma", "Reebok", "Lululemon", "Columbia", "North Face",
        "Patagonia", "Timberland", "Vans", "Converse", "ASICS", "Brooks", "New Balance", "Sennheiser", "Audio-Technica", "JBL"
    ]
    prefixes = ["Aura", "Velo", "Quant", "Zenith", "Novus", "Apex", "Lumi", "Evo", "Strata", "Nexus", "Omi", "Hyper", "Titan", "Vang", "Viper", "Ecl", "Sola", "Vert", "Pulse", "Cogni", "Aero", "Bio", "Orion", "Helio", "Chrono", "Atlas", "Kine", "Magna", "Echo", "Synth", "Aeth", "Pyra", "Prism", "Opti", "Spec", "Vort", "Mira", "Infi", "Hori", "Pinn"]
    suffixes = ["Tech", "Labs", "Audio", "Systems", "Design", "Living", "Sports", "Apparel", "Dynamics", "Global", "Direct", "Pro", "Max", "Prime", "Core", "Gear", "Works", "Craft", "Zone", "Plus"]
    
    brand_names = list(base_brands)
    while len(brand_names) < 420:
        p = random.choice(prefixes)
        s = random.choice(suffixes)
        name = f"{p}{s}" if random.random() > 0.3 else f"{p} {s}"
        if name not in brand_names:
            brand_names.append(name)
            
    brand_objs = []
    for idx, bname in enumerate(brand_names[:420]):
        slug = bname.lower().replace(" ", "-").replace("'", "")
        brand = Brand(name=bname, slug=slug, description=f"Global premier innovator in {bname} precision engineering and lifestyle design.")
        db.add(brand)
        brand_objs.append(brand)
    db.flush()

    # 3. RETAILERS (400+ Retailers)
    print(" [3/8] Generating 400+ Verified Retailer Accounts...")
    ret_prefixes = ["Amazon-AI Direct", "Apex Retail", "Global Gadgets", "Nordic Home", "Elite Fashion", "Sporting Goods", "Digital World", "Future Tech", "Prime Logistics", "Velocity Store", "Zenith Traders", "Optima Goods", "Pinnacle Market", "Hyperion Retail", "Vanguard Store", "Solaria Direct", "Chronos Emporium", "Atlas Commerce", "Echo Supplies", "Aether Retail"]
    ret_cities = ["Seattle, WA", "San Francisco, CA", "New York, NY", "Austin, TX", "Chicago, IL", "Boston, MA", "Los Angeles, CA", "Miami, FL", "Denver, CO", "Atlanta, GA"]
    
    retailer_objs = []
    for i in range(400):
        rname = f"{random.choice(ret_prefixes)} Hub #{i+1}"
        rslug = f"retailer-{i+1}-{rname.lower().replace(' ', '-').replace('#', '')}"
        ret = Retailer(
            store_name=rname,
            store_slug=rslug,
            store_logo="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=250&q=80",
            store_banner="https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=1200&q=80",
            business_description=f"Authorized global distributor and seller of premium merchandise. Offering verified products with Amazon-AI Prime guarantee.",
            verified_badge=True,
            rating=round(random.uniform(4.6, 5.0), 1),
            location=random.choice(ret_cities),
            followers_count=random.randint(500, 50000),
            years_of_selling=random.randint(2, 15),
            contact_email=f"support@{rslug}.com",
            contact_phone=f"+1 (555) {random.randint(100,999)}-{random.randint(1000,9999)}",
            total_sales=random.randint(1000, 80000),
            revenue=round(random.uniform(100000.0, 5000000.0), 2)
        )
        db.add(ret)
        retailer_objs.append(ret)
    db.flush()

    # 4. PRODUCTS (20,000+ Unique Products -> exactly 1,000 per category)
    print(" [4/8] Generating 20,000+ Unique Products (1,000 per category, zero duplicates)...")
    
    # Pre-define rich vocabulary arrays for combinatorial uniqueness
    adjectives = ["Ultra-Fast", "Quantum", "Pro-Grade", "Titanium", "Ergonomic", "Intelligent", "Wireless", "Next-Gen", "High-Fidelity", "Precision", "Stealth", "Cyber", "Aero", "Hyper", "Supreme", "Flagship", "Extreme", "Tactical", "Dynamic", "Elite"]
    materials = ["Aerospace Aluminum", "Carbon Fiber", "Recycled Polymer", "Anodized Titanium", "Gorilla Glass Armor", "Premium Mesh", "Organic Cotton & Silk", "Stainless Steel", "Ballistic Nylon", "Ceramic Shield"]
    colors = [["Space Black", "Silver", "Titanium Gray"], ["Midnight Blue", "Starlight White", "Rose Gold"], ["Emerald Green", "Obsidian Black", "Frost White"], ["Crimson Red", "Gunmetal Gray", "Solar Yellow"], ["Slate Gray", "Arctic White", "Deep Violet"]]
    storage_opts = [["256GB NVMe", "512GB NVMe", "1TB NVMe"], ["128GB", "256GB", "512GB"], ["8GB RAM / 512GB SSD", "16GB RAM / 1TB SSD", "32GB RAM / 2TB SSD"], ["Standard Edition", "Pro Edition", "Collector Edition"]]
    size_opts = [["S", "M", "L", "XL"], ["13-inch", "15-inch", "16-inch"], ["Standard", "Large", "Extra Large"], ["One Size Fits All", "Custom Fit"]]
    
    cat_specs_templates = {
        "Electronics": {"Processor": "Neural ML Core Gen 4", "Connectivity": "Wi-Fi 7 & Bluetooth 5.4", "Power": "100W USB-C PD", "Efficiency": "A++ Rated"},
        "Laptops & Ultrabooks": {"CPU": "16-Core AI Silicon", "GPU": "32-Core Tensor Graphics", "RAM": "32GB Unified DDR5", "Display": "16-inch Liquid Retina OLED (120Hz)"},
        "Mobiles & 5G Smartphones": {"Display": "6.8-inch Dynamic AMOLED 2X", "Camera": "200MP Main + 50MP Periscope Telephoto", "Battery": "5000mAh with 65W Fast Charge", "OS": "AI OS 18"},
        "Smart Watches & Wearables": {"Sensors": "ECG, SpO2, Skin Temp & Continuous HR", "Battery Life": "Up to 14 Days Ultra Mode", "Water Resistance": "10 ATM / 100M Dive Rated", "Case": "Grade 5 Titanium"},
        "Gaming Consoles & VR": {"Resolution": "4K 120FPS / 8K HDR Support", "Storage": "2TB NVMe Gen4 SSD", "Controller": "Haptic Feedback & Adaptive Triggers", "Audio": "3D Spatial Tempest Audio"},
        "Audio & Headphones": {"Noise Cancellation": "Dual Noise Sensor with 8 AI Mics", "Drivers": "40mm Custom Neodymium Drivers", "Codec": "LDAC, aptX HD & Lossless Spatial", "Battery": "45 Hours Continuous Playback"},
        "Televisions & Home Theater": {"Panel": "4K OLED EVO with Micro-Lens Array", "Refresh Rate": "144Hz VRR ProMotion", "HDR": "Dolby Vision IQ & HDR10+ Adaptive", "Sound": "2.1.2ch Dolby Atmos Built-in"},
        "Home Appliances": {"Suction/Power": "250 AW Air Watts / 1800W Motor", "Filtration": "5-Stage HEPA 99.999% Particle Trap", "Smart Control": "Voice Assist & IoT App Integration", "Noise Level": "Ultra-Quiet < 52 dB"},
        "Modern Furniture & Decor": {"Ergonomics": "3D Dynamic Lumbar & 4D Armrests", "Weight Limit": "350 lbs Reinforced Frame", "Material": "Breathable Elastomeric Mesh & Alloy", "Warranty": "10-Year Comprehensive Warranty"},
        "Kitchen & Dining": {"Capacity": "8-Quart Family Size / 15-Bar Pressure", "Modes": "12-in-1 Smart Cooking Presets", "Heating": "360° True Surround Convection", "Cleaning": "100% Dishwasher Safe Parts"},
        "Fashion & Luxury Apparel": {"Fabric": "100% Organic Merino Wool & Silk Blend", "Weave": "4-Way Stretch Weatherproof Tailoring", "Care": "Dry Clean Recommended / Wrinkle-Free", "Origin": "Handcrafted in Milan / Artisan Studio"},
        "Shoes & Footwear": {"Midsole": "Supercritical Nitrogen-Infused Foam", "Plate": "Full-Length Carbon Fiber Propulsion", "Upper": "Seamless Adaptive Primeknit Mesh", "Outsole": "Continental High-Traction Rubber"},
        "Sports & Outdoors": {"Durability": "IP68 Weatherproof & UV Protected", "Weight": "Ultra-Lightweight 1.2 kg Portable", "Material": "Ripstop 210D Nylon & Aircraft Aluminum", "Setup": "60-Second Instant Pop-Up Assembly"},
        "Fitness & Training": {"Resistance": "Digital Magnetic 0-100 Micro-Levels", "Display": "22-inch HD Interactive Touchscreen", "Metrics": "Real-Time Power, Cadence & Heart Rate", "Max Load": "400 lbs Commercial Gym Grade"},
        "Books & Audible": {"Format": "Hardcover Collector's Edition & Audiobook", "Pages/Duration": "512 Pages / 18 Hours 45 Min Narration", "Author": "Dr. Aris Thorne & DeepMind ML Fellows", "Publisher": "Amazon-AI Press & Global Science"},
        "Office & Workplace Tech": {"Sensor": "32,000 DPI Optical Precision Sensor", "Connectivity": "Tri-Mode (2.4GHz Wireless, BT, USB-C)", "Switches": "100M Click Optical-Mechanical Switches", "Ergonomics": "20-Degree Natural Hand Sculpting"},
        "Beauty & Personal Care": {"Active Ingredients": "Hyaluronic Acid 2%, Niacinamide & Peptides", "Technology": "Sonic Vibration 40,000 Strokes/Min", "Safety": "Dermatologist Tested, Hypoallergenic", "Result": "Clinically Proven 94% Efficacy in 7 Days"},
        "Health & Wellness": {"Accuracy": "Clinical Grade Medical Precision (+/- 0.1%)", "Sensors": "Bio-Impedance & Multi-Frequency Scan", "Connectivity": "Apple Health, Google Fit & Strava Sync", "Battery": "Rechargeable Li-ion 6 Months Life"},
        "Automotive & EV Tech": {"Output": "Level 2 48A / 11.5 kW Super Fast Charging", "Cable": "25-Foot All-Weather Commercial Grade", "Protection": "Over-Voltage, Surge & Thermal Monitoring", "Compatibility": "Universal J1772 & NACS EV Port Compatible"},
        "Toys & STEM Robotics": {"Programming": "Python, Scratch & Block-Based Coding App", "Sensors": "LiDAR Obstacle Avoidance & Color AI Vision", "Battery": "Modular Hot-Swappable 2-Hour Pack", "Age Range": "Ages 8+ to Advanced Adult Engineers"}
    }
    
    product_objects = []
    prod_id_counter = 1
    
    for cat_idx, cat in enumerate(cat_objs):
        cat_name = cat.name
        specs_tpl = cat_specs_templates.get(cat_name, {"Feature": "High Performance AI Standard", "Quality": "Premium Grade A", "Warranty": "2 Years Official"})
        
        # We generate exactly 1,000 unique products for this category
        for i in range(1000):
            # Assign retailer: 400 retailers, each gets 50 products across catalog -> index (prod_id_counter - 1) % 400
            ret = retailer_objs[(prod_id_counter - 1) % 400]
            brand = brand_objs[(prod_id_counter - 1) % len(brand_objs)]
            
            adj = adjectives[(i + cat_idx) % len(adjectives)]
            mat = materials[(i * 3) % len(materials)]
            col_var = colors[(i + cat_idx) % len(colors)]
            stor_var = storage_opts[(i + cat_idx) % len(storage_opts)]
            size_var = size_opts[(i + cat_idx) % len(size_opts)]
            
            # Unique Title generating algorithm
            item_name = f"{adj} {cat_name.split(' ')[0]} {brand.name.split(' ')[0]} Pro-{i+1}"
            title = f"{brand.name} {item_name} - {col_var[0]} ({stor_var[0]}, Model 2026-X{prod_id_counter})"
            
            price = round(random.uniform(29.99, 2999.99), 2)
            if "Book" in cat_name or "Toy" in cat_name or "Beauty" in cat_name:
                price = round(random.uniform(15.99, 149.99), 2)
                
            discount = random.choice([0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0])
            rating = round(random.uniform(4.2, 5.0), 1)
            reviews_cnt = random.randint(15, 1200)
            stock_qty = random.randint(0, 250)
            status = "In Stock" if stock_qty > 20 else ("Low Stock" if stock_qty > 0 else "Out of Stock")
            
            # Unique specifications & descriptions
            specs = dict(specs_tpl)
            specs["Model ID"] = f"MODEL-2026-{brand.slug.upper()[:3]}-{prod_id_counter:05d}"
            specs["Material"] = mat
            specs["Weight"] = f"{round(random.uniform(0.2, 8.5), 2)} kg"
            specs["Dimensions"] = f"{random.randint(10,50)} x {random.randint(10,40)} x {random.randint(2,20)} cm"
            
            desc = f"Experience the next evolution of {cat_name.lower()} with the {title}. Masterfully engineered by {brand.name} using {mat.lower()}, this device delivers unprecedented speed and reliability. Designed to integrate seamlessly into modern workflows and elevate daily productivity with Amazon-AI precision."
            mkt_desc = f"Why settle for ordinary when you can own the {brand.name} flagship? Featuring cutting-edge AI optimization, thermal regulation, and ergonomic perfection. Whether you are a professional researcher, creator, or enthusiast, this product is tailored to exceed your highest standards."
            
            features = [
                f"Integrated {adj.lower()} architecture delivering up to 3x faster performance over previous generations.",
                f"Crafted from premium {mat.lower()} for superior thermal dissipation and rugged durability.",
                "Amazon-AI Smart Sensor Suite automatically adapts power and calibration to your environment.",
                "Zero-latency wireless synchronization and universal USB-C / Lightning rapid charging support.",
                f"Full 2-Year Comprehensive Warranty backed by {ret.store_name} and Amazon Prime Logistics."
            ]
            
            ai_tips = [
                f"Ideal choice for users seeking peak performance in {cat_name.lower()}.",
                f"Rated #1 Best Value by Amazon-AI algorithm among {brand.name} products under ${price+100:.0f}.",
                "Highly recommended to pair with MagSafe charging accessories or extended warranty."
            ]
            
            box_items = [
                f"1x {brand.name} {item_name} Unit",
                "1x 100W GaN SuperFast USB-C Charger & Braided Cable",
                "1x Premium Protective Carry Case / Sleeve",
                "1x Amazon-AI Quick Start & Verification Passport"
            ]
            
            faqs_list = [
                {"question": f"Is this {brand.name} product compatible with latest AI OS systems?", "answer": "Yes! It is fully plug-and-play compatible with Windows, macOS, iOS, Android, and Linux systems."},
                {"question": "What is the warranty and return policy?", "answer": f"You get a 30-Day Money-Back Guarantee and a full 2-Year Manufacturer Warranty handled directly by {ret.store_name}."},
                {"question": "Does this support Cash on Delivery (COD)?", "answer": "Yes, 100% of our items support secure Cash on Delivery with zero upfront payment required."}
            ]
            
            prod = Product(
                title=title,
                description=desc,
                marketing_description=mkt_desc,
                price=price,
                discount_percentage=discount,
                rating=rating,
                reviews_count=reviews_cnt,
                stock=stock_qty,
                brand_id=brand.id,
                category_id=cat.id,
                retailer_id=ret.id,
                images=[
                    "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1000&q=80",
                    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1000&q=80",
                    "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=1000&q=80"
                ],
                gallery_images=[
                    "https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=1000&q=80",
                    "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=1000&q=80"
                ],
                specifications=specs,
                features=features,
                country_of_origin="United States / Japan",
                warranty="2 Years Official Manufacturer Warranty",
                model_number=f"MOD-{prod_id_counter:05d}",
                sku=f"SKU-{brand.slug.upper()[:3]}-{cat.slug.upper()[:3]}-{prod_id_counter:06d}",
                weight=specs["Weight"],
                dimensions=specs["Dimensions"],
                color_variants=col_var,
                storage_variants=stor_var,
                available_sizes=size_var,
                material=mat,
                manufacturing_date="2025-10-10",
                shipping_info="Free Express 2-Day Air via Amazon Prime",
                delivery_estimate="1-2 Business Days",
                return_policy="30-Day Hassle-Free Returns with Free Return Label",
                box_contents=box_items,
                package_dimensions="35 x 25 x 10 cm",
                faqs=faqs_list,
                qna=[],
                related_products=[],
                frequently_bought_together=[],
                accessories=[],
                ai_buying_tips=ai_tips
            )
            db.add(prod)
            product_objects.append(prod)
            
            # Create corresponding inventory
            inv = Inventory(
                product_id=prod_id_counter,
                sku=f"SKU-{brand.slug.upper()[:3]}-{cat.slug.upper()[:3]}-{prod_id_counter:06d}",
                quantity=stock_qty,
                warehouse_location=f"Zone {random.choice(['A','B','C','D','E','F'])} - Shelf {random.randint(1,50)}",
                restock_threshold=15,
                status=status
            )
            db.add(inv)
            prod_id_counter += 1

        # Flush every category (1000 products) to keep RAM usage minimal
        db.flush()
        print(f"    Category '{cat_name}' complete: 1,000 products created (Total: {prod_id_counter-1}/20,000)...")

    # 5. CUSTOMERS (50,000+ Customers via fast batching)
    print(" [5/8] Generating 50,000+ Realistic Customers via High-Speed Batch Engine...")
    user_mappings = []
    # Include default admin and test users first
    default_users = [
        {"id": 1, "email": "admin@amazon-ai.com", "hashed_password": get_password_hash("admin123"), "full_name": "Jeff Amazon Admin", "role": "admin", "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=250&q=80", "is_active": True, "is_verified": True, "created_at": datetime.datetime.utcnow()},
        {"id": 2, "email": "john.doe@gmail.com", "hashed_password": get_password_hash("password123"), "full_name": "John Doe", "role": "customer", "profile_picture": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=250&q=80", "is_active": True, "is_verified": True, "created_at": datetime.datetime.utcnow()},
        {"id": 3, "email": "sarah.connor@gmail.com", "hashed_password": get_password_hash("password123"), "full_name": "Sarah Connor", "role": "customer", "profile_picture": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=250&q=80", "is_active": True, "is_verified": True, "created_at": datetime.datetime.utcnow()},
        {"id": 4, "email": "michael.scott@dundermifflin.com", "hashed_password": get_password_hash("password123"), "full_name": "Michael Scott", "role": "customer", "profile_picture": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=250&q=80", "is_active": True, "is_verified": True, "created_at": datetime.datetime.utcnow()}
    ]
    user_mappings.extend(default_users)
    
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Margaret", "Anthony", "Betty", "Mark", "Sandra", "Steven", "Ashley", "Paul", "Kimberly", "Andrew", "Emily", "Joshua", "Donna", "Kenneth", "Michelle", "Kevin", "Dorothy", "Brian", "Carol", "George", "Amanda", "Edward", "Melissa", "Ronald", "Deborah"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"]
    
    # We use a static password hash for generated customers to save CPU hashing time (10000x faster!)
    default_hash = default_users[1]["hashed_password"]
    
    for i in range(5, 50005):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        user_mappings.append({
            "id": i,
            "email": f"{fn.lower()}.{ln.lower()}.{i}@amazon-ai.com",
            "hashed_password": default_hash,
            "full_name": f"{fn} {ln}",
            "role": "customer",
            "profile_picture": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=250&q=80",
            "is_active": True,
            "is_verified": True,
            "browsing_history": [random.randint(1, 1000), random.randint(1001, 2000), random.randint(2001, 3000)],
            "recently_viewed": [random.randint(1, 500), random.randint(501, 1000)],
            "favorite_categories": ["Electronics", "Laptops & Ultrabooks", "Audio & Headphones"],
            "preferred_brands": ["Apple", "Sony", "Samsung"],
            "created_at": datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(1, 365))
        })
        if len(user_mappings) >= 10000:
            db.bulk_insert_mappings(User, user_mappings)
            user_mappings = []
    if user_mappings:
        db.bulk_insert_mappings(User, user_mappings)
        user_mappings = []
    db.flush()
    print("    50,000+ Customer accounts successfully created.")

    # 6. REVIEWS (250,000+ Reviews via fast batching)
    print(" [6/8] Generating 250,000+ Product Reviews across all 20,000 products...")
    sample_reviews = [
        ("Absolute perfection! The build quality is top notch and delivery was lightning fast via COD.", 5.0, "Best purchase of the year!", ["Stunning display", "Incredible battery life", "Premium feel"], ["None"]),
        ("Exceeded my expectations in every way. The AI features really make a difference in daily workflow.", 5.0, "Incredible AI performance", ["Fast processing", "AI integration is flawless"], ["Price is slightly high"]),
        ("Great value for money. Very comfortable and battery lasts all week as advertised.", 4.5, "Highly recommended", ["Comfortable design", "Long battery"], ["Cable could be longer"]),
        ("Solid product overall, though I wish the charging cable was slightly longer.", 4.0, "Very good, minor improvement needed", ["Good build quality", "Reliable"], ["Heavier than expected"]),
        ("Unmatched noise cancellation and crystal clear audio. Five stars all the way!", 5.0, "Audio nirvana!", ["Best noise cancellation", "Crystal clear audio"], ["Case scratches easily"]),
        ("Very impressed with the shipping speed and packaging. Product works exactly as described.", 4.8, "Top seller and great product", ["Fast shipping", "Accurate description"], ["None"]),
        ("Decent performance for the price point. Perfect for students and casual use.", 4.0, "Solid daily driver", ["Affordable", "Easy setup"], ["Average speaker sound"])
    ]
    
    review_mappings = []
    rev_id = 1
    # Generate ~12-13 reviews per product across 20,000 products = 250,000+ reviews!
    for p_id in range(1, prod_id_counter):
        num_revs = 12 if p_id % 2 == 0 else 13
        for r in range(num_revs):
            comm, rat, title, pros, cons = sample_reviews[(p_id + r) % len(sample_reviews)]
            u_id = random.randint(2, 50000)
            review_mappings.append({
                "id": rev_id,
                "product_id": p_id,
                "user_id": u_id,
                "user_name": f"Verified Amazon-AI Buyer #{u_id}",
                "rating": rat,
                "title": title,
                "comment": comm,
                "pros": pros,
                "cons": cons,
                "verified_purchase": True,
                "review_images": [],
                "helpful_votes": random.randint(0, 85),
                "created_at": datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(1, 180))
            })
            rev_id += 1
            if len(review_mappings) >= 25000:
                db.bulk_insert_mappings(Review, review_mappings)
                review_mappings = []
    if review_mappings:
        db.bulk_insert_mappings(Review, review_mappings)
        review_mappings = []
    db.flush()
    print(f"    {rev_id-1:,} Product Reviews successfully created.")

    # 7. ORDERS (1,000,000+ Orders & Order Items via fast batching)
    print(" [7/8] Generating 1,000,000+ Order Records & Items via High-Speed Chunk Stream...")
    order_mappings = []
    order_item_mappings = []
    sales_mappings = []
    
    statuses = ["Delivered", "Delivered", "Delivered", "Out For Delivery", "Shipped", "Packed", "Pending"]
    
    for i in range(1, 1000001):
        u_id = random.randint(2, 50000)
        p_id = random.randint(1, 20000)
        qty = random.randint(1, 2)
        unit_p = 149.99  # average reference price for ultra-fast batch speed
        total_p = round(unit_p * qty, 2)
        tax = round(total_p * 0.08, 2)
        status = statuses[i % len(statuses)]
        
        order_date = datetime.datetime.utcnow() - datetime.timedelta(days=(i % 90))
        
        order_mappings.append({
            "id": i,
            "order_number": f"ORD-2026-{1000000 + i}",
            "user_id": u_id,
            "total_amount": round(total_p + tax, 2),
            "tax": tax,
            "delivery_charge": 0.0,
            "status": status,
            "payment_method": "Cash on Delivery",
            "delivery_address": {
                "full_name": f"Customer {u_id}",
                "phone": "+1 (555) 019-2834",
                "street_address": f"{random.randint(100, 9999)} Tech Innovation Blvd",
                "city": "Seattle", "state": "WA", "postal_code": "98109"
            },
            "timeline": [
                {"status": "Pending", "timestamp": str(order_date), "note": "Order placed successfully (Cash on Delivery)"},
                {"status": "Delivered", "timestamp": str(order_date + datetime.timedelta(days=2)), "note": "Package delivered and cash collected"}
            ],
            "created_at": order_date
        })
        
        order_item_mappings.append({
            "id": i,
            "order_id": i,
            "product_id": p_id,
            "quantity": qty,
            "unit_price": unit_p,
            "total_price": total_p
        })
        
        if i % 10 == 0: # sample sales history
            sales_mappings.append({
                "id": i // 10,
                "date": order_date,
                "product_id": p_id,
                "category_id": ((p_id - 1) // 1000) + 1,
                "units_sold": qty,
                "revenue": total_p,
                "profit": round(total_p * 0.28, 2)
            })
            
        if len(order_mappings) >= 50000:
            db.bulk_insert_mappings(Order, order_mappings)
            db.bulk_insert_mappings(OrderItem, order_item_mappings)
            if sales_mappings:
                db.bulk_insert_mappings(SalesHistory, sales_mappings)
            order_mappings = []
            order_item_mappings = []
            sales_mappings = []
            print(f"      ⏳ Inserted {i:,} / 1,000,000 Orders...")
            
    if order_mappings:
        db.bulk_insert_mappings(Order, order_mappings)
        db.bulk_insert_mappings(OrderItem, order_item_mappings)
        if sales_mappings:
            db.bulk_insert_mappings(SalesHistory, sales_mappings)
    db.flush()
    print("    1,000,000+ Orders & Order Items successfully created.")

    # 8. ANALYTICS EVENTS (2,000,000+ Events via fast batching)
    print(" [8/8] Generating 2,000,000+ Analytics Events (views, clicks, searches, wishlist, cart)...")
    event_types = ["view", "view", "click", "search", "wishlist_add", "cart_add", "checkout"]
    queries = ["best laptop under 80000", "5g smartphone", "noise cancelling headphones", "oled gaming monitor", "ergonomic office chair", "apple macbook pro", "sony wh1000xm5", "nike air zoom", "dyson vacuum"]
    
    event_mappings = []
    for i in range(1, 2000001):
        ev_type = event_types[i % len(event_types)]
        u_id = random.randint(2, 50000)
        p_id = random.randint(1, 20000)
        c_id = ((p_id - 1) // 1000) + 1
        q = queries[i % len(queries)] if ev_type == "search" else None
        
        event_mappings.append({
            "id": i,
            "event_type": ev_type,
            "user_id": u_id,
            "product_id": p_id if ev_type != "search" else None,
            "category_id": c_id if ev_type != "search" else None,
            "query": q,
            "metadata_json": {"source": "floating_search_bar" if ev_type == "search" else "product_card", "platform": "web_ios_theme"},
            "timestamp": datetime.datetime.utcnow() - datetime.timedelta(hours=(i % 720))
        })
        
        if len(event_mappings) >= 100000:
            db.bulk_insert_mappings(AnalyticsEvent, event_mappings)
            event_mappings = []
            print(f"      ⏳ Inserted {i:,} / 2,000,000 Analytics Events...")
            
    if event_mappings:
        db.bulk_insert_mappings(AnalyticsEvent, event_mappings)
        event_mappings = []
        
    db.commit()
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "="*80)
    print(f" [SUCCESS] AMAZON-AI ENTERPRISE PRODUCTION DATABASE CREATED IN {elapsed} SECONDS!")
    print("   Total Products: 20,000+ | Brands: 400+ | Retailers: 400+ | Customers: 50,000+")
    print("   Reviews: 250,000+ | Orders: 1,000,000+ | Analytics Events: 2,000,000+")
    print("="*80 + "\n")
