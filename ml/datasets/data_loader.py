import datetime
import random
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger
from ml.configs import DATASETS_DIR

class EnterpriseDataLoader:
    """
    Enterprise Data Loader for Retail Intelligence Platform.
    Extracts data from database or synthesizes realistic historical enterprise datasets
    for training, evaluation, and benchmark testing.
    """
    def __init__(self, db_session=None):
        self.db = db_session

    def load_sales_forecasting_data(self, num_days: int = 730) -> pd.DataFrame:
        """
        Loads 2 years (730 days) of daily retail sales and revenue time-series data.
        Includes seasonal trends, weekend spikes, holiday multipliers, and marketing spend.
        """
        logger.info(f"Loading/Generating {num_days} days of enterprise sales time-series data...")
        try:
            if self.db:
                from backend.models.models import SalesHistory
                sales = self.db.query(SalesHistory).all()
                if len(sales) > 50:
                    df = pd.DataFrame([{
                        "date": s.date,
                        "units_sold": s.units_sold,
                        "revenue": s.revenue,
                        "profit": s.profit
                    } for s in sales])
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.groupby("date").agg({"units_sold": "sum", "revenue": "sum", "profit": "sum"}).reset_index()
                    if len(df) >= 30:
                        logger.info("Successfully extracted real database sales history.")
                        return df
        except Exception as e:
            logger.debug(f"Database extraction fallback triggered: {e}")

        # Generate realistic 2-year enterprise data
        start_date = datetime.date.today() - datetime.timedelta(days=num_days)
        dates = [start_date + datetime.timedelta(days=i) for i in range(num_days)]
        
        data = []
        base_revenue = 12000.0
        
        for idx, d in enumerate(dates):
            # Day of week effect (Friday-Sunday spike)
            dow = d.weekday()
            weekend_mult = 1.35 if dow in [4, 5, 6] else 1.0
            
            # Seasonality (Q4 Holiday spike in Nov/Dec)
            month = d.month
            seasonal_mult = 1.60 if month in [11, 12] else (1.15 if month in [6, 7] else 1.0)
            
            # Holiday indicators (Black Friday, Cyber Monday, Prime Day)
            is_festival = 1 if (month == 11 and d.day >= 20) or (month == 7 and 10 <= d.day <= 15) else 0
            festival_mult = 2.2 if is_festival else 1.0
            
            # Trend growth over 2 years (+25% annual growth)
            trend_mult = 1.0 + (idx / num_days) * 0.50
            
            # Random noise & marketing campaign boost
            marketing_spend = round(random.uniform(500.0, 3000.0) * festival_mult, 2)
            noise = random.uniform(0.88, 1.12)
            
            daily_rev = round(base_revenue * weekend_mult * seasonal_mult * festival_mult * trend_mult * noise, 2)
            daily_units = int(daily_rev / random.uniform(85.0, 140.0))
            daily_profit = round(daily_rev * random.uniform(0.24, 0.32), 2)
            
            data.append({
                "date": pd.to_datetime(d),
                "revenue": daily_rev,
                "units_sold": daily_units,
                "profit": daily_profit,
                "marketing_spend": marketing_spend,
                "day_of_week": dow,
                "is_weekend": 1 if dow in [5, 6] else 0,
                "month": month,
                "is_festival": is_festival
            })
            
        df = pd.DataFrame(data)
        df.to_csv(DATASETS_DIR / "synthetic_sales_forecasting.csv", index=False)
        logger.info(f"Generated {len(df)} records of synthetic sales forecasting data.")
        return df

    def load_customer_churn_data(self, num_customers: int = 2500) -> pd.DataFrame:
        """
        Loads or generates rich customer behavior dataset for Churn Prediction and Segmentation.
        Features: recency, frequency, monetary, support tickets, app visits, discount sensitivity.
        """
        logger.info(f"Loading/Generating customer churn and RFM dataset ({num_customers} profiles)...")
        try:
            if self.db:
                from backend.models.models import User, Order
                users = self.db.query(User).filter(User.role == "customer").all()
                if len(users) > 20:
                    data = []
                    now = datetime.datetime.utcnow()
                    for u in users:
                        orders = u.orders
                        freq = len(orders)
                        monetary = sum(o.total_amount for o in orders)
                        last_order = max([o.created_at for o in orders]) if orders else u.created_at
                        recency = (now - last_order).days
                        data.append({
                            "user_id": u.id,
                            "email": u.email,
                            "recency": recency,
                            "frequency": freq,
                            "monetary": monetary,
                            "support_tickets": random.randint(0, 5),
                            "app_logins_30d": random.randint(1, 45),
                            "discount_sensitivity": round(random.uniform(0.1, 0.8), 2),
                            "churned": 1 if recency > 60 or freq == 0 else 0
                        })
                    return pd.DataFrame(data)
        except Exception as e:
            logger.debug(f"Database extraction fallback triggered: {e}")

        # Synthetic generation with realistic correlations
        np.random.seed(42)
        user_ids = np.arange(10001, 10001 + num_customers)
        
        # 3 archetypes: VIP (20%), Regular (50%), At-Risk/Inactive (30%)
        archetypes = np.random.choice(["VIP", "Regular", "At-Risk"], size=num_customers, p=[0.20, 0.50, 0.30])
        
        data = []
        for uid, arch in zip(user_ids, archetypes):
            if arch == "VIP":
                recency = np.random.randint(1, 15)
                frequency = np.random.randint(8, 45)
                monetary = round(np.random.uniform(1200.0, 8500.0), 2)
                tickets = np.random.randint(0, 2)
                logins = np.random.randint(20, 60)
                churned = 0 if np.random.random() > 0.05 else 1
            elif arch == "Regular":
                recency = np.random.randint(10, 45)
                frequency = np.random.randint(2, 10)
                monetary = round(np.random.uniform(250.0, 1500.0), 2)
                tickets = np.random.randint(0, 3)
                logins = np.random.randint(5, 25)
                churned = 0 if np.random.random() > 0.18 else 1
            else: # At-Risk
                recency = np.random.randint(46, 180)
                frequency = np.random.randint(1, 4)
                monetary = round(np.random.uniform(40.0, 400.0), 2)
                tickets = np.random.randint(1, 6)
                logins = np.random.randint(0, 6)
                churned = 1 if np.random.random() > 0.25 else 0
                
            data.append({
                "user_id": int(uid),
                "recency": int(recency),
                "frequency": int(frequency),
                "monetary": float(monetary),
                "support_tickets": int(tickets),
                "app_logins_30d": int(logins),
                "avg_basket_size": round(monetary / max(1, frequency), 2),
                "discount_sensitivity": round(np.random.uniform(0.05, 0.95), 2),
                "returns_count": np.random.randint(0, max(1, frequency // 3)),
                "churned": int(churned)
            })
            
        df = pd.DataFrame(data)
        df.to_csv(DATASETS_DIR / "synthetic_customer_churn.csv", index=False)
        logger.info(f"Generated {len(df)} customer churn & segmentation records.")
        return df

    def load_inventory_data(self) -> pd.DataFrame:
        """Loads inventory SKU data with warehouse locations, lead times, and daily sales velocities."""
        logger.info("Loading inventory SKU dataset...")
        try:
            if self.db:
                from backend.models.models import Product
                prods = self.db.query(Product).all()
                if len(prods) > 0:
                    data = []
                    for p in prods:
                        inv = p.inventory
                        data.append({
                            "product_id": p.id,
                            "sku": inv.sku if inv else f"SKU-{p.id:04d}",
                            "title": p.title,
                            "category": p.category.name if p.category else "General",
                            "brand": p.brand.name if p.brand else "Brand",
                            "stock": inv.quantity if inv else p.stock,
                            "price": p.price,
                            "rating": p.rating,
                            "reviews_count": p.reviews_count,
                            "daily_velocity": round(max(0.5, p.reviews_count / 30.0), 2),
                            "supplier_lead_time_days": random.randint(3, 14),
                            "unit_holding_cost": round(p.price * 0.02, 2)
                        })
                    return pd.DataFrame(data)
        except Exception as e:
            logger.debug(f"Database inventory fallback: {e}")

        # Synthetic fallback
        categories = ["Electronics", "Smartphones", "Audio", "Home & Kitchen", "Gaming", "Sports"]
        data = []
        for i in range(1, 101):
            price = round(random.uniform(29.99, 1999.99), 2)
            velocity = round(random.uniform(0.5, 25.0), 2)
            stock = random.randint(0, 150)
            data.append({
                "product_id": i,
                "sku": f"SKU-PROD-{i:04d}",
                "title": f"Enterprise AI Retail Product {i}",
                "category": random.choice(categories),
                "brand": random.choice(["Apple", "Samsung", "Sony", "Dyson", "Logitech", "Nike"]),
                "stock": stock,
                "price": price,
                "rating": round(random.uniform(3.8, 5.0), 1),
                "reviews_count": random.randint(10, 4500),
                "daily_velocity": velocity,
                "supplier_lead_time_days": random.randint(3, 14),
                "unit_holding_cost": round(price * 0.02, 2)
            })
        return pd.DataFrame(data)
