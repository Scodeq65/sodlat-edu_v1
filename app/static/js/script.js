document.addEventListener('DOMContentLoaded', function () {
    // Smooth scroll for anchors
    const anchors = document.querySelectorAll('a[href^="#"]');
    for (let anchor of anchors) {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    }

    // Mobile menu toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('nav ul');
    
    if (navToggle) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('nav-menu-visible');
        });
    }
});

// Simple form validation
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function (e) {
        const requiredFields = this.querySelectorAll('[required]');
        let valid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                valid = false;
                field.classList.add('error');
            } else {
                field.classList.remove('error');
            }
        });

        if (!valid) {
            e.preventDefault();
        }
    });
});