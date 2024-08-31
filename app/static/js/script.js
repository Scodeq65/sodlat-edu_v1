document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap modals
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        new bootstrap.Modal(modal);
    });

    // Example of handling form submissions
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            // You can add validation or other logic here
            console.log('Form submitted: ', form);
        });
    });

    // Example of adding dynamic behavior
    var addButton = document.querySelector('#add-button');
    if (addButton) {
        addButton.addEventListener('click', function() {
            // Example functionality for adding an item dynamically
            var container = document.querySelector('#dynamic-container');
            var newItem = document.createElement('div');
            newItem.textContent = 'New item added';
            container.appendChild(newItem);
        });
    }
});