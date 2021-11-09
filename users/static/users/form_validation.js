// Find the form element. We're assuming there's only one form on the page that
// needs validation.
const form = document.querySelector('form.needs-validation');
 
// Prevent the form from being submitted if there are invalid inputs.
form.addEventListener('submit', (event) => {
 if (!form.checkValidity()) {
   event.preventDefault();
   event.stopPropagation();
 }
 
 // Tell bootstrap that it should display feedback messages.
 form.classList.add('was-validated');
});
 
// Add a `data-validate` attribute to each input when it loses focus. We're
// going to use data-validate to stop invalid feedback from appearing too soon.
const inputs = form.querySelectorAll('input');
inputs.forEach((el) => {
 el.addEventListener('focusout', (event) => {
   el.dataset.validate = 'true';
 });
});
 
// Find the email input element.
const emailInput = form.querySelector('input[name="email"]');
 
// Find the invalid-feedback element that is a sibling of emailInput.
const emailInvalidFeedback = emailInput
   .parentNode
   .querySelector('.invalid-feedback');
 
// Attach a function to the input's `invalid` event. This is where we write
// our custom feedback messages for each potential constraint violation.
emailInput.addEventListener('invalid', () => {
 if (emailInput.validity.valueMissing) {
   emailInvalidFeedback.textContent =
       'Please enter your email address.';
 } else if (emailInput.validity.typeMismatch) {
   emailInvalidFeedback.textContent =
       'That doesn\'t look like an email address.';
 }
});
 
/** */
function checkEmailValidity() {
 if (emailInput.validity.valid && emailInput.dataset.validate) {
   // Clear text from any previous feedback.
   emailInvalidFeedback.textContent = '';
   emailInput.classList.remove('is-invalid');
 } else if (emailInput.dataset.validate) {
   emailInput.classList.add('is-invalid');
   // Fires an `invalid` event.
   emailInput.checkValidity();
 }
};
 
emailInput.addEventListener('input', checkEmailValidity);
emailInput.addEventListener('focusout', checkEmailValidity);
 
// Now for the password input.
const passwordInput = form.querySelector('input[name="password1"]');
const passwordInvalidFeedback = passwordInput
   .parentNode
   .querySelector('.invalid-feedback');
 
 
passwordInput.addEventListener('invalid', () => {
 if (passwordInput.validity.valueMissing) {
   passwordInvalidFeedback.textContent =
       'Please enter a password.';
 } else if (passwordInput.validity.tooShort) {
   passwordInvalidFeedback.textContent =
       'Passwords must be at least 8 character long.';
 } else if (passwordInput.validity.patternMismatch) {
   passwordInvalidFeedback.textContent =
       'Passwords must contain at least one digit, one lower case letter ' +
       'and one upper case letter.';
 }
});
 
/** */
function checkPasswordValidity() {
 if (passwordInput.validity.valid && passwordInput.dataset.validate) {
   // Clear text from any previous feedback.
   passwordInvalidFeedback.textContent = '';
   passwordInput.classList.remove('is-invalid');
 } else if (passwordInput.dataset.validate) {
   passwordInput.classList.add('is-invalid');
   // Fires an `invalid` event.
   passwordInput.checkValidity();
 }
};
 
passwordInput.addEventListener('input', checkPasswordValidity);
passwordInput.addEventListener('focusout', checkPasswordValidity);
 
 
// The second password input should match the first.
const password2Input = form.querySelector('input[name="password2"]');
const password2InvalidFeedback = password2Input
   .parentNode
   .querySelector('.invalid-feedback');
 
password2Input.addEventListener('invalid', () => {
 if (password2Input.validity.valueMissing) {
   password2InvalidFeedback.textContent =
       'Please confirm your password.';
 } else {
   password2InvalidFeedback.textContent =
       'Passwords don\'t match.';
 }
});
 
/**  */
function checkPassword2Validity() {
 if (password2Input.value === passwordInput.value ) {
   password2Input.setCustomValidity('');
   password2InvalidFeedback.textContent = '';
   password2Input.classList.remove('is-invalid');
 } else {
   password2Input.setCustomValidity('passwords don\'t match');
   password2Input.classList.add('is-invalid');
   password2Input.checkValidity();
 }
};
 
password2Input.addEventListener('input', checkPassword2Validity);
password2Input.addEventListener('focusout', checkPassword2Validity);


