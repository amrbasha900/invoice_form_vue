<!-- components/ItemsTable.vue -->
<template>
  <div>
    <DataTable :value="items" class="w-full mt-4 compact-table" responsiveLayout="scroll" @row-click="onRowClick"
      :rowHover="true" stripedRows :scrollable="true" scrollHeight="400px">
      <Column field="item" :header="$t('item')" headerClass="text-center" bodyClass="text-center">
        <template #body="slotProps">
          {{ slotProps.data.item?.label || slotProps.data.item }}
        </template>
      </Column>
      <Column field="qty" :header="$t('qty')" headerClass="text-center" bodyClass="text-center" />
      <Column field="rate" :header="$t('rate')" headerClass="text-center" bodyClass="text-center" />
      <Column :header="$t('amount')" headerClass="text-center" bodyClass="text-center">
  <template #body="slotProps">
    {{ formatAmount(slotProps.data.amount) }}
  </template>
</Column>      <Column :header="$t('customer')" headerClass="text-center" bodyClass="text-center">
        <template #body="slotProps">
          {{ slotProps.data.customer?.label || slotProps.data.customer }}
        </template>
      </Column>
    </DataTable>

    <div class="mt-4 grid grid-cols-2 items-center">
  <!-- Left: Add Item Button -->
  <div class="text-right">
    <Button
      v-if="isDraft && canUpdateDraft"
      :label="$t('addItem')"
      icon="pi pi-plus"
      class="p-button-sm whitespace-nowrap"
      @click="$emit('add-item')"
    />
  </div>

  <!-- Right: Total Amount -->
  <div class="text-left text-sm font-semibold text-gray-700 whitespace-nowrap">
    {{ $t('total') }}: {{ totalAmountFormatted  }}
  </div>
</div>

  </div>
</template>

<script setup>
// Import statements
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import { computed } from 'vue';
// Define props
const props = defineProps({
  items: {
    type: Array,
    required: true
  },
  isDraft: {
    type: Boolean,
    default: true
  },
  canUpdateDraft: {
    type: Boolean,
    default: true
  }
});

// Define emits
const emit = defineEmits(['row-click', 'add-item']);

// Format currency for display
const formatCurrency = (value) => {
  if (value === null || value === undefined) return '';
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "SAR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

// Handle row click
const onRowClick = (event) => {
  emit('row-click', event);
};
const totalAmount = computed(() => {
  return props.items.reduce((sum, item) => sum + (item.amount || 0), 0);
});
const totalAmountFormatted = computed(() => {
  return totalAmount.value.toFixed(2);
});
const formatAmount = (value) => {
  if (value == null || isNaN(value)) return '0.00';
  return Number(value).toFixed(2);
};

</script>

<style scoped>
/* Custom styles for compact table */
:deep(.compact-table) {
  /* Reduced text size */
  font-size: 0.75rem !important;
}

:deep(.compact-table .p-datatable-thead > tr > th) {
  /* Header styles */
  padding: 0.4rem 0.5rem !important;
  background-color: #f8f9fa;
  font-weight: 600 !important;
}

:deep(.compact-table .p-datatable-thead > tr > th .p-datatable-column-header-content) {
  /* Target the inner content div of the header cell */
  text-align: center !important;
  justify-content: center !important;
  display: flex !important;
}

:deep(.compact-table .p-datatable-tbody > tr > td) {
  /* Cell styles */
  padding: 0.2rem 0.5rem !important;
  text-align: center;
}

:deep(.compact-table .p-datatable-tbody > tr) {
  /* Reduced row height */
  height: 2rem !important;
  cursor: pointer;
}

/* Hover effect for better UX */
:deep(.compact-table .p-datatable-tbody > tr:hover) {
  background-color: #f5f5f5 !important;
}

/* Striped rows */
:deep(.compact-table .p-datatable-tbody > tr.p-datatable-striped) {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Add Item button */
:deep(.p-button-sm) {
  font-size: 0.75rem !important;
  padding: 0.3rem 0.7rem !important;
}
</style>