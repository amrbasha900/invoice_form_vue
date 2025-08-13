<!-- components/ItemsTable.vue - Enhanced with row delete icons -->
<template>
  <div>
    <DataTable :value="items" class="w-full mt-4 compact-table" responsiveLayout="scroll" @row-click="onRowClick"
      :rowHover="canUpdateDraft" :rowClass="rowClass" :scrollable="true" scrollHeight="400px">
      
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
      </Column>
      
      <Column :header="$t('customer')" headerClass="text-center" bodyClass="text-center">
        <template #body="slotProps">
          {{ slotProps.data.customer?.label || slotProps.data.customer }}
        </template>
      </Column>

      <!-- New Delete Action Column -->
      <Column v-if="showDeleteColumn" :header="$t('actions')" headerClass="text-center" bodyClass="text-center" style="width: 60px">
        <template #body="slotProps">
          <Button 
            icon="pi pi-trash" 
            class="p-button-rounded p-button-text p-button-danger p-button-sm"
            @click="onDeleteRow($event, slotProps.index)"
            type="button"
            :aria-label="$t('delete')"
            v-tooltip.top="$t('delete')"
          />
        </template>
      </Column>
    </DataTable>

    <div class="mt-4 grid grid-cols-2 items-center" style="direction: ltr;">
      <!-- Right: Total Amount -->
      <div class="text-left text-sm font-semibold text-gray-700 whitespace-nowrap">
        {{ $t('total') }}: {{ totalAmountFormatted }}
      </div>
      
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
    </div>
  </div>
</template>

<script setup>
// Import statements
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import { computed } from 'vue';
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const confirm = useConfirm();
const toast = useToast();

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
  },
  canDeleteInvoice: {
    type: Boolean,
    default: false
  }
});

// Define emits
const emit = defineEmits(['row-click', 'add-item', 'delete-item']);

// Computed property to show delete column only if user has delete permission
const showDeleteColumn = computed(() => {
  return props.canDeleteInvoice && props.isDraft && props.canUpdateDraft;
});

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

// Handle row click (but prevent if clicking on delete button)
const onRowClick = (event) => {
  // Only emit row click event if the user has permission to update
  // and if they didn't click on the delete button
  if (props.canUpdateDraft && !event.originalEvent.target.closest('.p-button')) {
    emit('row-click', event);
  }
};

// Handle delete row click
const onDeleteRow = (event, rowIndex) => {
  // Prevent row click event when delete button is clicked
  event.stopPropagation();
  
  // Show confirmation dialog
  confirm.require({
    message: t('confirmDeleteItem'),
    header: t('confirmDelete'),
    icon: "pi pi-exclamation-triangle",
    acceptClass: "p-button-danger",
    acceptLabel: t('yesDelete'),
    rejectLabel: t('cancel'),
    accept: () => {
      // Emit delete event with row index
      emit('delete-item', rowIndex);
    },
    reject: () => {
      toast.add({
        severity: "info",
        summary: t('cancelled'),
        life: 2000,
      });
    },
  });
};

// Set row class based on whether the row is clickable
const rowClass = (data) => {
  return {
    'cursor-default': !props.canUpdateDraft,
    'cursor-pointer': props.canUpdateDraft
  };
};

// Calculate total amount
const totalAmount = computed(() => {
  return props.items.reduce((sum, item) => sum + (item.amount || 0), 0);
});

// Format total amount for display
const totalAmountFormatted = computed(() => {
  return totalAmount.value.toFixed(2);
});

// Format individual amount for display
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
}

/* Hover effect for better UX - only when editable */
:deep(.compact-table .p-datatable-tbody > tr.cursor-pointer:hover) {
  background-color: #f5f5f5 !important;
}

/* No hover effect when not editable */
:deep(.compact-table .p-datatable-tbody > tr.cursor-default:hover) {
  background-color: inherit !important;
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

/* Delete button styles */
:deep(.p-button-rounded.p-button-text.p-button-danger) {
  width: 2rem !important;
  height: 2rem !important;
  padding: 0 !important;
  font-size: 0.75rem !important;
}

/* Hover effect for delete button */
:deep(.p-button-rounded.p-button-text.p-button-danger:hover) {
  background-color: rgba(239, 68, 68, 0.1) !important;
  color: #dc2626 !important;
}

/* Actions column specific styling */
:deep(.compact-table .p-datatable-tbody > tr > td:last-child) {
  padding: 0.1rem !important;
}
</style>