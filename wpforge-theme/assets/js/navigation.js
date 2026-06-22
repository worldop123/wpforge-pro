/**
 * WPForge Theme - Navigation JavaScript
 *
 * Mobile navigation and menu interactions
 *
 * @package WPForge_Theme
 * @since 1.0.0
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initMobileMenu();
        initDropdownMenus();
    });

    /**
     * Mobile menu toggle
     */
    function initMobileMenu() {
        var menuToggle = document.querySelector('.menu-toggle');
        var mainNav = document.querySelector('.main-navigation');

        if (!menuToggle || !mainNav) {
            return;
        }

        menuToggle.addEventListener('click', function () {
            var isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';

            menuToggle.setAttribute('aria-expanded', !isExpanded);
            mainNav.classList.toggle('toggled');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function (e) {
            if (!mainNav.contains(e.target) && !menuToggle.contains(e.target)) {
                if (mainNav.classList.contains('toggled')) {
                    menuToggle.setAttribute('aria-expanded', 'false');
                    mainNav.classList.remove('toggled');
                }
            }
        });

        // Close menu when pressing Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && mainNav.classList.contains('toggled')) {
                menuToggle.setAttribute('aria-expanded', 'false');
                mainNav.classList.remove('toggled');
                menuToggle.focus();
            }
        });
    }

    /**
     * Dropdown menus with keyboard support
     */
    function initDropdownMenus() {
        var menuItems = document.querySelectorAll('.main-navigation .menu-item-has-children');

        menuItems.forEach(function (item) {
            var link = item.querySelector('> a');
            var submenu = item.querySelector('> ul');

            if (!link || !submenu) {
                return;
            }

            // Add dropdown toggle button for mobile
            var toggleButton = document.createElement('button');
            toggleButton.className = 'dropdown-toggle';
            toggleButton.setAttribute('aria-expanded', 'false');
            toggleButton.setAttribute('aria-label', 'Toggle submenu');
            toggleButton.innerHTML = '<span class="screen-reader-text">Toggle submenu</span>';

            // Insert after the link
            link.parentNode.insertBefore(toggleButton, link.nextSibling);

            // Toggle on button click
            toggleButton.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();

                var isExpanded = toggleButton.getAttribute('aria-expanded') === 'true';
                toggleButton.setAttribute('aria-expanded', !isExpanded);
                item.classList.toggle('submenu-open');
            });

            // Keyboard support
            link.addEventListener('keydown', function (e) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    toggleButton.setAttribute('aria-expanded', 'true');
                    item.classList.add('submenu-open');

                    // Focus first submenu item
                    var firstItem = submenu.querySelector('a');
                    if (firstItem) {
                        firstItem.focus();
                    }
                }
            });

            // Close submenu on focus out
            item.addEventListener('focusout', function (e) {
                if (!item.contains(e.relatedTarget)) {
                    toggleButton.setAttribute('aria-expanded', 'false');
                    item.classList.remove('submenu-open');
                }
            });
        });
    }

})();
