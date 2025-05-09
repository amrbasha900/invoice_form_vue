import { createApp, reactive } from "vue";
import App from "./App.vue";
import router from './router';
import i18n from './i18n.js';

import './style.css';
import "./flags.css";

import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';
import call from "./controllers/call";
import Auth from "./controllers/auth";
import AppState from './plugins/appState.js';
import Noir from './presets/Noir.js';
import Permissions from './controllers/permission.js';
import '@primeuix/themes/nora';
import 'primeicons/primeicons.css';

import axios from 'axios';

// PrimeVue components
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import AutoComplete from 'primevue/autocomplete';
import Checkbox from 'primevue/checkbox';
import Dialog from 'primevue/dialog';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import DataView from 'primevue/dataview';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import FloatLabel from 'primevue/floatlabel';
import Menubar from "primevue/menubar";
import Tag from 'primevue/tag';
import IftaLabel from 'primevue/iftalabel';
import { useConfirm } from 'primevue/useconfirm';

// 👇 NEW: preload user language + apply lang/dir
async function initApp() {
  let userLang = localStorage.getItem('preferredLang') || 'en';

  try {
    const res = await axios.get('/api/method/frappe.auth.get_logged_user');
    const email = res.data.message;
    const userRes = await axios.get(`/api/resource/User/${email}`);
    const user = userRes.data.data;

    userLang = user.language || 'en';
    localStorage.setItem('preferredLang', userLang);
  } catch (err) {
    console.warn('[i18n] Failed to load user language. Defaulting to "en"');
  }

  // 🧠 Apply locale and dir BEFORE mounting app
  i18n.global.locale.value = userLang;
  document.documentElement.lang = userLang;
  document.documentElement.dir = userLang === 'ar' ? 'rtl' : 'ltr';

  // 🔨 Mount app after init
  const app = createApp(App);
  const auth = reactive(new Auth());
  const permissions = new Permissions();
  if (auth.isLoggedIn) {
    permissions.loadPermissions(auth.cookie.user_id);
  }
  app.use(router);
  app.use(i18n);

  app.provide("$auth", auth);
  app.provide('$permissions', permissions);

  app.provide("$call", call);

  app.use(PrimeVue, {
    theme: {
      preset: Noir,
      options: {
        prefix: 'p',
        darkModeSelector: '.p-dark',
        cssLayer: false,
      }
    }
  });

  app.use(AppState);
  app.use(ToastService);
  app.use(ConfirmationService);

  // Register components
  app.component('Button', Button);
  app.component('InputText', InputText);
  app.component('InputNumber', InputNumber);
  app.component('AutoComplete', AutoComplete);
  app.component('Checkbox', Checkbox);
  app.component('Dialog', Dialog);
  app.component('DataTable', DataTable);
  app.component('Column', Column);
  app.component('DataView', DataView);
  app.component('Toast', Toast);
  app.component('ConfirmDialog', ConfirmDialog);
  app.component('FloatLabel', FloatLabel);
  app.component('Menubar', Menubar);
  app.component('Tag', Tag);
  app.component('IftaLabel', IftaLabel);

  // Route guards
  // In main.js - Update the router guard
// In main.js - Simplify router guard
router.beforeEach((to, from, next) => {
  console.log(`Navigation from ${from.path} to ${to.path}, isLoggedIn: ${auth.isLoggedIn}`);
  
  // Check if the route requires authentication
  const requiresAuth = !to.matched.some(record => record.meta.isLoginPage);
  
  if (requiresAuth && !auth.isLoggedIn) {
    // Route requires auth but user is not logged in
    console.log('Redirecting to login');
    next({ name: 'Login', query: { route: to.path } });
  } else if (!requiresAuth && auth.isLoggedIn) {
    // Login page but user is already logged in
    console.log('Redirecting to home');
    next({ name: 'Home' });
  } else {
    // Normal navigation
    console.log('Proceeding with navigation');
    next();
  }
});

  app.mount("#app");
}

// 🚀 Fire it up!
initApp();
