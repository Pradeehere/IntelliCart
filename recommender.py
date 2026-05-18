import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
import math
warnings.filterwarnings('ignore')

def load_data():
    try:
        return pd.read_csv('ratings.csv')
    except Exception:
        return pd.DataFrame()

def safe_float(val):
    if pd.isna(val) or math.isnan(val) or math.isinf(val):
        return 0.0
    return float(round(val, 1))

def safe_float_2(val):
    if pd.isna(val) or math.isnan(val) or math.isinf(val):
        return 0.0
    return float(round(val, 2))

def get_user_based_recommendations(target_user):
    df = load_data()
    if df.empty:
        raise ValueError("Dataset could not be loaded.")
    if target_user not in df['user_id'].values:
        raise ValueError(f"User {target_user} not found in the dataset.")
        
    user_item_matrix = df.pivot_table(index='user_id', columns='product_id', values='rating')
    user_item_matrix = user_item_matrix.fillna(0)
    
    user_sim = cosine_similarity(user_item_matrix)
    user_sim_df = pd.DataFrame(user_sim, index=user_item_matrix.index, columns=user_item_matrix.index)
    
    sim_scores = user_sim_df[target_user].drop(target_user)
    top_neighbors = sim_scores.sort_values(ascending=False).head(10)
    
    if top_neighbors.empty or top_neighbors.max() == 0:
        return []
        
    target_user_ratings = user_item_matrix.loc[target_user]
    unrated_products = target_user_ratings[target_user_ratings == 0].index.tolist()
    
    if not unrated_products:
        return []
        
    recommendations = []
    
    for product in unrated_products:
        weighted_sum = 0
        sim_sum = 0
        
        for neighbor_id, similarity in top_neighbors.items():
            neighbor_rating = user_item_matrix.loc[neighbor_id, product]
            if neighbor_rating > 0:
                weighted_sum += similarity * neighbor_rating
                sim_sum += similarity
                
        if sim_sum > 0:
            predicted_rating = weighted_sum / sim_sum
            recommendations.append((product, predicted_rating))
            
    recommendations.sort(key=lambda x: x[1], reverse=True)
    top_5 = recommendations[:5]
    
    result = []
    for product_id, pred_rating in top_5:
        product_info = df[df['product_id'] == product_id].iloc[0]
        
        result.append({
            "product_id": str(product_id),
            "product_name": str(product_info['product_name']),
            "category": str(product_info['category']),
            "predicted_rating": safe_float(pred_rating),
            "reason": "Users with similar taste loved this"
        })
        
    return result

def get_item_based_recommendations(target_user):
    df = load_data()
    if df.empty:
        raise ValueError("Dataset could not be loaded.")
    if target_user not in df['user_id'].values:
        raise ValueError(f"User {target_user} not found in the dataset.")
        
    user_item_matrix = df.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)
    item_user_matrix = user_item_matrix.T
    
    item_sim = cosine_similarity(item_user_matrix)
    item_sim_df = pd.DataFrame(item_sim, index=item_user_matrix.index, columns=item_user_matrix.index)
    
    target_user_ratings = user_item_matrix.loc[target_user]
    highly_rated = target_user_ratings[target_user_ratings >= 4].index.tolist()
    rated_products = target_user_ratings[target_user_ratings > 0].index.tolist()
    
    candidate_products = {}
    
    for product in highly_rated:
        similar_items = item_sim_df[product].sort_values(ascending=False).drop(product).head(5)
        
        for sim_product, sim_score in similar_items.items():
            if sim_product not in rated_products:
                if sim_product not in candidate_products or sim_score > candidate_products[sim_product]:
                    candidate_products[sim_product] = sim_score
                    
    sorted_candidates = sorted(candidate_products.items(), key=lambda x: x[1], reverse=True)[:5]
    
    if not sorted_candidates:
        return []

    result = []
    for product_id, sim_score in sorted_candidates:
        product_info = df[df['product_id'] == product_id].iloc[0]
        
        if pd.isna(sim_score) or math.isnan(sim_score) or math.isinf(sim_score):
            sim_score = 0.0
            
        pred_rating = 1.0 + (sim_score * 4.0)
        pred_rating = min(5.0, max(1.0, pred_rating))
        
        result.append({
            "product_id": str(product_id),
            "product_name": str(product_info['product_name']),
            "category": str(product_info['category']),
            "predicted_rating": safe_float(pred_rating),
            "reason": "Similar to products you rated highly"
        })
        
    return result

def get_hybrid_recommendations(target_user):
    df = load_data()
    if df.empty:
        raise ValueError("Dataset could not be loaded.")
    if target_user not in df['user_id'].values:
        raise ValueError(f"User {target_user} not found in the dataset.")

    # 1. Get Collaborative Scores (User-Based CF predicted ratings)
    user_item_matrix = df.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)
    user_sim = cosine_similarity(user_item_matrix)
    user_sim_df = pd.DataFrame(user_sim, index=user_item_matrix.index, columns=user_item_matrix.index)
    
    sim_scores = user_sim_df[target_user].drop(target_user)
    top_neighbors = sim_scores.sort_values(ascending=False).head(10)
    
    target_user_ratings = user_item_matrix.loc[target_user]
    unrated_products = target_user_ratings[target_user_ratings == 0].index.tolist()
    
    if not unrated_products:
        return []
        
    cf_scores = {}
    for product in unrated_products:
        weighted_sum = 0
        sim_sum = 0
        for neighbor_id, similarity in top_neighbors.items():
            neighbor_rating = user_item_matrix.loc[neighbor_id, product]
            if neighbor_rating > 0:
                weighted_sum += similarity * neighbor_rating
                sim_sum += similarity
        if sim_sum > 0:
            cf_scores[product] = weighted_sum / sim_sum

    # 2. Get Content-Based Scores
    # Prepare unique product profiles
    unique_products = df.drop_duplicates(subset=['product_id']).copy()
    unique_products['metadata'] = unique_products['product_name'] + " " + unique_products['category']
    unique_products = unique_products.set_index('product_id')
    
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(unique_products['metadata'])
    prod_sim = cosine_similarity(tfidf_matrix)
    prod_sim_df = pd.DataFrame(prod_sim, index=unique_products.index, columns=unique_products.index)
    
    # Get user highly rated products (rating >= 4)
    user_rated_df = df[df['user_id'] == target_user]
    user_liked = user_rated_df[user_rated_df['rating'] >= 4]['product_id'].tolist()
    
    # If no highly rated products, fall back to any rated products
    if not user_liked:
        user_liked = user_rated_df['product_id'].tolist()
        
    content_scores = {}
    for product in unrated_products:
        if user_liked and product in prod_sim_df.index:
            # Average similarity of unrated product to user's liked products
            similarities = [prod_sim_df.loc[product, liked] for liked in user_liked if liked in prod_sim_df.index]
            content_scores[product] = np.mean(similarities) if similarities else 0.0
        else:
            content_scores[product] = 0.0

    # 3. Hybrid Calculation
    hybrid_recommendations = []
    for product in unrated_products:
        cf_score = cf_scores.get(product, 0.0)
        # Normalize CF score (1 to 5 scale -> 0 to 1 scale)
        cf_normalized = (cf_score - 1.0) / 4.0 if cf_score > 0 else 0.0
        content_score = content_scores.get(product, 0.0)
        
        # Combine (50% CF, 50% Content)
        hybrid_normalized = 0.5 * cf_normalized + 0.5 * content_score
        
        # Scale back to 1.0 - 5.0
        predicted_rating = 1.0 + (hybrid_normalized * 4.0)
        
        # If no CF or Content overlap, default predicted rating to a small value
        if cf_score == 0.0 and content_score == 0.0:
            predicted_rating = 1.0
            
        predicted_rating = min(5.0, max(1.0, predicted_rating))
        hybrid_recommendations.append((product, predicted_rating))
        
    hybrid_recommendations.sort(key=lambda x: x[1], reverse=True)
    top_5 = hybrid_recommendations[:5]
    
    result = []
    for product_id, pred_rating in top_5:
        product_info = df[df['product_id'] == product_id].iloc[0]
        result.append({
            "product_id": str(product_id),
            "product_name": str(product_info['product_name']),
            "category": str(product_info['category']),
            "predicted_rating": safe_float(pred_rating),
            "reason": "Recommended based on your preferred product features & similar shopper tastes"
        })
        
    return result

def get_similarity_map():
    df = load_data()
    if df.empty:
        return {"users": [], "matrix": []}
        
    user_item_matrix = df.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)
    users = sorted(user_item_matrix.index.tolist())[:15]
    subset_matrix = user_item_matrix.loc[users]
    
    user_sim = cosine_similarity(subset_matrix)
    user_sim = np.nan_to_num(user_sim, nan=0.0, posinf=0.0, neginf=0.0)
    matrix_rounded = np.round(user_sim, 2).tolist()
    
    safe_matrix = [[safe_float_2(val) for val in row] for row in matrix_rounded]
    safe_users = [str(u) for u in users]
    
    return {
        "users": safe_users,
        "matrix": safe_matrix
    }
    
def get_all_users():
    df = load_data()
    if df.empty:
        return []
    return [str(u) for u in sorted(df['user_id'].unique().tolist())]

def get_all_products():
    df = load_data()
    if df.empty:
        return []
    unique_prods = df.drop_duplicates(subset=['product_id']).copy()
    prods = []
    for _, row in unique_prods.iterrows():
        prods.append({
            "product_id": str(row['product_id']),
            "product_name": str(row['product_name']),
            "category": str(row['category'])
        })
    prods.sort(key=lambda x: x['product_name'])
    return prods
    
def get_user_ratings(user_id):
    df = load_data()
    if df.empty:
        return None
    user_data = df[df['user_id'] == user_id]
    if user_data.empty:
        return None
    
    ratings = []
    for _, row in user_data.iterrows():
        ratings.append({
            "product_id": str(row['product_id']),
            "product_name": str(row['product_name']),
            "category": str(row['category']),
            "rating": int(row['rating'])
        })
        
    return {
        "user_id": str(user_id),
        "ratings": ratings
    }

def add_user_rating(user_id, product_id, rating):
    df = load_data()
    if df.empty:
        raise ValueError("Dataset could not be loaded.")
    
    product_info = df[df['product_id'] == product_id]
    if product_info.empty:
        raise ValueError(f"Product {product_id} not found.")
        
    product_name = product_info.iloc[0]['product_name']
    category = product_info.iloc[0]['category']
    
    existing = df[(df['user_id'] == user_id) & (df['product_id'] == product_id)]
    
    if not existing.empty:
        df.loc[(df['user_id'] == user_id) & (df['product_id'] == product_id), 'rating'] = int(rating)
    else:
        new_row = pd.DataFrame([{
            'user_id': str(user_id),
            'product_id': str(product_id),
            'product_name': str(product_name),
            'category': str(category),
            'rating': int(rating)
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        
    df.to_csv('ratings.csv', index=False)
    return True

def get_analytics_metrics():
    df = load_data()
    if df.empty:
        return {
            "sparsity": "0.0%",
            "users": 0,
            "products": 0,
            "ratings": 0
        }
    users = df['user_id'].nunique()
    products = df['product_id'].nunique()
    ratings_count = len(df)
    
    sparsity = 1.0 - (ratings_count / (users * products))
    sparsity_percent = f"{round(sparsity * 100, 1)}%"
    
    return {
        "sparsity": sparsity_percent,
        "users": int(users),
        "products": int(products),
        "ratings": int(ratings_count)
    }
