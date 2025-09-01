// Main JavaScript for FindJob

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize animations
    initializeAnimations();
    
    // Form validation
    initializeFormValidation();
    
    // Counter animation
    initializeCounters();
    
    // Search functionality
    initializeSearch();
    
    // Auto-hide alerts
    initializeAlerts();
    
    // Password toggle
    initializePasswordToggle();
    
    // Smooth scrolling
    initializeSmoothScrolling();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover focus'
        });
    });
}

// Initialize scroll animations
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe cards for animation
    document.querySelectorAll('.card, .feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Enhanced form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalidField = form.querySelector('.form-control:invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                    firstInvalidField.classList.add('shake');
                    setTimeout(() => firstInvalidField.classList.remove('shake'), 500);
                }
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                validateField(input);
            });
            
            input.addEventListener('blur', function() {
                validateField(input);
            });
        });
    });
}

// Validate individual field
function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    
    // Remove previous validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Email validation
    if (type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (value && emailRegex.test(value)) {
            field.classList.add('is-valid');
        } else if (value) {
            field.classList.add('is-invalid');
        }
    }
    
    // Password validation
    if (type === 'password') {
        if (value.length >= 6) {
            field.classList.add('is-valid');
        } else if (value) {
            field.classList.add('is-invalid');
        }
    }
    
    // Required field validation
    if (field.hasAttribute('required')) {
        if (value) {
            if (!field.classList.contains('is-invalid')) {
                field.classList.add('is-valid');
            }
        } else {
            field.classList.add('is-invalid');
        }
    }
}

// Counter animation for statistics
function initializeCounters() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        // Start animation when element is visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(counter);
    });
}

// Search functionality with loading states
function initializeSearch() {
    const searchForm = document.getElementById('searchForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const jobListings = document.getElementById('jobListings');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            // Show loading state
            if (loadingSpinner && jobListings) {
                loadingSpinner.classList.remove('d-none');
                jobListings.style.opacity = '0.5';
            }
            
            // Add loading class to submit button
            const submitBtn = searchForm.querySelector('.search-btn');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Searching...';
                
                // Restore button after delay (simulated)
                setTimeout(() => {
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = originalText;
                    if (loadingSpinner && jobListings) {
                        loadingSpinner.classList.add('d-none');
                        jobListings.style.opacity = '1';
                    }
                }, 1000);
            }
        });
        
        // Real-time search (debounced)
        const searchInput = searchForm.querySelector('input[name="search"]');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    console.log('Searching for:', this.value);
                    // Implement real-time search here
                }, 500);
            });
        }
    }
}

// Auto-hide alerts with animation
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        // Add close animation
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.transform = 'translateX(100%)';
                alert.style.opacity = '0';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        }
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            if (alert && alert.parentNode) {
                alert.style.transform = 'translateX(100%)';
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
}

// Password visibility toggle
function initializePasswordToggle() {
    const toggleBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    
    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-eye');
                icon.classList.toggle('fa-eye-slash');
            }
        });
    }
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert alert
    if (alertContainer) {
        alertContainer.insertBefore(alert, alertContainer.firstChild);
        
        // Trigger animation
        setTimeout(() => {
            alert.style.transform = 'translateX(0)';
            alert.style.opacity = '1';
        }, 10);
        
        // Auto-hide
        setTimeout(() => {
            alert.style.transform = 'translateX(100%)';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }
}

// Loading state utility
function setLoadingState(element, isLoading) {
    if (isLoading) {
        element.classList.add('loading');
        element.style.pointerEvents = 'none';
    } else {
        element.classList.remove('loading');
        element.style.pointerEvents = 'auto';
    }
}

// Form data utility
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    return data;
}

// Validate email utility
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Add CSS for shake animation
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 20%, 40%, 60%, 80%, 100% {
            transform: translateX(0);
        }
        10%, 30%, 50%, 70%, 90% {
            transform: translateX(-5px);
        }
    }
    
    .shake {
        animation: shake 0.5s ease-in-out;
    }
`;
document.head.appendChild(style);