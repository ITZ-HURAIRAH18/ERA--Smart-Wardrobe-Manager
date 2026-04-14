/**
 * ERA E-Commerce - Main JavaScript
 * Handles interactive features, cart, wishlist, and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {

    // ========================================
    // TOAST NOTIFICATIONS
    // ========================================
    function showToast(message, type = 'success', duration = 4000) {
        const toastContainer = document.querySelector('.toast-container-era') || createToastContainer();
        
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };

        const toast = document.createElement('div');
        toast.className = `toast-era toast-${type}`;
        toast.innerHTML = `
            <i class="bi ${icons[type]} toast-era-icon"></i>
            <span class="toast-era-message">${message}</span>
            <button class="toast-era-close" aria-label="Close">&times;</button>
        `;

        toastContainer.appendChild(toast);

        // Close button
        toast.querySelector('.toast-era-close').addEventListener('click', function() {
            removeToast(toast);
        });

        // Auto dismiss
        setTimeout(() => removeToast(toast), duration);
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container-era';
        document.body.appendChild(container);
        return container;
    }

    function removeToast(toast) {
        toast.style.animation = 'toastSlideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }

    // Make showToast globally available
    window.showToast = showToast;

    // ========================================
    // WISHLIST TOGGLE
    // ========================================
    const wishlistButtons = document.querySelectorAll('.wishlist-toggle');
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const url = this.dataset.url;
            const icon = this.querySelector('i');

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    icon.classList.toggle('bi-heart-fill');
                    icon.classList.toggle('bi-heart');
                    if (icon.classList.contains('bi-heart-fill')) {
                        icon.style.color = '#ef4444';
                        showToast('Added to wishlist', 'success');
                    } else {
                        icon.style.color = '';
                        showToast('Removed from wishlist', 'info');
                    }
                }
            })
            .catch(() => showToast('Something went wrong', 'error'));
        });
    });

    // ========================================
    // AUTO-SLUG GENERATOR
    // ========================================
    const nameInputs = document.querySelectorAll('#product-name, #category-name');
    nameInputs.forEach(input => {
        input.addEventListener('input', function() {
            const slugField = this.closest('.row, .mb-3, .form-section')
                ?.querySelector('[readonly][id*="slug"]') 
                || document.querySelector('[readonly][id*="slug"]');
            
            if (slugField) {
                const slug = this.value.toLowerCase()
                    .replace(/[^a-z0-9]+/g, '-')
                    .replace(/^-+|-+$/g, '');
                slugField.value = slug;
            }
        });
    });

    // ========================================
    // IMAGE PREVIEW
    // ========================================
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('imagePreview');
                    if (preview) {
                        preview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 100%; max-height: 100%; object-fit: cover;">`;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // ========================================
    // SEARCH AUTOCOMPLETE (Shop Page)
    // ========================================
    const searchInput = document.querySelector('#searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value;
                if (query.length >= 2) {
                    // Could implement AJAX search here
                    console.log('Search:', query);
                }
            }, 300);
        });
    }

    // ========================================
    // CONFIRMATION DIALOGS
    // ========================================
    const deleteButtons = document.querySelectorAll('.confirm-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // ========================================
    // FORM VALIDATION FEEDBACK
    // ========================================
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'error');
            }
        });
    });

    // ========================================
    // SCROLL TO TOP BUTTON
    // ========================================
    const scrollTopBtn = document.createElement('button');
    scrollTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    scrollTopBtn.className = 'btn-era scroll-top-btn';
    scrollTopBtn.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 999;
        padding: 0;
    `;
    document.body.appendChild(scrollTopBtn);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollTopBtn.style.opacity = '1';
            scrollTopBtn.style.visibility = 'visible';
        } else {
            scrollTopBtn.style.opacity = '0';
            scrollTopBtn.style.visibility = 'hidden';
        }
    });

    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // ========================================
    // ANIMATE ON SCROLL
    // ========================================
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    animatedElements.forEach(el => observer.observe(el));

    // ========================================
    // UTILITY: GET CSRF TOKEN
    // ========================================
    function getCSRFToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }

    // ========================================
    // PRODUCT QUICK VIEW (Modal)
    // ========================================
    window.openQuickView = function(productId) {
        // Could implement modal-based product quick view
        console.log('Quick view product:', productId);
    };

    // ========================================
    // COLOR/SIZE SELECTOR HIGHLIGHT
    // ========================================
    const selectorButtons = document.querySelectorAll('.size-selector button, .color-selector button');
    selectorButtons.forEach(button => {
        button.addEventListener('click', function() {
            const parent = this.closest('.size-selector, .color-selector');
            parent.querySelectorAll('button').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // ========================================
    // QUANTITY INPUT VALIDATION
    // ========================================
    const quantityInputs = document.querySelectorAll('input[type="number"][min]');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const min = parseInt(this.min);
            const value = parseInt(this.value);
            if (value < min) {
                this.value = min;
                showToast(`Minimum quantity is ${min}`, 'warning');
            }
        });
    });

    // ========================================
    // FILTER ACCORDION (Mobile)
    // ========================================
    const filterToggles = document.querySelectorAll('.filter-toggle');
    filterToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const target = document.querySelector(this.dataset.target);
            if (target) {
                target.classList.toggle('show');
                this.querySelector('i')?.classList.toggle('bi-chevron-down');
                this.querySelector('i')?.classList.toggle('bi-chevron-up');
            }
        });
    });

    console.log('ERA E-Commerce JavaScript loaded successfully');
});
