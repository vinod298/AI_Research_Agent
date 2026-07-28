/**
 * Enterprise AI Research & Knowledge Assistant - Frontend App Controller
 */

const API_BASE = window.API_BASE_URL || localStorage.getItem('api_base_url') || '/api/v1';

class App {
    constructor() {
        this.documents = [];
        this.activeTab = 'tab-documents';
        this.token = localStorage.getItem('jwt_token') || null;
        this.username = localStorage.getItem('username') || 'Guest';
        this.init();
    }

    init() {
        this.bindNavigation();
        this.bindFileUpload();
        this.checkAuthStatus();
        this.refreshData();
    }

    checkAuthStatus() {
        const modal = document.getElementById('auth-modal');
        const badge = document.getElementById('user-badge');
        
        if (this.token) {
            modal.classList.add('hidden');
            badge.innerText = `User: ${this.username}`;
        } else {
            modal.classList.remove('hidden');
            badge.innerText = `User: Guest`;
        }
    }

    showAuthTab(tab) {
        const btnLogin = document.getElementById('btn-show-login');
        const btnReg = document.getElementById('btn-show-register');
        const formLogin = document.getElementById('login-form');
        const formReg = document.getElementById('register-form');

        if (tab === 'login') {
            btnLogin.classList.add('active');
            btnReg.classList.remove('active');
            formLogin.classList.remove('hidden');
            formReg.classList.add('hidden');
        } else {
            btnReg.classList.add('active');
            btnLogin.classList.remove('active');
            formReg.classList.remove('hidden');
            formLogin.classList.add('hidden');
        }
    }

    async handleLogin(event) {
        event.preventDefault();
        const usernameInput = document.getElementById('login-username').value;
        const passwordInput = document.getElementById('login-password').value;

        const bodyData = new URLSearchParams();
        bodyData.append('username', usernameInput);
        bodyData.append('password', passwordInput);

        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: bodyData
            });

            if (!res.ok) {
                const err = await res.json();
                alert(`Login Failed: ${err.detail || 'Invalid credentials'}`);
                return;
            }

            const data = await res.json();
            this.token = data.access_token;
            this.username = usernameInput;

            localStorage.setItem('jwt_token', this.token);
            localStorage.setItem('username', this.username);

            this.checkAuthStatus();
            this.refreshData();
        } catch (e) {
            alert(`Login error: ${e.message}`);
        }
    }

    async handleRegister(event) {
        event.preventDefault();
        const fullname = document.getElementById('reg-fullname').value;
        const email = document.getElementById('reg-email').value;
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;

        try {
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    full_name: fullname,
                    email: email,
                    username: username,
                    password: password
                })
            });

            if (!res.ok) {
                const err = await res.json();
                alert(`Registration Failed: ${err.detail || 'Registration error'}`);
                return;
            }

            alert('Account created successfully! Logging you in...');
            // Auto login after registration
            document.getElementById('login-username').value = username;
            document.getElementById('login-password').value = password;
            this.handleLogin(event);
        } catch (e) {
            alert(`Register error: ${e.message}`);
        }
    }

    continueAsGuest() {
        this.token = null;
        this.username = 'Guest';
        document.getElementById('auth-modal').classList.add('hidden');
        document.getElementById('user-badge').innerText = `User: Guest`;
        this.refreshData();
    }

    logout() {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('username');
        this.token = null;
        this.username = 'Guest';
        this.checkAuthStatus();
    }

    getAuthHeaders(headers = {}) {
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    bindNavigation() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const targetTab = btn.getAttribute('data-tab');
                this.switchTab(targetTab);
            });
        });
    }

    switchTab(tabId) {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        const activeBtn = document.querySelector(`.nav-btn[data-tab="${tabId}"]`);
        const activePane = document.getElementById(tabId);

        if (activeBtn) activeBtn.classList.add('active');
        if (activePane) activePane.classList.add('active');

        this.activeTab = tabId;
        
        const titles = {
            'tab-documents': 'Document Management & Ingestion',
            'tab-chat': 'RAG Research Assistant & Inline Citations',
            'tab-compare': 'Multi-Document Comparative Matrix',
            'tab-summarize': 'Multi-Granularity Summarizer',
            'tab-classify': 'TensorFlow Neural Category Classifier',
            'tab-analytics': 'Live System Analytics & Metrics'
        };
        document.getElementById('page-title').innerText = titles[tabId] || 'AI Research Assistant';

        if (tabId === 'tab-analytics') {
            this.loadAnalytics();
        }
    }

    bindFileUpload() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--primary)';
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = 'rgba(99, 102, 241, 0.4)';
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            if (e.dataTransfer.files.length) {
                this.uploadFiles(e.dataTransfer.files);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                this.uploadFiles(fileInput.files);
            }
        });
    }

    async uploadFiles(files) {
        for (let file of files) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch(`${API_BASE}/documents/upload`, {
                    method: 'POST',
                    headers: this.getAuthHeaders(),
                    body: formData
                });
                if (!res.ok) {
                    const err = await res.json();
                    alert(`Upload error: ${err.detail}`);
                    continue;
                }
                const doc = await res.json();
                console.log('Uploaded document:', doc);
            } catch (e) {
                alert(`Upload failed: ${e.message}`);
            }
        }
        
        setTimeout(() => this.refreshData(), 1000);
    }

    async refreshData() {
        const btn = document.getElementById('refresh-btn');
        if (btn) btn.classList.add('spin');

        try {
            const res = await fetch(`${API_BASE}/documents`, {
                headers: this.getAuthHeaders()
            });
            if (res.ok) {
                this.documents = await res.json();
                this.renderDocumentsTable();
                this.updateDocumentSelectors();
            }
            await this.loadAnalytics();
        } catch (e) {
            console.error('Failed to refresh data:', e);
        } finally {
            if (btn) {
                setTimeout(() => btn.classList.remove('spin'), 500);
            }
        }
    }

    renderDocumentsTable() {
        const tbody = document.getElementById('documents-table-body');
        document.getElementById('doc-count').innerText = `${this.documents.length} Documents`;

        if (!this.documents.length) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center">No documents uploaded yet. Upload a PDF to begin research.</td></tr>`;
            return;
        }

        tbody.innerHTML = this.documents.map(doc => `
            <tr>
                <td><strong>${doc.title || doc.filename}</strong><br><small class="text-muted">${doc.filename}</small></td>
                <td>${doc.page_count}</td>
                <td>${doc.chunk_count}</td>
                <td><span class="badge badge-category">${doc.predicted_category || 'Pending'}</span></td>
                <td><span class="badge badge-success">${doc.processing_status}</span></td>
                <td>
                    <button class="btn btn-secondary" onclick="app.deleteDocument('${doc.id}')">🗑️ Delete</button>
                </td>
            </tr>
        `).join('');
    }

    updateDocumentSelectors() {
        const compareContainer = document.getElementById('compare-doc-selector');
        if (compareContainer) {
            compareContainer.innerHTML = this.documents.map(doc => `
                <label style="display: block; margin-bottom: 0.5rem; cursor: pointer;">
                    <input type="checkbox" value="${doc.id}" class="compare-checkbox"> ${doc.title} (${doc.filename})
                </label>
            `).join('');
        }

        const sumSelect = document.getElementById('summarize-doc-select');
        if (sumSelect) {
            sumSelect.innerHTML = this.documents.map(doc => `
                <option value="${doc.id}">${doc.title} (${doc.filename})</option>
            `).join('');
        }
    }

    async deleteDocument(id) {
        if (!confirm('Are you sure you want to delete this document?')) return;
        try {
            await fetch(`${API_BASE}/documents/${id}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });
            this.refreshData();
        } catch (e) {
            alert(`Delete failed: ${e.message}`);
        }
    }

    async sendChatMessage() {
        const input = document.getElementById('chat-input');
        const question = input.value.trim();
        if (!question) return;

        const provider = document.getElementById('llm-provider-select').value;
        const msgContainer = document.getElementById('chat-messages');

        msgContainer.innerHTML += `
            <div class="message user-message">
                <div class="msg-avatar">👤</div>
                <div class="msg-content"><p>${this.escapeHtml(question)}</p></div>
            </div>
        `;
        input.value = '';
        msgContainer.scrollTop = msgContainer.scrollHeight;

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
                body: JSON.stringify({
                    question: question,
                    llm_provider: provider,
                    top_k: 5
                })
            });

            if (!res.ok) {
                throw new Error('Failed to fetch response');
            }

            const data = await res.json();

            let citationsHtml = '';
            if (data.citations && data.citations.length) {
                citationsHtml = `
                    <div class="citation-box">
                        <strong>📌 Verified Inline Citations (${data.citations.length}):</strong><br>
                        ${data.citations.map(c => `• <em>${c.filename}</em> (Page ${c.page_number}) - Score: ${c.relevance_score}`).join('<br>')}
                    </div>
                `;
            }

            msgContainer.innerHTML += `
                <div class="message assistant-message">
                    <div class="msg-avatar">🤖</div>
                    <div class="msg-content">
                        <p>${this.escapeHtml(data.answer).replace(/\n/g, '<br>')}</p>
                        ${citationsHtml}
                        <small class="text-muted" style="display:block; margin-top:0.5rem;">Latency: ${data.latency_ms}ms | Confidence: ${data.confidence_score}</small>
                    </div>
                </div>
            `;
            msgContainer.scrollTop = msgContainer.scrollHeight;
        } catch (e) {
            alert(`Chat error: ${e.message}`);
        }
    }

    async runDocumentComparison() {
        const checkboxes = document.querySelectorAll('.compare-checkbox:checked');
        const docIds = Array.from(checkboxes).map(cb => cb.value);

        if (docIds.length < 2) {
            alert('Please select at least 2 documents for comparison.');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/compare`, {
                method: 'POST',
                headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
                body: JSON.stringify({ document_ids: docIds })
            });

            const data = await res.json();
            document.getElementById('comparison-results').classList.remove('hidden');

            const wrapper = document.getElementById('comparison-table-wrapper');
            let tableHtml = `<table class="data-table"><thead><tr><th>Aspect</th>`;
            
            data.compared_documents.forEach(d => {
                tableHtml += `<th>${d.title}</th>`;
            });
            tableHtml += `</tr></thead><tbody>`;

            data.comparison_table.forEach(item => {
                tableHtml += `<tr><td><strong>${item.aspect}</strong></td>`;
                data.compared_documents.forEach(d => {
                    tableHtml += `<td>${item.document_summaries[d.filename] || 'N/A'}</td>`;
                });
                tableHtml += `</tr>`;
            });
            tableHtml += `</tbody></table>`;
            wrapper.innerHTML = tableHtml;

            document.getElementById('comparison-narrative').innerHTML = `<p>${data.narrative_analysis}</p><p><strong>Conclusion:</strong> ${data.conclusion}</p>`;
        } catch (e) {
            alert(`Comparison error: ${e.message}`);
        }
    }

    async generateSummary() {
        const docId = document.getElementById('summarize-doc-select').value;
        const summaryType = document.getElementById('summarize-type-select').value;

        if (!docId) {
            alert('Please upload and select a document first.');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/summarize`, {
                method: 'POST',
                headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
                body: JSON.stringify({ document_id: docId, summary_type: summaryType })
            });

            const data = await res.json();
            document.getElementById('summary-results').classList.remove('hidden');
            const card = document.getElementById('summary-content-card');

            let html = `<h3>Summary for: ${data.document_title}</h3>`;
            if (data.executive_summary) html += `<h4 class="mt-3">Executive Summary</h4><p>${data.executive_summary}</p>`;
            if (data.technical_summary) html += `<h4 class="mt-3">Technical Architecture</h4><p>${data.technical_summary}</p>`;
            if (data.bullet_summary) {
                html += `<h4 class="mt-3">Key Takeaways</h4><ul>${data.bullet_summary.map(b => `<li>${b}</li>`).join('')}</ul>`;
            }
            card.innerHTML = html;
        } catch (e) {
            alert(`Summarize error: ${e.message}`);
        }
    }

    async runClassification() {
        const text = document.getElementById('classify-text-input').value;
        if (!text) {
            alert('Please enter text to classify.');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/classify`, {
                method: 'POST',
                headers: this.getAuthHeaders({ 'Content-Type': 'application/json' }),
                body: JSON.stringify({ text: text })
            });

            const data = await res.json();
            document.getElementById('classify-results').classList.remove('hidden');
            document.getElementById('pred-cat').innerText = data.predicted_category;
            document.getElementById('pred-conf').innerText = `${(data.confidence * 100).toFixed(1)}%`;

            const container = document.getElementById('scores-container');
            container.innerHTML = data.all_scores.map(s => `
                <div style="margin-bottom: 0.5rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                        <span>${s.category}</span>
                        <span>${(s.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.1); height:8px; border-radius:4px; overflow:hidden;">
                        <div style="width:${(s.confidence * 100)}%; background:var(--primary); height:100%;"></div>
                    </div>
                </div>
            `).join('');
        } catch (e) {
            alert(`Classification error: ${e.message}`);
        }
    }

    async loadAnalytics() {
        try {
            const res = await fetch(`${API_BASE}/analytics`, {
                headers: this.getAuthHeaders()
            });
            if (res.ok) {
                const data = await res.json();
                document.getElementById('metric-docs').innerText = data.metrics.total_documents;
                document.getElementById('metric-chunks').innerText = data.metrics.total_chunks;
                document.getElementById('metric-pages').innerText = data.metrics.total_pages_processed;
                document.getElementById('metric-latency').innerText = `${data.latency.avg_rag_latency_ms} ms`;
            }
        } catch (e) {
            console.error('Failed loading analytics:', e);
        }
    }

    escapeHtml(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }
}

const app = new App();
