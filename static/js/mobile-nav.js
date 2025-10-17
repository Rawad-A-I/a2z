/**
 * Mobile Navigation JavaScript for A2Z Mart Webapp
 * Handles mobile menu interactions and navigation enhancements
 */

(function() {
    'use strict';

    // Mobile Navigation Manager
    class MobileNavigation {
        constructor() {
            this.menu = document.getElementById('mobile-menu');
            this.toggleButton = document.querySelector('.nav-mobile-toggle');
            this.menuIcon = document.getElementById('menu-icon');
            this.isOpen = false;
            
            this.init();
        }

        init() {
            if (!this.menu || !this.toggleButton) {
                console.warn('Mobile navigation elements not found');
                return;
            }

            this.bindEvents();
            this.setupAccessibility();
            this.handleResize();
        }

        bindEvents() {
            // Toggle button click
            this.toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggle();
            });

            // Close on outside click
            document.addEventListener('click', (e) => {
                if (this.isOpen && !this.menu.contains(e.target) && !this.toggleButton.contains(e.target)) {
                    this.close();
                }
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });

            // Handle window resize
            window.addEventListener('resize', () => {
                this.handleResize();
            });

            // Handle orientation change
            window.addEventListener('orientationchange', () => {
                setTimeout(() => {
                    this.handleResize();
                }, 100);
            });

            // Smooth scroll for anchor links
            this.setupSmoothScroll();
        }

        setupAccessibility() {
            // Set initial ARIA attributes
            this.toggleButton.setAttribute('aria-expanded', 'false');
            this.toggleButton.setAttribute('aria-controls', 'mobile-menu');
            
            // Handle focus management
            this.menu.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    this.handleTabNavigation(e);
                }
            });
        }

        handleTabNavigation(e) {
            const focusableElements = this.menu.querySelectorAll(
                'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
            );
            
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        }

        setupSmoothScroll() {
            const links = this.menu.querySelectorAll('a[href^="#"]');
            links.forEach(link => {
                link.addEventListener('click', (e) => {
                    const href = link.getAttribute('href');
                    if (href && href !== '#') {
                        const target = document.querySelector(href);
                        if (target) {
                            e.preventDefault();
                            this.close();
                            
                            // Smooth scroll to target
                            target.scrollIntoView({
                                behavior: 'smooth',
                                block: 'start'
                            });
                        }
                    }
                });
            });
        }

        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        }

        open() {
            this.menu.classList.add('open');
            this.toggleButton.setAttribute('aria-expanded', 'true');
            this.menuIcon.classList.remove('fa-bars');
            this.menuIcon.classList.add('fa-times');
            this.isOpen = true;

            // Focus first focusable element
            const firstFocusable = this.menu.querySelector('a[href], button, input');
            if (firstFocusable) {
                firstFocusable.focus();
            }

            // Prevent body scroll
            document.body.style.overflow = 'hidden';

            // Dispatch custom event
            this.dispatchEvent('mobileMenuOpen');
        }

        close() {
            this.menu.classList.remove('open');
            this.toggleButton.setAttribute('aria-expanded', 'false');
            this.menuIcon.classList.remove('fa-times');
            this.menuIcon.classList.add('fa-bars');
            this.isOpen = false;

            // Restore body scroll
            document.body.style.overflow = '';

            // Return focus to toggle button
            this.toggleButton.focus();

            // Dispatch custom event
            this.dispatchEvent('mobileMenuClose');
        }

        handleResize() {
            // Close menu on desktop
            if (window.innerWidth >= 768 && this.isOpen) {
                this.close();
            }
        }

        dispatchEvent(eventName) {
            const event = new CustomEvent(eventName, {
                detail: { isOpen: this.isOpen }
            });
            document.dispatchEvent(event);
        }
    }

    // Bottom Navigation Manager
    class BottomNavigation {
        constructor() {
            this.bottomNav = document.querySelector('.bottom-nav-mobile');
            this.items = document.querySelectorAll('.bottom-nav-mobile-item');
            
            this.init();
        }

        init() {
            if (!this.bottomNav) {
                console.warn('Bottom navigation not found');
                return;
            }

            this.bindEvents();
            this.setupActiveStates();
        }

        bindEvents() {
            // Handle item clicks
            this.items.forEach(item => {
                item.addEventListener('click', (e) => {
                    this.handleItemClick(e, item);
                });

                // Add touch feedback
                item.addEventListener('touchstart', () => {
                    item.classList.add('touching');
                });

                item.addEventListener('touchend', () => {
                    setTimeout(() => {
                        item.classList.remove('touching');
                    }, 150);
                });
            });

            // Handle scroll to show/hide bottom nav
            this.setupScrollBehavior();
        }

        handleItemClick(e, item) {
            // Add visual feedback
            item.classList.add('clicked');
            setTimeout(() => {
                item.classList.remove('clicked');
            }, 200);

            // Dispatch custom event
            const event = new CustomEvent('bottomNavClick', {
                detail: { 
                    item: item,
                    href: item.getAttribute('href')
                }
            });
            document.dispatchEvent(event);
        }

        setupActiveStates() {
            // Update active states based on current page
            const currentPath = window.location.pathname;
            
            this.items.forEach(item => {
                const href = item.getAttribute('href');
                if (href && currentPath.includes(href.split('/').pop())) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }

        setupScrollBehavior() {
            let lastScrollY = window.scrollY;
            let ticking = false;

            const updateNavVisibility = () => {
                const currentScrollY = window.scrollY;
                
                if (currentScrollY > lastScrollY && currentScrollY > 100) {
                    // Scrolling down - hide nav
                    this.bottomNav.style.transform = 'translateY(100%)';
                } else {
                    // Scrolling up - show nav
                    this.bottomNav.style.transform = 'translateY(0)';
                }
                
                lastScrollY = currentScrollY;
                ticking = false;
            };

            window.addEventListener('scroll', () => {
                if (!ticking) {
                    requestAnimationFrame(updateNavVisibility);
                    ticking = true;
                }
            });
        }
    }

    // Search Enhancement
    class MobileSearch {
        constructor() {
            this.searchInput = document.querySelector('.search-mobile-input');
            this.searchForm = document.querySelector('.search-mobile form');
            
            this.init();
        }

        init() {
            if (!this.searchInput) {
                console.warn('Mobile search input not found');
                return;
            }

            this.bindEvents();
            this.setupSearchSuggestions();
        }

        bindEvents() {
            // Handle form submission
            if (this.searchForm) {
                this.searchForm.addEventListener('submit', (e) => {
                    this.handleSearch(e);
                });
            }

            // Handle input changes
            this.searchInput.addEventListener('input', (e) => {
                this.handleInputChange(e);
            });

            // Handle focus/blur
            this.searchInput.addEventListener('focus', () => {
                this.handleFocus();
            });

            this.searchInput.addEventListener('blur', () => {
                this.handleBlur();
            });
        }

        handleSearch(e) {
            const query = this.searchInput.value.trim();
            if (!query) {
                e.preventDefault();
                this.searchInput.focus();
                return;
            }

            // Add loading state
            this.searchInput.disabled = true;
            this.searchInput.placeholder = 'Searching...';

            // Dispatch custom event
            const event = new CustomEvent('mobileSearch', {
                detail: { query: query }
            });
            document.dispatchEvent(event);
        }

        handleInputChange(e) {
            const query = e.target.value;
            
            // Dispatch custom event for search suggestions
            if (query.length > 2) {
                const event = new CustomEvent('mobileSearchInput', {
                    detail: { query: query }
                });
                document.dispatchEvent(event);
            }
        }

        handleFocus() {
            this.searchInput.parentElement.classList.add('focused');
        }

        handleBlur() {
            this.searchInput.parentElement.classList.remove('focused');
        }

        setupSearchSuggestions() {
            // This would integrate with your search API
            // For now, just a placeholder
        }
    }

    // Initialize when DOM is ready
    function initMobileNavigation() {
        // Check if we're on mobile
        if (window.innerWidth < 768) {
            new MobileNavigation();
            new BottomNavigation();
            new MobileSearch();
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileNavigation);
    } else {
        initMobileNavigation();
    }

    // Re-initialize on resize if needed
    window.addEventListener('resize', () => {
        if (window.innerWidth < 768 && !document.querySelector('.mobile-nav-initialized')) {
            document.body.classList.add('mobile-nav-initialized');
            initMobileNavigation();
        }
    });

    // Export for global access if needed
    window.MobileNavigation = MobileNavigation;
    window.BottomNavigation = BottomNavigation;
    window.MobileSearch = MobileSearch;

})();
