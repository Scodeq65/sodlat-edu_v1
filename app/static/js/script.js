/* static/js/script.js */

/* Wait for the DOM to be fully loaded */
document.addEventListener('DOMContentLoaded', function () {

    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Bootstrap-based form validation with additional custom validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                // Custom form validation (add error class on invalid fields)
                form.querySelectorAll('input[required]').forEach(input => {
                    if (!input.value) {
                        input.classList.add('is-invalid');
                    } else {
                        input.classList.remove('is-invalid');
                    }
                });
                form.classList.add('was-validated');
            }, false);
        });

    // Smooth scrolling for anchor links
    var scroll = new SmoothScroll('a[href*="#"]', {
        speed: 800,
        speedAsDuration: true
    });

    // Dynamic content update (example: update dashboard or courses)
    function updateContent(data) {
        const contentArea = document.querySelector('#content-area');
        contentArea.innerHTML = data;  // Replace with dynamic content
    }

    // AJAX request example for dynamic data loading
    function fetchData(url) {
        fetch(url)
            .then(response => response.json())
            .then(data => updateContent(data))
            .catch(error => console.error('Error:', error));
    }

    // Real-time notifications (example: new message or assignment alert)
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info notification';  // Bootstrap alert for consistency
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    // Trigger notifications (example usage)
    document.querySelectorAll('.notification-trigger').forEach(button => {
        button.addEventListener('click', function () {
            showNotification('New update available!');
        });
    });

    // Enhanced UI: Interactive hover effects
    document.querySelectorAll('.interactive-element').forEach(element => {
        element.addEventListener('mouseover', function () {
            this.classList.add('hover');
        });
        element.addEventListener('mouseout', function () {
            this.classList.remove('hover');
        });
    });

    // Toggle dashboard elements (optional interactive features)
    document.querySelectorAll('.dashboard-toggle').forEach(toggle => {
        toggle.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            targetElement.classList.toggle('hidden');
        });
    });

    // Custom AJAX form submission (example)
    document.querySelectorAll('.ajax-form').forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(form);
            const actionUrl = form.getAttribute('action');

            fetch(actionUrl, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                updateContent(data);  // Update UI based on the response
                showNotification('Form submitted successfully!');
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred. Please try again.');
            });
        });
    });

});