
import { APIClient } from './api.js';

const apiClient = APIClient.getInstance();
//await apiClient.authenticate(); // Authenticate first

async function renderNotifications(endpoint, targetElement) {
  const notifications = await apiClient.make_api_call(endpoint);

  const results = notifications.results || [];

  // Remove existing notifications and links
  targetElement.innerHTML = '';

  // Create links for count, next, and previous
  const countLink = document.createElement('a');
  countLink.href = '#';
  countLink.textContent = `Count: ${notifications.count}`;

  const linksContainer = document.createElement('div');
  linksContainer.classList.add('links-container');
  linksContainer.appendChild(countLink);

  if (notifications.next !== null) {
    const nextLink = document.createElement('a');
    nextLink.href = '#';
    nextLink.textContent = 'Next';
    nextLink.classList.add('link');
    nextLink.addEventListener('click', async () => {
      await renderNotifications(notifications.next, targetElement);
    });
    linksContainer.appendChild(nextLink);
  }

  if (notifications.previous !== null) {
    const prevLink = document.createElement('a');
    prevLink.href = '#';
    prevLink.textContent = 'Previous';
    prevLink.classList.add('link');
    prevLink.addEventListener('click', async () => {
      await renderNotifications(notifications.previous, targetElement);
    });
    linksContainer.appendChild(prevLink);
  }

  if (results.length > 0) {
    results.forEach(result => {
      const cardItem = document.createElement('a');
      cardItem.classList.add('card__item');
      cardItem.href = '#';

      const title = document.createElement('div');
      title.classList.add('card__item--title');
      title.textContent = result.subject;

      const description = document.createElement('div');
      description.classList.add('card__item--description');
      description.textContent = result.body;

      const time = document.createElement('div');
      time.classList.add('card__item--time');
      time.textContent = result.date_created;

      cardItem.appendChild(title);
      cardItem.appendChild(description);
      cardItem.appendChild(time);

      targetElement.appendChild(cardItem);
    });

    linksContainer.style.display = 'block';
  } else {
    linksContainer.style.display = 'none';

    const noResultsMessage = document.createElement('div');
    noResultsMessage.classList.add('no-results-message');
    noResultsMessage.textContent = 'No notifications found.';

    targetElement.appendChild(noResultsMessage);
  }

  targetElement.appendChild(linksContainer);
}


let tab1 = await renderNotifications('/api/notifications/unread_notifications', document.getElementById('tab1'));
let tab2 = await renderNotifications('/api/notifications/read_notifications/', document.getElementById('tab2'));
let tab3 = await renderNotifications('/api/notifications', document.getElementById('tab3'));
