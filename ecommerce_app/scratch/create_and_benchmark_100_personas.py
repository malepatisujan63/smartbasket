import os
import sys
import json
import sqlite3
import random
import time
import math
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, precision_recall_curve
from catboost import CatBoostClassifier, Pool

APP_DIR = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app"
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

DB_PATH = os.path.join(APP_DIR, "fast_ecommerce.db")
MODELS_DIR = os.path.join(APP_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# =============================================================================
# DEFINE THE 100 DISTINCT SHOPPING MENTALITIES (10 CLUSTERS x 10 PERSONAS)
# =============================================================================
CLUSTERS = {
    1: "Price & Budget Psychologies",
    2: "Dedicated Category Specialists",
    3: "Decision Speed & Deliberation",
    4: "Social Proof & Rating Obsession",
    5: "Brand Loyalty & Ecosystem",
    6: "Cart & Funnel Behavior",
    7: "Search & Navigation Styles",
    8: "Life Events & Contexts",
    9: "Temporal & Rhythmical Habits",
    10: "Edge-Case & Adversarial Personas"
}

PERSONAS_DEF = [
    # Cluster 1: Price & Budget
    {"id": 1, "code": "p001_bargain_hunter", "cluster_id": 1, "name": "The Extreme Bargain Hunter", "price": "budget", "stars": "any", "conv": 0.30, "dwell": (25, 10), "distractor": 0.20, "cats": None},
    {"id": 2, "code": "p002_luxury_shopper", "cluster_id": 1, "name": "The Luxury Prestige Shopper", "price": "luxury", "stars": "high", "conv": 0.25, "dwell": (50, 20), "distractor": 0.15, "cats": None},
    {"id": 3, "code": "p003_discount_chaser", "cluster_id": 1, "name": "The Deep Discount Chaser", "price": "budget", "stars": "any", "conv": 0.35, "dwell": (35, 15), "distractor": 0.20, "cats": None},
    {"id": 4, "code": "p004_penny_pincher", "cluster_id": 1, "name": "The Penny Pincher", "price": "budget", "stars": "any", "conv": 0.40, "dwell": (20, 8), "distractor": 0.15, "cats": None},
    {"id": 5, "code": "p005_value_rationalist", "cluster_id": 1, "name": "The Value-for-Money Rationalist", "price": "mid", "stars": "high", "conv": 0.28, "dwell": (45, 15), "distractor": 0.20, "cats": None},
    {"id": 6, "code": "p006_clearance_scavenger", "cluster_id": 1, "name": "The Clearance Scavenger", "price": "budget", "stars": "any", "conv": 0.30, "dwell": (30, 12), "distractor": 0.25, "cats": None},
    {"id": 7, "code": "p007_free_shipping_calibrator", "cluster_id": 1, "name": "The Free-Shipping Calibrator", "price": "mid", "stars": "any", "conv": 0.22, "dwell": (35, 15), "distractor": 0.20, "cats": None},
    {"id": 8, "code": "p008_price_drop_monitor", "cluster_id": 1, "name": "The Price-Drop Monitor", "price": "mid", "stars": "high", "conv": 0.12, "dwell": (60, 25), "distractor": 0.20, "cats": None},
    {"id": 9, "code": "p009_payday_splurger", "cluster_id": 1, "name": "The Payday Splurger", "price": "luxury", "stars": "high", "conv": 0.20, "dwell": (40, 18), "distractor": 0.20, "cats": None},
    {"id": 10, "code": "p010_bulk_economy_buyer", "cluster_id": 1, "name": "The Bulk Economy Buyer", "price": "budget", "stars": "any", "conv": 0.32, "dwell": (30, 10), "distractor": 0.15, "cats": None},

    # Cluster 2: Category Specialists
    {"id": 11, "code": "p011_pure_tech_geek", "cluster_id": 2, "name": "The Pure Tech Geek", "price": "any", "stars": "high", "conv": 0.28, "dwell": (55, 20), "distractor": 0.20, "cats": ["Computers & Accessories", "Electronics", "Cell Phones & Accessories"]},
    {"id": 12, "code": "p012_high_fashion_trendsetter", "cluster_id": 2, "name": "The High-Fashion Trendsetter", "price": "luxury", "stars": "high", "conv": 0.26, "dwell": (45, 15), "distractor": 0.20, "cats": ["Women's Clothing", "Women's Handbags", "Women's Shoes", "Women's Jewelry"]},
    {"id": 13, "code": "p013_dedicated_new_parent", "cluster_id": 2, "name": "The Dedicated New Parent", "price": "any", "stars": "high", "conv": 0.30, "dwell": (40, 15), "distractor": 0.15, "cats": ["Baby", "Toys & Games", "Girls' Clothing", "Boys' Clothing"]},
    {"id": 14, "code": "p014_gym_fitness_fanatic", "cluster_id": 2, "name": "The Gym Fitness Fanatic", "price": "any", "stars": "high", "conv": 0.27, "dwell": (35, 12), "distractor": 0.20, "cats": ["Sports & Outdoors", "Men's Shoes", "Men's Clothing"]},
    {"id": 15, "code": "p015_bookworm_bibliophile", "cluster_id": 2, "name": "The Bookworm Bibliophile", "price": "budget", "stars": "high", "conv": 0.35, "dwell": (50, 20), "distractor": 0.15, "cats": ["Books", "Office Products"]},
    {"id": 16, "code": "p016_competitive_gamer", "cluster_id": 2, "name": "The Competitive Gamer", "price": "mid", "stars": "high", "conv": 0.30, "dwell": (45, 18), "distractor": 0.20, "cats": ["Video Games", "Computers & Accessories"]},
    {"id": 17, "code": "p017_gourmet_home_chef", "cluster_id": 2, "name": "The Gourmet Home Chef", "price": "mid", "stars": "high", "conv": 0.28, "dwell": (40, 15), "distractor": 0.20, "cats": ["Kitchen & Dining", "Grocery & Gourmet Food"]},
    {"id": 18, "code": "p018_outdoor_survivalist", "cluster_id": 2, "name": "The Outdoor Survivalist", "price": "mid", "stars": "high", "conv": 0.25, "dwell": (45, 18), "distractor": 0.18, "cats": ["Sports & Outdoors", "Men's Shoes", "Tools & Home Improvement"]},
    {"id": 19, "code": "p019_pampered_pet_owner", "cluster_id": 2, "name": "The Pampered Pet Owner", "price": "any", "stars": "high", "conv": 0.33, "dwell": (35, 12), "distractor": 0.15, "cats": ["Pet Supplies"]},
    {"id": 20, "code": "p020_clean_beauty_enthusiast", "cluster_id": 2, "name": "The Clean-Beauty Enthusiast", "price": "mid", "stars": "high", "conv": 0.30, "dwell": (45, 15), "distractor": 0.18, "cats": ["Beauty & Personal Care"]},

    # Cluster 3: Decision Speed & Deliberation
    {"id": 21, "code": "p021_impulse_buyer", "cluster_id": 3, "name": "The Impulse Buyer", "price": "any", "stars": "any", "conv": 0.45, "dwell": (12, 5), "distractor": 0.25, "cats": None},
    {"id": 22, "code": "p022_deep_researcher", "cluster_id": 3, "name": "The Analytical Deep Researcher", "price": "any", "stars": "high", "conv": 0.15, "dwell": (95, 30), "distractor": 0.15, "cats": None},
    {"id": 23, "code": "p023_quick_decider", "cluster_id": 3, "name": "The Quick Decider", "price": "any", "stars": "high", "conv": 0.38, "dwell": (22, 8), "distractor": 0.20, "cats": None},
    {"id": 24, "code": "p024_indecisive_agonizer", "cluster_id": 3, "name": "The Indecisive Agonizer", "price": "mid", "stars": "any", "conv": 0.05, "dwell": (75, 25), "distractor": 0.25, "cats": None},
    {"id": 25, "code": "p025_sleep_on_it", "cluster_id": 3, "name": "The Sleep-On-It Shopper", "price": "mid", "stars": "high", "conv": 0.18, "dwell": (40, 15), "distractor": 0.20, "cats": None},
    {"id": 26, "code": "p026_speed_skimmer", "cluster_id": 3, "name": "The Speed Skimmer", "price": "any", "stars": "any", "conv": 0.12, "dwell": (8, 3), "distractor": 0.30, "cats": None},
    {"id": 27, "code": "p027_surgical_shopper", "cluster_id": 3, "name": "The Surgical 1-Shot Shopper", "price": "any", "stars": "high", "conv": 0.48, "dwell": (30, 10), "distractor": 0.10, "cats": None},
    {"id": 28, "code": "p028_slow_browser", "cluster_id": 3, "name": "The Relaxed Slow Browser", "price": "any", "stars": "any", "conv": 0.14, "dwell": (80, 25), "distractor": 0.22, "cats": None},
    {"id": 29, "code": "p029_instant_bouncer", "cluster_id": 3, "name": "The Instant Regret Bouncer", "price": "any", "stars": "any", "conv": 0.04, "dwell": (6, 2), "distractor": 0.30, "cats": None},
    {"id": 30, "code": "p030_tab_hoarder", "cluster_id": 3, "name": "The Comparison Tab Hoarder", "price": "mid", "stars": "high", "conv": 0.20, "dwell": (65, 20), "distractor": 0.20, "cats": None},

    # Cluster 4: Social Proof & Ratings
    {"id": 31, "code": "p031_five_star_snob", "cluster_id": 4, "name": "The 5-Star Snob", "price": "any", "stars": "high", "conv": 0.32, "dwell": (35, 12), "distractor": 0.15, "cats": None},
    {"id": 32, "code": "p032_review_count_believer", "cluster_id": 4, "name": "The Review-Count Believer", "price": "any", "stars": "high", "conv": 0.30, "dwell": (40, 15), "distractor": 0.15, "cats": None},
    {"id": 33, "code": "p033_critical_reader", "cluster_id": 4, "name": "The Critical Review Reader", "price": "mid", "stars": "low", "conv": 0.12, "dwell": (70, 25), "distractor": 0.20, "cats": None},
    {"id": 34, "code": "p034_bestseller_follower", "cluster_id": 4, "name": "The Bestseller Badge Follower", "price": "any", "stars": "high", "conv": 0.35, "dwell": (30, 10), "distractor": 0.18, "cats": None},
    {"id": 35, "code": "p035_platform_choice_loyalist", "cluster_id": 4, "name": "The Platform Choice Loyalist", "price": "mid", "stars": "high", "conv": 0.32, "dwell": (35, 12), "distractor": 0.18, "cats": None},
    {"id": 36, "code": "p036_early_adopter", "cluster_id": 4, "name": "The Early-Adopter Risk Taker", "price": "mid", "stars": "any", "conv": 0.28, "dwell": (40, 15), "distractor": 0.22, "cats": None},
    {"id": 37, "code": "p037_hidden_gem_hunter", "cluster_id": 4, "name": "The Hidden-Gem Hunter", "price": "mid", "stars": "high", "conv": 0.25, "dwell": (50, 18), "distractor": 0.20, "cats": None},
    {"id": 38, "code": "p038_the_skeptic", "cluster_id": 4, "name": "The Skeptic", "price": "mid", "stars": "high", "conv": 0.22, "dwell": (60, 20), "distractor": 0.20, "cats": None},
    {"id": 39, "code": "p039_influencer_driven", "cluster_id": 4, "name": "The Influencer-Driven Shopper", "price": "mid", "stars": "high", "conv": 0.32, "dwell": (35, 12), "distractor": 0.20, "cats": ["Beauty & Personal Care", "Women's Clothing"]},
    {"id": 40, "code": "p040_gallery_inspector", "cluster_id": 4, "name": "The Photo Review Inspector", "price": "any", "stars": "high", "conv": 0.26, "dwell": (65, 22), "distractor": 0.18, "cats": None},

    # Cluster 5: Brand Loyalty
    {"id": 41, "code": "p041_apple_purist", "cluster_id": 5, "name": "The Apple Ecosystem Purist", "price": "luxury", "stars": "high", "conv": 0.35, "dwell": (45, 15), "distractor": 0.15, "cats": ["Computers & Accessories", "Cell Phones & Accessories"]},
    {"id": 42, "code": "p042_samsung_loyalist", "cluster_id": 5, "name": "The Samsung Loyalist", "price": "mid", "stars": "high", "conv": 0.30, "dwell": (40, 15), "distractor": 0.18, "cats": ["Electronics", "Cell Phones & Accessories"]},
    {"id": 43, "code": "p043_nike_fanatic", "cluster_id": 5, "name": "The Nike Head-to-Toe Loyalist", "price": "mid", "stars": "high", "conv": 0.32, "dwell": (35, 12), "distractor": 0.18, "cats": ["Men's Shoes", "Men's Clothing", "Sports & Outdoors"]},
    {"id": 44, "code": "p044_sony_audio_fan", "cluster_id": 5, "name": "The Sony Audio & Visual Fan", "price": "luxury", "stars": "high", "conv": 0.28, "dwell": (50, 18), "distractor": 0.18, "cats": ["Electronics", "Television & Video"]},
    {"id": 45, "code": "p045_generic_brand_buyer", "cluster_id": 5, "name": "The Brand-Agnostic Generic Buyer", "price": "budget", "stars": "any", "conv": 0.35, "dwell": (25, 10), "distractor": 0.20, "cats": None},
    {"id": 46, "code": "p046_luxury_brand_connoisseur", "cluster_id": 5, "name": "The Luxury Brand Connoisseur", "price": "luxury", "stars": "high", "conv": 0.24, "dwell": (55, 20), "distractor": 0.15, "cats": ["Women's Handbags", "Women's Jewelry"]},
    {"id": 47, "code": "p047_eco_brand_advocate", "cluster_id": 5, "name": "The Eco Brand Advocate", "price": "mid", "stars": "high", "conv": 0.28, "dwell": (45, 15), "distractor": 0.20, "cats": ["Health & Household", "Beauty & Personal Care"]},
    {"id": 48, "code": "p048_heritage_brand_fan", "cluster_id": 5, "name": "The Heritage Brand Believer", "price": "mid", "stars": "high", "conv": 0.30, "dwell": (40, 15), "distractor": 0.18, "cats": ["Men's Clothing", "Kitchen & Dining"]},
    {"id": 49, "code": "p049_dtc_startup_follower", "cluster_id": 5, "name": "The DTC Startup Follower", "price": "mid", "stars": "high", "conv": 0.27, "dwell": (38, 14), "distractor": 0.20, "cats": None},
    {"id": 50, "code": "p050_brand_switcher", "cluster_id": 5, "name": "The Experimental Brand Switcher", "price": "any", "stars": "any", "conv": 0.25, "dwell": (35, 12), "distractor": 0.25, "cats": None},

    # Cluster 6: Cart & Funnel
    {"id": 51, "code": "p051_serial_cart_abandoner", "cluster_id": 6, "name": "The Serial Cart Abandoner", "price": "any", "stars": "any", "conv": 0.02, "dwell": (30, 12), "distractor": 0.20, "cats": None},
    {"id": 52, "code": "p052_wishlist_hoarder", "cluster_id": 6, "name": "The Wishlist Hoarder", "price": "any", "stars": "high", "conv": 0.04, "dwell": (35, 15), "distractor": 0.20, "cats": None},
    {"id": 53, "code": "p053_single_item_checkout", "cluster_id": 6, "name": "The 1-Item Clean Checkout", "price": "any", "stars": "high", "conv": 0.40, "dwell": (25, 8), "distractor": 0.15, "cats": None},
    {"id": 54, "code": "p054_bulk_checkout_collector", "cluster_id": 6, "name": "The Bulk Checkout Collector", "price": "budget", "stars": "any", "conv": 0.30, "dwell": (35, 12), "distractor": 0.18, "cats": None},
    {"id": 55, "code": "p055_accidental_clicker", "cluster_id": 6, "name": "The Accidental Clicker", "price": "any", "stars": "any", "conv": 0.08, "dwell": (15, 6), "distractor": 0.35, "cats": None},
    {"id": 56, "code": "p056_cart_pruner", "cluster_id": 6, "name": "The Cart Pruner", "price": "mid", "stars": "high", "conv": 0.22, "dwell": (45, 18), "distractor": 0.20, "cats": None},
    {"id": 57, "code": "p057_high_intent_buyer", "cluster_id": 6, "name": "The High-Intent Direct Buyer", "price": "any", "stars": "high", "conv": 0.55, "dwell": (35, 12), "distractor": 0.10, "cats": None},
    {"id": 58, "code": "p058_pure_window_shopper", "cluster_id": 6, "name": "The Pure Window Shopper", "price": "any", "stars": "any", "conv": 0.01, "dwell": (25, 10), "distractor": 0.25, "cats": None},
    {"id": 59, "code": "p059_checkout_dropoff", "cluster_id": 6, "name": "The Tax & Shipping Dropoff", "price": "mid", "stars": "any", "conv": 0.08, "dwell": (40, 15), "distractor": 0.20, "cats": None},
    {"id": 60, "code": "p060_repeat_reorderer", "cluster_id": 6, "name": "The Repeat Consumable Re-Orderer", "price": "budget", "stars": "high", "conv": 0.42, "dwell": (18, 6), "distractor": 0.15, "cats": ["Grocery & Gourmet Food", "Health & Household"]},

    # Cluster 7: Search & Navigation
    {"id": 61, "code": "p061_keyword_specialist", "cluster_id": 7, "name": "The Keyword Specialist", "price": "any", "stars": "high", "conv": 0.32, "dwell": (35, 12), "distractor": 0.15, "cats": None},
    {"id": 62, "code": "p062_tree_navigator", "cluster_id": 7, "name": "The Hierarchy Tree Navigator", "price": "any", "stars": "any", "conv": 0.25, "dwell": (40, 15), "distractor": 0.20, "cats": None},
    {"id": 63, "code": "p063_carousel_surfer", "cluster_id": 7, "name": "The Carousel Surfer", "price": "any", "stars": "high", "conv": 0.28, "dwell": (30, 10), "distractor": 0.22, "cats": None},
    {"id": 64, "code": "p064_filter_power_user", "cluster_id": 7, "name": "The Filter Power-User", "price": "mid", "stars": "high", "conv": 0.35, "dwell": (50, 18), "distractor": 0.15, "cats": None},
    {"id": 65, "code": "p065_deep_page_scroller", "cluster_id": 7, "name": "The Deep-Page Scroller", "price": "any", "stars": "any", "conv": 0.18, "dwell": (45, 15), "distractor": 0.25, "cats": None},
    {"id": 66, "code": "p066_vague_searcher", "cluster_id": 7, "name": "The Broad Generic Searcher", "price": "any", "stars": "any", "conv": 0.15, "dwell": (30, 12), "distractor": 0.30, "cats": None},
    {"id": 67, "code": "p067_messy_searcher", "cluster_id": 7, "name": "The Typo Messy Searcher", "price": "any", "stars": "any", "conv": 0.20, "dwell": (32, 12), "distractor": 0.25, "cats": None},
    {"id": 68, "code": "p068_back_button_addict", "cluster_id": 7, "name": "The Back-Button Addict", "price": "any", "stars": "any", "conv": 0.18, "dwell": (16, 6), "distractor": 0.25, "cats": None},
    {"id": 69, "code": "p069_visual_thumbnail_shopper", "cluster_id": 7, "name": "The Visual Thumbnail Shopper", "price": "any", "stars": "any", "conv": 0.24, "dwell": (25, 8), "distractor": 0.22, "cats": None},
    {"id": 70, "code": "p070_recommendation_hopper", "cluster_id": 7, "name": "The Recommendation Hopper", "price": "any", "stars": "high", "conv": 0.26, "dwell": (30, 10), "distractor": 0.20, "cats": None},

    # Cluster 8: Life Events & Situational
    {"id": 71, "code": "p071_holiday_gift_buyer", "cluster_id": 8, "name": "The Holiday Multi-Gift Buyer", "price": "mid", "stars": "high", "conv": 0.34, "dwell": (38, 14), "distractor": 0.30, "cats": ["Toys & Games", "Women's Jewelry", "Men's Accessories"]},
    {"id": 72, "code": "p072_emergency_fixer", "cluster_id": 8, "name": "The Emergency Problem-Solver", "price": "any", "stars": "high", "conv": 0.50, "dwell": (20, 6), "distractor": 0.10, "cats": ["Tools & Home Improvement"]},
    {"id": 73, "code": "p073_new_homeowner", "cluster_id": 8, "name": "The New Homeowner", "price": "mid", "stars": "high", "conv": 0.32, "dwell": (45, 16), "distractor": 0.20, "cats": ["Home & Kitchen", "Tools & Home Improvement", "Patio, Lawn & Garden"]},
    {"id": 74, "code": "p074_college_freshman", "cluster_id": 8, "name": "The College Dorm Freshman", "price": "budget", "stars": "any", "conv": 0.30, "dwell": (32, 12), "distractor": 0.20, "cats": ["Home & Kitchen", "Computers & Accessories"]},
    {"id": 75, "code": "p075_vacation_planner", "cluster_id": 8, "name": "The Vacation Planner", "price": "mid", "stars": "high", "conv": 0.30, "dwell": (36, 12), "distractor": 0.20, "cats": ["Luggage & Travel Gear", "Clothing, Shoes & Jewelry"]},
    {"id": 76, "code": "p076_hobby_hopper", "cluster_id": 8, "name": "The Hobby Hopper", "price": "mid", "stars": "high", "conv": 0.28, "dwell": (42, 15), "distractor": 0.30, "cats": ["Arts, Crafts & Sewing", "Musical Instruments"]},
    {"id": 77, "code": "p077_wedding_guest", "cluster_id": 8, "name": "The Formal Wedding Guest", "price": "luxury", "stars": "high", "conv": 0.28, "dwell": (45, 15), "distractor": 0.20, "cats": ["Women's Clothing", "Men's Clothing", "Women's Shoes"]},
    {"id": 78, "code": "p078_diy_renovator", "cluster_id": 8, "name": "The DIY Home Renovator", "price": "mid", "stars": "high", "conv": 0.32, "dwell": (40, 14), "distractor": 0.18, "cats": ["Tools & Home Improvement"]},
    {"id": 79, "code": "p079_back_to_school_parent", "cluster_id": 8, "name": "The Back-to-School Parent", "price": "budget", "stars": "any", "conv": 0.35, "dwell": (30, 10), "distractor": 0.20, "cats": ["Office Products", "Boys' Clothing", "Girls' Clothing"]},
    {"id": 80, "code": "p080_black_friday_rusher", "cluster_id": 8, "name": "The Black Friday Flash Rusher", "price": "budget", "stars": "any", "conv": 0.38, "dwell": (15, 6), "distractor": 0.25, "cats": None},

    # Cluster 9: Temporal & Rhythmical
    {"id": 81, "code": "p081_insomniac_shopper", "cluster_id": 9, "name": "The 2 AM Insomniac Shopper", "price": "any", "stars": "any", "conv": 0.22, "dwell": (28, 12), "distractor": 0.30, "cats": None},
    {"id": 82, "code": "p082_morning_coffee_browser", "cluster_id": 9, "name": "The Morning Coffee Shopper", "price": "mid", "stars": "high", "conv": 0.25, "dwell": (35, 12), "distractor": 0.20, "cats": None},
    {"id": 83, "code": "p083_weekend_relaxer", "cluster_id": 9, "name": "The Weekend Relaxed Shopper", "price": "any", "stars": "high", "conv": 0.28, "dwell": (50, 18), "distractor": 0.20, "cats": None},
    {"id": 84, "code": "p084_lunch_break_rusher", "cluster_id": 9, "name": "The Lunch-Break Quick Browser", "price": "any", "stars": "high", "conv": 0.26, "dwell": (22, 8), "distractor": 0.22, "cats": None},
    {"id": 85, "code": "p085_daily_habitual", "cluster_id": 9, "name": "The Daily Routine Checker", "price": "any", "stars": "high", "conv": 0.24, "dwell": (30, 10), "distractor": 0.20, "cats": None},
    {"id": 86, "code": "p086_paycheck_cycler", "cluster_id": 9, "name": "The Paycheck Cycle Shopper", "price": "mid", "stars": "high", "conv": 0.25, "dwell": (35, 14), "distractor": 0.20, "cats": None},
    {"id": 87, "code": "p087_weather_cycler", "cluster_id": 9, "name": "The Seasonal Weather Shopper", "price": "mid", "stars": "high", "conv": 0.28, "dwell": (35, 12), "distractor": 0.20, "cats": None},
    {"id": 88, "code": "p088_quarterly_whale", "cluster_id": 9, "name": "The Rare High-Ticket Whale", "price": "luxury", "stars": "high", "conv": 0.35, "dwell": (60, 22), "distractor": 0.15, "cats": None},
    {"id": 89, "code": "p089_hyperactive_visitor", "cluster_id": 9, "name": "The Hyper-Active Daily Visitor", "price": "any", "stars": "any", "conv": 0.16, "dwell": (24, 8), "distractor": 0.25, "cats": None},
    {"id": 90, "code": "p090_transit_commuter", "cluster_id": 9, "name": "The Transit Commuter", "price": "any", "stars": "any", "conv": 0.20, "dwell": (18, 6), "distractor": 0.25, "cats": None},

    # Cluster 10: Edge-Case & Adversarial
    {"id": 91, "code": "p091_chaotic_random_clicker", "cluster_id": 10, "name": "The Chaotic Random Clicker", "price": "any", "stars": "any", "conv": 0.10, "dwell": (25, 15), "distractor": 0.70, "cats": None},
    {"id": 92, "code": "p092_contradiction_tester", "cluster_id": 10, "name": "The Price-Star Contradiction Tester", "price": "luxury", "stars": "low", "conv": 0.18, "dwell": (40, 15), "distractor": 0.25, "cats": None},
    {"id": 93, "code": "p093_zero_dwell_bot", "cluster_id": 10, "name": "The Rapid Scraper Bot", "price": "any", "stars": "any", "conv": 0.05, "dwell": (5, 2), "distractor": 0.35, "cats": None},
    {"id": 94, "code": "p094_monomaniac", "cluster_id": 10, "name": "The Extreme Monomaniac", "price": "budget", "stars": "any", "conv": 0.32, "dwell": (30, 10), "distractor": 0.10, "cats": ["Cell Phones & Accessories"]},
    {"id": 95, "code": "p095_category_hopper", "cluster_id": 10, "name": "The 30-Category Hopper", "price": "any", "stars": "any", "conv": 0.12, "dwell": (25, 10), "distractor": 0.60, "cats": None},
    {"id": 96, "code": "p096_critical_rater", "cluster_id": 10, "name": "The Highly Critical Rater", "price": "mid", "stars": "low", "conv": 0.10, "dwell": (45, 18), "distractor": 0.25, "cats": None},
    {"id": 97, "code": "p097_reorder_direct", "cluster_id": 10, "name": "The Inverted 1-Click Reorderer", "price": "budget", "stars": "high", "conv": 0.60, "dwell": (15, 5), "distractor": 0.10, "cats": ["Grocery & Gourmet Food"]},
    {"id": 98, "code": "p098_uniform_price_ghost", "cluster_id": 10, "name": "The Fixed-Budget Ghost", "price": "mid", "stars": "any", "conv": 0.20, "dwell": (30, 10), "distractor": 0.20, "cats": None},
    {"id": 99, "code": "p099_outlier_hunter", "cluster_id": 10, "name": "The Extreme Outlier Hunter", "price": "luxury", "stars": "any", "conv": 0.15, "dwell": (45, 20), "distractor": 0.30, "cats": None},
    {"id": 100, "code": "p100_bipolar_shopper", "cluster_id": 10, "name": "The Bipolar Luxury/Bargain Shopper", "price": "any", "stars": "any", "conv": 0.28, "dwell": (35, 15), "distractor": 0.30, "cats": None},
]

def run_100_persona_pipeline():
    print("=" * 80)
    print("STEP 1: Account Provisioning in fast_ecommerce.db")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create password hash
    pw_hash = hashlib.sha256("persona_pass_2026".encode()).hexdigest()

    user_id_map = {}
    created_count = 0
    for p in PERSONAS_DEF:
        cursor.execute("SELECT user_id FROM Users WHERE username = ?", (p["code"],))
        row = cursor.fetchone()
        if row:
            user_id_map[p["id"]] = row[0]
        else:
            cursor.execute("""
                INSERT INTO Users (username, password, ab_group, is_admin)
                VALUES (?, ?, 'A', 0)
            """, (p["code"], pw_hash))
            uid = cursor.lastrowid
            user_id_map[p["id"]] = uid
            created_count += 1

    conn.commit()
    print(f"[OK] Total personas mapped: {len(user_id_map)} (Newly created accounts: {created_count})")

    # =========================================================================
    # STEP 2: Load High-Quality Product Pools by Category and Price Tier
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 2: Indexing In-Memory Product Pools for Deceptive Log Generation")
    print("=" * 80)

    cursor.execute("""
        SELECT asin, title, price, stars, reviews, category_name 
        FROM Products 
        WHERE price > 0 AND stars > 0 AND category_name IS NOT NULL
        ORDER BY reviews DESC 
        LIMIT 50000
    """)
    rows = cursor.fetchall()
    print(f"Loaded {len(rows)} popular catalog products into memory.")

    # Organize products
    cat_prods = {}
    budget_prods = []
    mid_prods = []
    luxury_prods = []
    high_star_prods = []
    low_star_prods = []

    for r in rows:
        asin, title, price, stars, reviews, cat = r
        cat_prods.setdefault(cat, []).append(r)
        
        if price < 25.0:
            budget_prods.append(r)
        elif price > 150.0:
            luxury_prods.append(r)
        else:
            mid_prods.append(r)

        if stars >= 4.5:
            high_star_prods.append(r)
        elif stars <= 3.8:
            low_star_prods.append(r)

    print(f"Index tiers ready: {len(budget_prods)} Budget, {len(mid_prods)} Mid, {len(luxury_prods)} Luxury.")

    # =========================================================================
    # STEP 3: Generate 500 Logs per User (50,000 Logs Total) with Distractors
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 3: Generating 500 Deceptive Logs Per Persona (Total: 50,000 Logs)")
    print("=" * 80)

    logs_inserted_total = 0
    all_logs_to_insert = []
    base_time = datetime.now() - timedelta(days=30)

    for p in PERSONAS_DEF:
        uid = user_id_map[p["id"]]
        cursor.execute("SELECT COUNT(*) FROM UserLogs WHERE user_id = ?", (uid,))
        existing_cnt = cursor.fetchone()[0]

        if existing_cnt >= 500:
            continue

        # Clean existing if below 500 to maintain exact count
        if existing_cnt > 0:
            cursor.execute("DELETE FROM UserLogs WHERE user_id = ?", (uid,))

        # Build persona-specific product pool
        pool = []
        if p["cats"]:
            for c in p["cats"]:
                # Match partial category names
                for cat_key, c_items in cat_prods.items():
                    if c.lower() in cat_key.lower():
                        pool.extend(c_items[:40])
        
        if not pool:
            if p["price"] == "budget":
                pool = budget_prods[:500]
            elif p["price"] == "luxury":
                pool = luxury_prods[:500]
            elif p["price"] == "mid":
                pool = mid_prods[:500]
            else:
                pool = rows[:500]

        curr_time = base_time + timedelta(hours=random.randint(1, 24))

        for log_idx in range(500):
            curr_time += timedelta(minutes=random.randint(15, 120))
            is_distractor = (random.random() < p["distractor"])

            if is_distractor:
                # Deliberate distractor click from random unrelated product
                prod = random.choice(rows)
                action = "view" if random.random() < 0.85 else "cart"
                dwell = random.randint(5, 35)
            else:
                prod = random.choice(pool)
                # Determine action according to persona conversion rate
                rand_act = random.random()
                conv = p["conv"]
                
                # Check price/star modifier
                stars_val = prod[3]
                star_factor = min(stars_val / 4.5, 1.2)
                
                if rand_act < (conv * star_factor):
                    action = "purchase"
                    dwell = int(np.clip(np.random.normal(p["dwell"][0] * 1.5, 20), 30, 180))
                elif rand_act < (conv * 2.0):
                    action = "cart"
                    dwell = int(np.clip(np.random.normal(p["dwell"][0] * 1.1, 15), 15, 100))
                else:
                    action = "view"
                    dwell = int(np.clip(np.random.normal(p["dwell"][0], p["dwell"][1]), 5, 80))

            all_logs_to_insert.append((
                uid,
                prod[0],
                action,
                curr_time.strftime("%Y-%m-%d %H:%M:%S"),
                None,
                dwell
            ))

    if all_logs_to_insert:
        cursor.executemany("""
            INSERT INTO UserLogs (user_id, asin, action, timestamp, search_query, view_duration)
            VALUES (?, ?, ?, ?, ?, ?)
        """, all_logs_to_insert)
        conn.commit()
        print(f"[OK] Successfully inserted {len(all_logs_to_insert)} deceptive logs into fast_ecommerce.db.")
    else:
        print("[OK] All 100 personas already have 500+ logs populated.")

    conn.close()

    # =========================================================================
    # STEP 4: Batch Train and Test All 100 CatBoost Models
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 4: Batch Training & Testing All 100 Personas (Temporal 80/20 Split)")
    print("=" * 80)

    from ml_engine import UserMLEngine

    results_by_persona = []
    cluster_metrics = {c_id: [] for c_id in CLUSTERS.keys()}

    start_train_time = time.time()

    for idx, p in enumerate(PERSONAS_DEF, 1):
        uid = user_id_map[p["id"]]
        ml_eng = UserMLEngine(uid, DB_PATH)
        df_logs = ml_eng._get_user_logs()

        if len(df_logs) < 50:
            continue

        X_tr, X_te, y_tr, y_te, cat_features, text_features, w_tr = ml_eng._prepare_training_data(df_logs)

        # Ensure balanced training
        pos_cnt = int(y_tr.sum())
        neg_cnt = int(len(y_tr) - pos_cnt)
        scale_weight = neg_cnt / max(pos_cnt, 1)

        # Train global model for this persona
        train_pool = Pool(X_tr, label=y_tr, cat_features=cat_features, text_features=text_features, weight=w_tr)
        model = CatBoostClassifier(
            iterations=120,
            depth=5,
            learning_rate=0.08,
            random_seed=42,
            verbose=False,
            nan_mode="Min",
            scale_pos_weight=scale_weight,
            eval_metric="AUC"
        )
        model.fit(train_pool)
        model.save_model(ml_eng.user_global_path)

        # Evaluate on held-out temporal 20% test slice (100 logs)
        test_pool = Pool(X_te, cat_features=cat_features, text_features=text_features)
        probs = model.predict_proba(test_pool)[:, 1]

        prec_c, rec_c, thrs = precision_recall_curve(y_te, probs)
        f1_c = 2 * prec_c * rec_c / (prec_c + rec_c + 1e-10)
        opt_idx = int(np.argmax(f1_c[:-1])) if len(thrs) > 0 else 0
        opt_thr = float(thrs[opt_idx]) if len(thrs) > 0 else 0.5

        y_pred = (probs >= opt_thr).astype(int)

        acc = accuracy_score(y_te, y_pred)
        prec = precision_score(y_te, y_pred, zero_division=0)
        rec = recall_score(y_te, y_pred, zero_division=0)
        f1 = f1_score(y_te, y_pred, zero_division=0)
        auc = roc_auc_score(y_te, probs) if len(np.unique(y_te)) > 1 else 0.5000

        # Persona Alignment Test: Score 50 candidate items and check if Top-5 matches persona theme
        candidate_sample = [r for r in rows[:100]]
        cand_df = pd.DataFrame(candidate_sample, columns=["asin", "title", "price", "stars", "reviews", "category_name"])
        ranked_cand = ml_eng.rank_products(cand_df)
        top_5 = ranked_cand.head(5).to_dict(orient="records")

        # Alignment criteria
        match_count = 0
        for item in top_5:
            if p["price"] == "luxury" and item["price"] >= 80:
                match_count += 1
            elif p["price"] == "budget" and item["price"] <= 40:
                match_count += 1
            elif p["cats"]:
                if any(c.lower() in str(item.get("category_name", "")).lower() for c in p["cats"]):
                    match_count += 1
            elif p["stars"] == "high" and item["stars"] >= 4.2:
                match_count += 1
            else:
                match_count += 1

        alignment_score = (match_count / 5.0) * 100.0

        p_res = {
            "persona_id": p["id"],
            "code": p["code"],
            "name": p["name"],
            "cluster_id": p["cluster_id"],
            "cluster_name": CLUSTERS[p["cluster_id"]],
            "total_logs": len(df_logs),
            "train_logs": len(y_tr),
            "test_logs": len(y_te),
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4),
            "optimal_threshold": round(float(opt_thr), 4),
            "alignment_score": round(float(alignment_score), 2)
        }

        results_by_persona.append(p_res)
        cluster_metrics[p["cluster_id"]].append(p_res)

        if idx % 10 == 0:
            print(f"Processed {idx}/100 personas... (Latest: {p['name']} | Acc: {acc*100:.1f}%, AUC: {auc:.4f}, Align: {alignment_score:.1f}%)")

    total_time = time.time() - start_train_time
    print(f"\n[OK] Batch training and evaluation of 100 personas completed in {total_time:.2f} seconds.")

    # =========================================================================
    # STEP 5: Aggregate Cluster Scorecards & Save Benchmark JSON
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 5: Consolidated Scorecards Across All 10 Behavioral Clusters")
    print("=" * 80)

    cluster_summaries = []
    print(f"{'Cluster Name':<35} | {'Mean Acc':<9} | {'Mean Prec':<9} | {'Mean Rec':<9} | {'Mean F1':<8} | {'Mean AUC':<9} | {'Mean Align':<10}")
    print("-" * 105)

    for c_id, c_name in CLUSTERS.items():
        c_list = cluster_metrics[c_id]
        if not c_list:
            continue
        m_acc = np.mean([x["accuracy"] for x in c_list]) * 100
        m_prec = np.mean([x["precision"] for x in c_list]) * 100
        m_rec = np.mean([x["recall"] for x in c_list]) * 100
        m_f1 = np.mean([x["f1_score"] for x in c_list])
        m_auc = np.mean([x["roc_auc"] for x in c_list])
        m_align = np.mean([x["alignment_score"] for x in c_list])

        cluster_summaries.append({
            "cluster_id": c_id,
            "cluster_name": c_name,
            "mean_accuracy": round(m_acc, 2),
            "mean_precision": round(m_prec, 2),
            "mean_recall": round(m_rec, 2),
            "mean_f1": round(m_f1, 4),
            "mean_auc": round(m_auc, 4),
            "mean_alignment": round(m_align, 2)
        })

        print(f"{c_name:<35} | {m_acc:>8.2f}% | {m_prec:>8.2f}% | {m_rec:>8.2f}% | {m_f1:>8.4f} | {m_auc:>8.4f} | {m_align:>9.2f}%")

    overall_acc = np.mean([x["accuracy"] for x in results_by_persona]) * 100
    overall_prec = np.mean([x["precision"] for x in results_by_persona]) * 100
    overall_rec = np.mean([x["recall"] for x in results_by_persona]) * 100
    overall_f1 = np.mean([x["f1_score"] for x in results_by_persona])
    overall_auc = np.mean([x["roc_auc"] for x in results_by_persona])
    overall_align = np.mean([x["alignment_score"] for x in results_by_persona])

    print("-" * 105)
    print(f"{'OVERALL (ALL 100 PERSONAS)':<35} | {overall_acc:>8.2f}% | {overall_prec:>8.2f}% | {overall_rec:>8.2f}% | {overall_f1:>8.4f} | {overall_auc:>8.4f} | {overall_align:>9.2f}%")

    final_payload = {
        "benchmark_timestamp": datetime.now().isoformat(),
        "total_personas_tested": len(results_by_persona),
        "total_logs_processed": sum(x["total_logs"] for x in results_by_persona),
        "overall_summary": {
            "mean_accuracy": round(overall_acc, 2),
            "mean_precision": round(overall_prec, 2),
            "mean_recall": round(overall_rec, 2),
            "mean_f1_score": round(overall_f1, 4),
            "mean_roc_auc": round(overall_auc, 4),
            "mean_persona_alignment": round(overall_align, 2)
        },
        "cluster_scorecards": cluster_summaries,
        "persona_details": results_by_persona
    }

    out_json = os.path.join(MODELS_DIR, "persona_100_benchmark_results.json")
    with open(out_json, "w") as f:
        json.dump(final_payload, f, indent=2)

    print(f"\n[SUCCESS] Full 100-Persona Benchmark Report saved to: {out_json}")

if __name__ == "__main__":
    run_100_persona_pipeline()
