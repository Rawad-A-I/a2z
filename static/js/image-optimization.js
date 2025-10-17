/**
 * Image optimization and preview functionality
 */

function previewImage(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        const reader = new FileReader();
        
        // Show loading state
        showImagePreview(input, 'loading');
        
        reader.onload = function(e) {
            // Show preview
            showImagePreview(input, 'loaded', e.target.result);
            
            // Show optimization info
            showOptimizationInfo(file);
        };
        
        reader.readAsDataURL(file);
    }
}

function showImagePreview(input, state, imageSrc = null) {
    let previewContainer = input.parentNode.querySelector('.image-preview');
    
    if (!previewContainer) {
        previewContainer = document.createElement('div');
        previewContainer.className = 'image-preview mt-2';
        input.parentNode.appendChild(previewContainer);
    }
    
    previewContainer.innerHTML = '';
    
    if (state === 'loading') {
        previewContainer.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-spinner fa-spin"></i> Processing image...
            </div>
        `;
    } else if (state === 'loaded' && imageSrc) {
        previewContainer.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle"></i> Image ready for upload
            </div>
            <div class="mt-2">
                <img src="${imageSrc}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;" alt="Preview">
            </div>
        `;
    }
}

function showOptimizationInfo(file) {
    const infoContainer = document.querySelector('.optimization-info');
    if (!infoContainer) return;
    
    const fileSize = (file.size / 1024 / 1024).toFixed(2); // MB
    const fileName = file.name;
    const fileType = file.type;
    
    let optimizationMessage = '';
    
    if (file.size > 5 * 1024 * 1024) { // 5MB
        optimizationMessage = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Large file detected:</strong> This image (${fileSize}MB) will be automatically optimized for web use.
            </div>
        `;
    } else if (file.size > 1 * 1024 * 1024) { // 1MB
        optimizationMessage = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                <strong>Optimization:</strong> This image (${fileSize}MB) will be compressed and resized for optimal web performance.
            </div>
        `;
    } else {
        optimizationMessage = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle"></i>
                <strong>Good size:</strong> This image (${fileSize}MB) will be optimized for web use.
            </div>
        `;
    }
    
    infoContainer.innerHTML = `
        <div class="card mt-3">
            <div class="card-header">
                <h6 class="mb-0"><i class="fas fa-cog"></i> Image Optimization Info</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <strong>Original File:</strong><br>
                        <small class="text-muted">
                            Name: ${fileName}<br>
                            Size: ${fileSize} MB<br>
                            Type: ${fileType}
                        </small>
                    </div>
                    <div class="col-md-6">
                        <strong>After Optimization:</strong><br>
                        <small class="text-muted">
                            Format: WebP<br>
                            Min Size: 400x400px<br>
                            Quality: 80%<br>
                            Estimated: 50-70% smaller
                        </small>
                    </div>
                </div>
                ${optimizationMessage}
            </div>
        </div>
    `;
}

function showOptimizationResults(originalSize, optimizedSize, savingsPercent) {
    const resultsContainer = document.querySelector('.optimization-results');
    if (!resultsContainer) return;
    
    const originalMB = (originalSize / 1024 / 1024).toFixed(2);
    const optimizedMB = (optimizedSize / 1024 / 1024).toFixed(2);
    const savingsMB = ((originalSize - optimizedSize) / 1024 / 1024).toFixed(2);
    
    resultsContainer.innerHTML = `
        <div class="alert alert-success">
            <h6><i class="fas fa-magic"></i> Image Optimization Complete!</h6>
            <div class="row">
                <div class="col-md-4">
                    <strong>Original:</strong> ${originalMB} MB
                </div>
                <div class="col-md-4">
                    <strong>Optimized:</strong> ${optimizedMB} MB
                </div>
                <div class="col-md-4">
                    <strong>Savings:</strong> ${savingsMB} MB (${savingsPercent}%)
                </div>
            </div>
        </div>
    `;
}

// Add optimization info container to forms
document.addEventListener('DOMContentLoaded', function() {
    // Add optimization info container to image upload forms
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        // Add optimization info container
        const infoContainer = document.createElement('div');
        infoContainer.className = 'optimization-info';
        input.parentNode.appendChild(infoContainer);
        
        // Add results container
        const resultsContainer = document.createElement('div');
        resultsContainer.className = 'optimization-results';
        input.parentNode.appendChild(resultsContainer);
    });
    
    // Add drag and drop functionality
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const container = input.closest('.form-group') || input.parentNode;
        
        // Add drag and drop styling
        container.style.border = '2px dashed #dee2e6';
        container.style.borderRadius = '8px';
        container.style.padding = '20px';
        container.style.textAlign = 'center';
        container.style.transition = 'all 0.3s ease';
        
        // Add drag and drop event listeners
        container.addEventListener('dragover', function(e) {
            e.preventDefault();
            container.style.borderColor = '#007bff';
            container.style.backgroundColor = '#f8f9fa';
        });
        
        container.addEventListener('dragleave', function(e) {
            e.preventDefault();
            container.style.borderColor = '#dee2e6';
            container.style.backgroundColor = 'transparent';
        });
        
        container.addEventListener('drop', function(e) {
            e.preventDefault();
            container.style.borderColor = '#dee2e6';
            container.style.backgroundColor = 'transparent';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                previewImage(input);
            }
        });
    });
});

// Utility function to format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
