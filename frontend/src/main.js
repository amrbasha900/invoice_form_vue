import { createApp, reactive } from "vue";
import App from "./App.vue";
import router from './router';
import './style.css'
import "./flags.css";

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import call from "./controllers/call";
import Auth from "./controllers/auth";
import AppState from './plugins/appState.js';
import Noir from './presets/Noir.js';
import '@primeuix/themes/nora'
import 'primeicons/primeicons.css'


// PrimeVue components
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import AutoComplete from 'primevue/autocomplete'
import Checkbox from 'primevue/checkbox'
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import DataView from 'primevue/dataview'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import FloatLabel from 'primevue/floatlabel'
import Menubar from "primevue/menubar"
import Tag from 'primevue/tag'
import { useConfirm } from 'primevue/useconfirm'



const app = createApp(App);
const auth = reactive(new Auth());

app.use(router);


app.provide("$auth", auth);
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
app.use(PrimeVue)
app.use(ToastService)
app.use(ConfirmationService)
// Register components
app.component('Button', Button)
app.component('InputText', InputText)
app.component('InputNumber', InputNumber)
app.component('AutoComplete', AutoComplete)
app.component('Checkbox', Checkbox)
app.component('Dialog', Dialog)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('DataView', DataView)
app.component('Toast', Toast)
app.component('ConfirmDialog', ConfirmDialog)
app.component('FloatLabel', FloatLabel)
app.component('Menubar', Menubar)
app.component('Tag', Tag)

// Configure route gaurds
router.beforeEach(async (to, from, next) => {
	if (to.matched.some((record) => !record.meta.isLoginPage)) {
		// this route requires auth, check if logged in
		// if not, redirect to login page.
		if (!auth.isLoggedIn) {
			next({ name: 'Login', query: { route: to.path } });
		} else {
			next();
		}
	} else {
		if (auth.isLoggedIn) {
			next({ name: 'Home' });
		} else {
			next();
		}
	}
});

app.mount("#app");
