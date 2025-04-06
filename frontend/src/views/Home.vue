<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">{{$t('dashboard')}}</h1>
      <p class="text-gray-600 mt-1">{{$t('dashboardWellcom')}}</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <!-- Draft Invoices Card -->
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">{{$t('draftInvoices')}}</h2>
          <div class="p-2 bg-blue-100 text-blue-800 rounded-full">
            <i class="pi pi-file-o"></i>
          </div>
        </div>
        <div class="text-3xl font-bold">{{ stats.draftCount || 0 }}</div>
        <div class="mt-2 text-sm text-gray-500">{{$t('pendingInvoices')}}</div>
        <div class="mt-4">
          <Button :label="$t('viewDrafts')" icon="pi pi-eye" @click="$router.push('/drafts')" class="p-button-text" />
        </div>
      </div>

      <!-- Submitted Invoices Card -->
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">{{$t('submittedInvoices')}}</h2>
          <div class="p-2 bg-green-100 text-green-800 rounded-full">
            <i class="pi pi-check-circle"></i>
          </div>
        </div>
        <div class="text-3xl font-bold">{{ stats.submittedCount || 0 }}</div>
        <div class="mt-2 text-sm text-gray-500">{{$t('completedInvoices')}}</div>
        <div class="mt-4">
          <Button :label="$t('viewSubmitted')" icon="pi pi-eye" class="p-button-text" />
        </div>
      </div>

      <!-- Quick Actions Card -->
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">{{$t('quickActions')}}</h2>
          <div class="p-2 bg-purple-100 text-purple-800 rounded-full">
            <i class="pi pi-bolt"></i>
          </div>
        </div>
        <div class="space-y-3">
          <Button :label="$t('createNewInvoice')" icon="pi pi-plus" @click="$router.push('/invoice')" class="w-full" />
          <Button :label="$t('viewDraftInvoices')" icon="pi pi-file-o" @click="$router.push('/drafts')" class="w-full p-button-outlined" />
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="bg-white shadow rounded-lg p-6 mb-8">
      <h2 class="text-lg font-semibold mb-4">{{$t('recentActivity')}}</h2>
      
      <div v-if="loading" class="flex justify-center my-6">
        <i class="pi pi-spin pi-spinner text-2xl"></i>
      </div>
      
      <div v-else-if="recentInvoices.length > 0" class="overflow-x-auto">
        <DataTable :value="recentInvoices" class="p-datatable-sm" responsiveLayout="scroll">
          <Column field="name" :header="$t('invoiceID')">
            <template #body="slotProps">
              <router-link :to="`/invoice?invoice_name=${slotProps.data.name}`" class="text-primary-600 hover:underline">
                {{ slotProps.data.name }}
              </router-link>
            </template>
          </Column>
          <Column field="posting_date" :header="$t('date')">
            <template #body="slotProps">
              {{ formatDate(slotProps.data.posting_date) }}
            </template>
          </Column>
          <Column field="customer_name" :header="$t('customer')" />
          <Column field="supplier_name" :header="$t('supplier')" />
          <Column field="status" :header="$t('status')">
            <template #body="slotProps">
              <Tag :value="slotProps.data.status" 
                  :severity="slotProps.data.status === 'Draft' ? 'warning' : 'success'" />
            </template>
          </Column>
          <Column :header="$t('actions')" bodyStyle="text-align:center">
            <template #body="slotProps">
              <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-sm" 
                     @click="$router.push(`/invoice?invoice_name=${slotProps.data.name}`)" />
            </template>
          </Column>
        </DataTable>
      </div>
      
      <div v-else class="text-center py-4 text-gray-500">
        {{$t('noRecentActivityFound')}}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const loading = ref(true)
const recentInvoices = ref([])
const stats = ref({
  draftCount: 0,
  submittedCount: 0
})

// Format date 
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  
  const date = new Date(dateString)
  if (isNaN(date)) return dateString
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

onMounted(async () => {
  try {
    loading.value = true
    
    // Get dashboard data
    const res = await axios.get('/api/method/invoice_form_vue.api.get_dashboard_data')
    const data = res.data.message.message || res.data
    
    // Update statistics
    stats.value = {
      draftCount: data.draft_count || 0,
      submittedCount: data.submitted_count || 0
    }
    
    // Update recent invoices
    recentInvoices.value = data.recent_invoices || []
    console.log(data)
    
  } catch (error) {
    console.error('Error loading dashboard data:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load dashboard data',
      life: 3000
    })
  } finally {
    loading.value = false
  }
})
</script>