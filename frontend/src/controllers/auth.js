// auth.js
import call from './call';
import axios from 'axios';

export default class Auth {
  constructor() {
    this.isLoggedIn = false;
    this.user = null;
    this.user_image = null;
    this.cookie = null;

    this.cookie = Object.fromEntries(
      document.cookie
        .split('; ')
        .map((part) => part.split('='))
        .map((d) => [d[0], decodeURIComponent(d[1])])
    );

    this.isLoggedIn = this.cookie.user_id && this.cookie.user_id !== 'Guest';
  }

  // auth.js - simplified login method
async login(email, password) {
	try {
	  // Make sure to pass the credentials exactly as expected by Frappe
	  const loginRes = await call('login', {
		usr: email,
		pwd: password
	  });
	  
	  if (loginRes) {
		this.isLoggedIn = true;
		this.user = email;
		return loginRes;
	  }
	  return false;
	} catch (error) {
	  console.error('Login error:', error);
	  throw error;
	}
  }

  async logout() {
    await call('logout');
    this.isLoggedIn = false;
    window.location.reload();
  }
}