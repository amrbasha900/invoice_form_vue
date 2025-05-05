// permissions.js
import call from './call';
import axios from "axios";

export default class Permissions {
  constructor() {
    this.permissions = {
      can_login: false,
      can_delete_invoice: false,
      can_submit_invoice: false,
      can_update_draft: false,
      can_update_submitted: false,
      can_show_drafts: false,
      can_show_submitted: false
    };
    this.loaded = false;
  }

  async loadPermissions(user) {
    try {
      if (!user) return;
      console.log("Loading permissions for user:", user);
      
      // Correctly pass the user parameter in the params object
      const response = await axios.get('/api/method/invoice_form_vue.api.check_user_permission', {
        params: { user: user }
      });

      if (response && response.data && response.data.message) {
        this.permissions = response.data.message;
        this.loaded = true;
        console.log("Permissions loaded:", this.permissions);
      }
    } catch (error) {
      console.error('Error loading permissions:', error);
    }
  }

  hasPermission(permission) {
    console.log(`Checking permission ${permission}:`, this.permissions[permission]);
    return this.permissions[permission] === true;
  }
}