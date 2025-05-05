<template>
  <div class="max-w-5xl mx-auto p-4 drafts-form">
    <div class="card">
      <DataView
        v-if="drafts.length > 0"
        :value="drafts"
        layout="list"
        :paginator="true"
        :rows="5"
      >
        <template #list="slotProps">
          <div class="flex flex-col">
            <!-- Draft invoice card -->
            <div v-for="(item, index) in slotProps.items" :key="item.name"  class="mb-4">
              <!-- Invoice Details -->
              <div
                class="grid grid-cols-[80%_20%] items-center rounded-lg shadow-sm p-4 bg-white mb-4"
                :class="{
                  'border-t border-surface-200 dark:border-surface-700':
                    index !== 0,
                }"
              >
                <div class="space-y-1 text-sm sm:text-base">
                  <div class="flex-1 text-sm sm:text-base">
                    <div
                      class="font-bold text-gray-800 mb-1 text-base sm:text-lg invoice-name">
                      <i class="pi pi-file text-blue-500 mr-1" />
                      {{ item.name }}
                    </div>
                    <div class="text-gray-500 mb-0.5">
                      <i class="pi pi-calendar mr-1" /> <b>{{$t('date')}} :</b>
                      {{ item.posting_date || "N/A" }}
                    </div>
                    <div class="text-gray-500 mb-0.5">
                      <i class="pi pi-truck mr-1" /> <b>{{$t('supplier')}} :</b>
                      {{ item.supplier_name || "N/A" }}
                    </div>
                    <div class="text-gray-400">
                      <i class="pi pi-list mr-1" /> <b>{{$t('itemsDraft')}} :</b>
                      {{ item.items?.length || 0 }}
                    </div>
                  </div>
                </div>
                <!-- Action Button -->
                <div class="flex justify-end items-center">
                  <div class="sm:text-right w-full sm:w-auto">
                    <Button
                      icon="pi pi-eye"
                      :label="$t('view')"
                      class="flex-auto md:flex-initial whitespace-nowrap"
                      @click="viewInvoice(item)"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </DataView>

      <div v-else class="text-center text-gray-500 mt-10">
        {{ $t('noDraftInvoicesAvailable') }}
         
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, inject, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { useToast } from "primevue/usetoast";

const drafts = ref([]);
const router = useRouter();
const toast = useToast();

const $permissions = inject("$permissions");

const viewInvoice = (invoice) => {
  router.push(`/invoice?invoice_name=${invoice.name}`);
};

onMounted(async () => {
  // ❌ Block if user lacks permission
  if (!$permissions?.hasPermission("can_show_drafts")) {
    toast.add({
      severity: "error",
      summary: "Access Denied",
      detail: "You do not have permission to view draft invoices.",
      life: 3000,
    });

    // Optional: redirect to Home or another safe page
    router.push({ name: "Home" });
    return;
  }

  try {
    const res = await axios.get(
      "/api/method/invoice_form_vue.api.get_draft_invoice_form"
    );
    drafts.value = res.data.message?.invoices || [];
  } catch (err) {
    console.error("Error fetching drafts:", err);
  }
});
</script>

<style scoped>
.drafts-form {
  margin: 50px auto;
}
b{
  font-weight: 600 !important;
}
.invoice-name{
  font-size: 16px;
  font-weight: 600;
}
</style>
