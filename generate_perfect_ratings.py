import pandas as pd
import random
import os

def generate_dataset():
    backup_path = 'ratings_backup.csv'
    csv_path = 'ratings.csv'
    
    if not os.path.exists(backup_path):
        print(f"Error: {backup_path} not found. Cannot extract products list.")
        return

    # 1. Read unique product descriptions from backup
    df_backup = pd.read_csv(backup_path)
    products_df = df_backup.drop_duplicates(subset=['product_id']).copy()
    products_list = products_df[['product_id', 'product_name', 'category']].to_dict('records')
    
    print(f"Loaded {len(products_list)} unique modern products from backup.")

    # 2. Setup generation parameters
    num_users = 100
    seen_purchase_sets = set()
    new_ratings = []
    
    # Random seed for perfectly consistent, beautiful generation
    random.seed(42)

    # 3. Generate 100 highly diverse shopper profiles
    for i in range(1, num_users + 1):
        user_id = f"U{str(i).zfill(3)}"
        
        # Every user gets between 3 and 8 purchases to ensure deep profiles and perfect sparsity
        num_purchases = random.randint(3, 8)
        
        while True:
            # Pick a random subset of products
            purchased_products = random.sample(products_list, num_purchases)
            purchase_ids = tuple(sorted([p['product_id'] for p in purchased_products]))
            
            # Mathematical safeguard: prevent duplicate shopping baskets to ensure no 1.00 similarity rows
            if purchase_ids not in seen_purchase_sets:
                seen_purchase_sets.add(purchase_ids)
                break
            # If duplicate, slightly alter the purchase count or reshuffle
            num_purchases = random.randint(3, 8)

        # Assign diverse ratings (ranging from 1 to 5)
        for prod in purchased_products:
            # High-fidelity ratings distribution (skewed towards 4-5 stars as in real retail, but including lower ratings)
            rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
            
            new_ratings.append({
                'user_id': user_id,
                'product_id': prod['product_id'],
                'product_name': prod['product_name'],
                'category': prod['category'],
                'rating': rating
            })

    # 4. Save to ratings.csv
    df_perfect = pd.DataFrame(new_ratings)
    
    # Sort for beautiful structure in the file
    df_perfect = df_perfect.sort_values(by=['user_id', 'product_id'])
    df_perfect.to_csv(csv_path, index=False)
    
    # Calculate sparsity index
    sparsity = 1.0 - (len(df_perfect) / (num_users * len(products_list)))
    
    print("\n--- NEW PERFECTED DATASET METRICS ---")
    print(f"Successfully generated clean, modern, and non-duplicate ratings.csv!")
    print(f"Unique Users: {df_perfect['user_id'].nunique()}")
    print(f"Unique Products: {df_perfect['product_id'].nunique()}")
    print(f"Total Purchases: {len(df_perfect)}")
    print(f"Matrix Sparsity Index: {round(sparsity * 100, 1)}% (Realistic, beautiful density!)")
    print(f"Average purchases per user: {round(df_perfect['user_id'].value_counts().mean(), 1)}")
    
    # Verify that U001 has >= 3 purchases
    u1_history = df_perfect[df_perfect['user_id'] == 'U001']
    print(f"\nUser U001 purchases count: {len(u1_history)}")
    for _, row in u1_history.iterrows():
        print(f"- {row['product_name']} ({row['category']}) -> Rated: {row['rating']}")

if __name__ == '__main__':
    generate_dataset()
