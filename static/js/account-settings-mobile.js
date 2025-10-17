// Mobile Account Settings JavaScript
class MobileAccountSettings {
    constructor() {
        this.currentSection = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupNotificationToggles();
    }

    setupEventListeners() {
        // Profile picture edit
        const editBtn = document.querySelector('.profile-section button');
        if (editBtn) {
            editBtn.addEventListener('click', () => this.editProfilePicture());
        }

        // Menu item clicks
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.onclick.toString().match(/'([^']+)'/)[1];
                this.openSection(section);
            });
        });

        // Back buttons
        document.querySelectorAll('.back-btn').forEach(btn => {
            btn.addEventListener('click', () => this.goBackToMenu());
        });
    }

    setupNotificationToggles() {
        document.querySelectorAll('.switch input').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const isChecked = e.target.checked;
                const container = e.target.closest('.flex');
                const title = container.querySelector('p').textContent;

                // Show feedback
                this.showToast(`${title} ${isChecked ? 'enabled' : 'disabled'}`, 'success');
            });
        });
    }

    openSection(sectionName) {
        this.currentSection = sectionName;

        // Hide main menu
        document.querySelector('.mobile-account-settings > .account-menu').style.display = 'none';
        document.querySelector('.profile-section').style.display = 'none';

        // Show section content
        const sectionContent = document.getElementById('section-content');
        sectionContent.classList.remove('hidden');

        // Hide all section pages
        document.querySelectorAll('.section-page').forEach(page => {
            page.classList.remove('active');
        });

        // Show target section
        const targetPage = document.getElementById(`${sectionName}-page`);
        if (targetPage) {
            targetPage.classList.add('active');
        }

        // Update header title
        const sectionTitles = {
            'notifications': 'Notification Settings',
            'orders': 'My Orders',
            'payment': 'Payment Methods',
            'cart': 'Shopping Cart',
            'wishlist': 'Wish List',
            'password': 'Change Password'
        };

        const headerTitle = document.querySelector('.section-header h2');
        if (headerTitle && sectionTitles[sectionName]) {
            headerTitle.textContent = sectionTitles[sectionName];
        }
    }

    goBackToMenu() {
        // Show main menu
        document.querySelector('.mobile-account-settings > .account-menu').style.display = 'block';
        document.querySelector('.profile-section').style.display = 'block';

        // Hide section content
        document.getElementById('section-content').classList.add('hidden');

        // Reset current section
        this.currentSection = null;
    }

    editProfilePicture() {
        // Create file input
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = (e) => this.handleProfilePictureUpload(e);

        // Trigger file selection
        input.click();
    }

    handleProfilePictureUpload(event) {
        const file = event.target.files[0];
        if (file) {
            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                this.showToast('Image must be smaller than 5MB', 'error');
                return;
            }

            // Validate file type
            if (!file.type.startsWith('image/')) {
                this.showToast('Please select a valid image file', 'error');
                return;
            }

            // Show loading state
            this.showLoading();

            // Simulate upload (replace with actual upload logic)
            setTimeout(() => {
                this.hideLoading();

                // Update profile picture preview
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('profile-picture').src = e.target.result;
                };
                reader.readAsDataURL(file);

                this.showToast('Profile picture updated successfully!', 'success');
            }, 1500);
        }
    }

    showLoading() {
        // Add loading overlay
        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        overlay.id = 'loading-overlay';
        overlay.innerHTML = `
            <div class="bg-white p-4 rounded-lg flex items-center space-x-3">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span class="text-gray-700">Loading...</span>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    showToast(message, type = 'info') {
        // Remove existing toasts
        document.querySelectorAll('.toast').forEach(toast => toast.remove());

        const toastTypes = {
            'success': 'bg-green-500',
            'error': 'bg-red-500',
            'warning': 'bg-yellow-500',
            'info': 'bg-blue-500'
        };

        const toast = document.createElement('div');
        toast.className = `toast fixed top-4 right-4 px-4 py-3 text-white rounded-lg shadow-lg z-50 ${toastTypes[type]}`;
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2"></i>
                <span class="text-sm">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    }
}

// Global functions for onclick handlers
function goBack() {
    if (window.mobileAccountSettings && window.mobileAccountSettings.currentSection) {
        window.mobileAccountSettings.goBackToMenu();
    } else {
        // Fallback for browsers without history
        window.location.href = '/';
    }
}

function openSection(sectionName) {
    if (window.mobileAccountSettings) {
        window.mobileAccountSettings.openSection(sectionName);
    }
}

function goBackToMenu() {
    if (window.mobileAccountSettings) {
        window.mobileAccountSettings.goBackToMenu();
    }
}

function editProfilePicture() {
    if (window.mobileAccountSettings) {
        window.mobileAccountSettings.editProfilePicture();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.mobileAccountSettings = new MobileAccountSettings();
});
