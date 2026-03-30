// Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// State Management
const state = {
    token: null,
    username: null,
    searchData: [],
    currentPage: 1,
    itemsPerPage: 8,
    selectedIdentityId: null,
    currentPeerGroupInfo: null
};

// Application Controller
const app = {

    // --- Initialization ---
    init() {
        // Check for existing token
        const savedToken = localStorage.getItem('iam_token');
        const savedUser = localStorage.getItem('iam_user');
        if (savedToken) {
            state.token = savedToken;
            state.username = savedUser;
            this.updateNav();
            this.showView('search-view');
        } else {
            this.showView('login-view');
        }
    },

    // --- Navigation & View Control ---
    showView(viewId) {
        document.querySelectorAll('.view').forEach(v => {
            if (v.id !== viewId) {
                v.classList.remove('active-view');
                setTimeout(() => v.classList.add('hidden'), 50); // Small timeout to allow transition
            }
        });

        const nextView = document.getElementById(viewId);
        nextView.classList.remove('hidden');
        // Force reflow for animation
        void nextView.offsetWidth;
        nextView.classList.add('active-view');

        if (viewId === 'login-view') {
            document.getElementById('top-nav').classList.add('hidden');
        } else {
            document.getElementById('top-nav').classList.remove('hidden');
        }

        if (viewId === 'anomalies-view') this.loadAnomalies();
        if (viewId === 'clusters-view') this.loadClusters();
    },

    updateNav() {
        document.getElementById('nav-user').innerHTML = `<i class="fa-solid fa-user-circle"></i> ${state.username}`;
    },

    // --- Authentication ---
    async login(event) {
        event.preventDefault();
        const usernameInput = document.getElementById('username').value;
        const passwordInput = document.getElementById('password').value;
        const errorMsg = document.getElementById('login-error');

        errorMsg.classList.add('hidden');

        const formData = new URLSearchParams();
        formData.append('username', usernameInput);
        formData.append('password', passwordInput);

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                state.token = data.access_token;
                state.username = usernameInput;
                localStorage.setItem('iam_token', state.token);
                localStorage.setItem('iam_user', state.username);

                this.updateNav();
                this.showView('search-view');
                // Auto-load some data
                this.searchIdentities('');
            } else {
                errorMsg.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Login error', error);
            errorMsg.innerText = "Network Error. Is the backend running?";
            errorMsg.classList.remove('hidden');
        }
    },

    logout() {
        state.token = null;
        state.username = null;
        localStorage.removeItem('iam_token');
        localStorage.removeItem('iam_user');
        this.showView('login-view');
    },

    // --- Identity Search ---
    async searchIdentities(queryParam = null) {
        const query = queryParam !== null ? queryParam : document.getElementById('search-query').value;

        const btn = document.querySelector('.search-bar-container .btn-primary');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Loading';

        try {
            const response = await fetch(`${API_BASE_URL}/identities/search?query=${encodeURIComponent(query)}&limit=100`, {
                headers: { 'Authorization': `Bearer ${state.token}` }
            });

            if (response.ok) {
                const data = await response.json();
                state.searchData = data;
                state.currentPage = 1; // Reset to page 1
                this.renderIdentitiesTable();

                document.getElementById('total-results').innerText = `${data.length} identities found`;
            } else if (response.status === 401) {
                this.logout();
            }
        } catch (error) {
            console.error('Search error', error);
        } finally {
            btn.innerHTML = originalText;
        }
    },

    renderIdentitiesTable() {
        const tbody = document.getElementById('identities-tbody');
        tbody.innerHTML = '';

        // Calculate pagination bounds
        const startIndex = (state.currentPage - 1) * state.itemsPerPage;
        const endIndex = startIndex + state.itemsPerPage;
        const pageData = state.searchData.slice(startIndex, endIndex);

        if (pageData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">No identities matched your search.</td></tr>`;
            return;
        }

        pageData.forEach((identity, index) => {
            const tr = document.createElement('tr');
            tr.style.animationDelay = `${index * 0.05}s`;
            tr.className = 'slide-up';

            tr.innerHTML = `
                <!-- <td><strong>${identity.identity_id}</strong></td> -->
                <td>${identity.name || 'N/A'}</td>
                <td>${identity.department}</td>
                <td>${identity.job_title}</td>
                <td>
                    <button class="btn btn-outline btn-sm" onclick="app.viewAccessReview('${identity.identity_id}')">
                        Review Access <i class="fa-solid fa-chevron-right ml-1"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        this.renderPagination();
    },

    renderPagination() {
        const container = document.getElementById('pagination-controls');
        container.innerHTML = '';

        const totalPages = Math.ceil(state.searchData.length / state.itemsPerPage);
        if (totalPages <= 1) return;

        // Prev Button
        const prevBtn = document.createElement('button');
        prevBtn.className = 'btn btn-outline btn-sm';
        prevBtn.innerHTML = '<i class="fa-solid fa-angle-left"></i>';
        prevBtn.disabled = state.currentPage === 1;
        prevBtn.onclick = () => { state.currentPage--; this.renderIdentitiesTable(); };
        container.appendChild(prevBtn);

        // Page info
        const span = document.createElement('span');
        span.style.padding = '0.4rem 1rem';
        span.innerText = `Page ${state.currentPage} of ${totalPages}`;
        container.appendChild(span);

        // Next Button
        const nextBtn = document.createElement('button');
        nextBtn.className = 'btn btn-outline btn-sm';
        nextBtn.innerHTML = '<i class="fa-solid fa-angle-right"></i>';
        nextBtn.disabled = state.currentPage === totalPages;
        nextBtn.onclick = () => { state.currentPage++; this.renderIdentitiesTable(); };
        container.appendChild(nextBtn);
    },

    // --- Access Review ---
    async viewAccessReview(identityId) {
        state.selectedIdentityId = identityId;
        this.showView('review-view');

        const tbody = document.getElementById('access-items-tbody');
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4"><i class="fa-solid fa-circle-notch fa-spin fa-2x text-primary"></i></td></tr>`;

        document.getElementById('review-identity-name').innerText = `Access Review: ${identityId}`;
        document.getElementById('review-identity-subtitle').innerText = "Loading details...";

        try {
            const response = await fetch(`${API_BASE_URL}/identities/${identityId}/access-review`, {
                headers: { 'Authorization': `Bearer ${state.token}` }
            });

            if (response.ok) {
                const data = await response.json();
                state.currentPeerGroupInfo = data.peer_group_info;

                // Update Headers
                const identityName = data.identity.name ? data.identity.name : data.identity.identity_id;
                document.getElementById('review-identity-name').innerText = `Review: ${identityName}`;
                document.getElementById('review-identity-subtitle').innerHTML = `
                    <i class="fa-solid fa-briefcase mr-1"></i> ${data.identity.job_title} &nbsp;&bull;&nbsp; 
                    <i class="fa-solid fa-building mr-1"></i> ${data.identity.department}
                `;

                this.renderAccessItems(data.access_items);
            } else {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-4">Failed to fetch review data.</td></tr>`;
            }
        } catch (error) {
            console.error('Review fetch error', error);
        }
    },

    renderAccessItems(items) {
        const tbody = document.getElementById('access-items-tbody');
        tbody.innerHTML = '';

        if (items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">No access items to review for this identity.</td></tr>`;
            return;
        }

        items.forEach((item, index) => {
            const tr = document.createElement('tr');
            tr.style.animationDelay = `${index * 0.05}s`;
            tr.className = 'slide-up';
            console.log(item.confidence_score);
            // Format Confidence
            const confPercent = Math.round(item.confidence_score);
            let confColor = 'var(--color-danger)';
            let badgeClass = 'badge-danger';
            let icon = 'fa-triangle-exclamation';

            if (confPercent >= 80) {
                confColor = 'var(--color-success)';
                badgeClass = 'badge-success';
                icon = 'fa-check';
            } else if (confPercent >= 50) {
                confColor = 'var(--color-warning)';
                badgeClass = 'badge-warning';
                icon = 'fa-circle-exclamation';
            }

            tr.innerHTML = `
                <td><strong>${item.access_item_name}</strong></td>
                <td><span class="badge" style="background:var(--bg-tertiary)">${item.item_type}</span></td>
            <!--<td>
                    <div>Lift: <strong>+${item.lift.toFixed(2)}x</strong></div>
                    <div class="text-muted" style="font-size:0.8rem">Global Avg: ${Number(item.global_adoption_rate || 0).toFixed(1)}%</div>
                </td>-->
                <td>
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-weight:600; color:${confColor}">
                        <span>
                            ${confPercent}%
                            <i class="fa-solid fa-circle-info info-icon" onclick="app.showExplanation('${item.access_item_name}', ${confPercent}, ${item.lift}, ${item.global_adoption_rate || 0}, '${item.validation_status || ''}')"></i>
                        </span>
                    </div>
                    <div class="confidence-bar-bg">
                        <div class="confidence-bar-fill" style="width: ${confPercent}%; background-color: ${confColor};"></div>
                    </div>
                </td>
                <td><span class="badge ${badgeClass}"><i class="fa-solid ${icon}"></i> Pending Review</span></td>
                <td>
                    <button class="btn btn-outline btn-sm" style="color:var(--color-success); border-color:var(--color-success)">Approve</button>
                    <button class="btn btn-outline btn-sm" style="color:var(--color-danger); border-color:var(--color-danger); margin-left:0.5rem">Revoke</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Trigger reflow for progress bars to animate
        setTimeout(() => {
            document.querySelectorAll('.confidence-bar-fill').forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                requestAnimationFrame(() => {
                    bar.style.width = width;
                });
            });
        }, 50);
    },

    // --- Access Recommendations ---
    async predictAccess() {
        const dept = document.getElementById('pred-dept').value || "Unknown";
        const title = document.getElementById('pred-title').value || "Unknown";
        const location = document.getElementById('pred-location').value || "Unknown";

        const resultsDiv = document.getElementById('recommendation-results');
        const tbody = document.getElementById('recommend-items-tbody');
        const btn = document.querySelector('#recommend-view .btn-primary');

        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        resultsDiv.classList.remove('hidden');
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">Loading models and running Inference Pipeline...</td></tr>`;

        try {
            const response = await fetch(`${API_BASE_URL}/recommendations/predict`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${state.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    department: dept,
                    job_title: title,
                    location: location
                })
            });

            if (response.ok) {
                const data = await response.json();
                state.currentPeerGroupInfo = data.peer_group_info;
                document.getElementById('recommend-cluster-title').innerText = `Predicted Peer Group ID: ${data.predicted_cluster_id}`;
                this.renderRecommendations(data.recommendations);
            } else {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">Error generating predictions. Check backend logs.</td></tr>`;
            }
        } catch (error) {
            console.error('Prediction fetch error', error);
            tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">Network Error. Ensure backend is running.</td></tr>`;
        } finally {
            btn.innerHTML = originalText;
        }
    },

    renderRecommendations(items) {
        const tbody = document.getElementById('recommend-items-tbody');
        tbody.innerHTML = '';

        if (items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">No high-probability items found for this cluster.</td></tr>`;
            return;
        }

        items.forEach((item, index) => {
            const tr = document.createElement('tr');
            tr.style.animationDelay = `${index * 0.05}s`;
            tr.className = 'slide-up';

            // Format Confidence
            const confPercent = Math.round(item.confidence_score * 100);
            let confColor = 'var(--color-danger)';

            if (confPercent >= 70) confColor = 'var(--color-success)';
            else if (confPercent >= 40) confColor = 'var(--color-warning)';

            tr.innerHTML = `
                <td><strong>${item.access_item_name}</strong></td>
                <td><span class="badge" style="background:var(--bg-tertiary)">${item.item_type}</span></td>
                <!-- <td>
                    <div><strong style="color:var(--color-accent)">+${item.lift.toFixed(2)}x</strong></div>
                </td> -->
                <td>
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-weight:600; color:${confColor}">
                        <span>
                            ${confPercent}% Hit Rate
                            <i class="fa-solid fa-circle-info info-icon" onclick="app.showExplanation('${item.access_item_name}', ${confPercent}, ${item.lift}, ${item.global_adoption_rate || 0}, '${item.validation_status || ''}')"></i>
                        </span>
                    </div>
                    <div class="confidence-bar-bg">
                        <div class="confidence-bar-fill" style="width: ${confPercent}%; background-color: ${confColor};"></div>
                    </div>
                </td>
                <td>
                    <button class="btn btn-outline btn-sm" style="color:var(--color-primary); border-color:var(--color-primary)"><i class="fa-solid fa-cart-plus"></i> Request</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        setTimeout(() => {
            document.querySelectorAll('#recommend-items-tbody .confidence-bar-fill').forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                requestAnimationFrame(() => bar.style.width = width);
            });
        }, 50);
    },

    closeExplanation() {
        document.getElementById('info-modal').classList.add('hidden');
    },

    showExplanation(itemName, confPercent, lift, globalRate, status) {
        const modal = document.getElementById('info-modal');
        const body = document.getElementById('info-modal-body');

        let pgInfo = state.currentPeerGroupInfo;
        let pgHtml = "";
        if (pgInfo && pgInfo.dominant_department) {
            pgHtml = `
            <div style="background: var(--bg-primary); padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 0.5rem; font-size: 0.9rem; color: var(--text-secondary);">Peer Group Profile (Cluster ${pgInfo.cluster_id})</h4>
                <div style="display:flex; gap: 1rem; font-size: 0.9rem;">
                    <div><i class="fa-solid fa-building text-primary"></i> <strong>${pgInfo.dominant_department}</strong></div>
                    <div><i class="fa-solid fa-briefcase text-primary"></i> <strong>${pgInfo.dominant_job_title}</strong></div>
                </div>
            </div>`;
        }

        const globalPct = globalRate ? Number(globalRate).toFixed(1) : "0.0";
        const liftVal = lift ? lift.toFixed(1) : "1.0";

        body.innerHTML = `
            ${pgHtml}
            <div style="margin-bottom: 1rem;">
                Our AI analyzes access patterns across the organization. For the predicted peer group this identity belongs to, we generated a Confidence Score of <strong>${confPercent}%</strong> for <strong>${itemName}</strong>.
            </div>
            
            <h4 style="margin: 1rem 0 0.5rem; font-size: 0.95rem;">How we calculated this:</h4>
            <ul style="margin-left: 1.5rem; margin-bottom: 1rem; color: var(--text-secondary); line-height: 1.6; font-size: 0.95rem;">
                <li><strong>${confPercent}%</strong> of the employees in this user's peer group currently hold this access.</li>
                <li>The company-wide average (Global Adoption Rate) for this item is only <strong>${globalPct}%</strong>.</li>
                <li>This means this access is <strong>${liftVal}x more common</strong> (Lift) in their specific group than the rest of the company.</li>
            </ul>

            <div style="padding: 1rem; border-left: 4px solid var(--color-accent); background: var(--bg-tertiary); font-size: 0.95rem; border-radius: 4px;">
                <strong>Conclusion:</strong> Because of this significant statistical lift and high peer adoption, the AI categorizes this access as:<br>
                <span class="badge badge-success mt-2" style="font-size: 0.85rem;">${status && status !== 'undefined' ? status : 'Recommended Output'}</span>
            </div>
        `;

        modal.classList.remove('hidden');
    },

    // --- Anomalies & Clusters ---
    async loadAnomalies() {
        const tbody = document.getElementById('anomalies-tbody');
        tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4"><i class="fa-solid fa-circle-notch fa-spin text-primary"></i> Loading anomalies...</td></tr>`;
        try {
            const response = await fetch(`${API_BASE_URL}/anomalies`, {
                headers: { 'Authorization': `Bearer ${state.token}` }
            });
            if (response.ok) {
                const data = await response.json();
                tbody.innerHTML = '';
                if (data.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">No anomalies identified.</td></tr>`;
                    return;
                }
                data.forEach((item, index) => {
                    const tr = document.createElement('tr');
                    tr.style.animationDelay = `${index * 0.05}s`;
                    tr.className = 'slide-up';
                    tr.innerHTML = `
                        <!--<td><strong>${item.identity_id}</strong></td>-->
                        <td>${item.name || 'N/A'}</td>
                        <td>${item.department}</td>
                        <td>${item.job_title}</td>
                        <td><span class="badge badge-danger"><i class="fa-solid fa-triangle-exclamation"></i> Anomaly</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-4">Failed to fetch anomalies.</td></tr>`;
            }
        } catch (error) {
            console.error('Anomalies fetch error', error);
        }
    },

    async loadClusters() {
        const tbody = document.getElementById('clusters-tbody');
        tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4"><i class="fa-solid fa-circle-notch fa-spin text-primary"></i> Loading clusters...</td></tr>`;
        try {
            const response = await fetch(`${API_BASE_URL}/clusters`, {
                headers: { 'Authorization': `Bearer ${state.token}` }
            });
            if (response.ok) {
                const data = await response.json();
                tbody.innerHTML = '';
                if (data.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">No clusters identified.</td></tr>`;
                    return;
                }
                data.forEach((item, index) => {
                    const tr = document.createElement('tr');
                    tr.style.animationDelay = `${index * 0.05}s`;
                    tr.className = 'slide-up';
                    tr.innerHTML = `
                        <td><strong>Cluster ${item.cluster_id}</strong></td>
                        <td><span style="font-weight: 500;">${item.total_users} users</span></td>
                        <td><span class="badge" style="background:var(--bg-tertiary)"><i class="fa-solid fa-building"></i> ${item.dominant_department}</span></td>
                        <td><span class="badge" style="background:var(--bg-tertiary)"><i class="fa-solid fa-briefcase"></i> ${item.dominant_job_title}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-4">Failed to fetch clusters.</td></tr>`;
            }
        } catch (error) {
            console.error('Clusters fetch error', error);
        }
    }
};

// Initialize app when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
