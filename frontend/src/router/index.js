import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import InvoiceForm from '../views/InvoiceForm.vue'
import Drafts from '../views/Drafts.vue'
import Settings from '../views/Settings.vue'
import Login from '../views/Login.vue'
import authRoutes from './auth';

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/invoice",
    name: "InvoiceForm",
    component: InvoiceForm,
  },
  {
    path: "/drafts",
    name: "Drafts",
    component: Drafts,
  },
  {
    path: "/settings",
    name: "Settings",
    component: Settings,
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: { 
      isLoginPage: true
    }
  },
  ...authRoutes,
];

const router = createRouter({
  history: createWebHistory("/invoice_form"),
  routes,
});

export default router;
