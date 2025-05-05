<template>
  <div class="home-container">
    <!-- Using the Logo Component -->
    <div class="logo-container">
      <LogoComponent class="logo-animation" />
    </div>

    <!-- Welcome Text -->
    <div class="welcome-text">
      <h1 class="text-xl font-bold text-gray-900">{{$t('dashboard')}}</h1>
      <p class="text-sm text-gray-600 mt-1">{{$t('dashboardWellcom')}}</p>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <Button 
        :label="$t('createNewInvoice')" 
        icon="pi pi-plus" 
        @click="$router.push('/invoice')" 
        class="p-button-md" 
      />
      <Button 
        :label="$t('viewDraftInvoices')" 
        icon="pi pi-file-o" 
        @click="$router.push('/drafts')" 
        class="p-button-outlined p-button-md mt-3" 
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue';
import Button from 'primevue/button';
import LogoComponent from '../components/LogoComponent.vue';

// Responsive viewport height handling to avoid mobile scrolling issues
const adjustHeight = () => {
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
};

onMounted(() => {
  adjustHeight();
  window.addEventListener('resize', adjustHeight);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', adjustHeight);
});
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  /* Use CSS custom property for true viewport height */
  height: calc(var(--vh, 1vh) * 100);
  max-height: 100vh;
  box-sizing: border-box;
  /* Add overflow control to prevent scrolling */
  overflow: hidden;
}

.logo-container {
  width: 100%;
  /* Smaller on mobile, larger on desktop */
  max-width: min(60vw, 220px);
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
  flex-shrink: 1;
}

.logo-animation {
  width: 100%;
  height: auto;
  /* Add floating animation to the SVG component */
  animation: float 6s infinite ease-in-out;
  /* Prevent oversizing */
  max-height: 35vh;
}

.welcome-text {
  text-align: center;
  margin-bottom: 2rem;
  /* Allow text to shrink if needed */
  flex-shrink: 1;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 250px;
  /* Allow buttons to shrink if needed */
  flex-shrink: 1;
}

/* Use medium sized buttons that work better on mobile */
.p-button-md {
  height: 3rem;
  font-size: 1rem;
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
}

/* Media query for larger screens */
@media (min-height: 700px) {
  .logo-container {
    max-width: 280px;
    margin-bottom: 2rem;
  }
  
  .welcome-text {
    margin-bottom: 2.5rem;
  }
  
  .p-button-md {
    height: 3.5rem;
  }
}

/* Media query for very small screens */
@media (max-height: 500px) {
  .logo-container {
    max-width: 150px;
    margin-bottom: 1rem;
  }
  
  .welcome-text {
    margin-bottom: 1rem;
  }
  
  .welcome-text h1 {
    font-size: 1.1rem;
  }
  
  .welcome-text p {
    font-size: 0.8rem;
  }
  
  .p-button-md {
    height: 2.5rem;
    font-size: 0.9rem;
  }
  
  .action-buttons .mt-3 {
    margin-top: 0.75rem;
  }
}
</style>