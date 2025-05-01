function validateForm() {
    const username = document.querySelector('input[name="Username"]').value.trim();
    const password = document.querySelector('input[name="password"]').value.trim();
    const errorDiv = document.querySelector('.error');

    if (!username) {
        errorDiv.textContent = "Enter the username !";
        errorDiv.style.display = "block";
        return false;
    } else if (!password) {
        errorDiv.textContent = "Enter the password !";
        errorDiv.style.display = "block";
        return false;
    } else {
        errorDiv.style.display = "none";
        return true;  // allow form to submit
    }
}