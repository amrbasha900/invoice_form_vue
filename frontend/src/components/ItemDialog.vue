<!-- components/ItemDialog.vue -->
<template>
  <Dialog 
    :header="t('addItem')" 
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    modal 
    :dismissableMask="true" 
    :style="{
      width: '100%',
      maxWidth: '400px',
      position: 'fixed',
      top: '2%',
      left: '50%',
      transform: 'translateX(-50%)',
    }" 
    :breakpoints="{ '960px': '95vw', '640px': '100vw' }"
  >
    <!-- Row navigation controls - only show if in edit mode -->
    <div v-if="editIndex !== null" class="flex justify-between items-center mb-3">
      <Button 
        icon="pi pi-chevron-up" 
        class="p-button-rounded p-button-outlined p-button-sm"
        @click="handlePrevRow"
        :disabled="editIndex === 0"
        type="button"
      />
      <span class="text-xs font-semibold">{{ t('item') }} {{ editIndex + 1 }} / {{ totalRows }}</span>
      <Button 
        icon="pi pi-chevron-down" 
        class="p-button-rounded p-button-outlined p-button-sm"
        @click="handleNextRow"
        :disabled="editIndex === totalRows - 1"
        type="button"
      />
    </div>
    
    <div class="mt-1">
      <div class="w-full">
      <div class="grid grid-cols-12 gap-1">
        <div class="col-span-11">
          <FloatLabel variant="on" class="w-full block">
            <AutoComplete 
              v-model="item.item" 
              inputId="item" 
              :suggestions="itemSuggestions" 
              optionLabel="label"
              @complete="searchItem" 
              :forceSelection="true" 
              :completeOnFocus="true" 
              class="w-full"
              :disabled="!canEditItem"
            />
            <label for="item">{{ t('itemCode') }}</label>
          </FloatLabel>
        </div>
        <div class="col-span-1 flex items-center justify-center">
          <Button 
            icon="pi pi-trash" 
            :class="[
              'p-button-rounded p-button-text',
              item.item ? 'p-button-danger' : ''
            ]" 
            @click="clearItem"
            type="button"
            aria-label="Clear item"
            :disabled="!canEditItem || !item.item"
          />
        </div>
      </div>
      <span v-if="validationErrors.item" class="text-sm text-red-500 validationErrors">
        {{ t('itemCodeIsRequired') }}
      </span>
    </div>
      
      <div class="grid grid-cols-3 sm:grid-cols-3 gap-x-6 gap-y-4 mb-4">
        <div>
          <FloatLabel variant="on">
            <InputText
              v-model="qtyInput"
              inputId="qty"
              class="w-full"
              inputmode="decimal"
              type="text"
              pattern="[0-9]*[.,]?[0-9]*"
              :disabled="!canEditItem"
            />
            <label for="qty">{{ t('qty') }}</label>
          </FloatLabel>
          <span v-if="validationErrors.qty" class="text-sm text-red-500 validationErrors">
            {{ t('qtyIsRequired') }}
          </span>
        </div>
        
        <div>
          <FloatLabel variant="on">
            <InputText
              v-model="rateInput"
              inputId="rate"
              class="w-full"
              inputmode="decimal"
              type="text"
              pattern="[0-9]*[.,]?[0-9]*"
              :disabled="!canEditItem"
            />
            <label for="rate">{{ t('rate') }}</label>
          </FloatLabel>
          <span v-if="validationErrors.rate" class="text-sm text-red-500 validationErrors">
            {{ t('rateIsRequired') }}
          </span>
        </div>
        
        <FloatLabel variant="on" class="w-full">
          <InputText 
            v-model="item.amount" 
            inputId="amount" 
            class="w-full" 
            :disabled="true" 
            mode="currency"
            currency="SAR" 
          />
          <label for="amount">{{ t('totalAmount') }}</label>
        </FloatLabel>
      </div>
      
      <div class="w-full">
        <div class="grid grid-cols-12 gap-1">
          <div class="col-span-11">
            <FloatLabel variant="on" class="w-full block">
              <AutoComplete
                v-model="item.customer"
                inputId="Customer"
                :suggestions="customerSuggestions"
                optionLabel="label"
                @complete="searchCustomer"
                :forceSelection="true"
                :completeOnFocus="true"
                class="w-full"
                :disabled="!canEditItem"
              />
              <label for="Customer">{{ t('customer') }}</label>
            </FloatLabel>
          </div>
          
          <div class="col-span-1 flex items-center justify-center">
            <Button 
              icon="pi pi-trash" 
              :class="[
                'p-button-rounded p-button-text',
                item.customer ? 'p-button-danger' : ''
              ]" 
              @click="clearCustomer"
              type="button"
              aria-label="Clear customer"
              :disabled="!canEditItem || !item.customer"
            />
          </div>
        </div>
        <span v-if="validationErrors.customer" class="text-sm text-red-500 validationErrors">
          {{ t('customerIsRequired') }}
        </span>
      </div>

      <!-- Add after the customer field in ItemDialog.vue -->
<div v-if="showItemRemark" class="w-full mt-4">
  <FloatLabel variant="on" class="w-full block">
    <Textarea
      v-model="item.remark"
      inputId="remark"
      rows="2"
      class="w-full"
      :disabled="!canEditItem"
    />
    <label for="remark">{{ t('remark') }}</label>
  </FloatLabel>
</div>
      
      <div class="grid grid-cols-3 gap-2 mt-4">
        <div class="col-span-1">
          <Button 
            v-if="canEditItem"
            :label="editIndex !== null ? t('update') : t('add')" 
            @click="saveItem" 
            class="w-full" 
          />
        </div>

        <div class="col-span-1"></div>

        <div class="col-span-1" v-if="editIndex !== null && canDeleteItem">
          <Button 
            :label="t('delete')" 
            icon="pi pi-trash" 
            severity="danger"
            @click="handleDelete" 
            class="w-full" 
          />
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { reactive, ref, computed, watch, inject } from "vue";
import Dialog from "primevue/dialog";
import Button from "primevue/button";
import AutoComplete from "primevue/autocomplete";
import InputText from "primevue/inputtext";
import FloatLabel from "primevue/floatlabel";
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import { useI18n } from 'vue-i18n';
import Textarea from "primevue/textarea";
const { t } = useI18n();

const confirm = useConfirm();
const toast = useToast();

import { onMounted } from "vue";
const $permissions = inject('$permissions');
// Props from parent
const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  itemData: {
    type: Object,
    default: () => ({
      item: "",
      qty: "",
      rate: "",
      amount: null,
      customer: "",
      qtyEditing: false,
      rateEditing: false
    })
  },
  editIndex: {
    type: Number,
    default: null
  },
  allItems: {
    type: Array,
    default: () => []
  },
  allCustomers: {
    type: Array,
    default: () => []
  },
  validationErrors: {
    type: Object,
    default: () => ({})
  },
  totalRows: {
    type: Number,
    default: 0
  },
  isDraft: Boolean,
  canUpdateDraft: Boolean,
  canUpdateSubmitted: Boolean,
  canDeleteInvoice: Boolean
});

// Emits
const emit = defineEmits([
  'update:visible',
  'save-item',
  'delete-item',
  'clear-customer',
  'update:itemData',
  'navigate-row',
  'clear-item',
]);

// Local data
const item = reactive({
  item: "",
  qty: "",
  rate: "",
  amount: null,
  customer: "",
  qtyEditing: false,
  rateEditing: false,
  remark: "",
});
const itemSuggestions = ref([]);
const customerSuggestions = ref([]);

// Navigation handlers with simpler naming to avoid potential conflicts
const handlePrevRow = () => {
  if (props.editIndex > 0) {
    emit('navigate-row', props.editIndex - 1);
  }
};

const handleNextRow = () => {
  if (props.editIndex < props.totalRows - 1) {
    emit('navigate-row', props.editIndex + 1);
  }
};

// Check if user can edit items
const canEditItem = computed(() => {
  if (props.isDraft) return props.canUpdateDraft;
  return props.canUpdateSubmitted;
});

// Check if user can delete items
const canDeleteItem = computed(() => {
  return props.canDeleteInvoice && canDeleteRow.value;
});

// Check if the current row can be deleted
const canDeleteRow = computed(() => {
  return props.isDraft && props.canUpdateDraft;
});
const showItemRemark = computed(() => {
  return $permissions?.hasPermission('show_item_remark') || false;
});
// Initialize local item from props
onMounted(() => {
  Object.keys(props.itemData).forEach(key => {
    if (key in item) {
      item[key] = props.itemData[key];
    }
  });
});

// Watch for changes in props.itemData to update local item
watch(() => props.itemData, (newValue) => {
  Object.keys(newValue).forEach(key => {
    if (key in item) {
      item[key] = newValue[key];
    }
  });
}, { deep: true });

// Calculated properties
const qtyInput = computed({
  get() {
    return item.qty === 0 && !item.qtyEditing ? '' : item.qty.toString();
  },
  set(value) {
    if (!canEditItem.value) return;
    
    item.qtyEditing = true;
    
    // If the field is being cleared (empty or just a decimal point), allow it
    if (value === '' || value === '.' || value === '،' || value === '٫') {
      item.qty = 0;
      calculateAmount();
      return;
    }
    
    // First replace all Arabic numerals with Western numerals
    let westernValue = value.replace(/[٠١٢٣٤٥٦٧٨٩]/g, (d) => {
      return String.fromCharCode(d.charCodeAt(0) - 1632 + 48);
    });
    
    // Replace Arabic decimal separators with Western decimal point
    westernValue = westernValue.replace(/[،٫]/g, '.');
    
    // In case a user enters mixed characters, ensure only digits and decimal points remain
    westernValue = westernValue.replace(/[^\d.]/g, '');
    
    // Handle multiple decimal points (keep only the first one)
    const parts = westernValue.split('.');
    if (parts.length > 2) {
      westernValue = parts[0] + '.' + parts.slice(1).join('');
    }
    
    // Only update if it's a valid number or an empty string (for deletion)
    if (westernValue === '') {
      item.qty = 0;
    } else {
      const numValue = parseFloat(westernValue);
      if (!isNaN(numValue)) {
        item.qty = numValue;
      }
    }
    
    calculateAmount();
  }
});

const rateInput = computed({
  get() {
    return item.rate === 0 && !item.rateEditing ? '' : item.rate.toString();
  },
  set(value) {
    if (!canEditItem.value) return;
    
    item.rateEditing = true;
    
    // If the field is being cleared (empty or just a decimal point), allow it
    if (value === '' || value === '.' || value === '،' || value === '٫') {
      item.rate = 0;
      calculateAmount();
      return;
    }
    
    // First replace all Arabic numerals with Western numerals
    let westernValue = value.replace(/[٠١٢٣٤٥٦٧٨٩]/g, (d) => {
      return String.fromCharCode(d.charCodeAt(0) - 1632 + 48);
    });
    
    // Replace Arabic decimal separators with Western decimal point
    westernValue = westernValue.replace(/[،٫]/g, '.');
    
    // In case a user enters mixed characters, ensure only digits and decimal points remain
    westernValue = westernValue.replace(/[^\d.]/g, '');
    
    // Handle multiple decimal points (keep only the first one)
    const parts = westernValue.split('.');
    if (parts.length > 2) {
      westernValue = parts[0] + '.' + parts.slice(1).join('');
    }
    
    // Only update if it's a valid number or an empty string (for deletion)
    if (westernValue === '') {
      item.rate = 0;
    } else {
      const numValue = parseFloat(westernValue);
      if (!isNaN(numValue)) {
        item.rate = numValue;
      }
    }
    
    calculateAmount();
  }
});

// Calculate amount when qty or rate changes
const calculateAmount = () => {
  // Calculate raw amount
  const rawAmount = (item.qty || 0) * (item.rate || 0);
  
  // Format to 2 decimal places using toFixed and convert back to number
  item.amount = parseFloat(rawAmount.toFixed(2));
};

// Watch for changes to qty or rate to update amount
watch(
  () => [item.qty, item.rate],
  () => {
    calculateAmount();
  },
  { deep: true }
);

// Methods
const searchItem = (event) => {
  if (!canEditItem.value) return;
  
  const query = event.query.toLowerCase();
  itemSuggestions.value = props.allItems.filter((i) =>
    i.label.toLowerCase().includes(query)
  );
};

const searchCustomer = (event) => {
  if (!canEditItem.value) return;
  
  const query = event.query?.toLowerCase() || "";
  customerSuggestions.value = !query
    ? props.allCustomers.slice(0, 5)
    : props.allCustomers.filter((c) => c.label.toLowerCase().includes(query));
};

const clearCustomer = () => {
  if (!canEditItem.value) return;
  
  item.customer = "";
  emit('clear-customer');
};

const saveItem = () => {
  if (!canEditItem.value) return;
  
  const itemData = {
    item: item.item,
    qty: item.qty,
    rate: item.rate,
    amount: item.amount,
    customer: item.customer,
    qtyEditing: item.qtyEditing,
    rateEditing: item.rateEditing,
    remark: item.remark, // ADD THIS
  };
  emit('save-item', itemData);
};

const handleDelete = () => {
  if (!canDeleteItem.value) return;
  
  confirm.require({
    message: t('confirmDeleteItem'),
    header: t('confirmDelete'),
    icon: "pi pi-exclamation-triangle",
    acceptClass: "p-button-danger",
    acceptLabel: t('yesDelete'),
    rejectLabel: t('cancel'),
    accept: () => {
      emit('delete-item', props.editIndex);
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

const clearItem = () => {
  if (!canEditItem.value) return;
  
  item.item = "";
  item.qty = "";
  item.rate = "";
  item.amount = null;
  item.remark = ""; // ADD THIS
  item.qtyEditing = false;
  item.rateEditing = false;
  emit('clear-item');
};
</script>

<style scoped>
.validationErrors {
  font-size: 11px;
  color: red;
}

:deep(.p-float-label) {
  display: block;
  width: 100%;
  margin-bottom: 1.5rem;
}

:deep(.p-inputtext),
:deep(.p-autocomplete),
:deep(.p-autocomplete-input),
:deep(.p-autocomplete-panel),
:deep(.p-datepicker),
:deep(.p-inputwrapper),
:deep(.p-element),
:deep(.p-inputtext-sm) {
  width: 100% !important;
  max-width: 500px !important;
  display: block;
  font-size: 0.75rem !important;
}

:deep(.p-autocomplete),
:deep(.p-inputnumber) {
  max-width: 500px !important;
  display: flex;
  width: 100% !important;
  margin-bottom: 10px !important;
  margin-top: 10px !important;
  font-size: 0.75rem !important;
}

/* Additional styles for dropdown items and label text */
:deep(.p-autocomplete-item) {
  font-size: 0.75rem !important;
  padding: 0.3rem 0.5rem !important;
}

:deep(.p-float-label label) {
  font-size: 0.75rem !important;
}

/* Reduce padding in autocomplete input */
:deep(.p-autocomplete .p-autocomplete-input) {
  padding: 0.3rem 0.5rem !important;
}

/* Make dropdown panel more compact */
:deep(.p-autocomplete-panel .p-autocomplete-items) {
  padding: 0.2rem !important;
}

/* Make dialog header smaller */
:deep(.p-dialog-header) {
  padding: 0.75rem !important;
}

:deep(.p-dialog-header-text) {
  font-size: 1rem !important;
}

/* Make dialog content more compact */
:deep(.p-dialog-content) {
  padding: 0.75rem !important;
}

/* Make buttons smaller */
:deep(.p-button) {
  font-size: 0.75rem !important;
  padding: 0.4rem 0.8rem !important;
}

/* Navigation button styles */
:deep(.p-button-sm) {
  font-size: 0.75rem !important;
  padding: 0.25rem !important;
}

/* Reduce vertical spacing between elements */
:deep(.p-float-label) {
  margin-bottom: 1rem !important;
}

/* Reduce the gap between grid items */
.gap-y-4 {
  row-gap: 0.75rem !important;
}
</style>