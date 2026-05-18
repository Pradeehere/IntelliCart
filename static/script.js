document.addEventListener('DOMContentLoaded', () => {
    // API Base URL
    const API_BASE = '/api';

    // Elements
    const userSelect = document.getElementById('user-select');
    const shopperWorkspace = document.getElementById('shopper-workspace');
    const purchaseHistoryContainer = document.getElementById('purchase-history-container');
    const purchaseHistoryGrid = document.getElementById('purchase-history-grid');
    
    // Algorithmic pill selector
    const algoPills = document.querySelectorAll('.algo-pill');
    const btnRecommend = document.getElementById('btn-recommend');
    const recLoading = document.getElementById('rec-loading');
    const recError = document.getElementById('rec-error');
    const recMessage = document.getElementById('rec-message');
    const recGrid = document.getElementById('rec-grid');
    
    // Heatmap Elements
    const heatmapLoading = document.getElementById('heatmap-loading');
    const heatmapError = document.getElementById('heatmap-error');
    const heatmapTable = document.getElementById('heatmap-table');

    // Simulated Shopping Elements
    const productSelect = document.getElementById('product-select');
    const ratingForm = document.getElementById('rating-form');
    const starInputs = document.querySelectorAll('.star-input');
    const ratingValue = document.getElementById('rating-value');
    const btnSubmitRating = document.getElementById('btn-submit-rating');
    const formMessage = document.getElementById('form-message');

    // Dashboard Elements
    const dashboardLoading = document.getElementById('dashboard-loading');
    const dashboardError = document.getElementById('dashboard-error');
    const dashboardGrid = document.getElementById('dashboard-grid');
    const statSparsity = document.getElementById('stat-sparsity');
    const statUsers = document.getElementById('stat-users');
    const statProducts = document.getElementById('stat-products');
    const statRatings = document.getElementById('stat-ratings');
    const statLatency = document.getElementById('stat-latency');

    // Selected Algorithm State
    let selectedAlgo = 'user-based';

    // Init
    fetchUsers();
    fetchProducts();
    fetchHeatmap();
    fetchAnalytics();

    // Algo Pill Click Listeners
    algoPills.forEach(pill => {
        pill.addEventListener('click', (e) => {
            algoPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            selectedAlgo = pill.getAttribute('data-algo');
            
            // If recommendations are showing, clear them so they can be re-fetched with new algo
            recGrid.classList.add('hidden');
            recMessage.classList.add('hidden');
            recError.classList.add('hidden');
        });
    });

    // Event Listeners
    userSelect.addEventListener('change', async (e) => {
        const userId = e.target.value;
        if (userId) {
            btnRecommend.disabled = false;
            shopperWorkspace.classList.remove('hidden');
            await fetchUserHistory(userId);
            
            // Clear recommendations on user change
            recGrid.classList.add('hidden');
            recMessage.classList.add('hidden');
            recError.classList.add('hidden');
            recGrid.innerHTML = '';
            
            // Reset feedback form
            resetFeedbackForm();
        }
    });

    btnRecommend.addEventListener('click', async () => {
        const userId = userSelect.value;
        if (!userId) return;
        
        await fetchRecommendations(userId, selectedAlgo);
    });

    // Star Rating Click Logic
    starInputs.forEach(star => {
        star.addEventListener('click', () => {
            const rating = parseInt(star.getAttribute('data-rating'));
            ratingValue.value = rating;
            btnSubmitRating.disabled = false;

            starInputs.forEach(s => {
                const sRating = parseInt(s.getAttribute('data-rating'));
                if (sRating <= rating) {
                    s.textContent = '★';
                    s.classList.add('active');
                } else {
                    s.textContent = '☆';
                    s.classList.remove('active');
                }
            });
        });
    });

    // Submit Simulation Rating
    ratingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userId = userSelect.value;
        const productId = productSelect.value;
        const rating = ratingValue.value;

        if (!userId || !productId || !rating) return;

        try {
            btnSubmitRating.disabled = true;
            formMessage.classList.add('hidden');

            const response = await fetch(`${API_BASE}/rate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    product_id: productId,
                    rating: parseInt(rating)
                })
            });

            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.error || 'Failed to submit rating');

            formMessage.textContent = 'Purchase recorded successfully!';
            formMessage.className = 'info-msg';
            formMessage.classList.remove('hidden');

            // Refresh user history, heatmap, and analytics in real-time
            await fetchUserHistory(userId);
            await fetchHeatmap();
            await fetchAnalytics();

            // Clear recommendations so the user has to request fresh ones
            recGrid.classList.add('hidden');
            recMessage.classList.add('hidden');
            
            // Reset feedback form input states
            resetFeedbackForm();

            // Fade message away after 3 seconds
            setTimeout(() => {
                formMessage.classList.add('hidden');
            }, 3000);

        } catch (error) {
            console.error('Error submitting rating:', error);
            formMessage.textContent = `Error: ${error.message}`;
            formMessage.className = 'error-msg';
            formMessage.classList.remove('hidden');
            btnSubmitRating.disabled = false;
        }
    });

    function resetFeedbackForm() {
        productSelect.value = '';
        ratingValue.value = '';
        btnSubmitRating.disabled = true;
        starInputs.forEach(s => {
            s.textContent = '☆';
            s.classList.remove('active');
        });
    }

    // Fetch Users
    async function fetchUsers() {
        try {
            const response = await fetch(`${API_BASE}/users`);
            const data = await response.json().catch(() => ({}));
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch users');
            }
            if (data.error) {
                throw new Error(data.error);
            }

            userSelect.innerHTML = '<option value="" disabled selected>Select a user...</option>';
            data.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user;
                option.textContent = `User ${user}`;
                userSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching users:', error);
            userSelect.innerHTML = '<option value="" disabled selected>Error loading users</option>';
        }
    }

    // Fetch Products (Unique listings for selector form)
    async function fetchProducts() {
        try {
            const response = await fetch(`${API_BASE}/products`);
            const data = await response.json().catch(() => ({}));

            if (!response.ok) throw new Error(data.error || 'Failed to fetch products');

            productSelect.innerHTML = '<option value="" disabled selected>Choose product...</option>';
            data.products.forEach(prod => {
                const option = document.createElement('option');
                option.value = prod.product_id;
                option.textContent = `${prod.product_name} (${prod.category})`;
                productSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching products:', error);
            productSelect.innerHTML = '<option value="" disabled selected>Error loading products</option>';
        }
    }

    // Fetch User History
    async function fetchUserHistory(userId) {
        try {
            purchaseHistoryGrid.innerHTML = '';

            const response = await fetch(`${API_BASE}/user/${userId}`);
            const data = await response.json().catch(() => ({}));
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch user history');
            }
            if (data.error) {
                throw new Error(data.error);
            }

            if (data.ratings && data.ratings.length > 0) {
                data.ratings.forEach(item => {
                    purchaseHistoryGrid.appendChild(createHistoryCard(item));
                });
            } else {
                purchaseHistoryGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #64748b;">No purchases logged yet.</div>';
            }
        } catch (error) {
            console.error('Error fetching user history:', error);
            alert(`Unable to load history: ${error.message}`);
        }
    }

    // Fetch Recommendations
    async function fetchRecommendations(userId, endpoint) {
        try {
            // UI State: Loading
            recGrid.classList.add('hidden');
            recMessage.classList.add('hidden');
            recError.classList.add('hidden');
            recLoading.classList.remove('hidden');
            btnRecommend.disabled = true;

            const response = await fetch(`${API_BASE}/recommend/${endpoint}/${userId}`);
            
            // Artificial delay for smooth animation experience
            await new Promise(r => setTimeout(r, 600));

            const data = await response.json().catch(() => ({}));
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch recommendations');
            }
            if (data.error) {
                throw new Error(data.error);
            }

            // UI State: Complete
            recLoading.classList.add('hidden');
            btnRecommend.disabled = false;

            // Render computed latency if present in response
            if (data.latency !== undefined) {
                statLatency.textContent = `${data.latency} ms`;
            }

            if (data.message && (!data.recommendations || data.recommendations.length === 0)) {
                recMessage.textContent = data.message;
                recMessage.classList.remove('hidden');
                return;
            }

            recGrid.innerHTML = '';
            data.recommendations.forEach(item => {
                recGrid.appendChild(createRecommendationCard(item));
            });
            recGrid.classList.remove('hidden');

        } catch (error) {
            console.error('Error fetching recommendations:', error);
            recLoading.classList.add('hidden');
            btnRecommend.disabled = false;
            recError.textContent = `Error: ${error.message}`;
            recError.classList.remove('hidden');
        }
    }

    // Fetch Heatmap
    async function fetchHeatmap() {
        try {
            const response = await fetch(`${API_BASE}/similarity-map`);
            const data = await response.json().catch(() => ({}));
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch similarity map');
            }
            if (data.error) {
                throw new Error(data.error);
            }

            heatmapLoading.classList.add('hidden');
            
            if (data.users && data.matrix) {
                renderHeatmap(data.users, data.matrix);
                heatmapTable.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error fetching heatmap:', error);
            heatmapLoading.classList.add('hidden');
            heatmapError.textContent = `Could not load similarity map: ${error.message}`;
            heatmapError.classList.remove('hidden');
        }
    }

    // Fetch Analytics
    async function fetchAnalytics() {
        try {
            dashboardLoading.classList.remove('hidden');
            dashboardGrid.classList.add('hidden');
            dashboardError.classList.add('hidden');

            const response = await fetch(`${API_BASE}/analytics`);
            const data = await response.json().catch(() => ({}));

            if (!response.ok) throw new Error(data.error || 'Failed to fetch analytics');

            statSparsity.textContent = data.sparsity || '0.0%';
            statUsers.textContent = data.users || '0';
            statProducts.textContent = data.products || '0';
            statRatings.textContent = data.ratings || '0';

            dashboardLoading.classList.add('hidden');
            dashboardGrid.classList.remove('hidden');
        } catch (error) {
            console.error('Error fetching analytics:', error);
            dashboardLoading.classList.add('hidden');
            dashboardError.textContent = `Could not load analytics metrics: ${error.message}`;
            dashboardError.classList.remove('hidden');
        }
    }

    // Helpers
    function getCategoryClass(category) {
        const cat = category.toLowerCase().replace(/[^a-z0-9]/g, '');
        const validCats = ['smartphones', 'audio', 'wearables', 'laptops', 'televisions', 
                           'cameras', 'accessories', 'storage', 'networking', 'peripherals', 'monitors'];
        return validCats.includes(cat) ? `cat-${cat}` : 'cat-default';
    }

    function createHistoryCard(item) {
        const card = document.createElement('div');
        card.className = 'card animate-card';
        
        let stars = '⭐'.repeat(item.rating) + '☆'.repeat(5 - item.rating);
        
        card.innerHTML = `
            <span class="badge ${getCategoryClass(item.category)}">${item.category}</span>
            <h4 class="card-title">${item.product_name}</h4>
            <div class="star-rating">${stars}</div>
            <p>Rating: ${item.rating}/5</p>
        `;
        return card;
    }

    function createRecommendationCard(item) {
        const card = document.createElement('div');
        card.className = 'card animate-card';
        
        // Progress bar calculation (percentage of 5.0)
        const percent = Math.round((item.predicted_rating / 5.0) * 100);
        
        card.innerHTML = `
            <span class="badge ${getCategoryClass(item.category)}">${item.category}</span>
            <h4 class="card-title">${item.product_name}</h4>
            <div class="score-text">⭐ ${item.predicted_rating.toFixed(1)} / 5.0</div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: ${percent}%;"></div>
            </div>
            <p class="rec-reason">${item.reason}</p>
        `;
        return card;
    }

    function renderHeatmap(users, matrix) {
        heatmapTable.innerHTML = '';
        
        // Header Row
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.appendChild(document.createElement('th')); // empty top-left
        
        users.forEach(user => {
            const th = document.createElement('th');
            th.textContent = user;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        heatmapTable.appendChild(thead);
        
        // Body Rows
        const tbody = document.createElement('tbody');
        for (let i = 0; i < users.length; i++) {
            const tr = document.createElement('tr');
            
            // Row header
            const th = document.createElement('th');
            th.textContent = users[i];
            tr.appendChild(th);
            
            // Cells
            for (let j = 0; j < users.length; j++) {
                const td = document.createElement('td');
                const score = matrix[i][j];
                
                td.textContent = score.toFixed(2);
                
                // Color interpolation: white (0) to light blue (0.5) to dark navy (1.0)
                let r, g, b;
                if (score >= 0.5) {
                    const t = (score - 0.5) / 0.5;
                    r = Math.round(147 + t * (15 - 147));
                    g = Math.round(197 + t * (23 - 197));
                    b = Math.round(253 + t * (42 - 253));
                } else {
                    const t = score / 0.5;
                    r = Math.round(255 + t * (147 - 255));
                    g = Math.round(255 + t * (197 - 255));
                    b = Math.round(255 + t * (253 - 255));
                }
                
                td.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
                
                if (score > 0.6) {
                    td.classList.add('cell-score');
                }
                
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
        heatmapTable.appendChild(tbody);
    }
});
