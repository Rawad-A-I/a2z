/**
 * Enhanced Color Fixes JavaScript
 * Dynamically enforces colorful styling and proper color contrast
 * Creates beautiful gradient cards with hover effects
 */

document.addEventListener('DOMContentLoaded', function() {
    // Function to apply enhanced colorful styling
    function applyColorfulStyling() {
        // Define solid background colors for each color class
        const colorStyles = {
            'bg-primary': '#007bff',
            'bg-success': '#28a745',
            'bg-warning': '#ffc107',
            'bg-danger': '#dc3545',
            'bg-info': '#17a2b8',
            'bg-secondary': '#6c757d'
        };
        
        const shadowStyles = {
            'bg-primary': '0 4px 15px rgba(0, 123, 255, 0.2)',
            'bg-success': '0 4px 15px rgba(40, 167, 69, 0.2)',
            'bg-warning': '0 4px 15px rgba(255, 193, 7, 0.2)',
            'bg-danger': '0 4px 15px rgba(220, 53, 69, 0.2)',
            'bg-info': '0 4px 15px rgba(23, 162, 184, 0.2)',
            'bg-secondary': '0 4px 15px rgba(108, 117, 125, 0.2)'
        };
        
        // Apply styling to all background classes
        Object.keys(colorStyles).forEach(bgClass => {
            const elements = document.querySelectorAll(`.${bgClass}`);
            
            elements.forEach(element => {
                // Apply solid background color
                element.style.setProperty('background-color', colorStyles[bgClass], 'important');
                element.style.setProperty('background', colorStyles[bgClass], 'important');
                element.style.setProperty('color', '#ffffff', 'important');
                element.style.setProperty('border', 'none', 'important');
                element.style.setProperty('box-shadow', shadowStyles[bgClass], 'important');
                element.style.setProperty('border-radius', '15px', 'important');
                element.style.setProperty('overflow', 'hidden', 'important');
                element.style.setProperty('transition', 'all 0.3s ease', 'important');
                
                // Also apply to card-body elements within colored cards
                const cardBodies = element.querySelectorAll('.card-body');
                cardBodies.forEach(cardBody => {
                    cardBody.style.setProperty('background-color', colorStyles[bgClass], 'important');
                    cardBody.style.setProperty('background', colorStyles[bgClass], 'important');
                    cardBody.style.setProperty('color', '#ffffff', 'important');
                });
                
                // Apply to all child elements
                const childElements = element.querySelectorAll('*');
                childElements.forEach(child => {
                    child.style.setProperty('color', '#ffffff', 'important');
                });
                
                // Enhanced text styling for headings
                const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6');
                headings.forEach(heading => {
                    heading.style.setProperty('text-shadow', '0 2px 4px rgba(0, 0, 0, 0.4)', 'important');
                    heading.style.setProperty('color', '#ffffff', 'important');
                    heading.style.setProperty('font-weight', '600', 'important');
                });
                
                // Enhanced icon styling
                const icons = element.querySelectorAll('i');
                icons.forEach(icon => {
                    icon.style.setProperty('color', '#ffffff', 'important');
                    icon.style.setProperty('text-shadow', '0 2px 4px rgba(0, 0, 0, 0.3)', 'important');
                    icon.style.setProperty('filter', 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2))', 'important');
                });
                
                // Enhanced badge styling
                const badges = element.querySelectorAll('.badge');
                badges.forEach(badge => {
                    badge.style.setProperty('color', '#ffffff', 'important');
                    badge.style.setProperty('text-shadow', '0 1px 2px rgba(0, 0, 0, 0.3)', 'important');
                    badge.style.setProperty('border', 'none', 'important');
                    badge.style.setProperty('box-shadow', '0 2px 4px rgba(0, 0, 0, 0.2)', 'important');
                });
            });
        });
        
        // Add hover effects to cards
        const cards = document.querySelectorAll('.card.bg-primary, .card.bg-success, .card.bg-warning, .card.bg-danger, .card.bg-info, .card.bg-secondary');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                if (window.innerWidth > 768) { // Only on desktop
                    this.style.setProperty('transform', 'translateY(-5px)', 'important');
                    this.style.setProperty('box-shadow', '0 15px 35px rgba(0, 0, 0, 0.2)', 'important');
                }
            });
            
            card.addEventListener('mouseleave', function() {
                if (window.innerWidth > 768) { // Only on desktop
                    this.style.setProperty('transform', 'translateY(0)', 'important');
                    // Restore original shadow
                    const bgClass = Array.from(this.classList).find(cls => cls.startsWith('bg-'));
                    if (bgClass && shadowStyles[bgClass]) {
                        this.style.setProperty('box-shadow', shadowStyles[bgClass], 'important');
                    }
                }
            });
        });
    }
    
    // Apply styling immediately
    applyColorfulStyling();
    
    // Reapply styling when window loads
    window.addEventListener('load', applyColorfulStyling);
    
    // Observe DOM for changes and reapply styling
    const observer = new MutationObserver(function(mutations) {
        let shouldReapply = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                shouldReapply = true;
            }
        });
        if (shouldReapply) {
            setTimeout(applyColorfulStyling, 100);
        }
    });
    
    observer.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
    
    // Reapply styling periodically for dynamic content
    setInterval(applyColorfulStyling, 2000);
    
    // Reapply on window resize
    window.addEventListener('resize', function() {
        setTimeout(applyColorfulStyling, 100);
    });
});