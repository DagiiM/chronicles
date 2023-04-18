export class APIClient {
  static __instance = null;

  static getInstance(base_url = 'https://eleso.ltd') {
    if (APIClient.__instance === null) {
      APIClient.__instance = new APIClient(base_url);
    }
    return APIClient.__instance;
  }

  constructor(base_url, tokenPrefix = 'Token') {
    if (APIClient.__instance !== null) {
      throw new Error('Cannot instantiate more than one APIClient instance');
    }
    this.base_url = base_url;
    this.token = null;
    this.authenticated = false;
    this.tokenPrefix = tokenPrefix;
    APIClient.__instance = this;
  }
  async authenticate(username, password) {
    try {
      const response = await fetch(`${this.base_url}/auth/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'username': username, 'password': password })
      });
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`API endpoint not found: ${response.url}`);
        }
        const jsonResponse = await response.json();
        const errorMessage = jsonResponse['non_field_errors'][0];
        throw new AuthenticationError(`${errorMessage}`);
      }
      const jsonResponse = await response.json();

      //
      const token = jsonResponse['token'];
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`
      };
      fetch(`${this.base_url}/get-user-id/`, { headers })
      .then(response => response.json())
      .then(data => {
        const userID = data['user_id'];
        sessionStorage.setItem('userID', userID); // Save user data in session storage
      })
      .catch(error => {
        console.error('Error:', error);
      });

      //
      
      this.authenticated = true;
      sessionStorage.setItem('token', token); // Save token in session storage
    } catch (e) {
      throw new Error(`${e}`);
    }
  }

  

  async logout() {
    try {
      const response = await fetch(`${this.base_url}/auth/logout/`, {
        method: 'POST',
        headers: { Authorization: `${this.tokenPrefix} ${this.token}` }
      });
      if (!response.ok) {
        throw new Error(`Logout failed: ${response.statusText}`);
      }
      this.token = null;
      this.authenticated = false;
    } catch (e) {
      throw new Error(`Logout failed: ${e}`);
    }
  }

  async make_api_call(url, method = 'GET', data = null, headers = null, authenticate = true) {
    const endpoint = url.startsWith(this.base_url) ? url.replace(this.base_url, '') : url;
    try {
      const authorizationHeader = authenticate ? { Authorization: `${this.tokenPrefix} ${sessionStorage.getItem('token')}` } : {};
      const userIDHeader = { 'X-User-ID': getUserIdFromSessionStorage() };
      const response = await fetch(url, {
        method: method,
        headers: {
          ...authorizationHeader,
          ...userIDHeader,
          ...headers
        },
        body: data ? JSON.stringify(data) : undefined
      });
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`API endpoint not found: ${response.url}`);
        }
        throw new Error(`API call failed: ${response.statusText}`);
      }
      return response.json();
    } catch (e) {
      if (e.message === 'Cannot make API call: not authenticated') {
        window.location.href = '/login'; // Redirect to login page
        return;
      }
      throw new Error(`API call failed: ${e}`);
    }
  }
  
}

function getUserIdFromSessionStorage() {
  const userData = sessionStorage.getItem('userId');
  console.log(userData)
  if(!userData){
    window.location.href = '/login'
  }
  return userData ? userData.userID : null;
}

export class AuthenticationError extends Error {
  constructor(message) {
    super(message);
    this.name = '';
  }
}
