import { APIClient, AuthenticationError } from './api.js';

const form = document.querySelector("#login-form");

// Get the submit button element
const submitButton = form.querySelector('button[type="submit"]');

// Get all required fields
const requiredFields = form.querySelectorAll('[required]');

// Add input event listener to all required fields
requiredFields.forEach((field) => {
  field.addEventListener('input', () => {
    // Disable the submit button if any required field is empty
    let allFieldsFilled = true;
    requiredFields.forEach((field) => {
      if (!field.value) {
        allFieldsFilled = false;
      }
    });
    if (allFieldsFilled) {
      submitButton.removeAttribute('disabled');
    } else {
      submitButton.setAttribute('disabled', true);
    }
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const username = form.username.value;
  const password = form.password.value;

  const client = new APIClient('', { username, password });

  try {
    await client.authenticate();
    showAlert('success','Authentication successful',5000);
    window.location.href = '/dashboard';
  } catch (e) {
    if (e instanceof AuthenticationError) {
      window.location.href = '/login';
      showAlert("failed",`${e}`);
    } else {
      showAlert("failed",`${e}`);
      console.error(`${e}`);
    }
  }

});
