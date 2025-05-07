<!-- views/InvoiceForm.vue (Permissions Fix) -->
<template>
  <div class="invoice-form max-w-2xl mx-auto p-4">
    <form @submit.prevent="saveInvoice">
      <!-- Invoice Header with Supplier and Customer -->
      <InvoiceHeader
        v-model:supplier="invoice.supplier"
        v-model:customer="invoice.customer"
        :invoice-name="invoiceName"
        :all-suppliers="allSuppliers"
        :all-customers="allCustomers"
        :validation-errors="validationErrors"
        @clear-supplier="onClearSupplier"
        @clear-customer="onClearCustomer"
        :disabled="isEditingDisabled"
      />

      <!-- Items Table -->
      <ItemsTable
        :items="invoice.items"
        :is-draft="isDraft"
        :can-update-draft="canEditInvoice"
        @row-click="onRowClick"
        @add-item="openAddDialog"
      />

      <!-- Action Buttons -->
      <InvoiceButtons
        :is-invoice-new="!invoiceName"
        @save="handleSaveInvoice"
        @delete="deleteInvoice"
        @submit="submitInvoice"
        :can-save="canEditInvoice"
        :can-delete="canDeleteInvoice"
        :can-submit="canSubmitInvoice"
      />
    </form>

    <!-- Add/Edit Item Dialog with added totalRows prop -->
    <ItemDialog
      :visible="showItemDialog"
      @update:visible="showItemDialog = $event"
      :itemData="newItem"
      :edit-index="editIndex"
      :all-items="allItems"
      :all-customers="allCustomers"
      :validation-errors="validationErrors"
      :totalRows="invoice.items.length" 
      @save-item="saveItem"
      @delete-item="handleDeleteItem"
      @clear-customer="isDirty = false"
      @navigate-row="handleRowNavigation" 
      @clear-item="isDirty = false"
      :is-draft="isDraft"
      :can-update-draft="canEditInvoice"
      :can-update-submitted="canEditInvoice"
      :can-delete-invoice="canDeleteInvoice"
    />
  </div>
</template>

<script setup>
import { inject, computed } from 'vue';
import { reactive, ref, onMounted, watch } from "vue";
import { useRoute, onBeforeRouteLeave } from "vue-router";
import axios from "axios";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";

// Import components
import InvoiceHeader from "../components/InvoiceHeader.vue";
import ItemsTable from "../components/ItemsTable.vue";
import InvoiceButtons from "../components/InvoiceButtons.vue";
import ItemDialog from "../components/ItemDialog.vue";
import { useI18n } from 'vue-i18n';

const $permissions = inject('$permissions');

const { t } = useI18n();
const route = useRoute();
const toast = useToast();
const confirm = useConfirm();

// State
const showItemDialog = ref(false);
const editIndex = ref(null);
const isInvoiceNew = ref(true); // Track if the invoice is new
const isDraft = ref(true);
const invoiceName = ref(null);
const invoiceLocked = ref(false); // Add this to track lock_update status
const invoice = reactive({
  supplier: "",
  customer: "",
  items: [],
});

// Form item
const newItem = reactive({
  item: "",
  qty: "",
  qtyEditing: false,
  rate: "",
  rateEditing: false,
  amount: null,
  customer: "",
});
const isDirty = ref(false);

// Required field keys
const requiredFields = ["item", "qty", "rate", "customer"];
const requiredMainFields = ["supplier"];
const validationErrors = reactive({});

// Suggestions
const allSuppliers = ref([]);
const allCustomers = ref([]);
const allItems = ref([]);

// Computed permissions
const canEditInvoice = computed(() => {
  if (invoiceLocked.value) return false;
  if (isDraft.value) return $permissions?.hasPermission('can_update_draft');
  return $permissions?.hasPermission('can_update_submitted');
});

const canDeleteInvoice = computed(() => {
  if (invoiceLocked.value) return false;
  return isDraft.value && $permissions?.hasPermission('can_delete_invoice');
});

const canSubmitInvoice = computed(() => {
  if (invoiceLocked.value) return false;
  return isDraft.value && $permissions?.hasPermission('can_submit_invoice');
});

const isEditingDisabled = computed(() => {
  return !canEditInvoice.value;
});

// NEW FUNCTION: Handle row navigation from dialog
const handleRowNavigation = (newIndex) => {
  console.log('Navigation requested to row:', newIndex);
  
  // Validate the index is within bounds
  if (newIndex < 0 || newIndex >= invoice.items.length) {
    console.error('Invalid row index:', newIndex);
    return;
  }
  
  // Update the edit index
  editIndex.value = newIndex;
  
  // Get the item data from the invoice items array
  const rowData = invoice.items[newIndex];
  
  // Format the data for the dialog
  Object.assign(newItem, {
    item: rowData.item?.label ? rowData.item : { label: rowData.item, code: rowData.item },
    qty: rowData.qty,
    rate: rowData.rate,
    customer: rowData.customer,
    amount: rowData.amount,
    qtyEditing: true,  // Set to true so existing values display properly
    rateEditing: true  // Set to true so existing values display properly
  });
  
  console.log('Updated dialog data for row:', newIndex, newItem);
};

// Validate form
const validateDialog = () => {
  let isValid = true;
  requiredFields.forEach((field) => {
    if (
      !newItem[field] ||
      (typeof newItem[field] === "number" && newItem[field] <= 0)
    ) {
      validationErrors[field] = true;
      isValid = false;
    } else {
      validationErrors[field] = false;
    }
  });
  return isValid;
};

const validateSupplier = () => {
  let isValid = true;
  requiredMainFields.forEach((field) => {
    if (
      !invoice[field] ||
      (typeof invoice[field] === "number" && invoice[field] <= 0)
    ) {
      validationErrors[field] = true;
      isValid = false;
    } else {
      validationErrors[field] = false;
    }
  });
  return isValid;
};

// Event handlers for header component
const onClearSupplier = () => {
  isDirty.value = false;
};

const onClearCustomer = () => {
  isDirty.value = false;
};

// Open add dialog
const openAddDialog = () => {
  // Check if user has permission to update before opening dialog
  if (!canEditInvoice.value) return;
  
  resetDialog();
  if (invoice.customer) {
    newItem.customer = invoice.customer;
  }
  showItemDialog.value = true;
};

// Open edit dialog from row
const onRowClick = (event) => {
  // Check if user has permission to edit before opening dialog
  if (!canEditInvoice.value) return;
  
  const row = event.data;
  editIndex.value = event.index;
  Object.assign(newItem, {
    item: row.item?.label ? row.item : { label: row.item, code: row.item },
    qty: row.qty,
    rate: row.rate,
    customer: row.customer,
    amount: row.amount,
    qtyEditing: true,  // Set to true so existing values display properly
    rateEditing: true  // Set to true so existing values display properly
  });
  showItemDialog.value = true;
};

// In InvoiceForm.vue script
const handleDeleteItem = async (index) => {
  // Check permission
  if (!canDeleteInvoice.value) return;
  
  if (index !== null && index >= 0 && index < invoice.items.length) {
    // Remove the item from the local array
    const itemToRemove = invoice.items[index];
    invoice.items.splice(index, 1);
    const itemName = itemToRemove.item?.label || itemToRemove.item;
    
    // Update the invoice in the database if it has already been saved
    if (invoiceName.value) {
      try {
        // Call the saveInvoice function with a custom toast message
        await handleSaveInvoice({
          severity: "success",
          summary: t('itemDeleted'),
          life: 2000,
        });
      } catch (error) {
        console.error("Failed to update invoice after deletion:", error);
        toast.add({
          severity: "error",
          summary: t('error'),
          detail: t('failedToUpdateAfterDeletion'),
          life: 3000,
        });
      }
    } else {
      // Just show a success message if this is a new unsaved invoice
      toast.add({
        severity: "success",
        summary: t('deleted'),
        life: 2000,
      });
    }
    
    // Reset the dialog and close it
    resetDialog();
    isDirty.value = false;
    showItemDialog.value = false;
  } else {
    console.error("Invalid index for deletion:", index);
    toast.add({
      severity: "error",
      summary: t('error'),
      detail: t('failedToDeleteItem'),
      life: 2000,
    });
  }
};

// Save item (add or update)
const saveItem = async (itemFormData) => {
  // Check permission
  if (!canEditInvoice.value) return;
  
  // Update newItem with the data from the dialog
  Object.assign(newItem, itemFormData);
  
  if (!validateDialog()) return;
  
  // Create item data object from form
  const itemData = {
    item: newItem.item.code,
    qty: newItem.qty,
    rate: newItem.rate,
    amount: newItem.qty * newItem.rate,
    customer: newItem.customer,
  };

  // Get the item name for toast messages
  const itemName = newItem.item.label || newItem.item.code;

  // Remember if this was an edit or add operation
  const wasEdit = editIndex.value !== null;

  // Add or update item in the items array
  if (wasEdit) {
    invoice.items[editIndex.value] = itemData;
  } else {
    invoice.items.push(itemData);
  }

  // Prepare the toast message with item name
  const hasInvoice = invoiceName.value && invoiceName.value.trim() !== '';

  const toastMessage = {
    severity: wasEdit ? "success" : "info",
    summary: wasEdit ? t('itemUpdated') : t('itemAdded'),
    life: 3000,
  };

  // If this is a new invoice that hasn't been saved yet, auto-save it first
  if (isInvoiceNew.value && !invoiceName.value) {
    try {
      // Make sure supplier (required field) is present
      if (!validateSupplier()) {
        toast.add({
          severity: "error",
          summary: t('error'),
          detail: t('selectSupplierBeforeAddingItems'),
          life: 3000,
        });
        return;
      }

      // Auto-save the invoice with custom toast
      await handleSaveInvoice({
        severity: "success",
        summary: t('invoiceCreated'),
        life: 3000,
      });
      
      // Close dialog only for new items, then reset the form
      if (!wasEdit) {
        resetDialog();
        showItemDialog.value = true;
      }
    } catch (error) {
      console.error("Failed to auto-save invoice:", error);
      toast.add({
        severity: "error",
        summary: t('error'),
        detail: t('failedToSaveInvoice'),
        life: 3000,
      });
      return;
    }
  } 
  // If this is an existing invoice, update it
  else if (!isInvoiceNew.value && invoiceName.value) {
    try {
      await handleSaveInvoice(toastMessage);
      
      // Close dialog only for new items, then reset the form
      if (!wasEdit) {
        resetDialog();
        showItemDialog.value = true;
      }
    } catch (error) {
      console.error("Failed to update invoice:", error);
      toast.add({
        severity: "error",
        summary: t('error'),
        detail: t('failedToUpdateInvoice'),
        life: 3000,
      });
      return;
    }
  }
  // If we're not auto-saving (just working with a new unsaved invoice)
  else {
    toast.add(toastMessage);
    
    // Close dialog only for new items, then reset the form
    if (!wasEdit) {
      resetDialog();
      showItemDialog.value = false;
    }
  }

  // Set dirty flag
  isDirty.value = false;
};

// Reset form + edit index
const resetDialog = () => {
  newItem.item = "";
  newItem.qty = "";
  newItem.qtyEditing = false;
  newItem.rate = "";
  newItem.rateEditing = false;
  newItem.amount = null;
  if (!invoice.customer) {
    newItem.customer = "";
  } else {
    newItem.customer = invoice.customer;
  }

  editIndex.value = null;
};

const resetInvoiceForm = () => {
  invoice.supplier = "";
  invoice.customer = "";
  invoice.items = [];
  invoiceName.value = null;
  isInvoiceNew.value = true;
};

// Save Invoice Logic
const handleSaveInvoice = async (customToast = null) => {
  // Check permission
  if (!canEditInvoice.value) return;
  
  if (!validateSupplier()) return;
  try {
    const invoiceData = {
      supplier: invoice.supplier,
      customer: invoice.customer,
      items: invoice.items,
      posting_date: new Date().toISOString().split("T")[0], // Get current date in YYYY-MM-DD format
      invoice_id: invoiceName.value, // Pass invoice ID for update, otherwise null for new
    };

    const response = await saveInvoice(invoiceData); // Pass the invoice data to saveInvoice method
    invoiceName.value = response.message.invoice_name; // Show the invoice name after save/update
    
    // Only show toast if customToast is not provided
    if (!customToast) {
      toast.add({
        summary: isInvoiceNew.value ? t('invoiceCreated') : t('invoiceUpdated'),
        life: 2000,
      });
    } else {
      // Use the custom toast if provided
      toast.add(customToast);
    }

    isInvoiceNew.value = false; // Mark as existing invoice
    isDirty.value = false;
  } catch (error) {
    // Show error in toast if API returns an error message
    toast.add({ severity: "error", summary: "Error", detail: error.message });
  }
};

const saveInvoice = async (invoiceData) => {
  try {
    if (!validateSupplier()) return;
    // Send invoice data to the backend to create or update
    const response = await axios.post(
      "/api/method/invoice_form_vue.api.create_invoice",
      {
        invoice_data: JSON.stringify(invoiceData),
      }
    );

    // Return response with invoice name and supplier info for display
    return response.data;
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Error",
      life: 2000,
    });
    throw new Error(
      error.response?.data?.message || "An unknown error occurred"
    );
  }
};

const deleteInvoice = async () => {
  // Check permission
  if (!canDeleteInvoice.value) return;
  
  try {
    confirm.require({
      message: t('confirmDeleteInvoice'),
      header: t('confirmDelete'),
      icon: 'pi pi-exclamation-triangle',
      acceptClass: 'p-button-danger',
      acceptLabel: t('yesDelete'),
      rejectLabel: t('cancel'),
      accept: async () => {
        const response = await axios.post(
          '/api/method/invoice_form_vue.api.delete_invoice',
          { invoice_name: invoiceName.value }
        );
        toast.add({
          severity: 'success',
          summary: t('invoiceDeleted'),
          life: 2000,
        });
        resetInvoiceForm();
        isDirty.value = false;
      },
    });
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: t('error'),
      detail: t('deleteInvoiceFailed'),
    });
  }
};

const submitInvoice = async () => {
  // Check permission
  if (!canSubmitInvoice.value) return;
  
  try {
    const response = await axios.post(
      "/api/method/invoice_form_vue.api.remove_from_invoice",
      { invoice_name: invoiceName.value }
    );
    toast.add({
      severity: "success",
      summary: t('invoiceSubmitted'),
      life: 2000,
    });
    resetInvoiceForm();
    isDirty.value = false;
  } catch (error) {
    toast.add({
      severity: "error",
      summary: t('error'),
      detail: t('submitInvoiceFailed'),
    });
  }
};

const loadInvoice = async (invoiceNameParam) => {
  try {
    const res = await axios.get(
      "/api/method/invoice_form_vue.api.get_invoice",
      {
        params: { invoice_name: invoiceNameParam },
      }
    );

    const invoiceData = res.data.message;

    // Set locked status - added this line
    invoiceLocked.value = invoiceData.lock_update === 1;

    invoice.supplier = {
      label: invoiceData.supplier_name,
      code: invoiceData.supplier,
    };

    invoice.customer = {
      label: invoiceData.customer_name,
      code: invoiceData.customer,
    };

    invoice.items = (invoiceData.items || []).map((item) => ({
      item: item.item_code,
      qty: item.qty,
      rate: item.price,
      amount: item.total,
      customer: {
        label: item.customer_name || item.customer,
        code: item.customer,
      },
    }));

    invoiceName.value = invoiceData.name;
    isInvoiceNew.value = false;
    isDraft.value = invoiceData.is_draft === 1;
  } catch (err) {
    console.error("Failed to load invoice:", err);
    toast.add({
      severity: "error",
      summary: "Error",
      detail: "Failed to load invoice data.",
    });
  }
};

function fixDropdownWidth() {
  // Create a style element if it doesn't exist
  let styleEl = document.getElementById('autocomplete-dropdown-fix');
  if (!styleEl) {
    styleEl = document.createElement('style');
    styleEl.id = 'autocomplete-dropdown-fix';
    document.head.appendChild(styleEl);
    
    // Add the CSS rules that directly target the problem
    styleEl.innerHTML = `
      /* Override the min-width that's causing the issue */
      .p-autocomplete-overlay {
        max-width: 100vw !important;
      }
      
      /* Make sure dropdown items wrap text */
      .p-autocomplete-option {
        white-space: normal !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
      }
      
      /* For smaller screens, make even tighter */
      @media screen and (max-width: 640px) {
        .p-autocomplete-overlay {
          max-width: 90vw !important;
          width: auto !important;
        }
      }
    `;
  }
}

// Watch for changes to track dirty state
watch(
  () => [invoice.supplier, invoice.customer, invoice.items],
  () => {
    isDirty.value = false;
  },
  { deep: true }
);

// Navigation guard
onBeforeRouteLeave((to, from, next) => {
  if (isDirty.value) {
    const answer = window.confirm("You have unsaved changes. Do you really want to leave?");
    if (answer) {
      next(); // Allow navigation
    } else {
      next(false); // Cancel navigation
    }
  } else {
    next(); // No changes, safe to leave
  }
});

// Load data when component is mounted
onMounted(async () => {
  try {
    fixDropdownWidth();
    const response = await axios.get(
      "/api/method/invoice_form_vue.api.get_suppliers_and_customers"
    );
    const result = response.data.message || response.data;

    const formatList = (list) =>
      (list || []).map((entry) => ({
        label:
          entry.customer_name ||
          entry.supplier_name ||
          entry.name ||
          entry.item_name,
        code: entry.name || "",
      }));

    allSuppliers.value = formatList(result.suppliers);
    allCustomers.value = formatList(result.customers);
    allItems.value = formatList(result.items);

    if (route.query.invoice_name) {
      await loadInvoice(route.query.invoice_name);
    }
  } catch (error) {
    console.error("Error loading supplier/customer data:", error);
  }
});
</script>

<style scoped>
.invoice-form {
  margin: 50px auto;
  font-size: 0.9rem;
}

/* Force FloatLabel children to full width */
:deep(.p-float-label) {
  display: block;
  width: 100%;
  margin-bottom: 1.5rem;
}

:deep(.p-datatable) {
   max-width: 500px !important;
}

:deep(.p-button) {
   max-width: 500px !important;
   margin: 10px auto;
}

.validationErrors {
  font-size: 11px;
  color: red;
}

[dir="rtl"] .p-autocomplete-option {
  text-align: right;
  font-size: 0.9rem;
}

.p-autocomplete-overlay {
  max-width: 200px !important;
  font-size: 0.9rem;
}
</style>