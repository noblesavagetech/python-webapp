document.addEventListener('DOMContentLoaded', async () => {
    requireAuth();

    try {
        // Load user and company info
        const userData = await apiRequest('/auth/me', 'GET');
        displayCompanyInfo(userData.company);
        displayHealthScore(userData.company);
        
        // Check Wave status
        await checkWaveStatus();
        
        // Display questionnaire status
        displayQuestionnaireStatus(userData.company);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            logout();
        }
    }
});

function displayCompanyInfo(company) {
    const container = document.getElementById('companyInfo');
    container.innerHTML = `
        <p><strong>Company:</strong> ${company.name}</p>
        <p><strong>Email:</strong> ${company.email}</p>
        ${company.industry ? `<p><strong>Industry:</strong> ${company.industry}</p>` : ''}
        ${company.size ? `<p><strong>Size:</strong> ${company.size}</p>` : ''}
        <p><strong>Member since:</strong> ${new Date(company.created_at).toLocaleDateString()}</p>
    `;
}

function displayHealthScore(company) {
    const container = document.getElementById('healthScore');
    
    if (company.financial_health_score !== null && company.financial_health_score !== undefined) {
        const score = company.financial_health_score;
        let scoreColor = '#EF4444'; // red
        if (score >= 70) scoreColor = '#10B981'; // green
        else if (score >= 40) scoreColor = '#F59E0B'; // yellow
        
        container.innerHTML = `
            <div style="font-size: 3rem; font-weight: bold; color: ${scoreColor}; margin: 1rem 0;">
                ${score.toFixed(1)}
            </div>
            <p>out of 100</p>
        `;
    } else {
        container.innerHTML = `
            <p>Complete the financial assessment to get your score</p>
            <a href="/questionnaire" class="btn btn-primary" style="margin-top: 1rem;">Take Assessment</a>
        `;
    }
}

async function checkWaveStatus() {
    const statusContainer = document.getElementById('waveStatus');
    const actionsContainer = document.getElementById('waveActions');
    
    try {
        const result = await apiRequest('/wave/status', 'GET');
        
        if (result.connected) {
            statusContainer.innerHTML = `
                <p style="color: #10B981;">✓ Connected to Wave</p>
                ${result.token.wave_business_id ? `<p><small>Business ID: ${result.token.wave_business_id}</small></p>` : ''}
            `;
            
            actionsContainer.innerHTML = `
                <button onclick="syncWaveData()" class="btn btn-primary" style="margin-right: 0.5rem;">Sync Data</button>
                <button onclick="disconnectWave()" class="btn btn-secondary">Disconnect</button>
            `;
        } else {
            statusContainer.innerHTML = `
                <p style="color: #EF4444;">Not connected to Wave</p>
            `;
            
            actionsContainer.innerHTML = `
                <button onclick="connectWave()" class="btn btn-primary">Connect to Wave</button>
            `;
        }
    } catch (error) {
        statusContainer.innerHTML = `
            <p style="color: #EF4444;">Error checking Wave status</p>
        `;
    }
}

async function connectWave() {
    try {
        const result = await apiRequest('/wave/authorize', 'GET');
        // Open Wave authorization in new window
        window.open(result.authorization_url, 'Wave Authorization', 'width=600,height=700');
        
        // Poll for connection status
        const interval = setInterval(async () => {
            const status = await apiRequest('/wave/status', 'GET');
            if (status.connected) {
                clearInterval(interval);
                await checkWaveStatus();
                alert('Successfully connected to Wave!');
            }
        }, 3000);
    } catch (error) {
        alert('Error connecting to Wave: ' + error.message);
    }
}

async function syncWaveData() {
    try {
        await apiRequest('/wave/sync', 'POST');
        alert('Data sync initiated successfully!');
    } catch (error) {
        alert('Error syncing data: ' + error.message);
    }
}

async function disconnectWave() {
    if (!confirm('Are you sure you want to disconnect Wave?')) {
        return;
    }
    
    try {
        await apiRequest('/wave/disconnect', 'POST');
        await checkWaveStatus();
        alert('Wave disconnected successfully');
    } catch (error) {
        alert('Error disconnecting Wave: ' + error.message);
    }
}

function displayQuestionnaireStatus(company) {
    const container = document.getElementById('questionnaireStatus');
    
    if (company.questionnaire_completed) {
        container.innerHTML = `
            <p style="color: #10B981;">✓ Assessment completed</p>
            <a href="/questionnaire" class="btn btn-secondary" style="margin-top: 1rem;">Retake Assessment</a>
        `;
    } else {
        container.innerHTML = `
            <p>You haven't completed the financial assessment yet</p>
            <a href="/questionnaire" class="btn btn-primary" style="margin-top: 1rem;">Complete Assessment</a>
        `;
    }
}
