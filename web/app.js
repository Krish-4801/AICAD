// Global variables for 3D Viewer
let scene, camera, renderer, controls;
let currentMesh = null;
let currentRequestId = null;
let pollInterval = null;

// History data structures
let historyData = [];
const historyMap = new Map();

// DOM Elements
const serverStatusDot = document.getElementById('server-status-dot');
const serverStatusText = document.getElementById('server-status-text');
const historyList = document.getElementById('history-list');
const btnGenerate = document.getElementById('btn-generate');
const promptInput = document.getElementById('prompt-input');
const generationForm = document.getElementById('generation-form');
const chatMessages = document.getElementById('chat-messages');

// Tabs
const tab3d = document.getElementById('tab-3d');
const tab2d = document.getElementById('tab-2d');
const tabCode = document.getElementById('tab-code');
const content3d = document.getElementById('content-3d');
const content2d = document.getElementById('content-2d');
const contentCode = document.getElementById('content-code');

// Actions / Interactive
const canvasContainer = document.getElementById('canvas-container');
const viewerControls = document.getElementById('viewer-controls');
const btnResetView = document.getElementById('btn-reset-view');
const btnToggleWireframe = document.getElementById('btn-toggle-wireframe');
const snapshotContainer = document.getElementById('snapshot-container');
const codeDisplay = document.getElementById('code-display');
const btnCopyCode = document.getElementById('btn-copy-code');
const downloadCard = document.getElementById('download-card');

// Downloads
const downloadStep = document.getElementById('download-step');
const downloadStl = document.getElementById('download-stl');
const downloadPy = document.getElementById('download-py');

// Global Loading overlay
const globalLoading = document.getElementById('global-loading');
const globalLoadingText = document.getElementById('global-loading-text');

// Init application
document.addEventListener('DOMContentLoaded', () => {
    init3DViewer();
    checkServerConnection();
    loadHistory().then(() => {
        // Automatically select latest model on page load
        if (historyData.length > 0) {
            selectHistoryItem(historyData[0]);
        } else {
            showOnboarding();
        }
    });
    setupEventListeners();
    
    // Check connection every 10 seconds
    setInterval(checkServerConnection, 10000);
});

// Setup 3D Viewer Scene
function init3DViewer() {
    const width = canvasContainer.clientWidth || 400;
    const height = canvasContainer.clientHeight || 400;

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x06090f);

    // Camera
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(100, 100, 100);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    
    // Clear placeholder and append canvas
    const canvas = canvasContainer.querySelector('canvas');
    if (canvas) canvas.remove();
    
    const placeholder = canvasContainer.querySelector('.viewer-placeholder');
    if (placeholder) placeholder.remove();

    canvasContainer.appendChild(renderer.domElement);

    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.screenSpacePanning = true;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x333333);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight1.position.set(1, 1, 1).normalize();
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x555555, 0.5);
    dirLight2.position.set(-1, -1, -1).normalize();
    scene.add(dirLight2);

    const pointLight = new THREE.PointLight(0x6366f1, 0.5, 100);
    pointLight.position.set(0, 50, 0);
    scene.add(pointLight);

    // Grid Helper
    const gridHelper = new THREE.GridHelper(200, 50, 0x6366f1, 0x222530);
    gridHelper.position.y = -0.01;
    scene.add(gridHelper);

    // Axes Helper
    const axesHelper = new THREE.AxesHelper(30);
    scene.add(axesHelper);

    // Animation Loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', onWindowResize);
}

function onWindowResize() {
    if (!canvasContainer || !camera || !renderer) return;
    const width = canvasContainer.clientWidth;
    const height = canvasContainer.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}

// Check connection to backend
async function checkServerConnection() {
    try {
        const response = await fetch('/api/history');
        if (response.ok) {
            serverStatusDot.className = 'status-dot online';
            serverStatusText.textContent = 'Agent Server Online';
        } else {
            throw new Error();
        }
    } catch (e) {
        serverStatusDot.className = 'status-dot offline';
        serverStatusText.textContent = 'Agent Server Offline';
    }
}

// Load Generation History
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) return;
        historyData = await response.json();
        
        historyMap.clear();
        historyData.forEach(item => {
            historyMap.set(item.id, item);
        });
        
        renderHistorySidebar();
        
        // Refresh active chat if running
        if (currentRequestId) {
            const currentItem = historyMap.get(currentRequestId);
            if (currentItem) {
                renderChatAndWorkspace(currentItem);
            }
        }
    } catch (e) {
        console.error('Failed to load history', e);
    }
}

// Render History Items in Sidebar
function renderHistorySidebar() {
    if (historyData.length === 0) {
        historyList.innerHTML = '<div class="no-history">No models generated yet</div>';
        return;
    }

    historyList.innerHTML = '';
    historyData.forEach(item => {
        const date = new Date(item.timestamp * 1000).toLocaleString();
        const div = document.createElement('div');
        div.className = `history-item ${item.id === currentRequestId ? 'active' : ''}`;
        div.id = `history-item-${item.id}`;
        
        let title = item.prompt;
        if (title.length > 50) {
            title = title.substring(0, 47) + '...';
        }

        const isEdit = !!item.parent_id;
        const titleHTML = isEdit
            ? `<h4><i class="fa-solid fa-pen-to-square" style="color: var(--primary); margin-right: 4px;"></i> Edit: ${escapeHTML(title)}</h4>`
            : `<h4><i class="fa-solid fa-circle-plus" style="color: var(--accent-emerald); margin-right: 4px;"></i> ${escapeHTML(title)}</h4>`;

        let statusClass = item.status;
        let statusLabel = item.status;
        if (item.status === 'processing') {
            statusLabel = item.step || 'processing';
        }

        div.innerHTML = `
            ${titleHTML}
            <p>${date}</p>
            <span class="status-badge ${statusClass}">${statusLabel}</span>
        `;
        
        div.addEventListener('click', () => {
            selectHistoryItem(item);
        });
        
        historyList.appendChild(div);
    });
}

// Select a past generation item
function selectHistoryItem(item) {
    currentRequestId = item.id;

    // Update active UI classes
    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
    const activeEl = document.getElementById(`history-item-${item.id}`);
    if (activeEl) activeEl.classList.add('active');

    // Update chat input hints
    let briefTitle = item.prompt;
    if (briefTitle.length > 25) {
        briefTitle = briefTitle.substring(0, 22) + '...';
    }
    document.getElementById('chat-title').textContent = `Thread: ${briefTitle}`;
    promptInput.placeholder = "Ask to edit this model (e.g. 'make it 10mm thicker')...";

    renderChatAndWorkspace(item);
}

// Trace the parent tree and render the conversation
function renderChatAndWorkspace(item) {
    // 1. Trace the chain backwards
    let chain = [];
    let curr = item;
    while (curr) {
        chain.unshift(curr);
        if (curr.parent_id) {
            curr = historyMap.get(curr.parent_id);
        } else {
            curr = null;
        }
    }

    // 2. Render messages
    chatMessages.innerHTML = '';
    chain.forEach(req => {
        appendUserMessageHTML(chatMessages, req);
        appendAgentMessageHTML(chatMessages, req);
    });

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // 3. Update right side panel
    updateWorkspaceRightPanel(item);

    // 4. Handle Polling for active requests
    if (item.status === 'pending' || item.status === 'processing') {
        startPolling(item.id);
    } else {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    }
}

function appendUserMessageHTML(container, req) {
    const timeStr = new Date(req.timestamp * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    const div = document.createElement('div');
    div.className = 'chat-msg user';
    div.innerHTML = `
        <div class="chat-msg-meta">You • ${timeStr}</div>
        <div class="chat-msg-content">${escapeHTML(req.prompt)}</div>
    `;
    container.appendChild(div);
}

function appendAgentMessageHTML(container, req) {
    const timeStr = req.timestamp ? new Date(req.timestamp * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '';
    const div = document.createElement('div');
    div.className = 'chat-msg agent';
    div.id = `agent-msg-${req.id}`;
    
    if (req.status === 'success') {
        div.innerHTML = `
            <div class="chat-msg-meta">CAD Agent • ${timeStr}</div>
            <div class="chat-msg-content agent-success">
                <div class="agent-success-header">
                    <i class="fa-solid fa-circle-check"></i> Watertight Model Created
                </div>
                <p>Watertight parametric STEP geometry compiled successfully.</p>
                <div class="agent-success-actions">
                    <button class="btn-small" onclick="switchTab('3d')"><i class="fa-solid fa-cube"></i> View 3D</button>
                    <button class="btn-small" onclick="switchTab('code')"><i class="fa-solid fa-code"></i> View Code</button>
                </div>
            </div>
        `;
    } else if (req.status === 'failed') {
        div.innerHTML = `
            <div class="chat-msg-meta">CAD Agent • ${timeStr}</div>
            <div class="chat-msg-content agent-failed">
                <div class="agent-failed-header">
                    <i class="fa-solid fa-circle-xmark"></i> Generation Failed
                </div>
                <p>${escapeHTML(req.error || 'Unknown pipeline execution error')}</p>
            </div>
        `;
    } else {
        // Pending/Processing
        const template = document.getElementById('progress-template');
        const clone = template.firstElementChild.cloneNode(true);
        clone.id = `progress-box-${req.id}`;
        
        div.innerHTML = `<div class="chat-msg-meta">CAD Agent • Processing...</div>`;
        div.appendChild(clone);
        
        updateProgressBoxUI(clone, req);
    }
    
    container.appendChild(div);
}

function updateProgressBoxUI(box, req) {
    const logsContent = box.querySelector('.status-logs-content');
    if (logsContent) {
        logsContent.textContent = req.error || req.logs || `Status: ${req.status}\nStep: ${req.step || 'queued'}`;
        logsContent.scrollTop = logsContent.scrollHeight;
    }
    
    const stepOrder = ['queued', 'waking', 'coding', 'compiling', 'visualizing'];
    const currentStepIdx = stepOrder.indexOf(req.step || 'queued');
    
    const stepItems = box.querySelectorAll('.step-item');
    stepItems.forEach((stepEl, idx) => {
        stepEl.className = 'step-item';
        
        if (idx < currentStepIdx) {
            stepEl.classList.add('completed');
        } else if (idx === currentStepIdx) {
            if (req.status === 'failed') {
                stepEl.className = 'step-item active';
            } else {
                stepEl.classList.add('active');
            }
        }
    });

    if (req.status === 'success') {
        stepItems.forEach(stepEl => {
            stepEl.className = 'step-item completed';
        });
    }
}

// Onboarding Welcome
function showOnboarding() {
    currentRequestId = null;
    document.getElementById('chat-title').textContent = "New CAD Session";
    promptInput.placeholder = "Describe a new 3D model to generate...";
    
    chatMessages.innerHTML = `
        <div id="chat-onboarding" class="chat-onboarding">
            <div class="onboarding-welcome">
                <i class="fa-solid fa-wand-magic-sparkles onboarding-icon text-gradient"></i>
                <h3>Generative CAD Assistant</h3>
                <p>Describe your 3D part in natural language to generate STEP/STL files, then refine it in chat!</p>
            </div>
            <div class="onboarding-suggestions">
                <h4>Try a suggestion:</h4>
                <div class="suggestions">
                    <span class="suggestion-tag" data-prompt="Make an L-bracket, 50mm on each side, 4mm thick, with 2 M4 clearance holes on each leg.">L-Bracket</span>
                    <span class="suggestion-tag" data-prompt="A simple hex nut with 10mm flat-to-flat distance, 5mm thickness, and an M5 threaded clearance hole.">M5 Hex Nut</span>
                    <span class="suggestion-tag" data-prompt="An enclosure lid: rectangular box cover 120x80mm, 2.5mm wall thickness, with a 1.5mm lip and four corner screw holes.">Enclosure Lid</span>
                </div>
            </div>
        </div>
    `;
    
    // Suggestion binds
    chatMessages.querySelectorAll('.suggestion-tag').forEach(tag => {
        tag.addEventListener('click', () => {
            promptInput.value = tag.getAttribute('data-prompt');
            promptInput.focus();
        });
    });

    updateWorkspaceRightPanel({ status: 'new' });
    
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// Update Right Workspace Panel
function updateWorkspaceRightPanel(item) {
    if (item.status === 'success') {
        downloadCard.classList.remove('hidden');
        viewerControls.classList.remove('hidden');

        // Load 3D model
        load3DModel(`/requests/${item.id}/model.stl`);

        // Load snapshot
        if (item.snapshot_path) {
            snapshotContainer.innerHTML = `<img src="${item.snapshot_path}" alt="CAD Render Snapshot">`;
        } else {
            snapshotContainer.innerHTML = `
                <div class="viewer-placeholder">
                    <i class="fa-solid fa-triangle-exclamation placeholder-icon"></i>
                    <p>No snapshot render available</p>
                </div>`;
        }

        // Load Python Code
        if (item.code) {
            codeDisplay.textContent = item.code;
            Prism.highlightElement(codeDisplay);
        } else {
            codeDisplay.textContent = '# No generator code saved.';
        }

        // Setup Downloads
        downloadStep.href = `/requests/${item.id}/model.step`;
        downloadStl.href = `/requests/${item.id}/model.stl`;
        downloadPy.href = `/requests/${item.id}/model.py`;
    } else {
        downloadCard.classList.add('hidden');
        viewerControls.classList.add('hidden');
        
        show3DPlaceholder();
        
        if (item.status === 'pending' || item.status === 'processing') {
            snapshotContainer.innerHTML = `
                <div class="viewer-placeholder">
                    <i class="fa-solid fa-spinner fa-spin placeholder-icon"></i>
                    <p>Generating CAD files... Snapshot will appear here when complete</p>
                </div>`;
            codeDisplay.textContent = '# Generating Python code... Please wait.';
        } else if (item.status === 'failed') {
            snapshotContainer.innerHTML = `
                <div class="viewer-placeholder text-danger">
                    <i class="fa-solid fa-circle-xmark placeholder-icon"></i>
                    <p>Generation failed</p>
                </div>`;
            codeDisplay.textContent = `# Generation Failed.\n\nError: ${item.error || 'Unknown error'}`;
        } else {
            // New state (Onboarding)
            snapshotContainer.innerHTML = `
                <div class="viewer-placeholder">
                    <i class="fa-solid fa-image placeholder-icon"></i>
                    <p>Snapshot image will be displayed here</p>
                </div>`;
            codeDisplay.textContent = '# Generated build123d code will appear here...';
        }
    }
}

// Show placeholder in canvas container
function show3DPlaceholder() {
    canvasContainer.innerHTML = `
        <div class="viewer-placeholder">
            <i class="fa-solid fa-drafting-compass placeholder-icon"></i>
            <p>Generate a CAD model to interact with it in 3D</p>
        </div>`;
    if (currentMesh) {
        scene.remove(currentMesh);
        currentMesh = null;
    }
}

// Load STL into Three.js
function load3DModel(url) {
    showLoadingOverlay('Loading 3D model...');

    // Re-initialize viewer if placeholder is currently showing
    if (!canvasContainer.querySelector('canvas')) {
        init3DViewer();
    }

    // Remove existing mesh
    if (currentMesh) {
        scene.remove(currentMesh);
        currentMesh = null;
    }

    const loader = new THREE.STLLoader();
    loader.load(url, (geometry) => {
        geometry.computeVertexNormals();
        geometry.center();

        // Material (Premium metallic look with slight roughness)
        const material = new THREE.MeshStandardMaterial({
            color: 0x94a3b8, // light slate
            metalness: 0.7,
            roughness: 0.3,
            side: THREE.DoubleSide
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        scene.add(mesh);
        currentMesh = mesh;

        // Auto-zoom to fit the object
        geometry.computeBoundingSphere();
        const sphere = geometry.boundingSphere;
        const radius = sphere.radius;

        const fov = camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(radius / Math.sin(fov / 2)) * 1.5;

        camera.position.set(cameraZ, cameraZ, cameraZ);
        camera.lookAt(new THREE.Vector3(0, 0, 0));
        
        controls.target.set(0, 0, 0);
        controls.update();

        hideLoadingOverlay();
    }, 
    (xhr) => {
        if (xhr.lengthComputable) {
            const percent = Math.round((xhr.loaded / xhr.total) * 100);
            globalLoadingText.textContent = `Loading 3D Model: ${percent}%`;
        }
    },
    (error) => {
        console.error('An error happened while loading the STL mesh', error);
        hideLoadingOverlay();
        canvasContainer.innerHTML = `
            <div class="viewer-placeholder">
                <i class="fa-solid fa-triangle-exclamation placeholder-icon text-danger"></i>
                <p>Failed to load 3D model geometry</p>
            </div>`;
    });
}

// Start polling API for status
function startPolling(id) {
    if (pollInterval) clearInterval(pollInterval);
    
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${id}`);
            if (!response.ok) return;
            const data = await response.json();

            historyMap.set(id, data);
            
            // Find active progress box inside chat and update it
            const progressBox = document.getElementById(`progress-box-${id}`);
            if (progressBox) {
                updateProgressBoxUI(progressBox, data);
            }

            if (data.status === 'success' || data.status === 'failed') {
                clearInterval(pollInterval);
                pollInterval = null;
                await loadHistory();
            }
        } catch (e) {
            console.error('Polling error', e);
        }
    }, 1500);
}

// Tabs switching handler
function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    if (tabName === '3d') {
        tab3d.classList.add('active');
        content3d.classList.add('active');
        onWindowResize();
    } else if (tabName === '2d') {
        tab2d.classList.add('active');
        content2d.classList.add('active');
    } else if (tabName === 'code') {
        tabCode.classList.add('active');
        contentCode.classList.add('active');
    }
}

// Event Listeners setup
function setupEventListeners() {
    // Form Submit
    generationForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = promptInput.value.trim();
        if (!prompt) return;

        btnGenerate.disabled = true;
        btnGenerate.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';

        const requestBody = { prompt };
        if (currentRequestId) {
            requestBody.parent_id = currentRequestId;
        }

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) throw new Error('API request failed');
            const data = await response.json();

            promptInput.value = '';
            currentRequestId = data.id;

            historyMap.set(data.id, data);
            await loadHistory();
        } catch (err) {
            alert('Failed to send request to CAD pipeline server.');
        } finally {
            btnGenerate.disabled = false;
            btnGenerate.innerHTML = '<i class="fa-solid fa-play"></i> Run CAD Agent';
        }
    });

    // Suggestions Click
    document.querySelectorAll('.suggestion-tag').forEach(tag => {
        tag.addEventListener('click', () => {
            promptInput.value = tag.getAttribute('data-prompt');
            promptInput.focus();
        });
    });

    // New Model button
    const btnNewChat = document.getElementById('btn-new-chat');
    if (btnNewChat) {
        btnNewChat.addEventListener('click', () => {
            showOnboarding();
        });
    }

    // Tab Buttons
    tab3d.addEventListener('click', () => switchTab('3d'));
    tab2d.addEventListener('click', () => switchTab('2d'));
    tabCode.addEventListener('click', () => switchTab('code'));

    // Viewer Reset View
    btnResetView.addEventListener('click', () => {
        if (!currentMesh) return;
        currentMesh.geometry.computeBoundingSphere();
        const radius = currentMesh.geometry.boundingSphere.radius;
        const fov = camera.fov * (Math.PI / 180);
        let cameraZ = Math.abs(radius / Math.sin(fov / 2)) * 1.5;
        camera.position.set(cameraZ, cameraZ, cameraZ);
        camera.lookAt(new THREE.Vector3(0, 0, 0));
        controls.target.set(0, 0, 0);
        controls.update();
    });

    // Toggle Wireframe
    btnToggleWireframe.addEventListener('click', () => {
        if (!currentMesh) return;
        currentMesh.material.wireframe = !currentMesh.material.wireframe;
        btnToggleWireframe.classList.toggle('active');
        btnToggleWireframe.innerHTML = currentMesh.material.wireframe ? 
            '<i class="fa-solid fa-cubes"></i> Shaded' : 
            '<i class="fa-solid fa-border-none"></i> Wireframe';
    });

    // Copy Code Button
    btnCopyCode.addEventListener('click', () => {
        navigator.clipboard.writeText(codeDisplay.textContent).then(() => {
            const originalHTML = btnCopyCode.innerHTML;
            btnCopyCode.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                btnCopyCode.innerHTML = originalHTML;
            }, 2000);
        });
    });
}

// Utility Loader functions
function showLoadingOverlay(text) {
    globalLoadingText.textContent = text;
    globalLoading.classList.remove('hidden');
}

// Global scope switchTab helper (called from inline button onclick events)
window.switchTab = switchTab;

function hideLoadingOverlay() {
    globalLoading.classList.add('hidden');
}

function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
