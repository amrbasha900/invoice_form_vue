<template>

  <div :dir="dir" class="min-h-screen bg-gray-50">
        <Toast position="top-right" />

    <!-- HEADER -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <Menubar :model="menuItems" :key="locale" class="border-0 custom-menubar">
          <template #start>
            <router-link to="/" class="font-bold text-xl text-blue-600 mr-4">
            </router-link>
          </template>
        </Menubar>
      </div>
    </header>

    <!-- MAIN -->
    <main class="py-6">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <router-view :key="$route.fullPath" />
      </div>
    </main>

    <!-- GLOBAL UI -->
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref,computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { watch } from 'vue'
import { useI18n } from 'vue-i18n'
const route = useRoute()

const { t, locale } = useI18n()

const storedLang = localStorage.getItem('preferredLang') || 'en'

const dir = computed(() => (locale.value === 'ar' ? 'rtl' : 'ltr'))

// optional, apply it globally too:
watch(locale, (lang) => {
  document.documentElement.lang = lang
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'
})
const router = useRouter()

const menuItems = computed(() => [
  {
    label: t('menu.home'),
    icon: 'pi pi-home',
    command: () => router.push('/'),
    class: route.path === '/' ? 'active-menu-item' : ''
  },
  {
    label: t('menu.new_invoice'),
    icon: 'pi pi-plus',
    command: () => router.push('/invoice'),
    class: route.path === '/invoice' ? 'active-menu-item' : ''
  },
  {
    label: t('menu.drafts'),
    icon: 'pi pi-list',
    command: () => router.push('/drafts'),
    class: route.path === '/drafts' ? 'active-menu-item' : ''
  },
  {
    label: '',
    icon: 'pi pi-cog',
    command: () => router.push('/settings'),
    class: route.path === '/settings' ? 'active-menu-item' : ''
  }
])


</script>


<style scoped>
:deep(.p-menuitem.active-menu-item .p-menuitem-icon) {
  color: #1d4ed8 !important; /* Same as text */
  font-weight: bold;
  font-size: 1.25rem; /* Slightly larger icon */
}

/* ✅ Make menubar fill 100% and show left/right 1px border */
:deep(.p-menubar) {
  width: 100% !important;
  display: flex !important;
  align-items: center;
  justify-content: flex-start;
  padding: 0 !important;
  border-left: 1px solid #d1d5db !important;   /* Tailwind gray-300 */
  border-right: 1px solid #d1d5db !important;
  border-top: none !important;
  border-bottom: none !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

/* 🔥 Horizontal list always */
:deep(.p-menubar-root-list) {
  display: flex !important;
  flex-direction: row !important;
  align-items: center;
  gap: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  width: 100% !important;
  flex-wrap: nowrap;
}

:deep(.p-menubar-button) {
  display: none !important;
}

:deep(.p-menuitem) {
  text-align: center !important;
}

:deep(.p-menuitem-link) {
  padding: 0.75rem 1rem !important;
  font-weight: 500;
  color: #2563eb;
  border-radius: 0.375rem;
  background: transparent;
  transition: background-color 0.2s;
}

:deep(.p-menuitem-link:hover) {
  background-color: #eff6ff;
  color: #1d4ed8;
}

:deep(.p-menuitem-icon) {
  margin-right: 0.5rem !important;
}
:deep(.active-menu-item) {
  background-color: #eff6ff !important; /* Tailwind blue-50 */
  color: #1d4ed8 !important;            /* Tailwind blue-700 */
  font-weight: bold;
  border-radius: 6px;
}

/* Mobile toast styles */
.p-toast {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.p-toast-top {
  top: env(safe-area-inset-top, 10px) !important;
  left: 0;
  right: 0;
  align-items: center;
}

.p-toast-message {
  margin: 0 1rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-width: 0;
}

.p-toast-message-content {
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
}

.p-toast-message-text {
  margin-left: 0.5rem;
}

.p-toast-message-icon {
  font-size: 1.5rem;
}

.p-toast-summary {
  font-weight: 600;
  font-size: 1rem;
}

.p-toast-detail {
  margin-top: 0.25rem;
  font-size: 0.875rem;
}

/* Custom colors for different toast types */
.p-toast-message-success {
  background-color: #d4edda;
  color: #155724;
}

.p-toast-message-error {
  background-color: #f8d7da;
  color: #721c24;
}

.p-toast-message-info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.p-toast-message-warn {
  background-color: #fff3cd;
  color: #856404;
}
</style>
