// =============================================================
// Bangladesh Scouts Site — Combined Script
// One mobile-menu handler, one gallery handler, no dead code.
// =============================================================

// ----- Loading Page -----
window.addEventListener('load', function () {
    const loadingPage = document.getElementById('loading-page');
    if (!loadingPage) return;
    setTimeout(() => {
        loadingPage.style.opacity = '0';
        setTimeout(() => {
            loadingPage.style.display = 'none';
        }, 500);
    }, 1500);
});

// ----- Mobile Menu Toggle (single source of truth) -----
// Matches CSS: nav ul / nav ul.show / .mobile-menu.active
function initMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu');
    const nav = document.querySelector('nav ul');

    if (!mobileMenuBtn || !nav) return;

    mobileMenuBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        const isShowing = nav.classList.contains('show');

        nav.classList.toggle('show');
        this.classList.toggle('active');

        const menuItems = nav.querySelectorAll('li a');
        if (!isShowing) {
            menuItems.forEach((item, index) => {
                item.style.animation = `fadeInColor 0.4s ease forwards ${index * 0.1}s`;
                item.style.opacity = '1';
            });
        } else {
            menuItems.forEach((item, index) => {
                item.style.animation = `fadeOutColor 0.3s ease forwards ${index * 0.1}s`;
            });
        }
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!nav.contains(e.target) && !mobileMenuBtn.contains(e.target) && nav.classList.contains('show')) {
            nav.classList.remove('show');
            mobileMenuBtn.classList.remove('active');
        }
    });
}

// ----- Smooth Scrolling with Color Highlight -----
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#' || !targetId) return;

            const targetElement = document.querySelector(targetId);
            if (!targetElement) return;

            e.preventDefault();

            targetElement.style.animation = 'colorHighlight 1.2s ease';

            const offsetTop = targetElement.offsetTop - 80;

            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });

            setTimeout(() => {
                targetElement.style.animation = '';
            }, 1200);

            // Close mobile menu if open
            const nav = document.querySelector('nav ul');
            const mobileMenuBtn = document.querySelector('.mobile-menu');
            if (nav && nav.classList.contains('show')) {
                nav.classList.remove('show');
                mobileMenuBtn?.classList.remove('active');
            }
        });
    });
}

// ----- Form Handling with Color Feedback -----
function initFormHandling() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);

            input.addEventListener('focus', function () {
                this.style.borderColor = 'var(--accent)';
                this.style.boxShadow = '0 0 0 2px rgba(231, 111, 81, 0.1)';
            });

            input.addEventListener('blur', function () {
                this.style.boxShadow = 'none';
            });
        });

        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            if (!validateForm(this)) return;

            const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
            if (!submitBtn) return;

            const originalText = submitBtn.innerHTML;
            const originalBg = submitBtn.style.background;

            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> পাঠানো হচ্ছে...';
            submitBtn.style.background = 'var(--secondary)';
            submitBtn.style.transform = 'scale(0.95)';

            try {
                await simulateAPICall();

                submitBtn.style.background = '#27ae60';
                submitBtn.innerHTML = '<i class="fas fa-check"></i> সফল!';

                showColorMessage('success', 'আপনার বার্তা সফলভাবে পাঠানো হয়েছে!');
                this.reset();

            } catch (error) {
                submitBtn.style.background = '#e74c3c';
                submitBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> আবার চেষ্টা করুন';
                showColorMessage('error', 'দুঃখিত, কিছু সমস্যা হয়েছে।');
            } finally {
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.style.background = originalBg;
                    submitBtn.style.transform = '';
                }, 2000);
            }
        });
    });
}

// ----- Field Validation -----
function validateField(e) {
    const field = e.target;
    const value = field.value.trim();

    clearFieldError(field);

    let isValid = true;
    let errorMessage = '';

    field.classList.remove('valid', 'invalid');

    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'এই ঘরটি পূরণ করা আবশ্যক';
    } else if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'সঠিক ইমেইল ঠিকানা লিখুন';
        }
    } else if (field.name === 'phone' && value) {
        const phoneRegex = /^(?:\+88|01)?\d{11}$/;
        if (!phoneRegex.test(value.replace(/\s/g, ''))) {
            isValid = false;
            errorMessage = 'সঠিক মোবাইল নম্বর লিখুন';
        }
    }

    if (isValid && value) {
        field.classList.add('valid');
        field.style.borderColor = '#27ae60';
    } else if (!isValid) {
        field.classList.add('invalid');
        field.style.borderColor = '#e74c3c';
        showFieldError(field, errorMessage);
    } else {
        field.style.borderColor = '';
    }

    return isValid;
}

function clearFieldError(e) {
    const field = e.target || e;
    field.style.borderColor = '';
    field.classList.remove('invalid');

    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input, textarea, select');

    inputs.forEach(input => {
        const event = new Event('blur');
        input.dispatchEvent(event);
        if (input.classList.contains('invalid')) {
            isValid = false;
        }
    });

    return isValid;
}

// ----- Toast Messages -----
function showColorMessage(type, message) {
    const messageEl = document.createElement('div');
    messageEl.className = `color-message ${type}-message`;
    messageEl.innerHTML = `
        <div class="message-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(messageEl);

    setTimeout(() => {
        messageEl.classList.add('show');
    }, 100);

    setTimeout(() => {
        messageEl.classList.remove('show');
        setTimeout(() => {
            messageEl.remove();
        }, 300);
    }, 3000);
}

// ----- Active Navigation Highlight -----
// Compares real, normalized pathnames instead of splitting strings by hand.
// Splitting by '/' and popping the last segment breaks on trailing-slash
// URLs (e.g. Django's default /about/, /activities/), because every such
// URL ends in an empty segment — which was previously misread as "home".
function initActiveNav() {
    const normalize = (path) => (path.length > 1 && path.endsWith('/')) ? path.slice(0, -1) : path;
    const currentPath = normalize(window.location.pathname);
    const navLinks = document.querySelectorAll('nav a[href]');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');

        // Skip dropdown toggles ("#") — they aren't real pages and should
        // never be marked active.
        if (!href || href === '#') return;

        // link.pathname resolves the href the same way the browser does,
        // so relative/absolute Django URLs compare correctly.
        const linkPath = normalize(link.pathname);

        if (linkPath === currentPath) {
            link.classList.add('active');
            link.style.color = 'var(--accent)';
            link.style.fontWeight = '700';
        }

        link.addEventListener('mouseenter', function () {
            if (!this.classList.contains('active')) {
                this.style.color = 'var(--secondary)';
                this.style.backgroundColor = 'transparent';
            }
        });

        link.addEventListener('mouseleave', function () {
            if (!this.classList.contains('active')) {
                this.style.color = '';
            }
        });
    });
}

// ----- Gallery + Lightbox (single source of truth) -----
// Works for gallery items already present in the HTML.
function initGalleryLightbox() {
    const galleryItems = document.querySelectorAll('.gallery-item');

    galleryItems.forEach(item => {
        item.addEventListener('mouseenter', function () {
            const overlay = this.querySelector('.gallery-overlay') || createGalleryOverlay(this);
            overlay.style.backgroundColor = 'rgba(44, 85, 48, 0.8)';
        });

        item.addEventListener('mouseleave', function () {
            const overlay = this.querySelector('.gallery-overlay');
            if (overlay) {
                overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
            }
        });

        item.addEventListener('click', function () {
            const img = this.querySelector('img');
            if (!img) return;
            createColorLightbox(img.src, img.alt || 'Gallery Image');
        });
    });
}

// Optionally populate the gallery from a data array (window.galleryData),
// if the page defines one. Safe no-op otherwise.
function initializeGalleryFromData() {
    const imageGallery = document.getElementById('imageGallery');
    const imageCount = document.getElementById('imageCount');
    if (!imageGallery || !window.galleryData || !Array.isArray(window.galleryData.images)) return;

    imageCount.textContent = window.galleryData.images.length;

    window.galleryData.images.forEach(image => {
        const galleryItem = document.createElement('div');
        galleryItem.className = 'gallery-item';
        galleryItem.innerHTML = `
            <img src="${image.url}" alt="${image.alt}" loading="lazy"
                 onerror="this.src='../images/placeholder.jpg'; this.alt='ছবিটি লোড করতে সমস্যা হচ্ছে'">
            <div class="gallery-overlay">
                <i class="fas fa-search-plus"></i>
            </div>
        `;
        imageGallery.appendChild(galleryItem);
    });

    // Newly injected items need their own lightbox/hover bindings
    initGalleryLightbox();
}

function createColorLightbox(imgSrc, imgAlt) {
    if (document.querySelector('.lightbox')) return;

    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <img src="${imgSrc}" alt="${imgAlt}">
            <button class="lightbox-close" aria-label="Close">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

    document.body.appendChild(lightbox);
    document.body.style.overflow = 'hidden';

    setTimeout(() => {
        lightbox.classList.add('show');
    }, 10);

    const closeLightbox = () => {
        lightbox.classList.remove('show');
        setTimeout(() => {
            lightbox.remove();
            document.body.style.overflow = '';
        }, 300);
    };

    lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
    });

    document.addEventListener('keydown', function escClose(e) {
        if (e.key === 'Escape') {
            closeLightbox();
            document.removeEventListener('keydown', escClose);
        }
    });
}

function createGalleryOverlay(item) {
    const overlay = document.createElement('div');
    overlay.className = 'gallery-overlay';
    overlay.innerHTML = '<i class="fas fa-search-plus"></i>';

    item.style.position = 'relative';
    item.appendChild(overlay);

    return overlay;
}

// ----- Scroll Reveal Animations -----
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                entry.target.style.background = 'linear-gradient(45deg, transparent, rgba(44, 85, 48, 0.03), transparent)';
                entry.target.style.animation = 'colorPulse 2s ease';

                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.activity-card, .team-member, .event-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
}

// ----- Back to Top -----
function initBackToTop() {
    const backToTopBtn = document.querySelector('.back-to-top');
    if (!backToTopBtn) return;

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('active');
        } else {
            backToTopBtn.classList.remove('active');
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ----- Utilities -----
function simulateAPICall() {
    return new Promise((resolve) => {
        setTimeout(resolve, 1500);
    });
}

function showFieldError(field, message) {
    let errorElement = field.parentNode.querySelector('.field-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        field.parentNode.appendChild(errorElement);
    }

    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

// ----- Single Init -----
document.addEventListener('DOMContentLoaded', function () {
    initMobileMenu();
    initSmoothScroll();
    initFormHandling();
    initializeGalleryFromData(); // no-op unless window.galleryData exists
    initGalleryLightbox();
    initScrollAnimations();
    initActiveNav();
    initBackToTop();
});