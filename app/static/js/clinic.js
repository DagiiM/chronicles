import { APIClient } from './api.js';

const apiClient = APIClient.getInstance();

async function renderClinics(endpoint, targetElement) {
  const clinics = await apiClient.make_api_call(endpoint);

  const results = clinics.results || [];

  // Remove existing clinics and links
  targetElement.innerHTML = '';

  // Create links for count, next, and previous
  const countLink = document.createElement('a');
  countLink.href = '#';
  countLink.textContent = `Count: ${clinics.count}`;

  const linksContainer = document.createElement('div');
  linksContainer.classList.add('links-container');
  linksContainer.appendChild(countLink);

  if (clinics.next !== null) {
    const nextLink = document.createElement('a');
    nextLink.href = '#';
    nextLink.textContent = 'Next';
    nextLink.classList.add('link');
    nextLink.addEventListener('click', async () => {
      await renderClinics(clinics.next, targetElement);
    });
    linksContainer.appendChild(nextLink);
  }

  if (clinics.previous !== null) {
    const prevLink = document.createElement('a');
    prevLink.href = '#';
    prevLink.textContent = 'Previous';
    prevLink.classList.add('link');
    prevLink.addEventListener('click', async () => {
      await renderClinics(clinics.previous, targetElement);
    });
    linksContainer.appendChild(prevLink);
  }

  if (results.length > 0) {
    results.forEach(result => {
      const cardItem = document.createElement('a');
      //cardItem.href = `/clinics/${result.id}`;
      cardItem.href = `#`;
      cardItem.classList.add('clinic__card');
      const cardHeader = document.createElement('div');
      cardHeader.classList.add('clinic__card--header');
      const nameElement = document.createElement('h3');
      nameElement.classList.add('clinic__card--name');
      nameElement.textContent = result.name;
      cardHeader.appendChild(nameElement);
      const cardInfo = document.createElement('div');
      cardInfo.classList.add('clinic__card--info');
      const isActiveElement = document.createElement('p');
      isActiveElement.classList.add('clinic__card--status');
      isActiveElement.textContent = `Active: ${result.is_active}`;
      cardInfo.appendChild(isActiveElement);

      const createdAtElement = document.createElement('p');
      createdAtElement.classList.add('clinic__card__created_at');
      createdAtElement.textContent = `Opening Date: ${result.created_at}`;
      cardInfo.appendChild(createdAtElement);

      cardItem.append(cardHeader,cardInfo)

      targetElement.appendChild(cardItem);
    });
  }

  targetElement.appendChild(linksContainer);
}

// Retrieve all clinics
renderClinics('/api/clinics/', document.getElementById('tab3'));

// Retrieve clinics near me
async function getClinicsNearMe() {
  try {
    const position = await getCurrentPosition();
    const { latitude, longitude } = position.coords;
    const radius = 10; // default radius in kilometers
    const clinicsEndpoint = `/api/clinics/clinics_near_me/?latitude=${latitude}&longitude=${longitude}&radius=${radius}`;
    renderClinics(clinicsEndpoint, document.getElementById('tab1'));
  } catch (error) {
    console.log(error);
  }
}

async function getCurrentPosition() {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject);
  });
}

getClinicsNearMe();

// Retrieve new clinics
renderClinics('/api/clinics/new_clinics/', document.getElementById('tab2'));
