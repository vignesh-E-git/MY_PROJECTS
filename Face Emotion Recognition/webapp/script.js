// ==================== Global State ====================
let uploadedFile = null;

// Emotion emoji mapping
const emotionEmojis = {
    'angry': '😠',
    'disgust': '🤢',
    'fear': '😨',
    'happy': '😊',
    'sad': '😢',
    'surprise': '😲',
    'neutral': '😐'
};

// ==================== Navigation Functions ====================
function navigateToApp() {
    window.location.href = 'app.html';
}

function navigateToIntro() {
    window.location.href = 'index.html';
}

// ==================== Page Initialization ====================
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the app page
    if (document.getElementById('uploadZone')) {
        initializeUpload();
    }
});

// ==================== Upload Functionality ====================
function initializeUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    // Click to upload
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        
        const file = e.dataTransfer.files[0];
        handleFileSelect(file);
    });
}

function handleFileSelect(file) {
    // Validate file
    if (!file) {
        return;
    }

    // Check file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp'];
    if (!validTypes.includes(file.type)) {
        showError('Invalid file type. Please upload an image file (JPG, PNG, GIF, or BMP).');
        return;
    }

    // Check file size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
        showError('File is too large. Maximum size is 16MB.');
        return;
    }

    // Store file
    uploadedFile = file;

    // Show preview
    showPreview(file);
}

function showPreview(file) {
    const reader = new FileReader();
    
    reader.onload = (e) => {
        const imagePreview = document.getElementById('imagePreview');
        imagePreview.src = e.target.result;
        
        // Hide upload section, show preview section
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('previewSection').style.display = 'block';
    };
    
    reader.readAsDataURL(file);
}

// ==================== Analysis Function ====================
async function analyzeEmotion() {
    if (!uploadedFile) {
        showError('No file selected. Please upload an image first.');
        return;
    }

    // Hide preview, show loading
    document.getElementById('previewSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'block';

    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', uploadedFile);

        // Send request to backend
        const response = await fetch('http://localhost:5000/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Show results
            showResults(data);
        } else {
            throw new Error(data.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to analyze emotion. Please try again.');
    }
}

// ==================== Results Display ====================
function showResults(data) {
    const { emotion, confidence, all_confidences } = data;

    // Hide loading, show results
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';

    // Update main emotion display
    const emotionEmoji = document.getElementById('emotionEmoji');
    const emotionLabel = document.getElementById('emotionLabel');
    const confidenceBadge = document.getElementById('confidenceBadge');

    emotionEmoji.textContent = emotionEmojis[emotion] || '😊';
    emotionLabel.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    confidenceBadge.textContent = `${(confidence * 100).toFixed(1)}% Confident`;

    // Apply emotion-specific color to label
    emotionLabel.style.color = getEmotionColor(emotion);

    // Update confidence bars
    const confidenceBars = document.getElementById('confidenceBars');
    confidenceBars.innerHTML = '';

    // Sort emotions by confidence (descending)
    const sortedEmotions = Object.entries(all_confidences)
        .sort((a, b) => b[1] - a[1]);

    sortedEmotions.forEach(([emotionName, confidenceValue]) => {
        const barElement = createConfidenceBar(emotionName, confidenceValue);
        confidenceBars.appendChild(barElement);
    });
}

function createConfidenceBar(emotion, confidence) {
    const percentage = (confidence * 100).toFixed(1);
    
    const barDiv = document.createElement('div');
    barDiv.className = 'confidence-bar';
    
    barDiv.innerHTML = `
        <div class="confidence-header">
            <span class="confidence-name">${emotionEmojis[emotion]} ${emotion.charAt(0).toUpperCase() + emotion.slice(1)}</span>
            <span class="confidence-value">${percentage}%</span>
        </div>
        <div class="confidence-track">
            <div class="confidence-fill ${emotion}" style="width: ${percentage}%"></div>
        </div>
    `;
    
    return barDiv;
}

function getEmotionColor(emotion) {
    const colors = {
        'angry': '#EF4444',
        'disgust': '#10B981',
        'fear': '#8B5CF6',
        'happy': '#F59E0B',
        'sad': '#3B82F6',
        'surprise': '#EC4899',
        'neutral': '#6B7280'
    };
    return colors[emotion] || '#8B5CF6';
}

// ==================== Error Handling ====================
function showError(message) {
    // Hide all sections
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('previewSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Show error section
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

// ==================== Reset Function ====================
function resetUpload() {
    // Clear uploaded file
    uploadedFile = null;
    
    // Reset file input
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.value = '';
    }
    
    // Hide all sections except upload
    document.getElementById('uploadSection').style.display = 'block';
    document.getElementById('previewSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
}

// ==================== Keyboard Shortcuts ====================
document.addEventListener('keydown', (e) => {
    // ESC to reset
    if (e.key === 'Escape') {
        const resultsSection = document.getElementById('resultsSection');
        const errorSection = document.getElementById('errorSection');
        
        if (resultsSection && resultsSection.style.display === 'block') {
            resetUpload();
        } else if (errorSection && errorSection.style.display === 'block') {
            resetUpload();
        }
    }
});
