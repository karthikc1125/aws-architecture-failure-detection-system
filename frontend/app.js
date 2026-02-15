async function analyze() {
    const text = document.getElementById("userInput").value;
    const resultsDiv = document.getElementById("results");

    if (!text.trim()) {
        alert("Please describe your architecture first.");
        return;
    }

    // Loading State
    resultsDiv.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p><strong>Running Failure Simulation...</strong></p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.7;">Querying Knowledge Base • Matching against 200+ Patterns • Creating Architecture</p>
        </div>
    `;

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description: text })
        });

        const data = await response.json();

        // --- Render Results ---
        let html = `<div class="result-section">`;

        // 1. Top Metrics
        html += `
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value" style="color: ${data.review_score >= 7 ? 'var(--accent-green)' : 'var(--accent-red)'}">
                        ${data.review_score}/10
                    </div>
                    <div class="metric-label">Resilience Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${data.detected_failures.length}</div>
                    <div class="metric-label">Risks Detected</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${data.proposed_architecture.components.length}</div>
                    <div class="metric-label">New Components</div>
                </div>
            </div>
        `;

        // 2. Failure Analysis
        html += `<h2 style="display: flex; align-items: center; gap: 1rem;">
            ⚠️ Failure Prediction Report
            <span style="font-size: 0.9rem; background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); padding: 4px 12px; border-radius: 99px;">
                ${data.detected_failures.length} Possible Scenarios
            </span>
        </h2>`;

        if (data.detected_failures.length === 0) {
            html += `<div class="card" style="border-left: 4px solid var(--accent-green);">✅ No obvious failure patterns detected based on current description.</div>`;
        } else {
            data.detected_failures.forEach(f => {
                html += `
                    <div class="failure-item">
                        <div class="failure-title">
                            <span>${f.name}</span>
                            <div style="display: flex; gap: 0.5rem; align-items: center;">
                                <span style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">${f.failure_class}</span>
                                <span style="font-size: 0.75rem; color: ${f.likelihood >= 80 ? '#ef4444' : '#f59e0b'}; font-weight: 700; background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 4px;">
                                    ${(f.likelihood || 50)}% PROBABILITY
                                </span>
                            </div>
                        </div>
                        
                        <!-- Likelihood Bar -->
                        <div style="width: 100%; height: 4px; background: #1e293b; border-radius: 2px; margin: 0.4rem 0 0.8rem 0; overflow: hidden;">
                             <div style="width: ${(f.likelihood || 50)}%; height: 100%; background: linear-gradient(90deg, ${f.likelihood >= 80 ? '#ef4444' : '#f59e0b'}, ${f.likelihood >= 80 ? '#b91c1c' : '#d97706'}); box-shadow: 0 0 8px ${f.likelihood >= 80 ? '#ef4444' : '#f59e0b'};"></div>
                        </div>

                        <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.5;">${f.description}</div>
                        ${f.mitigation ? `
                            <div class="failure-mitigation">
                                <span>🛠️ Recommendation:</span> ${f.mitigation}
                            </div>
                        ` : ''}
                    </div>
                `;
            });
        }

        // 3. Proposed Architecture
        html += `<h2 style="margin-top: 3rem;">🏗️ Proposed Resilient Architecture</h2>`;
        html += `<div class="card" style="border-color: var(--accent-blue);">`;

        // Components Badges
        html += `<div style="margin-bottom: 1.5rem;">`;
        data.proposed_architecture.components.forEach(c => {
            html += `<span class="arch-component">📦 ${c.name}</span>`;
        });
        html += `</div>`;

        // Description
        html += `<div style="background: #0f172a; padding: 1.5rem; border-radius: 8px; white-space: pre-wrap; font-family: var(--font-family); color: #cbd5e1;">${data.proposed_architecture.description}</div>`;
        html += `</div>`;

        html += `</div>`; // End result-section

        resultsDiv.innerHTML = html;

    } catch (e) {
        resultsDiv.innerHTML = `
            <div class="card" style="border-color: var(--accent-red); color: var(--accent-red);">
                <h3>System Error</h3>
                <p>${e.message}</p>
                <p style="font-size: 0.9rem; margin-top: 1rem; color: #fff;">Is the backend server running?</p>
            </div>
        `;
    }
}

/* Settings Modal Logic */
function openSettings() {
    document.getElementById('settingsModal').style.display = 'flex';
    // Load saved settings
    const savedModel = localStorage.getItem('safecloud_model') || 'google/gemini-2.0-flash-exp:free';
    const savedKey = localStorage.getItem('safecloud_api_key') || '';

    // Note: These IDs settingModel/settingApiKey refer to old modal logic inside analyze.html or similar?
    // Let's assume the DOM elements exist or are handled by analyze.html script block.
    // However, since we moved logic to inline script in index/analyze.html, this file might be partially redundant or needs alignment.
    // For now, I am preserving the existing structure but fixing the syntax error found.

    const mInput = document.getElementById('settingModel');
    if (mInput) mInput.value = savedModel;

    const kInput = document.getElementById('settingApiKey');
    if (kInput) kInput.value = savedKey;
}

function closeSettings() {
    document.getElementById('settingsModal').style.display = 'none';
}

function saveSettings() {
    const mInput = document.getElementById('settingModel');
    const kInput = document.getElementById('settingApiKey');

    if (!mInput || !kInput) return; // Guard

    const model = mInput.value;
    const apiKey = kInput.value;

    localStorage.setItem('safecloud_model', model);
    localStorage.setItem('safecloud_api_key', apiKey);

    alert('Settings Saved! Using ' + model);
    closeSettings();

    // Update analyze page dropdown if it exists
    const aiModelDropdown = document.getElementById('aiModel');
    if (aiModelDropdown) {
        // Check if option exists, if not add it
        let exists = false;
        for (let i = 0; i < aiModelDropdown.options.length; i++) {
            if (aiModelDropdown.options[i].value === model) exists = true;
        }

        if (!exists) {
            const opt = document.createElement('option');
            opt.value = model;
            opt.innerHTML = model + ' (Custom)';
            aiModelDropdown.appendChild(opt);
        }
        aiModelDropdown.value = model;
    }
}
