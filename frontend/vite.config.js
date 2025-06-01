import path from 'path';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa';
import vue from '@vitejs/plugin-vue';
import fs from "fs"

// Detect if we're in production or if HTTPS is required
const isProduction = process.env.NODE_ENV === 'production';
const forceHttps = process.env.VITE_FORCE_HTTPS === 'true';
const useHttps = isProduction || forceHttps;

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
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/pwa-512x512.png',
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
		...(useHttps && {
			https: {
				// Try to use existing certificates, fallback to Vite's built-in
				...(fs.existsSync('certs/key.pem') && fs.existsSync('certs/cert.pem') ? {
					key: fs.readFileSync('certs/key.pem'),
					cert: fs.readFileSync('certs/cert.pem')
				} : true)
			}
		}),
		proxy: getProxyOptions(useHttps),
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

function getProxyOptions(useHttps = false) {
	const config = getCommonSiteConfig()
	const webserver_port = config ? config.webserver_port : 8000
	const protocol = useHttps ? 'https' : 'http';
	
	if (!config) {
		console.log("No common_site_config.json found, using default port 8000")
	}
	console.log(`Using webserver port: ${webserver_port} with ${protocol}`)
	
	return {
		"^/(app|login|api|assets|files|private)": {
			target: `${protocol}://localhost:${webserver_port}`,
			ws: true,
			changeOrigin: true,
			secure: !useHttps, // Only secure for actual HTTPS, not self-signed
			timeout: 30000,
			router: function (req) {
				const site_name = req.headers.host.split(":")[0]
				console.log(`Proxying ${req.url} to ${protocol}://localhost:${webserver_port}`)
				return `${protocol}://localhost:${webserver_port}`
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