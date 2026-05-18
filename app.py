# pip install -r requirements.txt
# python app.py
# Open http://localhost:5000 in browser

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import traceback
import time
from recommender import (
    get_all_users, get_user_ratings, get_user_based_recommendations,
    get_item_based_recommendations, get_hybrid_recommendations,
    get_similarity_map, get_all_products, add_user_rating,
    get_analytics_metrics
)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/users', methods=['GET'])
def api_users():
    try:
        users = get_all_users()
        return jsonify({"users": users}), 200
    except Exception as e:
        print("Error in /api/users:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['GET'])
def api_products():
    try:
        products = get_all_products()
        return jsonify({"products": products}), 200
    except Exception as e:
        print("Error in /api/products:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/<user_id>', methods=['GET'])
def api_user(user_id):
    try:
        data = get_user_ratings(user_id)
        if not data:
            return jsonify({"error": "User not found"}), 404
        return jsonify(data), 200
    except Exception as e:
        print(f"Error in /api/user/{user_id}:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommend/user-based/<user_id>', methods=['GET'])
def api_recommend_user_based(user_id):
    try:
        start_time = time.time()
        recommendations = get_user_based_recommendations(user_id)
        latency = round((time.time() - start_time) * 1000, 1) # ms
        
        if not recommendations:
            return jsonify({
                "user_id": user_id,
                "method": "user-based",
                "message": "No new recommendations \u2014 you've explored everything!",
                "recommendations": [],
                "latency": latency
            }), 200
            
        return jsonify({
            "user_id": user_id,
            "method": "user-based",
            "recommendations": recommendations,
            "latency": latency
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in /api/recommend/user-based/{user_id}:")
        traceback.print_exc()
        return jsonify({"error": "Internal server error: " + str(e)}), 500

@app.route('/api/recommend/item-based/<user_id>', methods=['GET'])
def api_recommend_item_based(user_id):
    try:
        start_time = time.time()
        recommendations = get_item_based_recommendations(user_id)
        latency = round((time.time() - start_time) * 1000, 1) # ms
        
        if not recommendations:
            return jsonify({
                "user_id": user_id,
                "method": "item-based",
                "message": "No new recommendations \u2014 you've explored everything!",
                "recommendations": [],
                "latency": latency
            }), 200
            
        return jsonify({
            "user_id": user_id,
            "method": "item-based",
            "recommendations": recommendations,
            "latency": latency
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in /api/recommend/item-based/{user_id}:")
        traceback.print_exc()
        return jsonify({"error": "Internal server error: " + str(e)}), 500

@app.route('/api/recommend/hybrid/<user_id>', methods=['GET'])
def api_recommend_hybrid(user_id):
    try:
        start_time = time.time()
        recommendations = get_hybrid_recommendations(user_id)
        latency = round((time.time() - start_time) * 1000, 1) # ms
        
        if not recommendations:
            return jsonify({
                "user_id": user_id,
                "method": "hybrid",
                "message": "No new recommendations \u2014 you've explored everything!",
                "recommendations": [],
                "latency": latency
            }), 200
            
        return jsonify({
            "user_id": user_id,
            "method": "hybrid",
            "recommendations": recommendations,
            "latency": latency
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error in /api/recommend/hybrid/{user_id}:")
        traceback.print_exc()
        return jsonify({"error": "Internal server error: " + str(e)}), 500

@app.route('/api/similarity-map', methods=['GET'])
def api_similarity_map():
    try:
        data = get_similarity_map()
        return jsonify(data), 200
    except Exception as e:
        print("Error in /api/similarity-map:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/rate', methods=['POST'])
def api_rate():
    try:
        req_data = request.get_json() or {}
        user_id = req_data.get('user_id')
        product_id = req_data.get('product_id')
        rating = req_data.get('rating')
        
        if not user_id or not product_id or rating is None:
            return jsonify({"error": "Missing user_id, product_id, or rating"}), 400
            
        add_user_rating(user_id, product_id, int(rating))
        return jsonify({"message": "Rating submitted successfully!"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print("Error in /api/rate:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    try:
        data = get_analytics_metrics()
        return jsonify(data), 200
    except Exception as e:
        print("Error in /api/analytics:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
