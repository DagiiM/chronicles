import { APIClient } from './api.js';

const apiClient = APIClient.getInstance();

function renderConsultationChat(endpoint, targetElement, userID) {
  // Define HTML structure of the chat container
  const chatContainer = `
    <section class="chat" id='consult-chat'>
      <div class='chat__container'>
      </div>
      <div class="chat__send">
        <input class="chat__input" type="text" placeholder="Type your message">
        <button class="chat__button"><i class="icon icon-send"></i></button>
      </div>
      <div class="chat__switch">
      <div class='chat__switch-inner'>
      <label class="chat__label"></label>
      <input class="chat__input-switch" type="checkbox">
    </div>
      </div>

    </section>
  `;
  // Create a container for the chat and add the HTML structure to it
  const chatWrapper = document.createElement('div');
  chatWrapper.innerHTML = chatContainer.trim();
  const chatElement = chatWrapper.firstChild;

  // Get the send message input and button
  const messageInput = chatElement.querySelector('.chat__input');
  const sendButton = chatElement.querySelector('.chat__button');

  // Get the switch input and label
  const switchInput = chatElement.querySelector('.chat__input-switch');
  const switchLabel = chatElement.querySelector('.chat__label');

  // Set initial switch state and content recipient
  const isBot = "true";
  let recipient = isBot ? 'Bot' : 'Staff';

  // Configure switch input
  switchInput.checked = isBot;
  switchInput.addEventListener('change', () => {
    recipient = switchInput.checked ? 'Bot' : 'Staff';
    switchLabel.textContent = `Consult with ${recipient}`;
  });

  // Configure switch label
  switchLabel.textContent = `Consult with ${recipient}`;

  // Configure send button
  sendButton.addEventListener('click', async () => {
    const message = messageInput.value.trim();
    if (message) {
      const data = {
        sender: userID,
        content: message,
        bot: isBot
      };
      await sendMessage(endpoint, data);
      messageInput.value = '';
    }
  });

  // Add chat container to the target element
  targetElement.appendChild(chatElement);

  async function sendMessage(endpoint, data) {
    try {
      let submitBtn = document.querySelector('button.chat__button')
      submitBtn.innerHTML='...'
      submitBtn.setAttribute('disabled', 'disabled')
      let smscontainer = document.querySelector('.chat__container')
      const response = await apiClient.make_api_call(
        endpoint,
        'POST',
        { ...data },
        { 'Content-Type': 'application/json' },
        true
      );
      submitBtn.innerHTML='<i class="icon icon-send"></i>'
      submitBtn.removeAttribute('disabled', 'disabled')
      // Scroll to the bottom of the chat container
      window.scrollTo(0, smscontainer.scrollHeight);
  
    } catch (e) {
      console.error('Error sending message:', e);
    }
  }

}
const userid = sessionStorage.getItem('userID');

async function loadConsultations(endpoint, sender) {
  const userid = sessionStorage.getItem('userID');
  if (userid === null) {
    // Redirect to login page
    window.location.href = '/login';
  } else {
    try {
      const response = await apiClient.make_api_call(endpoint);
      let results = response.results || [];
      const chatBox = document.querySelector('#consult-chat .chat__container');

      // Initialize array to store message IDs
      let messageIds = [];

      for (let message of results) {
        // Check if message ID is already in the array
        if (messageIds.includes(message.id)) {
          continue; // Skip adding this message to the DOM
        }

        const messageEl = document.createElement('div');
        if (String(message.sender) === userid) {
          messageEl.classList.add('chat__sent');
        } else {
          messageEl.classList.add('chat__receive');
        }
        messageEl.innerHTML = message.content;
        chatBox.appendChild(messageEl);

        // Add message ID to the array
        messageIds.push(message.id);
      }

      if (response.next) {
        await loadConsultations(response.next);
      } else {
        // Set the scroll position after all the messages have been added to the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
        window.scrollTo(0, chatBox.scrollHeight);
      }

      // Poll for new messages every 5 seconds
      setInterval(async () => {
        const response = await apiClient.make_api_call(endpoint);
        let results = response.results || [];
      
        let messagesAdded = false;
      
        for (let message of results) {
          // Check if message ID is already in the array
          if (messageIds.includes(message.id)) {
            continue; // Skip adding this message to the DOM
          }
      
          const messageEl = document.createElement('div');
          if (String(message.sender) === userid) {
            messageEl.classList.add('chat__sent');
          } else {
            messageEl.classList.add('chat__receive');
          }
      
          messageEl.innerHTML = message.content;
          chatBox.appendChild(messageEl);
      
          // Add message ID to the array
          messageIds.push(message.id);
      
          // Set flag to indicate messages were added
          messagesAdded = true;
        }
      
        // Set the scroll position if new messages were added
        if (messagesAdded) {
          chatBox.scrollTop = chatBox.scrollHeight;
          window.scrollTo(0, chatBox.scrollHeight)
        }
      }, 5000);
    } catch (e) {
      console.error('Error loading consultations:', e);
    }
  }
}








loadConsultations('api/consultations',userid)
renderConsultationChat('/api/consultations/', document.getElementById('tab1'), 1);
