function checkPasswordStrength() {
    const password = document.getElementById("password").value;
    const strengthMsg = document.getElementById("strength-message");

    const strongRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$/;
    const mediumRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$/;

    if (strongRegex.test(password)) {
        strengthMsg.textContent = "Strong password";
        strengthMsg.style.color = "green";
    } else if (mediumRegex.test(password)) {
        strengthMsg.textContent = "Medium password";
        strengthMsg.style.color = "orange";
    } else {
        strengthMsg.textContent = "Weak password";
        strengthMsg.style.color = "red";
    }
}

function validateform() {
    const password = document.querySelector('input[name="password"]').value.trim();
    const confirm_password = document.querySelector('input[name="confirm-password"]').value.trim();
    const errorDiv = document.querySelector('.error');

    if (!password) {
        errorDiv.textContent = "Enter the password!";
        errorDiv.style.display = "block";
        return false;
    } else if (!confirm_password) {
        errorDiv.textContent = "Enter the confirm password!";
        errorDiv.style.display = "block";
        return false;
    } else if (password !== confirm_password) {
        errorDiv.textContent = "Passwords do not match!";
        errorDiv.style.display = "block";
        return false;
    } else {
        errorDiv.style.display = "none";
        return true;
    }
}
