document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle search form date input default value
    const searchDateInput = document.querySelector('.search-form input[type="date"]');
    if (searchDateInput && !searchDateInput.value) {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        searchDateInput.value = `${year}-${month}-${day}`;
    }

    // Handle role toggle in login/signup forms
    const roleToggleButtons = document.querySelectorAll('.role-toggle .btn');
    const roleInput = document.querySelector('input[name="role"]');
    
    if (roleToggleButtons.length && roleInput) {
        roleToggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                roleToggleButtons.forEach(btn => btn.classList.remove('active', 'btn-primary'));
                this.classList.add('active', 'btn-primary');
                roleInput.value = this.dataset.role;
            });
        });
    }

    // Display confirmation dialogs for important actions
    const confirmationForms = document.querySelectorAll('.needs-confirmation');
    confirmationForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!confirm('Are you sure you want to proceed?')) {
                event.preventDefault();
            }
        });
    });

    // Handle flash messages auto-close
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});
