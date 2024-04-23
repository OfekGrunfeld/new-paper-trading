
document.addEventListener('DOMContentLoaded', function() {
    const updateSelect = document.getElementById('attribute_to_update');
    const emailField = document.getElementById('emailField');
    const usernameField = document.getElementById('usernameField');
    const passwordField = document.getElementById('passwordField');

    const emailInput = document.getElementById('new_email');
    const usernameInput = document.getElementById('new_username');
    const passwordInput = document.getElementById('new_password');

    function updateFieldVisibility() {
        // Hide all fields and remove required attribute
        emailField.classList.add('hidden');
        usernameField.classList.add('hidden');
        passwordField.classList.add('hidden');
        
        emailInput.required = false;
        usernameInput.required = false;
        passwordInput.required = false;

        // Show and set required based on selected option
        switch(updateSelect.value) {
            case 'email':
                emailField.classList.remove('hidden');
                emailInput.required = true;
                break;
            case 'username':
                usernameField.classList.remove('hidden');
                usernameInput.required = true;
                break;
            case 'password':
                passwordField.classList.remove('hidden');
                passwordInput.required = true;
                break;
        }
    }
    
    updateSelect.addEventListener('change', updateFieldVisibility);
    updateFieldVisibility();  // Initial call to set the correct state when the page loads
});
