<template>
  <div class="max-w-2xl mx-auto px-4 py-6 space-y-6 settings-form">
    <!-- USER INFO CARD -->
    <!-- USER INFO CARD -->
    <div class="settings-card">
      <div class="grid grid-cols-[auto_1fr] gap-x-8 items-center mb-2">
        <!-- Avatar -->
        <div class="shrink-0">
          <img
            v-if="user?.user_image"
            :src="user.user_image"
            alt="Avatar"
            class="w-14 h-14 rounded-full object-cover border border-gray-300"
          />
          <div
            v-else
            class="avatar-placeholder"
          >
            {{ userInitials }}
          </div>
        </div>

        <!-- User Info -->
        <div class="flex flex-col">
          <div class="text-gray-800 font-semibold text-base leading-snug">
            {{ user?.full_name || 'Unnamed User' }}
          </div>
          <div class="text-gray-500 text-sm leading-tight">
            {{ user?.email || 'No email' }}
          </div>
        </div>
      </div>
    </div>


    <!-- LANGUAGE CARD -->
    <div class="settings-card">
      <div class="card-header">
        <i class="pi pi-globe icon text-green-600" />
        <span>Language</span>
      </div>
      <div class="card-body flex gap-3 flex-wrap">
        <Button 
          label="English"
          icon="pi pi-flag"
          :class="{ 'p-button-outlined': selectedLang !== 'en' }"
          @click="changeLang('en')"
        />
        <Button 
          label="Arabic"
          icon="pi pi-globe"
          :class="{ 'p-button-outlined': selectedLang !== 'ar' }"
          @click="changeLang('ar')"
        />
      </div>
    </div>

    <!-- LOGOUT CARD -->
    <div class="settings-card">
      <div class="card-header">
        <i class="pi pi-sign-out icon text-red-500" />
        <span>Logout</span>
      </div>
      <div class="card-body">
        <div class="flex flex-wrap items-center justify-center gap-10">
        <Button 
          label="Move to ERPNext" 
          icon="pi pi-th-large"
          severity="info"
            class="w-full my-50px"
          @click="goToDesk"
        />
        <div class="h-3"></div>
        <Button 
          label="Logout" 
          icon="pi pi-power-off"
          severity="danger"
            class="w-full my-50px"
          @click="logout"
        />
      </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const user = ref({})
const selectedLang = ref('en')
const toast = useToast()
const router = useRouter()

const fetchUser = async () => {
  try {
    const res = await axios.get('/api/method/frappe.auth.get_logged_user')
    const userEmail = res.data.message
    const userRes = await axios.get(`/api/resource/User/${userEmail}`)
    user.value = userRes.data.data
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load user info' })
  }
}

const changeLang = async (lang) => {
  try {
    selectedLang.value = lang
    await axios.post('/api/method/frappe.translate.set_user_language', { language: lang })
    toast.add({ severity: 'success', summary: 'Language Changed', detail: lang.toUpperCase() })
    location.reload()
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to change language' })
  }
}

const logout = async () => {
  try {
    await axios.post('/api/method/logout')

    // Show toast first
    toast.add({ severity: 'success', summary: 'Logged Out' })

    // Short delay to allow toast to render
    setTimeout(() => {
      location.replace('/invoice_form') // Hard redirect
    }, 1000)

  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: `$${err} : Logout failed` })
  }
}

const goToDesk = async () => {
  try {

    setTimeout(() => {
      location.replace('/app') // Hard redirect
    }, 1000)

  } catch (err) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Logout failed' })
  }
}

const userInitials = computed(() => {
  if (!user.value?.full_name) return '?'
  return user.value.full_name
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

onMounted(fetchUser)
</script>

<style scoped>
:deep(.p-button) {
   max-width: 500px !important;
   margin: 10px auto;
}
.settings-form {
  margin: 50px auto;
}

.settings-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  padding: 1.25rem;
  margin-bottom: 10px;
}

.card-header {
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  color: #374151; /* Tailwind gray-700 */
}

.icon {
  font-size: 1.5rem;
}

.avatar-placeholder {
  width: 56px;
  height: 56px;
  border-radius: 9999px;
  background: #e0f2fe;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.25rem;
  line-height: 1;
}

</style>
