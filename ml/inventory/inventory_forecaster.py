import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from ml.utils.logger import logger
from ml.feature_engineering.product_features import ProductFeatureGenerator

class EnterpriseInventoryForecaster:
    """
    Enterprise Inventory Intelligence & Stockout Prevention Engine.
    Calculates Safety Stock, Reorder Point (ROP), Reorder Quantity (EOQ approximation),
    Lead Time demand buffers, Warehouse Utilization, and Automated Low Stock Alerts.
    """
    def __init__(self, service_level_z: float = 1.65): # 1.65 = 95% service level
        self.service_level_z = service_level_z
        self.feature_generator = ProductFeatureGenerator()

    def analyze_inventory_health(self, df_products: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Processes entire SKU catalog to predict stockout dates, calculate safety stock,
        and generate automated reorder alerts.
        """
        logger.info("Executing Enterprise Inventory Intelligence health audit...")
        df_p = self.feature_generator.generate_product_features(df_products)
        
        results = []
        total_warehouse_capacity_units = 10000
        total_current_stock = int(df_p['stock'].sum()) if 'stock' in df_p.columns else 0
        warehouse_utilization_pct = round((total_current_stock / total_warehouse_capacity_units) * 100, 1)
        
        for _, row in df_p.iterrows():
            pid = int(row['id']) if 'id' in row else 0
            sku = str(row.get('sku', f"SKU-{pid:04d}"))
            title = str(row.get('title', f"Product {pid}"))
            category = str(row.get('category', 'General'))
            stock = int(row.get('stock', 50))
            price = float(row.get('price', 49.99))
            daily_vel = float(row.get('daily_velocity', 2.0))
            lead_time = int(row.get('supplier_lead_time_days', 7))
            holding_cost = float(row.get('unit_holding_cost', price * 0.02))
            
            # 1. Calculate Safety Stock
            # Formula: Z * sqrt(Lead Time) * std_dev_daily_demand
            std_dev_demand = max(0.5, daily_vel * 0.35)
            safety_stock = int(np.ceil(self.service_level_z * np.sqrt(lead_time) * std_dev_demand))
            
            # 2. Reorder Point (ROP)
            # ROP = (Daily Velocity * Lead Time) + Safety Stock
            rop = int(np.ceil((daily_vel * lead_time) + safety_stock))
            
            # 3. Economic Order Quantity (EOQ approximation)
            # EOQ = sqrt((2 * Annual Demand * Order Cost) / Holding Cost)
            annual_demand = daily_vel * 365.0
            order_cost = 50.0 # Fixed supplier order processing fee
            eoq = int(np.ceil(np.sqrt((2.0 * annual_demand * order_cost) / max(0.5, holding_cost))))
            
            # 4. Days Until Stockout & Restock Date
            days_left = int(stock / daily_vel) if daily_vel > 0 else 999
            restock_date = (datetime.date.today() + datetime.timedelta(days=max(0, days_left - lead_time))).strftime("%Y-%m-%d")
            
            # 5. Determine Alert Status & Action
            if stock <= safety_stock or days_left <= lead_time:
                status = "Critical Out of Stock Risk"
                action = f"IMMEDIATE REORDER REQUIRED: Order {eoq} units immediately. Stock will deplete before supplier lead time ({lead_time} days)."
            elif stock <= rop or days_left <= 15:
                status = "Restock Recommended"
                action = f"SCHEDULE REORDER: Stock reached Reorder Point ({rop} units). Submit purchase order for {eoq} units within {max(1, days_left - lead_time)} days."
            else:
                status = "Healthy Inventory Buffer"
                action = f"OPTIMAL STOCK: Current stock ({stock} units) exceeds Reorder Point ({rop} units). No action required."
                
            results.append({
                "product_id": pid,
                "sku": sku,
                "title": title,
                "category": category,
                "quantity": stock,
                "price": price,
                "daily_velocity": f"{daily_vel} units/day",
                "days_until_stockout": days_left,
                "supplier_lead_time_days": lead_time,
                "safety_stock_units": safety_stock,
                "reorder_point_rop": rop,
                "optimal_reorder_qty_eoq": eoq,
                "projected_restock_date": restock_date,
                "total_inventory_value": round(stock * price, 2),
                "status": status,
                "ai_recommendation": action
            })
            
        # Sort by urgency (days until stockout ascending)
        results = sorted(results, key=lambda x: x["days_until_stockout"])
        logger.info(f"Inventory audit completed across {len(results)} SKUs. Warehouse utilization: {warehouse_utilization_pct}%.")
        return results

    def get_warehouse_metrics_summary(self, sku_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Returns macro warehouse KPI dashboard metrics."""
        total_skus = len(sku_reports)
        if total_skus == 0:
            return {}
            
        critical_count = sum(1 for r in sku_reports if r["status"] == "Critical Out of Stock Risk")
        warning_count = sum(1 for r in sku_reports if r["status"] == "Restock Recommended")
        healthy_count = sum(1 for r in sku_reports if r["status"] == "Healthy Inventory Buffer")
        
        total_val = sum(r["total_inventory_value"] for r in sku_reports)
        total_units = sum(r["quantity"] for r in sku_reports)
        
        return {
            "total_skus_monitored": total_skus,
            "total_inventory_valuation": round(total_val, 2),
            "total_units_in_stock": total_units,
            "warehouse_utilization_pct": round(min(100.0, (total_units / 10000.0) * 100), 1),
            "status_breakdown": {
                "critical": critical_count,
                "warning": warning_count,
                "healthy": healthy_count
            },
            "immediate_reorders_needed": critical_count + warning_count
        }
