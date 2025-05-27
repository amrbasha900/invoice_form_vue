import path from 'path';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa';

import vue from '@vitejs/plugin-vue';
import fs from "fs"

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [vue(), tailwindcss(),
    VitePWA({ 
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      manifest: {
        name: 'Invoice Form App',
        short_name: 'InvoiceApp',
        description: 'Invoice management built with Vue + Frappe',
        theme_color: '#ffffff',
        background_color: '#ffffff',
        start_url: '/invoice_form/',
        scope: '/invoice_form/',
        display: 'standalone',
        icons: [
          {
            src: '/pwa-192x192.png',  // Added leading slash
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/pwa-512x512.png',  // Added leading slash
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
	],
	server: {
		port: 8080,
		host: '0.0.0.0', // Allow external connections
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
			target: `http://localhost:${webserver_port}`,  // Changed to localhost
			ws: true,
			changeOrigin: true,
			secure: false,
			timeout: 30000, // 30 second timeout
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
	// traverse up till we find frappe-bench with sites directory
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