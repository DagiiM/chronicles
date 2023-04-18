class TokenManager {
  constructor() {
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  async getToken() {
    if (!this.token) {
      this.redirectToLogin();
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
  }

  redirectToLogin() {
    window.location.href = '/login';
  }
}

/**
 * Builds a URL with query parameters.
 * @param {string} baseUrl - The base URL.
 * @param {Object} queryParams - An object containing the query parameters.
 * @returns {string} - The built URL.
 */
function buildUrl(baseUrl, queryParams) {
  const url = new URL(baseUrl);
  for (const [key, value] of Object.entries(queryParams)) {
    url.searchParams.append(key, value);
  }
  return url.toString();
}

const tokenManager = new TokenManager

async function sendRequest(baseUrl, endpoint, method, templateName, data, queryParams, cacheName) {
  const token = await tokenManager.getToken();
  try {
/*    // Validate inputs
    if (typeof baseUrl !== 'string' || typeof endpoint !== 'string' || typeof method !== 'string' || typeof token !== 'string') {
      throw new Error('Invalid input type');
    }
*/
    // Validate HTTP method
    const allowedMethods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];
    if (!allowedMethods.includes(method.toUpperCase())) {
      throw new Error(`Invalid HTTP method: ${method}`);
    }

    // Create URL
    const url = buildUrl(baseUrl, queryParams) + endpoint;

    // Create options object
    const options = {
      method,
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    };

    if (method === 'POST') {
      options.body = JSON.stringify(data);
    }

    // Check if response is cached
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(url);
    if (cachedResponse) {
      const responseData = await cachedResponse.json();
      renderResponse(responseData, templateName);
      return responseData;
    }

    // Send request and cache response
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }

    const responseData = await response.json();
    cache.put(url, response.clone());

    // Render response
    renderResponse(responseData, templateName);
    return responseData;
  } catch (error) {
    showAlert('Error', error.message);
    throw error;
  }

}
