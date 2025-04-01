/** @type {import('tailwindcss').Config} */
import PrimeUI from 'tailwindcss-primeui';


module.exports = {
    content: [
      './index.html',
      './src/**/*.{vue,js,ts,jsx,tsx}',
      '../../frappe/**/templates/**/*.html' // if you're rendering Frappe templates too
    ],
    theme: {
      extend: {},
    },
    plugins: [PrimeUI],
  }
  