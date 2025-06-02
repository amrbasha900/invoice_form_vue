import path from 'path';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa';
import vue from '@vitejs/plugin-vue';
import fs from "fs"

// https://vitejs.dev/config/
export default defineConfig({
	base: '/invoice_form/', // Add base path for proper asset loading
	plugins: [vue(), tailwindcss(),
    VitePWA({ 
      registerType: 'autoUpdate',
      workbox: {
        // Configure service worker to handle SPA routing
        navigateFallback: '/invoice_form/index.html',
        navigateFallbackDenylist: [
          /^\/_/,
          /\/[^/?]+\.[^/]+$/,
          /^\/api/,
          /^\/app/,
          /^\/login/,
          /^\/assets/,
          /^\/files/,
          /^\/private/
        ],
        // Cache strategy for better performance
        runtimeCaching: [
          {
            urlPattern: /^\/invoice_form\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'invoice-app-pages',
              networkTimeoutSeconds: 3,
            },
          },
        ],
      },
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'Invoice Form App',
        short_name: 'InvoiceApp',
        description: 'Invoice management built with Vue + Frappe',
        theme_color: '#ffffff',
        background_color: '#ffffff',
        start_url: '/invoice_form/home', // Updated to point to /home
        scope: '/invoice_form/',
        display: 'standalone',
        icons: [
          {
            src: '/invoice_form/pwa-192x192.png', // Updated with base path
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/invoice_form/pwa-512x512.png', // Updated with base path
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
	],
	server: {
		port: 8080,
		host: '0.0.0.0',
		proxy: getProxyOptions(),
	},
	resolve: {
		alias: {
			'@': path.resolve(__dirname, 'src')
		}
	},
	build: {
		outDir: '../invoice_form_vue/public/frontend',
		emptyOutDir: true,
		target: 'es2015',
		rollupOptions: {
			output: {
				// Ensure proper chunking for better caching
				manualChunks: {
					vendor: ['vue', 'vue-router'],
					ui: ['primevue']
				}
			}
		}
	},
});

function getProxyOptions() {
	const config = getCommonSiteConfig()
	const webserver_port = config ? config.webserver_port : 8000
	
	if (!config) {
		console.log("No common_site_config.json found, using default port 8000")
	}
	console.log(`Using webserver port: ${webserver_port}`)
	
	return {
		"^/(app|login|api|assets|files|private)": {
			target: `http://localhost:${webserver_port}`,
			ws: true,
			changeOrigin: true,
			secure: false,
			timeout: 30000,
			router: function (req) {
				const site_name = req.headers.host.split(":")[0]
				console.log(`Proxying ${req.url} to http://localhost:${webserver_port}`)
				return `http://localhost:${webserver_port}`
			},
		},
	}
}

function getCommonSiteConfig() {
	let currentDir = path.resolve(".")
	while (currentDir !== "/") {
		if (
			fs.existsSync(path.join(currentDir, "sites")) &&
			fs.existsSync(path.join(currentDir, "apps"))
		) {
			let configPath = path.join(currentDir, "sites", "common_site_config.json")
			if (fs.existsSync(configPath)) {
				try {
					return JSON.parse(fs.readFileSync(configPath))
				} catch (error) {
					console.error("Error parsing common_site_config.json:", error)
					return null
				}
			}
			return null
		}
		currentDir = path.resolve(currentDir, "..")
	}
	return null
}