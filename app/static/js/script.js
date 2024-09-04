// script.js

// Form validation example
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function (event) {
            const isValid = validateForm(form);
            if (!isValid) {
                event.preventDefault();
                alert('Please fill out all required fields.');
            }
        });
    });
});

function validateForm(form) {
    // Simple validation logic
    let isValid = true;
    form.querySelectorAll('input[required]').forEach(input => {
        if (!input.value) {
            isValid = false;
            input.classList.add('error');
        } else {
            input.classList.remove('error');
        }
    });
    return isValid;
}

// Dynamic content update example
function updateContent(data) {
    const contentArea = document.querySelector('#content-area');
    contentArea.innerHTML = data;  // Replace with dynamic content
}

// AJAX request example
function fetchData(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => updateContent(data))
        .catch(error => console.error('Error:', error));
}

// Interactive dashboard features example
document.querySelector('#dashboard-toggle').addEventListener('click', function () {
    document.querySelector('#dashboard-content').classList.toggle('hidden');
});

// Real-time notifications example
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

// Enhanced UI example
document.querySelectorAll('.interactive-element').forEach(element => {
    element.addEventListener('mouseover', function () {
        this.classList.add('hover');
    });
    element.addEventListener('mouseout', function () {
        this.classList.remove('hover');
    });
});