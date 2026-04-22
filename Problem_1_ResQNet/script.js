document.addEventListener('DOMContentLoaded', () => {

    /* ==========================================================================
       CLOCK & DATE
       ========================================================================== */
    function updateClock() {
        const now = new Date();
        document.getElementById('sidebar-clock').textContent = now.toLocaleTimeString('en-US', { hour12: false });
        document.getElementById('sidebar-date').textContent = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' }).toUpperCase();
    }
    setInterval(updateClock, 1000);
    updateClock();

    /* ==========================================================================
       NAVIGATION TABS
       ========================================================================== */
    const navLinks = document.querySelectorAll('.nav-link');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const pageTitle = document.getElementById('page-title');

    function switchTab(tabId, title) {
        navLinks.forEach(link => link.classList.remove('active'));
        const activeNav = Array.from(navLinks).find(n => n.dataset.tab === tabId);
        if (activeNav) activeNav.classList.add('active');

        tabPanes.forEach(pane => pane.classList.add('hidden'));
        document.getElementById(tabId).classList.remove('hidden');

        if(title) pageTitle.textContent = title;
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(e.currentTarget.dataset.tab, e.currentTarget.textContent.trim());
        });
    });

    const goInputBtn = document.getElementById('go-to-input-btn');
    if(goInputBtn) {
        goInputBtn.addEventListener('click', () => switchTab('tab-input', 'Log Emergency'));
    }

    /* ==========================================================================
       MOCK DATA
       ========================================================================== */
    const graphNodes = {
        'Sector 1': { x: 50, y: 50 },
        'Sector 2': { x: 200, y: 40 },
        'Sector 3': { x: 400, y: 80 },
        'Sector 4': { x: 100, y: 200 },
        'Downtown': { x: 250, y: 150 },
        'Highway': { x: 450, y: 250 },
        'Station': { x: 150, y: 280 }
    };

    const edges = [
        ['Sector 1', 'Sector 2', 5],
        ['Sector 1', 'Sector 4', 7],
        ['Sector 2', 'Downtown', 3],
        ['Sector 2', 'Sector 3', 8],
        ['Sector 4', 'Downtown', 4],
        ['Sector 4', 'Station', 2],
        ['Downtown', 'Highway', 6],
        ['Downtown', 'Station', 3],
        ['Sector 3', 'Highway', 4]
    ];

    const resources = [
        { id: 'AMB-01', type: 'Medical', status: 'Available', loc: 'Station' },
        { id: 'AMB-02', type: 'Medical', status: 'Busy', loc: 'Downtown' },
        { id: 'AMB-03', type: 'Medical', status: 'Available', loc: 'Sector 1' },
        { id: 'FTR-Alpha', type: 'Fire', status: 'Available', loc: 'Sector 2' },
        { id: 'FTR-Bravo', type: 'Fire', status: 'Busy', loc: 'Sector 3' },
        { id: 'RSC-Unit', type: 'Rescue', status: 'Available', loc: 'Station' },
        { id: 'POL-01', type: 'Police', status: 'Available', loc: 'Downtown' },
        { id: 'POL-02', type: 'Police', status: 'Busy', loc: 'Highway' }
    ];

    const hospitals = [
        { name: 'Central City Hospital', beds: 45, max: 120, status: 'Active' },
        { name: 'Mercy Medical Center', beds: 12, max: 80, status: 'Busy' },
        { name: 'St. Jude Emergency', beds: 2, max: 50, status: 'Full' },
        { name: 'Northside Trauma', beds: 28, max: 60, status: 'Active' }
    ];

    let activeEmergencies = [
        { id: 'INC-901', title: 'Multi-vehicle collision', loc: 'Highway Junction', type: 'Accident', status: 'crit', time: '10:42 AM', unit: 'POL-02, AMB-02' },
        { id: 'INC-900', title: 'Industrial Fire', loc: 'Sector 3', type: 'Fire', status: 'high', time: '10:15 AM', unit: 'FTR-Bravo' },
        { id: 'INC-899', title: 'Medical - Cardiac', loc: 'Downtown Sector', type: 'Medical', status: 'med', time: '09:50 AM', unit: 'AMB-04 (Cleared)' }
    ];

    let timelineEvents = [
        { time: '10:45:12', msg: 'AMB-02 arrived at Highway Junction.' },
        { time: '10:42:05', msg: 'INC-901 reported. AI dispatched POL-02 & AMB-02.' },
        { time: '10:25:30', msg: 'Fire contained at Sector 3. FTR-Bravo remains on site.' },
        { time: '10:15:10', msg: 'INC-900 reported. Fire severity HIGH.' }
    ];


    /* ==========================================================================
       DASHBOARD POPULATION (INITIAL)
       ========================================================================== */
    function renderEmergencyCards() {
        const container = document.getElementById('emergency-cards');
        if(!container) return;
        container.innerHTML = '';
        
        activeEmergencies.forEach(e => {
            const html = `
                <div class="e-card ${e.status}-border">
                    <div class="e-time">${e.time}</div>
                    <div class="e-info">
                        <div class="e-title">${e.id} — ${e.title}</div>
                        <div class="e-loc">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2"/></svg>
                            ${e.loc}
                        </div>
                    </div>
                    <div class="e-meta">
                        <div class="e-status ${e.status}">${e.status === 'crit' ? 'CRITICAL' : e.status === 'high' ? 'HIGH' : 'MODERATE'}</div>
                        <div class="e-unit">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none"><path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                            ${e.unit}
                        </div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });
    }

    function renderAlerts() {
        const container = document.getElementById('alert-center');
        if(!container) return;
        const alerts = [
            { title: 'Hospital Capacity Warning', desc: 'St. Jude Emergency is at 96% capacity. AI diverting new trauma to Central City.' },
            { title: 'Resource Shortage', desc: 'Sector 3 has 0 available Fire units. AI pre-positioning FTR-Alpha.' },
            { title: 'Route Congestion', desc: 'Heavy traffic on Main St. Route paths updated for all active units.' }
        ];
        
        container.innerHTML = '';
        alerts.forEach(a => {
            const html = `
                <div class="alert-item">
                    <div class="alert-icon">
                        <svg viewBox="0 0 24 24" fill="none"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </div>
                    <div class="alert-content">
                        <div class="a-title">${a.title}</div>
                        <div class="a-desc">${a.desc}</div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });
    }

    function renderTimeline() {
        const container = document.getElementById('timeline-panel');
        if(!container) return;
        container.innerHTML = '';
        timelineEvents.forEach(e => {
            const html = `
                <div class="tl-item">
                    <div class="tl-node"></div>
                    <div class="tl-content">
                        <div class="tl-time">${e.time}</div>
                        <div class="tl-text">${e.msg}</div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });
    }

    function renderResources() {
        const container = document.getElementById('resources-grid');
        const summary = document.getElementById('deploy-summary');
        if(!container || !summary) return;

        container.innerHTML = '';
        let avail = 0, busy = 0;

        resources.forEach(r => {
            const isAvail = r.status === 'Available';
            if(isAvail) avail++; else busy++;
            const badgeClass = isAvail ? 'badge-active' : 'badge-busy';
            
            const html = `
                <div class="grid-card">
                    <div class="card-top">
                        <div>
                            <div class="card-title">${r.id}</div>
                            <div class="card-sub">${r.type} Unit</div>
                        </div>
                        <div class="status-badge ${badgeClass}">${r.status}</div>
                    </div>
                    <div class="card-data-row">
                        <span style="color:var(--text-secondary)">Current Sector:</span>
                        <span class="gold-text">${r.loc}</span>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });

        summary.innerHTML = `
            <div class="ds-item"><div class="ds-val">${resources.length}</div><div class="ds-lbl">Total Units</div></div>
            <div class="ds-item"><div class="ds-val positive">${avail}</div><div class="ds-lbl">Available</div></div>
            <div class="ds-item"><div class="ds-val negative">${busy}</div><div class="ds-lbl">Deployed</div></div>
        `;
    }

    function renderHospitals() {
        const container = document.getElementById('hospital-grid');
        const dept = document.getElementById('dept-grid');
        if(!container || !dept) return;

        container.innerHTML = '';
        hospitals.forEach(h => {
            let badge = 'badge-active';
            if(h.status === 'Busy') badge = 'badge-busy';
            if(h.status === 'Full') badge = 'badge-full';

            const pct = Math.round(((h.max - h.beds) / h.max) * 100);

            const html = `
                <div class="grid-card">
                    <div class="card-top">
                        <div>
                            <div class="card-title">${h.name}</div>
                            <div class="card-sub">Level 1 Trauma Center</div>
                        </div>
                        <div class="status-badge ${badge}">${h.status}</div>
                    </div>
                    <div class="card-data-row">
                        <span style="color:var(--text-secondary)">Available Beds:</span>
                        <span style="font-family:var(--font-mono); font-weight:600">${h.beds} / ${h.max}</span>
                    </div>
                    <div style="height:4px; background:var(--bg-base); margin-top:8px; border-radius:2px;">
                        <div style="height:100%; width:${pct}%; background:${pct > 90 ? 'var(--status-red)' : pct > 70 ? 'var(--status-amber)' : 'var(--status-green)'}; border-radius:2px;"></div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });

        const depts = [
            { n: 'Emergency (ER)', b: 14, m: 40 },
            { n: 'Intensive Care (ICU)', b: 3, m: 25 },
            { n: 'Surgery', b: 8, m: 15 },
            { n: 'Burn Unit', b: 5, m: 10 }
        ];

        dept.innerHTML = '';
        depts.forEach(d => {
            const html = `
                <div class="grid-card">
                    <div class="card-title" style="font-size:0.9rem; margin-bottom:8px;">${d.n}</div>
                    <div class="card-data-row" style="border:none; margin:0; padding:0;">
                        <span style="color:var(--text-secondary); font-size:0.75rem;">City-wide Avail:</span>
                        <span class="gold-text" style="font-family:var(--font-mono)">${d.b} beds</span>
                    </div>
                </div>
            `;
            dept.insertAdjacentHTML('beforeend', html);
        });
    }

    /* Initialize Views */
    renderEmergencyCards();
    renderAlerts();
    renderTimeline();
    renderResources();
    renderHospitals();

    /* ==========================================================================
       CANVAS DRAWING (HEATMAP & GRAPH)
       ========================================================================== */
    function drawGraph(canvasId, highlightedPath, isHeatmap) {
        const canvas = document.getElementById(canvasId);
        if(!canvas) return;
        const ctx = canvas.getContext('2d');
        
        // Auto-scale logic
        const cw = canvas.parentElement.clientWidth || canvas.width;
        const ch = canvas.parentElement.clientHeight || canvas.height;
        // padding
        const pad = 30;
        
        // Calculate bounds
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        Object.values(graphNodes).forEach(n => {
            if(n.x < minX) minX = n.x; if(n.x > maxX) maxX = n.x;
            if(n.y < minY) minY = n.y; if(n.y > maxY) maxY = n.y;
        });

        // Add dummy margins if 0
        if(maxX === minX) maxX += 1;
        if(maxY === minY) maxY += 1;

        canvas.width = cw;
        canvas.height = ch;
        ctx.clearRect(0,0,cw,ch);

        const getXY = (x, y) => {
            const px = pad + ((x - minX) / (maxX - minX)) * (cw - pad*2);
            const py = pad + ((y - minY) / (maxY - minY)) * (ch - pad*2);
            return {px, py};
        };

        // Heatmap blobs
        if(isHeatmap) {
            Object.keys(graphNodes).forEach(node => {
                const {px, py} = getXY(graphNodes[node].x, graphNodes[node].y);
                
                // create radial gradient blob
                const rad = node === 'Highway' ? 80 : (node === 'Sector 3' ? 100 : 50);
                const colorStr = node === 'Sector 3' ? '239, 68, 68' : (node === 'Highway' ? '245, 158, 11' : '59, 130, 246');
                
                const grad = ctx.createRadialGradient(px, py, 0, px, py, rad);
                grad.addColorStop(0, `rgba(${colorStr}, 0.5)`);
                grad.addColorStop(1, `rgba(${colorStr}, 0)`);
                
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(px, py, rad, 0, Math.PI*2);
                ctx.fill();
            });
        }

        // Draw Edges
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        edges.forEach(e => {
            const n1 = graphNodes[e[0]], n2 = graphNodes[e[1]];
            if(n1 && n2) {
                const p1 = getXY(n1.x, n1.y);
                const p2 = getXY(n2.x, n2.y);
                ctx.beginPath();
                ctx.moveTo(p1.px, p1.py);
                ctx.lineTo(p2.px, p2.py);
                ctx.stroke();
            }
        });

        // Highlight Path
        if(highlightedPath && highlightedPath.length > 1) {
            ctx.lineWidth = 4;
            ctx.strokeStyle = '#D4AF37'; // Gold
            ctx.beginPath();
            highlightedPath.forEach((node, i) => {
                const n = graphNodes[node] || graphNodes['Downtown'];
                const p = getXY(n.x, n.y);
                if(i===0) ctx.moveTo(p.px, p.py);
                else ctx.lineTo(p.px, p.py);
            });
            ctx.stroke();
        }

        // Draw Nodes
        Object.keys(graphNodes).forEach(node => {
            const p = getXY(graphNodes[node].x, graphNodes[node].y);
            const isHl = highlightedPath && highlightedPath.includes(node);
            
            ctx.beginPath();
            ctx.arc(p.px, p.py, 6, 0, Math.PI*2);
            ctx.fillStyle = isHl ? '#D4AF37' : '#141C2A';
            ctx.fill();
            ctx.lineWidth = 2;
            ctx.strokeStyle = isHl ? '#FFF' : '#475569';
            ctx.stroke();

            // Label
            ctx.fillStyle = '#94A3B8';
            ctx.font = '11px JetBrains Mono, monospace';
            ctx.textAlign = 'center';
            ctx.fillText(node, p.px, p.py - 12);
        });
    }

    // Initial canvas draws (timeout to ensure sizing applies)
    setTimeout(() => {
        drawGraph('heatmapCanvas', null, true);
        drawGraph('routeCanvas', ['Station', 'Downtown', 'Highway'], false); // Mock active route on dashboard
    }, 100);

    // Redraw on resize
    window.addEventListener('resize', () => {
        drawGraph('heatmapCanvas', null, true);
        drawGraph('routeCanvas', ['Station', 'Downtown', 'Highway'], false);
        if(!document.getElementById('tab-results').classList.contains('hidden')) {
            drawGraph('resultsRouteCanvas', window.lastPath, false);
        }
    });


    /* ==========================================================================
       AI LOGIC & FORM SUBMISSION
       ========================================================================== */
    const form = document.getElementById('emergency-form');
    const analyzeBtn = document.getElementById('analyze-btn');

    if(form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // UI Loading state
            const btnText = analyzeBtn.querySelector('.btn-text');
            const spinner = analyzeBtn.querySelector('.loading-spinner');
            btnText.classList.add('hidden');
            spinner.classList.remove('hidden');
            analyzeBtn.disabled = true;

            const data = {
                loc: document.getElementById('location').value.trim() || 'Sector 4',
                type: document.getElementById('emergencyType').value,
                sev: document.getElementById('injurySeverity').value,
                delay: parseInt(document.getElementById('timeDelay').value, 10),
                risk: document.getElementById('riskLevel').value
            };

            // Simulate processing
            setTimeout(() => {
                processAI(data);
                
                btnText.classList.remove('hidden');
                spinner.classList.add('hidden');
                analyzeBtn.disabled = false;
                
                switchTab('tab-results', 'AI Analysis & Dispatch');
            }, 1800);
        });
    }

    function processAI(data) {
        // Rule Engine (Priority)
        let priority = 'LOW';
        if (data.sev === 'High' || data.risk === 'High' || data.delay > 30) priority = 'CRITICAL';
        else if (data.sev === 'Medium' || data.risk === 'Medium' || data.delay > 15) priority = 'HIGH';

        // ML Classification Simulation
        let mlSeverity = 'MINOR';
        let score = (data.sev === 'High' ? 3 : data.sev === 'Medium' ? 2 : 1) + 
                    (data.risk === 'High' ? 3 : data.risk === 'Medium' ? 2 : 1);
        if(score >= 5) mlSeverity = 'SEVERE';
        else if(score >= 3) mlSeverity = 'MODERATE';

        // CSP (Unit Assignment)
        let cType = data.type === 'Fire' ? 'Fire' : (data.type === 'Medical' ? 'Medical' : 'Police');
        let assigned = resources.find(r => r.type === cType && r.status === 'Available');
        if(!assigned) assigned = resources.find(r => r.status === 'Available') || { id: 'MUTUAL-AID-01', loc: 'Station' };

        // Graph Pathfinding
        let dest = Object.keys(graphNodes).find(k => data.loc.toLowerCase().includes(k.toLowerCase())) || 'Sector 4';
        let start = assigned.loc;
        let path = [start];
        if(start !== dest) {
            if(start !== 'Downtown' && dest !== 'Downtown') path.push('Downtown');
            path.push(dest);
        }
        let eta = (path.length - 1) * 4 + Math.floor(Math.random() * 3);
        if(eta === 0) eta = 2; // min eta
        
        window.lastPath = path;

        // Means-End Plan
        let plan = [
            `Incident registered via Neural Ingestion. Assigned Priority: <span class="gold-text">${priority}</span>`,
            `Dispatching <span class="gold-text">${assigned.id}</span> from ${assigned.loc}.`,
            `Navigating optimal path (${path.join(' → ')}). ETA: ${eta} mins.`
        ];
        if(data.type === 'Medical') plan.push(`Alerting Central City Hospital to reserve Trauma Bay 2.`);
        else if(data.type === 'Fire') plan.push(`Connecting to city water grid to optimize hydrant pressure at ${dest}.`);
        else plan.push(`Notifying traffic control to alter signal patterns along response corridor.`);

        // Render to UI
        document.getElementById('results-placeholder').classList.add('hidden');
        document.getElementById('active-results').classList.remove('hidden');

        document.getElementById('res-priority').textContent = priority;
        document.getElementById('res-priority').className = `res-kpi-val ${priority === 'CRITICAL' ? 'negative' : (priority === 'HIGH' ? 'negative' : 'positive')}`;
        
        document.getElementById('res-severity').textContent = mlSeverity;
        
        document.getElementById('res-unit').textContent = assigned.id;
        document.getElementById('res-eta').textContent = `${eta} min`;
        
        const etaDisp = document.getElementById('eta-display');
        etaDisp.textContent = `ETA: ${eta} min`;
        etaDisp.classList.remove('hidden');

        const planList = document.getElementById('res-plan');
        planList.innerHTML = '';
        plan.forEach(step => {
            planList.insertAdjacentHTML('beforeend', `<div class="plan-step">${step}</div>`);
        });

        // Add to active emergencies and timeline
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', {hour12: false});
        
        const newIncId = `INC-${902 + Math.floor(Math.random()*100)}`;
        activeEmergencies.unshift({
            id: newIncId,
            title: `${data.type} Emergency`,
            loc: data.loc,
            type: data.type,
            status: priority === 'CRITICAL' ? 'crit' : (priority==='HIGH'?'high':'med'),
            time: now.toLocaleTimeString('en-US', {hour:'2-digit', minute:'2-digit'}),
            unit: assigned.id
        });
        if(activeEmergencies.length > 4) activeEmergencies.pop();

        timelineEvents.unshift({
            time: timeStr,
            msg: `${newIncId} processed. AI dispatched ${assigned.id} to ${data.loc}.`
        });
        if(timelineEvents.length > 5) timelineEvents.pop();

        document.getElementById('kpi-active').textContent = activeEmergencies.length + 9; // dummy counter increase
        
        renderEmergencyCards();
        renderTimeline();

        // Draw graph (timeout for display:block to calculate dims)
        setTimeout(() => {
            drawGraph('resultsRouteCanvas', path, false);
        }, 100);
    }
});
