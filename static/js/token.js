// tokenManager.js

class TokenManager {
    constructor() {
      this.token = null;
    }
  
    setToken(token) {
      this.token = token;
    }
  
    async getToken() {
      if (!this.token) {
        // Make a request to your server to retrieve the token
        const response = await fetch('/api/token');
        const data = await response.json();
        this.token = data.token;
      }
      return this.token;
    }
  
    clearToken() {
      this.token = null;
    }
  }
  
  export default new TokenManager();
  