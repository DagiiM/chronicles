import { APIClient, AuthenticationError } from './api.js';

// Get the login form element
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

// Add submit event listener to the login form
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  // Get the username and password from the form
  const username = form.username.value;
  const password = form.password.value;

  // Create an instance of the APIClient with the given credentials
  const client = APIClient.getInstance();

  try {
    // Authenticate the client with the given credentials
    await client.authenticate(username, password);

    // Redirect to the home page on successful authentication
    //window.location.href = '/';
  } catch (e) {
    if (e instanceof AuthenticationError) {
      // Redirect to the login page if there was an authentication error
      window.location.href = '/login';
      console.error(`${e}`);
    } else {
      console.error(`${e}`);
    }
  }
});
