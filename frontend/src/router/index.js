import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import InvoiceForm from '../views/InvoiceForm.vue'

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
  ...authRoutes,
];

const router = createRouter({
  base: "/frontend/",
  history: createWebHistory(),
  routes,
});

export default router;
