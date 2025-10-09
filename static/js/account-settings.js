// Account Settings JavaScript
class AccountSettings {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupPasswordStrength();
        this.updateNotificationCounts();
    }

    setupEventListeners() {
        // Desktop sidebar navigation
        document.querySelectorAll('.settings-nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchSection(item.dataset.section);
            });
        });

        // Form submissions
        document.getElementById('personal-info-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.savePersonalInfo();
        });

        document.getElementById('password-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.changePassword();
        });

        // Mobile navigation
        document.getElementById('mobile-back-btn')?.addEventListener('click', () => {
            this.goBackToSettings();
        });
    }

    setupPasswordStrength() {
        const passwordInputs = [
            document.getElementById('new_password'),
            document.getElementById('mobile_new_password')
        ];

        passwordInputs.forEach(input => {
            if (input) {
                input.addEventListener('input', (e) => {
                    this.updatePasswordStrength(e.target.value, input.id.includes('mobile'));
                });
            }
        });
    }

    switchSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.settings-section').forEach(section => {
            section.classList.remove('active');
        });

        // Remove active state from nav items
        document.querySelectorAll('.settings-nav-item').forEach(item => {
            item.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Add active state to nav item
        const targetNav = document.querySelector(`[data-section="${sectionId}"]`);
        if (targetNav) {
            targetNav.classList.add('active');
        }

        // Scroll to top on mobile
        if (window.innerWidth <= 768) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    // Mobile Navigation
    openMobileSection(sectionId) {
        // Hide all mobile sections
        document.querySelectorAll('.mobile-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.querySelector(`[data-section="${sectionId}"]`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update mobile header
        const headerTitle = document.querySelector('.mobile-header h1');
        if (headerTitle) {
            const sectionNames = {
                'personal-info': 'Personal Information',
                'security': 'Security & Password',
                'notifications': 'Notifications',
                'linked-accounts': 'Linked Accounts',
                'danger-zone': 'Danger Zone'
            };
            headerTitle.textContent = sectionNames[sectionId] || 'Account Settings';
        }
    }

    goBackToSettings() {
        // Hide all mobile sections
        document.querySelectorAll('.mobile-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show main settings list
        document.querySelector('.mobile-sections').style.display = 'block';

        // Reset header
        const headerTitle = document.querySelector('.mobile-header h1');
        if (headerTitle) {
            headerTitle.textContent = 'Account Settings';
        }
    }

    // Personal Information
    savePersonalInfo() {
        const form = document.getElementById('personal-info-form');
        const formData = new FormData(form);

        this.showLoading();

        // Simulate API call
        setTimeout(() => {
            this.hideLoading();
            this.showAlert('Personal information updated successfully!', 'success');
        }, 1000);
    }

    previewProfilePicture(input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('profile-preview').src = e.target.result;
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    // Security & Password
    changePassword() {
        const form = document.getElementById('password-form');
        const formData = new FormData(form);

        const currentPassword = formData.get('current_password');
        const newPassword = formData.get('new_password');
        const confirmPassword = formData.get('confirm_password');

        if (newPassword !== confirmPassword) {
            this.showAlert('New passwords do not match!', 'error');
            return;
        }

        if (newPassword.length < 8) {
            this.showAlert('Password must be at least 8 characters long!', 'error');
            return;
        }

        this.showLoading();

        // Simulate API call
        setTimeout(() => {
            this.hideLoading();
            this.showAlert('Password updated successfully!', 'success');
            form.reset();
            this.updatePasswordStrength('', false);
        }, 1500);
    }

    updatePasswordStrength(password, isMobile = false) {
        const strengthText = isMobile ?
            document.getElementById('mobile-password-strength') :
            document.getElementById('password-strength');
        const strengthBar = isMobile ?
            document.getElementById('mobile-password-strength-bar') :
            document.getElementById('password-strength-bar');

        if (!strengthText || !strengthBar) return;

        let strength = 0;
        let feedback = 'Weak';

        if (password.length >= 8) strength += 25;
        if (password.match(/[a-z]/)) strength += 25;
        if (password.match(/[A-Z]/)) strength += 25;
        if (password.match(/[0-9]/)) strength += 25;

        if (strength < 50) {
            feedback = 'Weak';
            strengthBar.style.backgroundColor = '#ef4444';
        } else if (strength < 75) {
            feedback = 'Medium';
            strengthBar.style.backgroundColor = '#f59e0b';
        } else {
            feedback = 'Strong';
            strengthBar.style.backgroundColor = '#10b981';
        }

        strengthText.textContent = feedback;
        strengthBar.style.width = `${strength}%`;
    }

    toggle2FA() {
        const modal = document.getElementById('2fa-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    enable2FA() {
        this.showLoading();
        setTimeout(() => {
            this.hideLoading();
            this.showAlert('Two-factor authentication enabled!', 'success');
            document.getElementById('2fa-modal').classList.add('hidden');
        }, 1000);
    }

    disable2FA() {
        this.showLoading();
        setTimeout(() => {
            this.hideLoading();
            this.showAlert('Two-factor authentication disabled!', 'warning');
            document.getElementById('2fa-modal').classList.add('hidden');
        }, 1000);
    }

    logoutSession(sessionId) {
        this.showAlert(`Session ${sessionId} logged out successfully!`, 'success');
    }

    logoutAllSessions() {
        this.showLoading();
        setTimeout(() => {
            this.hideLoading();
            this.showAlert('All sessions logged out successfully!', 'success');
        }, 1000);
    }

    // Notifications
    toggleNotification(button) {
        const type = button.dataset.type;
        const setting = button.dataset.setting;
        const isActive = button.querySelector('.notification-toggle-slider').classList.contains('active');

        // Toggle visual state
        const slider = button.querySelector('.notification-toggle-slider');
        if (isActive) {
            slider.classList.remove('active');
        } else {
            slider.classList.add('active');
        }

        // Update counts
        this.updateNotificationCounts();

        // Show immediate feedback
        this.showAlert(`${type} ${setting} notifications ${isActive ? 'disabled' : 'enabled'}!`, 'success');
    }

    updateNotificationCounts() {
        // Update desktop counts
        const emailToggles = document.querySelectorAll('.notification-toggle[data-type="email"] .notification-toggle-slider.active');
        const smsToggles = document.querySelectorAll('.notification-toggle[data-type="sms"] .notification-toggle-slider.active');
        const pushToggles = document.querySelectorAll('.notification-toggle[data-type="push"] .notification-toggle-slider.active');

        document.getElementById('email-count') && (document.getElementById('email-count').textContent = emailToggles.length);
        document.getElementById('sms-count') && (document.getElementById('sms-count').textContent = smsToggles.length);
        document.getElementById('push-count') && (document.getElementById('push-count').textContent = pushToggles.length);

        // Update mobile counts
        document.getElementById('mobile-email-count') && (document.getElementById('mobile-email-count').textContent = emailToggles.length);
        document.getElementById('mobile-sms-count') && (document.getElementById('mobile-sms-count').textContent = smsToggles.length);
        document.getElementById('mobile-push-count') && (document.getElementById('mobile-push-count').textContent = pushToggles.length);
    }

    // Linked Accounts
    connectAccount(provider) {
        this.showAlert(`${provider} account connected successfully!`, 'success');
    }

    disconnectAccount(provider) {
        if (confirm(`Are you sure you want to disconnect your ${provider} account?`)) {
            this.showAlert(`${provider} account disconnected successfully!`, 'success');
        }
    }

    // Danger Zone
    showDeactivateModal() {
        const modal = document.getElementById('deactivate-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    showDeleteModal() {
        const modal = document.getElementById('delete-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    deactivateAccount() {
        const form = document.getElementById('deactivate-form');
        this.showLoading();

        setTimeout(() => {
            this.hideLoading();
            this.showAlert('Account deactivated successfully!', 'warning');
            document.getElementById('deactivate-modal').classList.add('hidden');
        }, 1500);
    }

    deleteAccount() {
        const form = document.getElementById('delete-form');
        const password = form.querySelector('#delete_password').value;
        const confirm = form.querySelector('#delete_confirm').checked;

        if (!password) {
            this.showAlert('Please enter your password!', 'error');
            return;
        }

        if (!confirm) {
            this.showAlert('Please confirm that you understand this action cannot be undone!', 'error');
            return;
        }

        this.showLoading();

        setTimeout(() => {
            this.hideLoading();
            this.showAlert('Account deleted successfully!', 'error');
            document.getElementById('delete-modal').classList.add('hidden');
        }, 2000);
    }

    // Modal Management
    openEditModal(type) {
        const modalMap = {
            'personal-info': 'personal-info-modal',
            'change-password': 'password-modal'
        };

        const modalId = modalMap[type];
        if (modalId) {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.remove('hidden');
            }
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    // UI Helpers
    showLoading() {
        // Add loading overlay or spinner
        console.log('Loading...');
    }

    hideLoading() {
        // Remove loading overlay or spinner
        console.log('Loading complete');
    }

    showAlert(message, type = 'info') {
        // Create and show alert
        const alertTypes = {
            'success': 'bg-green-100 border-green-500 text-green-700',
            'error': 'bg-red-100 border-red-500 text-red-700',
            'warning': 'bg-yellow-100 border-yellow-500 text-yellow-700',
            'info': 'bg-blue-100 border-blue-500 text-blue-700'
        };

        const alertClass = alertTypes[type] || alertTypes.info;

        // Create alert element
        const alert = document.createElement('div');
        alert.className = `fixed top-4 right-4 px-4 py-3 rounded-md border-l-4 ${alertClass} z-50 max-w-sm`;
        alert.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} mr-2"></i>
                <span class="text-sm">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(alert);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    resetPersonalInfoForm() {
        const form = document.getElementById('personal-info-form');
        if (form) {
            form.reset();
            // Reset profile picture preview
            const preview = document.getElementById('profile-preview');
            if (preview) {
                preview.src = '{% if user.profile.profile_image %}{{ user.profile.profile_image.url }}{% else %}{% static "images/default-avatar.png" %}{% endif %}';
            }
        }
    }
}

// Mobile modal preview functions
function previewProfilePictureMobile(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('mobile-profile-preview').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function previewModalProfilePicture(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('mobile-modal-profile-preview').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new AccountSettings();
});

