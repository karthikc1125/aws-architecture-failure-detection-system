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
        const response = await fetch("/api/analyze/deployed", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description: text })
        });

        const data = await response.json();

        // --- Render Results ---
        let html = `<div class="result-section">`;

        // 1. Display Analysis Type
        html += `<div style="margin-bottom: 1.5rem; padding: 1rem; background: #1e293b; border-left: 4px solid var(--accent-blue); border-radius: 4px;">
            <div style="color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em;">Analysis Type</div>
            <div style="color: #e2e8f0; font-size: 1.1rem; margin-top: 0.5rem;">${data.analysis_type || 'Architecture Analysis'}</div>
        </div>`;

        // 2. Status & Summary
        html += `<div style="margin-bottom: 1.5rem;">
            <h2 style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                📊 Analysis Status
                <span style="font-size: 0.9rem; background: ${data.status === 'optimized' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)'}; color: ${data.status === 'optimized' ? '#22c55e' : '#ef4444'}; border: 1px solid ${data.status === 'optimized' ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)'}; padding: 4px 12px; border-radius: 99px; text-transform: capitalize;">
                    ${data.status}
                </span>
            </h2>
        </div>`;

        // 3. Key Metrics
        if (data.issues && data.issues.length > 0) {
            html += `
                <div class="metric-grid" style="margin-bottom: 2rem;">
                    <div class="metric-card">
                        <div class="metric-value" style="color: var(--accent-red);">${data.issues.length}</div>
                        <div class="metric-label">Issues Found</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color: var(--accent-orange);">${data.quick_wins ? data.quick_wins.length : 0}</div>
                        <div class="metric-label">Quick Wins</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color: var(--accent-green);">${data.total_potential_savings || '20-40%'}</div>
                        <div class="metric-label">Potential Savings</div>
                    </div>
                </div>
            `;
        }

        // 4. Issues Section
        if (data.issues && data.issues.length > 0) {
            html += `<h2 style="display: flex; align-items: center; gap: 1rem;">
                ⚠️ Issues Identified
                <span style="font-size: 0.9rem; background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); padding: 4px 12px; border-radius: 99px;">
                    ${data.issues.length} Issues
                </span>
            </h2>`;
            data.issues.forEach((issue, idx) => {
                const severity = issue.severity || 'Medium';
                const severityColor = severity === 'Critical' ? '#ef4444' : severity === 'High' ? '#f59e0b' : '#3b82f6';
                html += `
                    <div class="failure-item">
                        <div class="failure-title">
                            <span>${issue.issue || issue}</span>
                            <span style="font-size: 0.75rem; color: ${severityColor}; font-weight: 700; background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 4px;">
                                ${severity}
                            </span>
                        </div>
                        ${issue.recommendation ? `
                            <div class="failure-mitigation">
                                <span>💡 Recommendation:</span> ${issue.recommendation}
                            </div>
                        ` : ''}
                    </div>
                `;
            });
        }

        // 5. Quick Wins Section
        if (data.quick_wins && data.quick_wins.length > 0) {
            html += `<h2 style="margin-top: 2rem; display: flex; align-items: center; gap: 1rem;">
                ⚡ Quick Wins
                <span style="font-size: 0.9rem; background: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.4); padding: 4px 12px; border-radius: 99px;">
                    ${data.quick_wins.length} Actions
                </span>
            </h2>`;
            data.quick_wins.forEach((win, idx) => {
                html += `
                    <div class="card" style="border-left: 4px solid var(--accent-green); margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #22c55e; margin-bottom: 0.5rem;">✅ ${win.opportunity || win}</div>
                        <div style="color: #cbd5e1; font-size: 0.95rem;">${win.savings ? `Potential Savings: ${win.savings}` : ''}</div>
                    </div>
                `;
            });
        }

        // 6. Implementation Details
        if (data.implementation_effort) {
            html += `<div class="card" style="border-color: var(--accent-blue); margin-top: 2rem;">
                <h3>📋 Implementation Details</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>
                        <div style="color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em;">Effort Required</div>
                        <div style="color: #e2e8f0; font-size: 1rem; margin-top: 0.5rem;">${data.implementation_effort}</div>
                    </div>
                    <div>
                        <div style="color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em;">Est. Savings</div>
                        <div style="color: #22c55e; font-size: 1rem; margin-top: 0.5rem;">${data.total_potential_savings || 'Variable'}</div>
                    </div>
                </div>
            </div>`;
        }

        // 7. Recommendations Section
        if (data.recommendations && data.recommendations.length > 0) {
            html += `<h2 style="margin-top: 2rem; display: flex; align-items: center; gap: 1rem;">
                🛠️ Recommendations
                <span style="font-size: 0.9rem; background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.4); padding: 4px 12px; border-radius: 99px;">
                    ${data.recommendations.length} Suggestions
                </span>
            </h2>`;
            data.recommendations.forEach((rec, idx) => {
                html += `
                    <div class="card" style="border-left: 4px solid #3b82f6; margin-bottom: 1rem;">
                        <div style="font-weight: 600; color: #3b82f6; margin-bottom: 0.5rem;">${idx + 1}. ${rec.recommendation || rec}</div>
                        <div style="color: #cbd5e1; font-size: 0.95rem;">${rec.priority ? `Priority: ${rec.priority}` : ''}</div>
                    </div>
                `;
            });
        }

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
