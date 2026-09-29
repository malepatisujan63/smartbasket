import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import json
import os
import random
from database import engine

class NCFModel(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim=32, hidden_layers=[64, 32, 16], dropout_rate=0.2):
        super(NCFModel, self).__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.item_embedding = nn.Embedding(num_items, embedding_dim)
        
        mlp_modules = []
        input_size = embedding_dim * 2
        for h_size in hidden_layers:
            mlp_modules.append(nn.Linear(input_size, h_size))
            mlp_modules.append(nn.ReLU())
            if dropout_rate > 0:
                mlp_modules.append(nn.Dropout(dropout_rate))
            input_size = h_size
            
        mlp_modules.append(nn.Linear(input_size, 1))
        mlp_modules.append(nn.Sigmoid())
        
        self.mlp = nn.Sequential(*mlp_modules)
        
    def forward(self, user_indices, item_indices):
        user_emb = self.user_embedding(user_indices)
        item_emb = self.item_embedding(item_indices)
        cat = torch.cat([user_emb, item_emb], dim=-1)
        return self.mlp(cat).squeeze(-1)

class InteractionDataset(Dataset):
    def __init__(self, data):
        self.users = torch.tensor([x[0] for x in data], dtype=torch.long)
        self.items = torch.tensor([x[1] for x in data], dtype=torch.long)
        self.labels = torch.tensor([x[2] for x in data], dtype=torch.float32)
        
    def __len__(self):
        return len(self.labels)
        
    def __getitem__(self, idx):
        return self.users[idx], self.items[idx], self.labels[idx]

class NCFEngine:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.model_path = os.path.join(base_dir, "ncf_model.pth")
        self.mappings_path = os.path.join(base_dir, "ncf_mappings.json")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.user_map = {}
        self.item_map = {}
        self.item_map_rev = {}
        
    def train(self, epochs=5, batch_size=256, neg_ratio=4):
        print(f"Starting NCF training on {self.device} with Hard Negative Mining...")
        
        # 1. Fetch data joined with category for in-category hard negatives
        query = """
            SELECT l.user_id, l.asin, p.category_name 
            FROM "UserLogs" l
            JOIN "Products" p ON l.asin = p.asin
            WHERE l.action IN ('view', 'cart', 'purchase')
            ORDER BY l.log_id DESC LIMIT 100000
        """
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            
        if len(df) < 100:
            print("Not enough data to train NCF.")
            return False
            
        # 2. Create mappings
        unique_users = df['user_id'].unique().tolist()
        unique_items = df['asin'].unique().tolist()
        
        self.user_map = {u: i for i, u in enumerate(unique_users)}
        self.item_map = {item: i for i, item in enumerate(unique_items)}
        self.item_map_rev = {i: item for i, item in enumerate(unique_items)}
        
        # Build category -> items mapping for hard negative mining
        cat_to_items = {}
        user_to_cats = {}
        for _, row in df.iterrows():
            u = self.user_map[row['user_id']]
            item_i = self.item_map[row['asin']]
            c = row.get("category_name")
            if c:
                cat_to_items.setdefault(c, []).append(item_i)
                user_to_cats.setdefault(u, set()).add(c)

        # 3. Prepare positive samples
        interactions = set()
        for _, row in df.iterrows():
            u_idx = self.user_map[row['user_id']]
            i_idx = self.item_map[row['asin']]
            interactions.add((u_idx, i_idx))
            
        data = []
        unique_item_count = len(unique_items)
        for u_idx, i_idx in interactions:
            data.append((u_idx, i_idx, 1.0)) # Positive
            
            # Generate negative samples: 50% hard in-category, 50% global random
            user_cats = list(user_to_cats.get(u_idx, []))
            for k in range(neg_ratio):
                neg_i = None
                if k % 2 == 0 and user_cats:
                    # Sample hard negative from same category
                    target_cat = random.choice(user_cats)
                    cand_pool = cat_to_items.get(target_cat, [])
                    if cand_pool:
                        for _ in range(10):
                            cand = random.choice(cand_pool)
                            if (u_idx, cand) not in interactions:
                                neg_i = cand
                                break

                # Global random negative fallback
                if neg_i is None:
                    attempts = 0
                    neg_i = random.randint(0, unique_item_count - 1)
                    while (u_idx, neg_i) in interactions and attempts < 15:
                        neg_i = random.randint(0, unique_item_count - 1)
                        attempts += 1

                if (u_idx, neg_i) not in interactions:
                    data.append((u_idx, neg_i, 0.0))
                
        # 4. DataLoader
        dataset = InteractionDataset(data)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # 5. Initialize Model
        self.model = NCFModel(num_users=len(unique_users), num_items=len(unique_items), dropout_rate=0.2).to(self.device)
        criterion = nn.BCELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # 6. Training Loop
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for users, items, labels in loader:
                users = users.to(self.device)
                items = items.to(self.device)
                labels = labels.to(self.device)
                
                optimizer.zero_grad()
                preds = self.model(users, items)
                loss = criterion(preds, labels)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss/len(loader):.4f}")
            
        # 7. Save
        torch.save(self.model.state_dict(), self.model_path)
        with open(self.mappings_path, 'w') as f:
            json.dump({
                "user_map": self.user_map,
                "item_map": self.item_map,
                "item_map_rev": self.item_map_rev
            }, f)
        print("NCF Training Complete and Saved.")
        return True

    def load(self):
        if not os.path.exists(self.model_path) or not os.path.exists(self.mappings_path):
            return False
            
        with open(self.mappings_path, 'r') as f:
            mappings = json.load(f)
            self.user_map = {int(k) if str(k).isdigit() else k: v for k, v in mappings["user_map"].items()}
            self.item_map = mappings["item_map"]
            # JSON dict keys are strings, convert back to int for item_map_rev
            self.item_map_rev = {int(k): v for k, v in mappings["item_map_rev"].items()}
            
        self.model = NCFModel(num_users=len(self.user_map), num_items=len(self.item_map)).to(self.device)
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.eval()
        return True
        
    def rank_items_for_user(self, user_id, items_to_rank):
        """
        user_id: raw user ID (int or str)
        items_to_rank: list of raw item IDs (list of str asins)
        Returns a sorted list of (asin, score) descending.
        """
        if not self.model:
            if not self.load():
                return None
                
        u_key = int(user_id) if int(user_id) in self.user_map else str(user_id)
        if u_key not in self.user_map:
            return None # Cold start user
            
        u_idx = self.user_map[u_key]
        
        # Filter to items the model knows about
        valid_items = [asin for asin in items_to_rank if asin in self.item_map]
        if not valid_items:
            return None
            
        i_indices = [self.item_map[asin] for asin in valid_items]
        
        u_tensor = torch.tensor([u_idx] * len(i_indices), dtype=torch.long).to(self.device)
        i_tensor = torch.tensor(i_indices, dtype=torch.long).to(self.device)
        
        with torch.no_grad():
            scores = self.model(u_tensor, i_tensor).cpu().numpy()
            
        results = list(zip(valid_items, scores))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def is_ready(self):
        return self.model is not None or self.load()

NCFRecommender = NCFEngine
