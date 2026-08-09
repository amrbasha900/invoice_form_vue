// This file makes it easier to import assets in your components
import './logoAnimation.css';

// Export the path to the logo
export const logoPath = new URL('./logo.png', import.meta.url).href;