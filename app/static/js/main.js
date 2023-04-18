const root = document.documentElement;
const body = document.querySelector("body");
const menuIcon = document.querySelector('.header-nav-ul-li__menuicon');
const aside = document.querySelector('aside');
const toggle = document.querySelector('aside .toggle');
const searchBox = document.querySelector('aside .search-box');
const modeSwitch = document.querySelector('aside .mode');
const modeText = document.querySelector('aside .mode .mode-text');

 if (modeSwitch){
  modeSwitch.addEventListener('click', () => {
    body.classList.toggle('dark');
    
    if(body.classList.contains('dark')) {
    modeText.innerText="Light Mode"
    }
    else{
      modeText.innerHTML="Dark Mode"
    }
  });
 }

 if (toggle){
  toggle.addEventListener('click', () => {
    aside.classList.toggle('close');
  });
 }
if (menuIcon){
  menuIcon.addEventListener('click', () => {
    aside.classList.toggle('aside-flex');
  });
  
  document.addEventListener('click', (event) => {
    if (aside.classList.contains('aside-flex') && (!aside.contains(event.target) && !menuIcon.contains(event.target))) {
      aside.classList.remove('aside-flex');
    }
    
  });
}
/**
 * Displays an alert with a message for a specified duration.
 * @param {string} title - The title of the alert.
 * @param {string} message - The message to display in the alert.
 * @param {number} duration - The duration to display the alert in milliseconds.
 */
  function showAlert(title, message,duration=1500) {
    let alert = document.querySelector('.alert-text');
    alert.innerText = message;
    const modal = document.querySelector('.modal');
          modal.style.display = 'block';
          setTimeout(() => {
            modal.style.display = 'none';
          }, duration);
  }

  function openTab(evt, tabId) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabId).style.display = "block";
    evt.currentTarget.className += " active";
  }


