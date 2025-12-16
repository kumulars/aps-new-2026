/**
 * APS Symposium Gallery
 * Modern lightbox with keyboard/touch navigation
 */

(function() {
    'use strict';

    // Elements
    const lightbox = document.getElementById('galleryLightbox');
    const lightboxImage = document.getElementById('lightboxImage');
    const lightboxCaption = document.getElementById('lightboxCaption');
    const lightboxCounter = document.getElementById('lightboxCounter');
    const closeBtn = document.getElementById('lightboxClose');
    const prevBtn = document.getElementById('lightboxPrev');
    const nextBtn = document.getElementById('lightboxNext');
    const galleryGrid = document.getElementById('galleryGrid');

    if (!lightbox || !galleryGrid) return;

    // State
    let currentIndex = 0;
    let galleryItems = [];
    let touchStartX = 0;
    let touchEndX = 0;

    // Initialize gallery items
    function initGallery() {
        const items = galleryGrid.querySelectorAll('.gallery-item');
        galleryItems = Array.from(items).map(item => {
            const link = item.querySelector('.gallery-link');
            return {
                url: link.dataset.fullUrl,
                caption: link.dataset.caption || ''
            };
        });

        // Add click handlers
        items.forEach((item, index) => {
            item.querySelector('.gallery-link').addEventListener('click', (e) => {
                e.preventDefault();
                openLightbox(index);
            });
        });
    }

    // Open lightbox
    function openLightbox(index) {
        currentIndex = index;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
        loadImage(index);
        updateCounter();
        updateNavButtons();
    }

    // Close lightbox
    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
        lightboxImage.classList.remove('loaded');
    }

    // Load image
    function loadImage(index) {
        const item = galleryItems[index];
        lightboxImage.classList.remove('loaded');

        // Create new image to preload
        const img = new Image();
        img.onload = function() {
            lightboxImage.src = item.url;
            lightboxImage.alt = item.caption;
            lightboxImage.classList.add('loaded');
        };
        img.src = item.url;

        // Update caption
        lightboxCaption.textContent = item.caption;
    }

    // Navigate
    function goToPrev() {
        if (currentIndex > 0) {
            currentIndex--;
            loadImage(currentIndex);
            updateCounter();
            updateNavButtons();
        }
    }

    function goToNext() {
        if (currentIndex < galleryItems.length - 1) {
            currentIndex++;
            loadImage(currentIndex);
            updateCounter();
            updateNavButtons();
        }
    }

    // Update UI
    function updateCounter() {
        lightboxCounter.textContent = `${currentIndex + 1} / ${galleryItems.length}`;
    }

    function updateNavButtons() {
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex === galleryItems.length - 1;
    }

    // Event Listeners

    // Close button
    closeBtn.addEventListener('click', closeLightbox);

    // Navigation buttons
    prevBtn.addEventListener('click', goToPrev);
    nextBtn.addEventListener('click', goToNext);

    // Close on backdrop click
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (!lightbox.classList.contains('active')) return;

        switch (e.key) {
            case 'Escape':
                closeLightbox();
                break;
            case 'ArrowLeft':
                goToPrev();
                break;
            case 'ArrowRight':
                goToNext();
                break;
        }
    });

    // Touch/Swipe support
    lightbox.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    lightbox.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swiped left - go next
                goToNext();
            } else {
                // Swiped right - go prev
                goToPrev();
            }
        }
    }

    // Lazy loading with Intersection Observer
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px'
        });

        // Observe all gallery images
        document.querySelectorAll('.gallery-thumb[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Initialize
    initGallery();

})();
