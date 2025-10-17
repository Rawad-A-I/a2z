/**
 * Modern Account Page JavaScript
 * Handles all interactive functionality for the modern account settings page
 */

class ModernAccountPage {
    constructor() {
        this.currentTab = 'profile';
        this.modals = new Map();
        this.forms = new Map();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeModals();
        this.initializeForms();
        this.loadUserData();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-item').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Modal triggers
        document.querySelectorAll('[data-modal]').forEach(trigger => {
            trigger.addEventListener('click', (e) => this.openModal(e.target.dataset.modal));
        });

        // Form submissions
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        });

        // Toggle switches
        document.querySelectorAll('.toggle-switch input').forEach(toggle => {
            toggle.addEventListener('change', (e) => this.handleToggle(e));
        });

        // Close modals on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal(e.target.id);
            }
        });

        // Close modals with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        // Real-time form validation
        document.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('blur', (e) => this.validateField(e.target));
            field.addEventListener('input', (e) => this.clearFieldError(e.target));
        });
    }

    initializeModals() {
        const modalIds = [
            'editProfileModal',
            'changePasswordModal',
            'deleteAccountModal',
            'avatarModal',
            'securityModal',
            'billingModal'
        ];

        modalIds.forEach(id => {
            const modal = document.getElementById(id);
            if (modal) {
                this.modals.set(id, modal);
            }
        });
    }

    initializeForms() {
        const formIds = [
            'editProfileForm',
            'changePasswordForm',
            'deleteAccountForm',
            'notificationForm',
            'privacyForm'
        ];

        formIds.forEach(id => {
            const form = document.getElementById(id);
            if (form) {
                this.forms.set(id, form);
            }
        });
    }

    // Tab Management
    switchTab(tabName) {
        // Update current tab
        this.currentTab = tabName;

        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tab items
        document.querySelectorAll('.tab-item').forEach(item => {
            item.classList.remove('active');
        });

        // Show selected tab content
        const targetTab = document.getElementById(`${tabName}-tab`);
        if (targetTab) {
            targetTab.classList.add('active');
        }

        // Add active class to clicked tab item
        const targetTabItem = document.querySelector(`[data-tab="${tabName}"]`);
        if (targetTabItem) {
            targetTabItem.classList.add('active');
        }

        // Load tab-specific data
        this.loadTabData(tabName);
    }

    loadTabData(tabName) {
        switch (tabName) {
            case 'security':
                this.loadSecurityData();
                break;
            case 'billing':
                this.loadBillingData();
                break;
            case 'preferences':
                this.loadPreferencesData();
                break;
            case 'privacy':
                this.loadPrivacyData();
                break;
        }
    }

    // Modal Management
    openModal(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
            
            // Focus first input in modal
            const firstInput = modal.querySelector('input, select, textarea');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }

    closeModal(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
            
            // Reset form if exists
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
                this.clearFormErrors(form);
            }
        }
    }

    closeAllModals() {
        this.modals.forEach((modal, id) => {
            this.closeModal(id);
        });
    }

    // Form Handling
    handleFormSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const formId = form.id;

        // Validate form
        if (!this.validateForm(form)) {
            return;
        }

        // Show loading state
        this.showFormLoading(form);

        // Handle different forms
        switch (formId) {
            case 'editProfileForm':
                this.submitProfileUpdate(form);
                break;
            case 'changePasswordForm':
                this.submitPasswordChange(form);
                break;
            case 'deleteAccountForm':
                this.submitAccountDeletion(form);
                break;
            case 'notificationForm':
                this.submitNotificationPreferences(form);
                break;
            case 'privacyForm':
                this.submitPrivacySettings(form);
                break;
        }
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        // Custom validation for specific forms
        if (form.id === 'changePasswordForm') {
            isValid = this.validatePasswordForm(form) && isValid;
        }

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        const fieldName = field.name || field.id;

        // Clear previous errors
        this.clearFieldError(field);

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            this.showFieldError(field, `${this.getFieldLabel(field)} is required`);
            return false;
        }

        // Type-specific validation
        switch (fieldType) {
            case 'email':
                if (value && !this.isValidEmail(value)) {
                    this.showFieldError(field, 'Please enter a valid email address');
                    return false;
                }
                break;
            case 'tel':
                if (value && !this.isValidPhone(value)) {
                    this.showFieldError(field, 'Please enter a valid phone number');
                    return false;
                }
                break;
            case 'password':
                if (value && !this.isValidPassword(value)) {
                    this.showFieldError(field, 'Password must be at least 8 characters with uppercase, lowercase, and number');
                    return false;
                }
                break;
        }

        return true;
    }

    validatePasswordForm(form) {
        const newPassword = form.querySelector('input[type="password"]:nth-of-type(2)');
        const confirmPassword = form.querySelector('input[type="password"]:nth-of-type(3)');

        if (newPassword.value !== confirmPassword.value) {
            this.showFieldError(confirmPassword, 'Passwords do not match');
            return false;
        }

        return true;
    }

    showFieldError(field, message) {
        field.classList.add('error');
        
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-red-600 text-sm mt-1';
        errorDiv.textContent = message;
        
        // Insert after field
        field.parentNode.insertBefore(errorDiv, field.nextSibling);
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorDiv = field.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    clearFormErrors(form) {
        form.querySelectorAll('.field-error').forEach(error => error.remove());
        form.querySelectorAll('.error').forEach(field => field.classList.remove('error'));
    }

    // Form Submission Handlers
    async submitProfileUpdate(form) {
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/accounts/update-profile/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccessMessage('Profile updated successfully!');
                this.closeModal('editProfileModal');
                this.loadUserData();
            } else {
                this.showErrorMessage(result.message || 'Failed to update profile');
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
        } finally {
            this.hideFormLoading(form);
        }
    }

    async submitPasswordChange(form) {
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/accounts/change-password/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccessMessage('Password updated successfully!');
                this.closeModal('changePasswordModal');
            } else {
                this.showErrorMessage(result.message || 'Failed to update password');
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
        } finally {
            this.hideFormLoading(form);
        }
    }

    async submitAccountDeletion(form) {
        if (!confirm('Are you absolutely sure? This action cannot be undone.')) {
            this.hideFormLoading(form);
            return;
        }

        const formData = new FormData(form);
        
        try {
            const response = await fetch('/accounts/delete-account/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccessMessage('Account deletion initiated. You will receive a confirmation email.');
                this.closeModal('deleteAccountModal');
                // Redirect to home page after delay
                setTimeout(() => {
                    window.location.href = '/';
                }, 3000);
            } else {
                this.showErrorMessage(result.message || 'Failed to delete account');
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
        } finally {
            this.hideFormLoading(form);
        }
    }

    // Toggle Handlers
    handleToggle(e) {
        const toggle = e.target;
        const setting = toggle.dataset.setting;
        const value = toggle.checked;

        this.updateSetting(setting, value);
    }

    async updateSetting(setting, value) {
        try {
            const response = await fetch('/accounts/update-setting/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    setting: setting,
                    value: value
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccessMessage(`${setting} ${value ? 'enabled' : 'disabled'} successfully!`);
            } else {
                this.showErrorMessage(result.message || 'Failed to update setting');
                // Revert toggle
                const toggle = document.querySelector(`[data-setting="${setting}"]`);
                if (toggle) {
                    toggle.checked = !value;
                }
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
            // Revert toggle
            const toggle = document.querySelector(`[data-setting="${setting}"]`);
            if (toggle) {
                toggle.checked = !value;
            }
        }
    }

    // Data Loading
    async loadUserData() {
        try {
            const response = await fetch('/accounts/user-data/');
            const data = await response.json();

            if (data.success) {
                this.updateUserInterface(data.user);
            }
        } catch (error) {
            console.error('Failed to load user data:', error);
        }
    }

    async loadSecurityData() {
        try {
            const response = await fetch('/accounts/security-data/');
            const data = await response.json();

            if (data.success) {
                this.updateSecurityInterface(data.security);
            }
        } catch (error) {
            console.error('Failed to load security data:', error);
        }
    }

    async loadBillingData() {
        try {
            const response = await fetch('/accounts/billing-data/');
            const data = await response.json();

            if (data.success) {
                this.updateBillingInterface(data.billing);
            }
        } catch (error) {
            console.error('Failed to load billing data:', error);
        }
    }

    async loadPreferencesData() {
        try {
            const response = await fetch('/accounts/preferences-data/');
            const data = await response.json();

            if (data.success) {
                this.updatePreferencesInterface(data.preferences);
            }
        } catch (error) {
            console.error('Failed to load preferences data:', error);
        }
    }

    async loadPrivacyData() {
        try {
            const response = await fetch('/accounts/privacy-data/');
            const data = await response.json();

            if (data.success) {
                this.updatePrivacyInterface(data.privacy);
            }
        } catch (error) {
            console.error('Failed to load privacy data:', error);
        }
    }

    // Interface Updates
    updateUserInterface(userData) {
        // Update profile information
        if (userData.full_name) {
            document.querySelector('.profile-name').textContent = userData.full_name;
        }
        if (userData.email) {
            document.querySelector('.profile-email').textContent = userData.email;
        }
        if (userData.avatar) {
            document.querySelector('.profile-avatar').src = userData.avatar;
        }

        // Update statistics
        if (userData.stats) {
            document.querySelector('.stat-orders').textContent = userData.stats.orders;
            document.querySelector('.stat-wishlist').textContent = userData.stats.wishlist;
            document.querySelector('.stat-reviews').textContent = userData.stats.reviews;
            document.querySelector('.stat-points').textContent = userData.stats.points;
        }
    }

    updateSecurityInterface(securityData) {
        // Update 2FA status
        if (securityData.two_factor) {
            const toggle = document.querySelector('[data-setting="two_factor"]');
            if (toggle) {
                toggle.checked = securityData.two_factor.enabled;
            }
        }

        // Update sessions
        if (securityData.sessions) {
            this.updateSessionsList(securityData.sessions);
        }
    }

    updateSessionsList(sessions) {
        const sessionsContainer = document.querySelector('.sessions-list');
        if (!sessionsContainer) return;

        sessionsContainer.innerHTML = '';

        sessions.forEach(session => {
            const sessionElement = this.createSessionElement(session);
            sessionsContainer.appendChild(sessionElement);
        });
    }

    createSessionElement(session) {
        const div = document.createElement('div');
        div.className = 'session-item';
        div.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="device-icon device-${session.device_type}">
                        <i class="fas fa-${this.getDeviceIcon(session.device_type)}"></i>
                    </div>
                    <div>
                        <div class="font-medium">${session.device_name}</div>
                        <div class="text-sm text-gray-600">${session.last_active} • ${session.location}</div>
                    </div>
                </div>
                ${session.is_current ? 
                    '<span class="text-green-600 text-sm font-medium">Current</span>' :
                    `<button class="text-red-600 hover:text-red-800 text-sm" onclick="accountPage.revokeSession('${session.id}')">Revoke</button>`
                }
            </div>
        `;
        return div;
    }

    getDeviceIcon(deviceType) {
        const icons = {
            'desktop': 'desktop',
            'mobile': 'mobile-alt',
            'tablet': 'tablet-alt'
        };
        return icons[deviceType] || 'desktop';
    }

    // Utility Functions
    showFormLoading(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
        }
    }

    hideFormLoading(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
        }
    }

    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }

    showMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm ${
            type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'
        }`;
        
        messageDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} mr-2"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-gray-500 hover:text-gray-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(messageDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    getFieldLabel(field) {
        const label = field.closest('.setting-item')?.querySelector('label');
        return label ? label.textContent.replace(':', '') : field.name || field.id;
    }

    // Validation Helpers
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidPhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    }

    isValidPassword(password) {
        // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
        return passwordRegex.test(password);
    }

    // Session Management
    async revokeSession(sessionId) {
        if (!confirm('Are you sure you want to revoke this session?')) {
            return;
        }

        try {
            const response = await fetch(`/accounts/revoke-session/${sessionId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccessMessage('Session revoked successfully!');
                this.loadSecurityData(); // Reload sessions
            } else {
                this.showErrorMessage(result.message || 'Failed to revoke session');
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
        }
    }

    // Data Export
    async exportData() {
        try {
            const response = await fetch('/accounts/export-data/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccessMessage('Data export initiated. You will receive an email when ready.');
            } else {
                this.showErrorMessage(result.message || 'Failed to initiate data export');
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
        }
    }

    // Avatar Upload
    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file);

        try {
            const response = await fetch('/accounts/upload-avatar/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccessMessage('Avatar updated successfully!');
                // Update avatar in UI
                const avatarImg = document.querySelector('.profile-avatar');
                if (avatarImg) {
                    avatarImg.src = result.avatar_url;
                }
            } else {
                this.showErrorMessage(result.message || 'Failed to upload avatar');
            }
        } catch (error) {
            this.showErrorMessage('Network error. Please try again.');
        }
    }
}

// Initialize the account page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.accountPage = new ModernAccountPage();
});

// Global functions for backward compatibility
function switchTab(tabName) {
    if (window.accountPage) {
        window.accountPage.switchTab(tabName);
    }
}

function openModal(modalId) {
    if (window.accountPage) {
        window.accountPage.openModal(modalId);
    }
}

function closeModal(modalId) {
    if (window.accountPage) {
        window.accountPage.closeModal(modalId);
    }
}

function openEditProfileModal() {
    openModal('editProfileModal');
}

function openPasswordModal() {
    openModal('changePasswordModal');
}

function openDeleteAccountModal() {
    openModal('deleteAccountModal');
}

function openAvatarModal() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file && window.accountPage) {
            window.accountPage.uploadAvatar(file);
        }
    };
    input.click();
}

function openSecurityModal() {
    switchTab('security');
}

function toggle2FA(checkbox) {
    if (window.accountPage) {
        window.accountPage.updateSetting('two_factor', checkbox.checked);
    }
}

function toggleBiometric(checkbox) {
    if (window.accountPage) {
        window.accountPage.updateSetting('biometric', checkbox.checked);
    }
}

function updateNotification(type, checkbox) {
    if (window.accountPage) {
        window.accountPage.updateSetting(`notification_${type}`, checkbox.checked);
    }
}

function updatePrivacy(setting, checkbox) {
    if (window.accountPage) {
        window.accountPage.updateSetting(`privacy_${setting}`, checkbox.checked);
    }
}

function editField(fieldName) {
    if (window.accountPage) {
        window.accountPage.showSuccessMessage(`${fieldName} edit mode activated!`);
    }
}

function revokeSession(sessionId) {
    if (window.accountPage) {
        window.accountPage.revokeSession(sessionId);
    }
}

function viewAllSessions() {
    if (window.accountPage) {
        window.accountPage.showSuccessMessage('Opening session management...');
    }
}

function exportData() {
    if (window.accountPage) {
        window.accountPage.exportData();
    }
}

function connectApp(appName) {
    if (window.accountPage) {
        window.accountPage.showSuccessMessage(`Connecting to ${appName}...`);
    }
}

function disconnectApp(appName) {
    if (window.accountPage) {
        if (confirm(`Are you sure you want to disconnect ${appName}?`)) {
            window.accountPage.showSuccessMessage(`${appName} disconnected successfully!`);
        }
    }
}
