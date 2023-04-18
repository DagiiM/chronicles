
import { APIClient } from './api.js';

const apiClient = APIClient.getInstance();

function generateRandomContrastingColor() {
    const hue = Math.floor(Math.random() * 360);
    const saturation = '70%';
    const lightness = Math.floor(Math.random() * 25) + 70 + '%'; // Generates lightness values between 70% and 95%
    return `hsl(${hue}, ${saturation}, ${lightness})`;
  }
  
function getContrastingColor(color) {
    let luminance;
    if (color.startsWith('rgb')) {
      // RGB color
      const rgbValues = color.match(/(\d+)/g).map(Number);
      luminance = 0.2126 * rgbValues[0] + 0.7152 * rgbValues[1] + 0.0722 * rgbValues[2];
    } else {
      // HSL color
      const hslValues = color.match(/(\d+)/g).map(Number);
      const s = hslValues[1] / 100;
      const l = hslValues[2] / 100;
      const r = l + s * Math.min(l, 1 - l);
      const g = l + s * Math.min(l, 1 - l);
      const b = l - s * Math.min(l, 1 - l) / 2;
      luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }
    return luminance > 0.5 ? 'black' : 'white';
  }
  
  
  
  // Usage:
 // applyRandomColorAndBackgroundToSelector('.appointment__item');
 const renderAppointments = async (endpoint, targetElement) => {
    try {
      const appointmentsData = await apiClient.make_api_call(endpoint);
      const results = appointmentsData.results || [];
  
      // Remove existing appointments and links
      targetElement.innerHTML = '';
  
      // Create links for count, next, and previous
      const countLink = document.createElement('a');
      countLink.href = '#';
      countLink.textContent = `Count: ${appointmentsData.count}`;
      countLink.classList.add('links-container__count');
  
      const linksContainer = document.createElement('div');
      linksContainer.classList.add('links-container');
      linksContainer.appendChild(countLink);
  
      if (appointmentsData.next !== null) {
        const nextLink = document.createElement('a');
        nextLink.href = '#';
        nextLink.textContent = 'Next';
        nextLink.classList.add('link');
        nextLink.addEventListener('click', async () => {
          await renderAppointments(appointmentsData.next, targetElement);
        });
        linksContainer.appendChild(nextLink);
      }
  
      if (appointmentsData.previous !== null) {
        const prevLink = document.createElement('a');
        prevLink.href = '#';
        prevLink.textContent = 'Previous';
        prevLink.classList.add('link');
        prevLink.addEventListener('click', async () => {
          await renderAppointments(appointmentsData.previous, targetElement);
        });
        linksContainer.appendChild(prevLink);
      }
  
      const appointmentGrid = document.createElement('div');
      appointmentGrid.classList.add('appointment-grid');
  
      if (results.length > 0) {
        results.forEach(result => {
          const appointmentItem = document.createElement('div');
          appointmentItem.classList.add('appointment__item');
          
            // Set random and contrasting background color of appointment item
            const backgroundColor = generateRandomContrastingColor();
            appointmentItem.style.backgroundColor = backgroundColor;
            appointmentItem.style.color = getContrastingColor(backgroundColor);
  
          const startTime = document.createElement('div');
          startTime.classList.add('appointment__item--start-time');
          startTime.textContent = `Start Time: ${result.start_time}`;
  
          const endTime = document.createElement('div');
          endTime.classList.add('appointment__item--end-time');
          endTime.textContent = `End Time: ${result.end_time}`;
  
          const date = document.createElement('div');
          date.classList.add('appointment__item--date');
          date.textContent = `Date: ${result.appointment_date}`;
  
          const status = document.createElement('div');
          status.classList.add('appointment__item--status');
          status.textContent = `Status: ${result.status}`;
  
          const type = document.createElement('div');
          type.classList.add('appointment__item--type');
          type.textContent = `Type: ${result.appointment_type}`;
  
          appointmentItem.appendChild(startTime);
          appointmentItem.appendChild(endTime);
          appointmentItem.appendChild(date);
          appointmentItem.appendChild(status);
          appointmentItem.appendChild(type);
  
          appointmentGrid.appendChild(appointmentItem);
        });
  
        linksContainer.style.display = 'block';
      } else {
        linksContainer.style.display = 'none';
  
        const noResultsMessage = document.createElement('div');
        noResultsMessage.classList.add('no-results-message');
        noResultsMessage.textContent = 'No appointments found.';
  
        appointmentGrid.appendChild(noResultsMessage);
      }
  
      targetElement.appendChild(linksContainer);
      targetElement.appendChild(appointmentGrid);
    } catch (error) {
      console.error(`Failed to load appointments: ${error}`);
    }
  };
  

  const renderAboutAppointments = async (endpoint, targetElement) => {
    try {
      const aboutAppointmentsData = await apiClient.make_api_call(endpoint);
      const aboutAppointments = aboutAppointmentsData[0] || {};
  
      // Remove existing content
      targetElement.innerHTML = '';
  
      const content = document.createElement('div');
      content.className = 'about-appointments'
      content.innerHTML = aboutAppointments.content;
  
      const verifiedStatus = document.createElement('div');
      verifiedStatus.textContent = aboutAppointments.is_verified ? 'Verified' : 'Not Verified';
  
      const verifiedDate = document.createElement('div');
      verifiedDate.textContent = `Verified Date: ${aboutAppointments.verified_date}`;
  
      targetElement.appendChild(content);
      targetElement.appendChild(verifiedStatus);
      targetElement.appendChild(verifiedDate);
    } catch (error) {
      console.error(`Failed to load about appointments: ${error}`);
    }
  };
  
  const renderAppointmentsFeedback = async (endpoint, targetElement) => {
    try {
      const feedbackData = await apiClient.make_api_call(endpoint);
      const FeedbackAppointments = feedbackData[0] || {};
  
      // Remove existing content
      targetElement.innerHTML = '';
  
      const content = document.createElement('div');
      content.className = 'appointments-feedback'
      content.innerHTML = FeedbackAppointments.content;
  
      const verifiedStatus = document.createElement('div');
      verifiedStatus.textContent = aboutAppointments.is_verified ? 'Verified' : 'Not Verified';
  
      const verifiedDate = document.createElement('div');
      verifiedDate.textContent = `Verified Date: ${aboutAppointments.verified_date}`;
  
      targetElement.appendChild(content);
      targetElement.appendChild(verifiedStatus);
      targetElement.appendChild(verifiedDate);
    } catch (error) {
      console.error(`Failed to load about appointments: ${error}`);
    }
  };
  



  const renderBookAppointment = async (endpoint, targetElement) => {
    try {
      const clinics = await apiClient.make_api_call(`/api/clinics`);
      const clinicSelect = createSelect('clinic', 'Select a clinic to Book Appointment');
  
      clinics.results.forEach((clinic) => {
        const option = createOption(clinic.id, clinic.name);
        clinicSelect.appendChild(option);
      });
  
      const Bookform = document.createElement('form');
      Bookform.setAttribute('method', 'post');
      Bookform.setAttribute('action', 'api/appointments/');
      Bookform.classList.add('general-form-container')
      targetElement.appendChild(Bookform);
  
      const clinicWrapper = createWrapper(clinicSelect, 'Select a clinic');
      Bookform.appendChild(clinicWrapper);
  
      clinicSelect.addEventListener('change', async () => {
        
        const selectedClinicId = clinicSelect.value;
        const appointmentTypes = await apiClient.make_api_call(`/api/clinics/${selectedClinicId}/appointment_types`);
        const appointmentTypeSelect = createSelect('appointment-type', 'Select an appointment type');
  
        appointmentTypes.forEach((appointmentType) => {
          const option = createOption(appointmentType.id, `${appointmentType.name} - ${appointmentType.charge}`);
          appointmentTypeSelect.appendChild(option);
        });
  
        const appointmentWrapper = createWrapper(appointmentTypeSelect, 'Select an appointment type');
        Bookform.appendChild(appointmentWrapper);
  
        appointmentTypeSelect.addEventListener('change', async () => {
          const selectedAppointmentTypeId = appointmentTypeSelect.value;
          const fullCapacityDays = await apiClient.make_api_call(
            `/api/clinics/${selectedClinicId}/full_capacity_days/`,
            'POST',
            { appointment_type: selectedAppointmentTypeId },
            { 'Content-Type': 'application/json' }
          );
          const fullCapacityDaysResponse = fullCapacityDays.results;
          Bookform.querySelectorAll('.calendar-container').forEach((calendar) => calendar.remove());
          Bookform.querySelectorAll('.appointment-submit-button').forEach((aptbtn) => aptbtn.remove());

          let calender = renderCalendar(fullCapacityDaysResponse)
          Bookform.appendChild(calender);

          const submitButton = document.createElement('button');
          submitButton.setAttribute('type', 'submit');
          submitButton.setAttribute('disabled', true);
          submitButton.textContent = 'Book Appointment';
          submitButton.classList.add('btn-primary');
          submitButton.classList.add('appointment-submit-button');
          Bookform.appendChild(submitButton);
          
          // add event listener for form submission
        Bookform.addEventListener('submit', async (event) => {
          event.preventDefault();
          if(!sessionStorage.getItem('userID')){
            window.location.href = '/login';
          }
          // Change the button text to 'Scheduling'
          submitButton.textContent = 'Scheduling...';

          // collect form data
          const formData = new FormData(Bookform);
          const patientId = sessionStorage.getItem('userID');
            if (patientId === null) {
              // Redirect to login page
              window.location.href = '/login';
            } else {
              const data = {
                clinic: formData.get('clinic'),
                appointment_type: formData.get('appointment-type'),
                patient: patientId,
                appointment_date: formData.get('appointment-date'),
                start_time: formData.get('start-time'),
                end_time: formData.get('end-time'),
              };

                      submitData(data)
            }
            async function submitData(data) {
              try {
                await apiClient.make_api_call(
                  'api/appointments/', 
                  'POST',
                  { ...data},
                  { 'Content-Type': 'application/json' },
                  true
                );
                showAlert('success', 'Appointment Scheduled Successfully', 5000);
              } catch (error) {
                showAlert('failure', 'Oops there was an error try a different date', 5000);
              }finally {
                // Change the button text back to 'Book Appointment'
                submitButton.textContent = 'Book Appointment';
              }
            }
        });

        });
      });
    } catch (error) {
      console.error(`Failed to render book appointment form: ${error}`);
    }
  };

  function getUserIdFromSessionStorage() {
    const userData = JSON.parse(sessionStorage.getItem('userID'));
    if (!userData) {
      window.location.href = '/login'
    }
  }

  
  const createSelect = (name, label) => {
    const select = document.createElement('select');
    select.setAttribute('name', name);
    select.setAttribute('id', name);
  
    const defaultOption = createOption('', label);
    defaultOption.disabled = true;
    defaultOption.selected = true;
    select.appendChild(defaultOption);
  
    return select;
  };
  
  const createOption = (value, text) => {
    const option = document.createElement('option');
    option.value = value;
    option.text = text;
    return option;
  };
  
  const createWrapper = (select, label) => {
    const selectLabel = document.createElement('label');
    selectLabel.setAttribute('for', select.id);
    selectLabel.innerText = label;
  
    const wrapper = document.createElement('div');
    wrapper.classList.add('select-wrapper');
    wrapper.appendChild(selectLabel);
    wrapper.appendChild(select);
  
    return wrapper;
  };
  
  
  const renderCalendar = (fullCapacityDays) => {
    const today = new Date();
    const year = today.getFullYear();
    const next30Days = Array.from({ length: 30 }, (_, index) => {
      const date = new Date();
      date.setDate(today.getDate() + index);
      return date;
    });
 
    const calendarContainer = document.createElement('div');
    calendarContainer.classList.add('calendar-container');
  
    const monthElement = document.createElement('div');
    monthElement.classList.add('calendar-month');
    monthElement.textContent = today.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  
    calendarContainer.appendChild(monthElement);
  
    const daysContainer = document.createElement('div');
    daysContainer.classList.add('days-container');
  
    const appointmentDateField = document.createElement('input');
    appointmentDateField.setAttribute('type', 'hidden');
    appointmentDateField.setAttribute('name', 'appointment-date');
  
    const startTimeLabelField = document.createElement('label');
    startTimeLabelField.setAttribute('name', 'start-time');
    startTimeLabelField.style.display = 'none';
    const startTimeField = document.createElement('input');
    startTimeField.setAttribute('type', 'time');
    startTimeField.setAttribute('name', 'start-time');
    startTimeField.setAttribute('required', true);
    startTimeField.style.display = 'none';
  
    const endTimeLabelField = document.createElement('label');
    endTimeLabelField.setAttribute('name', 'end-time');
    endTimeLabelField.style.display = 'none';
    const endTimeField = document.createElement('input');
    endTimeField.setAttribute('type', 'time');
    endTimeField.setAttribute('name', 'end-time');
    endTimeField.setAttribute('required', true);
    endTimeField.style.display = 'none';
  
    next30Days.forEach((date) => {
      const dateElement = document.createElement('div');
      dateElement.classList.add('calendar-date');
  
      const dayOfWeekElement = document.createElement('div');
      dayOfWeekElement.classList.add('calendar-day-of-week');
      dayOfWeekElement.textContent = date.toLocaleDateString('en-US', { weekday: 'short' });
  
      const dayOfMonthElement = document.createElement('div');
      dayOfMonthElement.classList.add('calendar-day-of-month');
      dayOfMonthElement.textContent = date.getDate();
  
      dateElement.appendChild(dayOfWeekElement);
      dateElement.appendChild(dayOfMonthElement);
  
      const dateISOString = date.toISOString().split('T')[0];
  
      // check if weekend (Saturday or Sunday)
      if (date.getDay() === 0 || date.getDay() === 6) {
        dateElement.classList.add('calendar-date--weekend');
        dateElement.classList.add('calendar-date--unselectable');
      } 
        // Add class for today's date
      if (date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()) {
        dateElement.classList.add('calendar-date--today');
        dateElement.classList.add('calendar-date--unselectable');
        }
      
      else if (fullCapacityDays && fullCapacityDays.includes(dateISOString)) {
        dateElement.classList.add('calendar-date--full-capacity');
        dateElement.classList.add('calendar-date--unselectable');
      } else {
        dateElement.addEventListener('click', () => {
          // Remove existing selected class
          const selectedDate = document.querySelector('.calendar-date--selected');
          if (selectedDate) {
            selectedDate.classList.remove('calendar-date--selected');
          }
          // Add selected class to clicked date
          dateElement.classList.add('calendar-date--selected');
          appointmentDateField.value = dateISOString;        

          startTimeLabelField.style.display = 'block';
          startTimeField.style.display = 'block';
          startTimeLabelField.innerText='Start Time'

          endTimeLabelField.style.display = 'block';
          endTimeLabelField.innerText = 'End Time'
          endTimeField.style.display = 'block';
          endTimeField.disabled = true;

          startTimeField.addEventListener('change', () => {
            if (startTimeField.value.length > 0) {
              endTimeField.disabled = false;
            } else {
              endTimeField.disabled = true;
            }
            
            if (startTimeField.value.length > 0 && endTimeField.value.length > 0) {
              submitButton.disabled = false;
            } else {
              submitButton.disabled = true;
            }
          });

          endTimeField.addEventListener('change', () => {
            if (startTimeField.value.length > 0 && endTimeField.value.length > 0) {
              submitButton.disabled = false;
            } else {
              submitButton.disabled = true;
            }
          });

          let submitButton = document.querySelector('.appointment-submit-button');
          submitButton.disabled = true;
          
        });
      }
  
      daysContainer.appendChild(dateElement);
  
    });
  
    calendarContainer.appendChild(daysContainer);
    calendarContainer.appendChild(appointmentDateField);
  
    // Create a container to hold the start and end time fields
    const timeFieldsContainer = document.createElement('div');
    timeFieldsContainer.classList.add('time-fields-container');
    timeFieldsContainer.appendChild(startTimeLabelField);
    timeFieldsContainer.appendChild(startTimeField);
    timeFieldsContainer.appendChild(endTimeLabelField);
    timeFieldsContainer.appendChild(endTimeField);
    calendarContainer.appendChild(timeFieldsContainer);
  
    return calendarContainer;
  };
  

// Get all elements with the class 'about-appointments'
const appointmentElems = document.querySelectorAll('.about-appointments');

// Loop through each element and process its content
appointmentElems.forEach((elem) => {
  // Get the text content of the element
  const text = elem.textContent;

  // Split the text into an array of words
  const words = text.split(' ');

  // Create a new string to hold the processed text
  let processedText = '';

  // Loop through each word in the array and add appropriate markup
  words.forEach((word) => {
    // Check if the word starts with a digit
    if (/^\d/.test(word)) {
      // If it does, wrap it in a <strong> tag
      processedText += `<strong>${word}</strong> `;
    } else {
      // If it doesn't, just add it to the string
      processedText += `${word} `;
    }
  });

  // Set the HTML content of the element to the processed text
  elem.innerHTML = processedText;
});

  await renderAboutAppointments('/api/appointments/about_appointment', document.querySelector('#tab1'));
  await renderBookAppointment('/api/appointments', document.querySelector('#tab2'));
  await renderAppointments('/api/appointments', document.querySelector('#tab3'));
  