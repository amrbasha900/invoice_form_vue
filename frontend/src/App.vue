<template>
  <div class="min-h-screen bg-gray-50">
    <!-- HEADER -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <Menubar :model="menuItems" class="border-0 custom-menubar">
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
        <router-view />
      </div>
    </main>

    <!-- GLOBAL UI -->
    <Toast position="bottom-right" />
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const menuItems = ref([
  {
    label: 'Home',
    icon: 'pi pi-home',
    command: () => router.push('/')
  },
  {
    label: 'New',
    icon: 'pi pi-plus',
    command: () => router.push('/invoice')
  },
  {
    label: 'Drafts',
    icon: 'pi pi-list',
    command: () => router.push('/drafts')
  }
])
</script>


<style scoped>
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
  gap: 1rem !important;
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
</style>
