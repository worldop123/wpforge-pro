/**
 * WPForge Theme - Main JavaScript
 *
 * Ultra-lightweight, performance-optimized JavaScript
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

(function () {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function () {
        initBackToTop();
        initSmoothScroll();
        initLazyLoad();
    });

    /**
     * Back to top button
     */
    function initBackToTop() {
        var backToTop = document.querySelector('.back-to-top');
        if (!backToTop) {
            return;
        }

        var scrollThreshold = 300;

        window.addEventListener('scroll', function () {
            if (window.scrollY > scrollThreshold) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        }, { passive: true });

        backToTop.addEventListener('click', function () {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    /**
     * Smooth scroll for anchor links
     */
    function initSmoothScroll() {
        var anchorLinks = document.querySelectorAll('a[href^="#"]');

        anchorLinks.forEach(function (link) {
            link.addEventListener('click', function (e) {
                var targetId = this.getAttribute('href');

                if (targetId === '#') {
                    return;
                }

                var targetElement = document.querySelector(targetId);

                if (targetElement) {
                    e.preventDefault();

                    var headerOffset = 80;
                    var elementPosition = targetElement.getBoundingClientRect().top;
                    var offsetPosition = elementPosition + window.scrollY - headerOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    /**
     * Native lazy loading fallback
     */
    function initLazyLoad() {
        // Check if native lazy loading is supported
        if ('loading' in HTMLImageElement.prototype) {
            return;
        }

        // Fallback for browsers that don't support native lazy loading
        var lazyImages = document.querySelectorAll('img[loading="lazy"]');

        if ('IntersectionObserver' in window) {
            var imageObserver = new IntersectionObserver(function (entries, observer) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        var img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                        }
                        observer.unobserve(img);
                    }
                });
            });

            lazyImages.forEach(function (img) {
                imageObserver.observe(img);
            });
        } else {
            // Fallback for older browsers
            lazyImages.forEach(function (img) {
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                }
            });
        }
    }

})();
