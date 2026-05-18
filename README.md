# 🛒 IntelliCart — Smart Recommendations, Smarter Shopping

IntelliCart is a highly aesthetic, full-stack **E-Commerce Collaborative Filtering Recommender System** that computes real-time product recommendations. It leverages User-Based, Item-Based, and Hybrid Content-Collaborative machine learning algorithms powered by Cosine Similarity and TF-IDF text features.

Designed as a premium, academic-grade portfolio showcase, the system is backed by a memory-efficient streaming pipeline that parses the raw 4.18 GB **UCSD Amazon Electronics Reviews dataset** and maps historical ratings to a sleek modern consumer electronics catalog.

---

## 🚀 Key Features

* **3-Engine Algorithm Suite**: Choose dynamically between:
  1. **User-Based Collaborative Filtering** (Weighted neighbors rating predictions).
  2. **Item-Based Collaborative Filtering** (Product-to-product similarities).
  3. **Hybrid Recommendation Engine** (50/50 blend of User-CF and content-based Scikit-learn TF-IDF text analysis).
* **Simulated Interactive Shopping**: Rate and purchase products live in the client UI using a premium star-rating interface and see the transaction dynamically log in the backend.
* **Real-Time Similarity Heatmap Grid**: Renders a live, responsive HSL-colored cosine similarity matrix mapping user relationships organically with zero fake profile duplication.
* **Diagnostics & Business Analytics**: Tracks real-time Matrix Sparsity %, active shopper/product counts, transaction size, and computational latencies down to the millisecond.
* **Big-Data Stream Parser**: Includes an optimized, memory-efficient streaming parser (`parse_amazon.py`) that reads gigabyte-scale datasets line-by-line in seconds without OOM crashes.

---

## 🛠️ Technology Stack

* **Frontend**: Pure HTML5, Semantic CSS3 (Glassmorphism, custom light/dark theme cards, hover micro-animations), ES6 JavaScript (Asynchronous fetch REST pipeline).
* **Backend**: Python 3, Flask, Flask-CORS.
* **Data Science / Machine Learning**: Pandas, NumPy, Scikit-learn (`TfidfVectorizer`).
* **Data Storage**: Local relational CSV transaction tables (`ratings.csv`).

---

## 🏃 Run the Project Locally

### 1. Prerequisites
Ensure you have Python 3 installed. Clone the repository and navigate into the project directory:
```bash
git clone <your-repository-url>
cd IntelliCart-Data-Mining
```

### 2. Install Dependencies
Install all required mathematical, server, and machine learning dependencies:
```bash
pip install -r requirements.txt
```

### 3. Start the Flask Server
Launch the development API backend server:
```bash
python app.py
```
By default, the server will launch in debug mode on **`http://localhost:5000`** (or `http://localhost:5001`).

### 4. Open the Interface
Open your browser and navigate to **`http://localhost:5000`** to experience the dashboard!

---

## 📊 Working with the Amazon Dataset (`Electronics_5.json`)

To demonstrate parsing large-scale datasets:
1. Download the **Electronics (5-core)** subset from Julian McAuley's [UCSD Amazon Product Review Dataset](https://meliza.hpl.hp.com/data/amazon/).
2. Place the `Electronics_5.json` file (approx. 4.18 GB) in the project root.
3. Run the memory-efficient streaming parser to compile a newly balanced matrix:
   ```bash
   python parse_amazon.py
   ```
This will automatically parse the last 3 years of data (2016-2018), map older ASIN codes to modern premium products, eliminate purchase vector duplicates, and output a perfect $88.9\%$ sparse benchmark catalog.

---

## 📂 Project Structure

```text
├── app.py                     # Flask API routing layer & response serializer
├── recommender.py             # Math engines (User-CF, Item-CF, Hybrid, Cosine Similarity)
├── parse_amazon.py            # Memory-efficient Amazon UCSD streaming parser pipeline
├── data_preprocessing.py      # Modern high-fidelity benchmark preprocessing utility
├── ratings.csv                # Active in-memory e-commerce ratings dataset
├── PROJECT_WALKTHROUGH.md     # Detailed mathematical equations & defense guides
├── templates/
│   └── index.html             # Sleek dashboard markup
├── static/
│   ├── style.css              # Custom styling design tokens & animation schemes
│   └── script.js              # REST endpoints coordinator & interactive UI handlers
└── requirements.txt           # Server & AI library dependencies
```

---

## 🎓 License
This project is open-source and available under the [MIT License](LICENSE).
