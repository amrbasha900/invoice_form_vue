<!-- views/InvoiceForm.vue (Permissions Fix) -->
<template>
  <div class="invoice-form max-w-2xl mx-auto p-4">
    <Toast group="compact" position="top-center" class="compact-toast" />
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
<div v-if="showInvoiceRemark" class="mt-4">
  <FloatLabel variant="on" class="w-full">
    <Textarea
      v-model="invoice.invoice_remark"
      inputId="invoice_remark"
      rows="3"
      class="w-full"
      :disabled="isEditingDisabled"
    />
    <label for="invoice_remark">{{ $t('invoiceRemark') || 'Invoice Remark' }}</label>
  </FloatLabel>
</div>
      <!-- Items Table -->
      <ItemsTable
  :items="invoice.items"
  :is-draft="isDraft"
  :can-update-draft="canEditInvoice"
  :can-delete-invoice="canDeleteInvoice"
  @row-click="onRowClick"
  @add-item="openAddDialog"
  @delete-item="handleDeleteItemFromTable"
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
    <!-- Credit Limit Error Dialog -->
<CreditLimitDialog
  :visible="showCreditLimitDialog"
  @update:visible="showCreditLimitDialog = $event"
  :data="creditLimitData"
  @close="onCreditLimitDialogClose"
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
import Toast from "primevue/toast";

// Import components
import InvoiceHeader from "../components/InvoiceHeader.vue";
import ItemsTable from "../components/ItemsTable.vue";
import InvoiceButtons from "../components/InvoiceButtons.vue";
import ItemDialog from "../components/ItemDialog.vue";
import CreditLimitDialog from '../components/CreditLimitDialog.vue';
import { useI18n } from 'vue-i18n';
const showCreditLimitDialog = ref(false);
const creditLimitData = ref({});
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
  invoice_remark: "",
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
  remark: "",
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
const showInvoiceRemark = computed(() => {
  return $permissions?.hasPermission('show_invoice_remark') || false;
});

const showItemRemark = computed(() => {
  return $permissions?.hasPermission('show_item_remark') || false;
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
    remark: rowData.remark || "", // ADD THIS
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

// Compact toast positioned at top to avoid covering the item dialog
const showCompactToast = (options = {}) => {
  toast.add({
    group: "compact",
    life: options.life ?? 2000,
    closable: options.closable ?? false,
    severity: options.severity ?? "info",
    summary: options.summary,
  });
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
    remark: row.remark || "",
    amount: row.amount,
    qtyEditing: true,  // Set to true so existing values display properly
    rateEditing: true  // Set to true so existing values display properly
  });
  showItemDialog.value = true;
};


const onCreditLimitDialogClose = () => {
  toast.add({
    severity: 'info',
    summary: t('actionCancelled') || 'Action Cancelled',
    detail: t('pleaseAdjustInvoice') || 'Please adjust the invoice amounts',
    life: 5000
  });
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
      showCompactToast({
        severity: "success",
        summary: t('deleted'),
      });
    }
    
    // Reset the dialog and close it
    resetDialog();
    isDirty.value = false;
    showItemDialog.value = false;
  } else {
    console.error("Invalid index for deletion:", index);
    showCompactToast({
      severity: "error",
      summary: t('failedToDeleteItem'),
    });
  }
};

// Complete rewrite of the saveItem function to prevent row addition on error

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
    remark: newItem.remark
  };

  // Get the item name for toast messages
  const itemName = newItem.item.label || newItem.item.code;

  // Remember if this was an edit or add operation
  const wasEdit = editIndex.value !== null;
  
  // IMPORTANT: Do NOT modify the invoice.items array yet
  // We'll only do that after the server confirms the save was successful
  
  // Make a copy of the current items array that includes our changes
  let updatedItems = [...invoice.items];
  if (wasEdit) {
    updatedItems[editIndex.value] = itemData;
  } else {
    updatedItems.push(itemData);
  }
  
  // Prepare data for saving
  const invoiceDataToSave = {
    supplier: invoice.supplier,
    customer: invoice.customer,
    invoice_remark: invoice.invoice_remark,
    items: updatedItems, // Use the updated items list for saving
    posting_date: new Date().toISOString().split("T")[0],
    invoice_id: invoiceName.value,
  };

  try {
    // For a new invoice
    if (isInvoiceNew.value && !invoiceName.value) {
      // Make sure supplier (required field) is present
      if (!validateSupplier()) {
        showCompactToast({
          severity: "error",
          summary: t('selectSupplierBeforeAddingItems'),
        });
        return;
      }

      // Save the invoice to the server
      const response = await axios.post(
        "/api/method/invoice_form_vue.api.create_invoice",
        {
          invoice_data: JSON.stringify(invoiceDataToSave),
        }
      );
      
      // Update local state ONLY after successful save
      invoiceName.value = response.data.message.invoice_name;
      isInvoiceNew.value = false;
      invoice.items = updatedItems; // Now update the items array
      
      showCompactToast({
        severity: "success",
        summary: "Done تم",
        life: 500,
      });
      
      // Reset dialog for new items
      if (!wasEdit) {
        resetDialog();
        showItemDialog.value = true; // Keep dialog open for adding more items
      } else {
        showItemDialog.value = true;
      }
    } 
    // For an existing invoice
    else if (!isInvoiceNew.value && invoiceName.value) {
      // Save the invoice to the server
      const response = await axios.post(
        "/api/method/invoice_form_vue.api.create_invoice",
        {
          invoice_data: JSON.stringify(invoiceDataToSave),
        }
      );
      
      // Update local state ONLY after successful save
      invoice.items = updatedItems; // Now update the items array
      
      showCompactToast({
        severity: "success",
        summary: "Done تم",
        life: 2000,
      });
      
      // Reset dialog for new items
      if (!wasEdit) {
        resetDialog();
        showItemDialog.value = true; // Keep dialog open for adding more items
      } else {
        showItemDialog.value = true;
      }
    }
    // For a new unsaved invoice (just working locally)
    else {
      // Update the local items array directly
      invoice.items = updatedItems;
      
      showCompactToast({
        severity: wasEdit ? "success" : "info",
        summary: "Done تم",
        life: 2000,
      });
      
      // Reset dialog for new items
      if (!wasEdit) {
        resetDialog();
        showItemDialog.value = true;
      } else {
        showItemDialog.value = true;
      }
    }

    // Set dirty flag
    isDirty.value = false;
  } catch (error) {
    console.error("Failed to save item:", error);
    
    // Do NOT update the invoice.items array here
    // The original state is maintained because we never modified it on error
    
    // Check if this is a credit limit error
    if (!handleCreditLimitError(error, confirm, toast)) {
      // If not a credit limit error, show generic error
      showCompactToast({
        severity: "error",
        summary: wasEdit ? "Failed to update invoice" : "Failed to save invoice",
      });
    }
    
    // Do not close the dialog on error, let the user try again
  }
};

// Reset form + edit index
const resetDialog = () => {
  newItem.item = "";
  newItem.qty = "";
  newItem.qtyEditing = false;
  newItem.rate = "";
  newItem.rateEditing = false;
  newItem.amount = null;
  newItem.remark = "";
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
  invoice.invoice_remark = "";
  invoice.items = [];
  invoiceName.value = null;
  isInvoiceNew.value = true;
};

// Save Invoice Logic
const handleSaveInvoice = async (customToast = null) => {
  // Check permission
  if (!canEditInvoice.value) return;
  
  if (!validateSupplier()) return;
  
  // Add credit limit pre-validation
  const creditLimitsOk = await validateCustomerCreditLimits();
  if (!creditLimitsOk) return;
  
  try {
    const invoiceData = {
      supplier: invoice.supplier,
      customer: invoice.customer,
      invoice_remark: invoice.invoice_remark,
      items: invoice.items,
      posting_date: new Date().toISOString().split("T")[0],
      invoice_id: invoiceName.value,
    };

    console.log("📝 Invoice remark being sent:", invoiceData.invoice_remark);
    
    let response;
    try {
      response = await axios.post(
        "/api/method/invoice_form_vue.api.create_invoice",
        {
          invoice_data: JSON.stringify(invoiceData),
        }
      );
      
      console.log("📤 API Response received successfully");
      
    } catch (axiosError) {
      console.log("⚠️ Axios error in handleSaveInvoice:", axiosError);
      
      // Check if it's a parsing error on successful update (status 200)
      if (axiosError.response && axiosError.response.status === 200) {
        console.log("✅ Status 200 but parsing failed - assuming success and verifying...");
        
        // If we have an invoice name, verify by reloading
        if (invoiceName.value) {
          try {
            await loadInvoice(invoiceName.value);
            
            isDirty.value = false;
            
            if (!customToast) {
              toast.add({
                summary: t('invoiceUpdated'),
                life: 2000,
              });
            } else {
              toast.add(customToast);
            }
            return; // Exit successfully
            
          } catch (reloadError) {
            console.error("❌ Reload verification failed:", reloadError);
          }
        } else {
          // For new invoices, we can't verify easily, so just assume success
          isInvoiceNew.value = false;
          isDirty.value = false;
          
          toast.add({
            summary: t('invoiceCreated'),
            life: 2000,
          });
          return;
        }
      }
      
      // If not a parsing error, re-throw
      throw axiosError;
    }
    
    // Normal successful response handling
    if (response && response.data && response.data.message) {
      invoiceName.value = response.data.message.invoice_name;
    }
    isInvoiceNew.value = false;
    isDirty.value = false;
    
    if (!customToast) {
      toast.add({
        summary: isInvoiceNew.value ? t('invoiceCreated') : t('invoiceUpdated'),
        life: 2000,
      });
    } else {
      toast.add(customToast);
    }
    
  } catch (error) {
    console.error("❌ Failed to save invoice:", error);
    
    if (!handleCreditLimitError(error, confirm, toast)) {
      toast.add({ 
        severity: "error", 
        summary: t('error'), 
        detail: error.message || t('unknownError'),
        life: 3000 
      });
    }
  }
};

// Optional: Add a utility function to help with debugging
const debugApiResponse = (response, operation) => {
  console.log(`🔍 Debugging ${operation}:`);
  console.log("Response object:", response);
  console.log("Response data:", response?.data);
  console.log("Response status:", response?.status);
  console.log("Response headers:", response?.headers);
  
  if (response?.data) {
    try {
      console.log("Response data as string:", JSON.stringify(response.data));
    } catch (e) {
      console.log("Cannot stringify response data:", e);
    }
  }
};

const validateCustomerCreditLimits = async () => {
  try {
    // Extract unique customers from invoice items
    const customers = [...new Set(invoice.items
      .map(item => typeof item.customer === 'object' ? item.customer.code : item.customer)
      .filter(Boolean)
    )];
    
    if (customers.length === 0) return true;
    
    // Prepare item data for credit check
    const itemsData = invoice.items.map(item => ({
      customer: typeof item.customer === 'object' ? item.customer.code : item.customer,
      total: item.amount || (item.qty * item.rate)
    }));
    
    // Call API to check credit limits
    const response = await axios.post(
      "/api/method/agricultural_marketing.agricultural_marketing.doctype.invoice_form.invoice_form.validate_invoice_multiple_customers",
      {
        doc_json: JSON.stringify({
          company: "Your Company", // Replace with actual company field from your data
          items: itemsData,
          name: invoiceName.value || null
        })
      }
    );
    
    // If validation fails, show credit limit warning dialog
    if (response.data.message && !response.data.message.valid) {
      const violations = response.data.message.violations || [];
      
      if (violations.length > 0) {
        // Create a nicely formatted message showing all credit limit issues
        let message = `<div style="font-family: Arial, sans-serif;">
          <h4 style="color: #d73527; margin-bottom: 15px;">${t('creditLimitWarning')}</h4>`;
        
        violations.forEach((violation, index) => {
          message += `
            <div style="margin-bottom: 10px; border: 1px solid #ffcdd2; padding: 10px; background-color: #fff5f5;">
              <h5 style="color: #d73527; margin: 0 0 10px 0;">${index + 1}. ${violation.customer_name}</h5>
              <div><strong>${t('creditLimit')}:</strong> ${formatCurrency(violation.credit_limit)}</div>
              <div><strong>${t('excessAmount')}:</strong> ${formatCurrency(violation.excess_amount)}</div>
            </div>
          `;
        });
        
        message += `<p>${t('creditLimitExceededQuestion')}</p></div>`;
        
        // Show confirmation dialog
        return new Promise(resolve => {
          confirm.require({
            message: message,
            header: t('creditLimitExceeded'),
            icon: 'pi pi-exclamation-triangle',
            acceptClass: 'p-button-danger',
            acceptLabel: t('proceedAnyway'),
            rejectLabel: t('cancel'),
            accept: () => {
              // User wants to proceed despite credit limit warnings
              toast.add({
                severity: 'warn',
                summary: t('proceedingWithWarnings'),
                life: 3000
              });
              resolve(true);
            },
            reject: () => {
              // User chooses to adjust the invoice
              toast.add({
                severity: 'info',
                summary: t('actionCancelled'),
                detail: t('pleaseAdjustInvoice'),
                life: 3000
              });
              resolve(false);
            }
          });
        });
      }
    }
    
    // No violations found
    return true;
  } catch (error) {
    console.error('Error checking credit limits:', error);
    // If the validation check itself fails, proceed with save
    // The server will still perform the final validation
    return true;
  }
};
const formatCurrency = (value) => {
  if (value == null) return '0.00';
  
  // If value is already a string (like "31,000.00"), return it as is
  if (typeof value === 'string') {
    // Check if it's a properly formatted currency string
    if (/^[\d,]+\.\d{2}$/.test(value) || /^[\d\.]+$/.test(value)) {
      return value;
    }
    
    // Try to convert it to a number first
    const parsedValue = parseFloat(value.replace(/,/g, ''));
    if (isNaN(parsedValue)) {
      return value; // Return original string if we can't parse it
    }
    value = parsedValue;
  }
  
  // Format the number
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const saveInvoice = async (invoiceData) => {
  try {
    if (!validateSupplier()) return;
    
    // No need to store original state as we're not modifying it until after success
    
    // Send invoice data to the backend
    const response = await axios.post(
      "/api/method/invoice_form_vue.api.create_invoice",
      {
        invoice_data: JSON.stringify(invoiceData),
      }
    );

    // Return response with invoice name and supplier info for display
    return response.data;
  } catch (error) {
    console.error("API error:", error);
    
    // Rethrow the error for the calling function to handle
    throw error;
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

// Add this new function
const handleDeleteItemFromTable = async (index) => {
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
          detail: t('itemDeletedFromInvoice', { itemName, invoiceName: invoiceName.value }),
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
        
        // Rollback: re-add the item if save failed
        invoice.items.splice(index, 0, itemToRemove);
      }
    } else {
      // Just show a success message if this is a new unsaved invoice
      toast.add({
        severity: "success",
        summary: t('deleted'),
        detail: t('itemRemoved', { itemName }),
        life: 2000,
      });
    }
    
    isDirty.value = false;
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
    invoice.invoice_remark = invoiceData.invoice_remark
    invoice.items = (invoiceData.items || []).map((item) => ({
      item: item.item_code,
      qty: item.qty,
      rate: item.price,
      amount: item.total,
        remark: item.remark || "", // ADD THIS

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



// Improved handleCreditLimitError function with better debugging and fallback values

const handleCreditLimitError = (error, confirmInstance, toast) => {
  // Check if we have a response with data
  if (!error.response?.data) return false;
  
  const errorData = error.response.data;
  let errorMessage = '';
  
  // Extract error message from various possible formats
  if (errorData._server_messages) {
    try {
      const messages = JSON.parse(errorData._server_messages);
      errorMessage = messages[0] || '';
    } catch (e) {
      errorMessage = errorData._server_messages;
    }
  } else if (errorData.message) {
    errorMessage = errorData.message;
  } else if (errorData._error_message) {
    errorMessage = errorData._error_message;
  }
  
  console.log('Credit limit error raw message:', errorMessage);
  
  // Check if this is a credit limit error
  const isCreditLimitError = typeof errorMessage === 'string' && (
    errorMessage.includes('Credit Limit Exceeded') || 
    errorMessage.includes('Multiple Credit Limits Exceeded') ||
    errorMessage.includes('credit limit') ||
    errorMessage.includes('Excess Amount') ||
    errorMessage.includes('Total Exposure')
  );
  
  if (isCreditLimitError) {
    try {
      // Extract customer data directly from invoice
      const customerName = typeof invoice.customer === 'object' 
        ? invoice.customer.label 
        : invoice.customer;
      
      // Calculate total invoice amount
      const invoiceAmount = invoice.items.reduce((sum, item) => {
        return sum + (item.amount || (item.qty * item.rate));
      }, 0);
      
      // Get values directly from the error message using more flexible regex
      const extractValue = (pattern) => {
        const match = errorMessage.match(pattern);
        return match ? match[1].trim() : null;
      };
      
      // Try different patterns to match the data
      const creditLimit = 
        extractValue(/Credit Limit:<\/strong><\/td>\s*<td[^>]*>([^<]+)<\/td>/) ||
        extractValue(/Credit Limit:.*?(\d[\d,\.]+)/) ||
        "0.00";
        
      const currentBalance = 
        extractValue(/Current Balance[^:]*:<\/strong><\/td>\s*<td[^>]*>([^<]+)<\/td>/) ||
        extractValue(/Current Balance[^:]*:.*?(\d[\d,\.]+)/) ||
        "0.00";
        
      const draftInvoices = 
        extractValue(/Draft Invoices:<\/strong><\/td>\s*<td[^>]*>([^<]+)<\/td>/) ||
        extractValue(/Draft Invoices:.*?(\d[\d,\.]+)/) ||
        "0.00";
        
      const draftPayments = 
        extractValue(/Draft Payments\/Receipts:<\/strong><\/td>\s*<td[^>]*>([^<]+)<\/td>/) ||
        extractValue(/Draft Payments\/Receipts:.*?(\d[\d,\.]+)/) ||
        "0.00";
        
      const totalBalance = 
        extractValue(/Total Current Balance:<\/strong><\/td>\s*<td[^>]*><strong>([^<]+)<\/strong><\/td>/) ||
        extractValue(/Total Current Balance:.*?<strong>([^<]+)<\/strong>/) ||
        extractValue(/Total Current Balance:.*?(\d[\d,\.]+)/) ||
        "0.00";
        
      const totalExposure = 
        extractValue(/Total Exposure:<\/strong><\/td>\s*<td[^>]*><strong>([^<]+)<\/strong><\/td>/) ||
        extractValue(/Total Exposure:.*?<strong>([^<]+)<\/strong>/) ||
        extractValue(/Total Exposure:.*?(\d[\d,\.]+)/) ||
        "0.00";
        
      const excessAmount = 
        extractValue(/Excess Amount:<\/strong><\/td>\s*<td[^>]*><strong>([^<]+)<\/strong><\/td>/) ||
        extractValue(/Excess Amount:.*?<strong>([^<]+)<\/strong>/) ||
        extractValue(/Excess Amount:.*?(\d[\d,\.]+)/) ||
        "0.00";
      
      console.log('Extracted credit limit data:', {
        customer: customerName,
        creditLimit,
        currentBalance,
        draftInvoices,
        draftPayments,
        totalBalance,
        invoiceAmount: formatCurrency(invoiceAmount),
        totalExposure,
        excessAmount
      });
      
      // Update the data for our custom dialog with better fallbacks
      creditLimitData.value = {
        customer: customerName || 'Unknown Customer',
        company: invoice.supplier?.label || '',
        creditLimit: creditLimit,
        currentBalance: currentBalance,
        draftInvoices: draftInvoices,
        draftPayments: draftPayments,
        totalBalance: totalBalance,
        invoiceAmount: formatCurrency(invoiceAmount),
        totalExposure: totalExposure,
        excessAmount: excessAmount
      };
      
      // Show our custom dialog
      showCreditLimitDialog.value = true;
      
      return true;
    } catch (e) {
      console.error('Error parsing credit limit message:', e);
      
      // Calculate total invoice amount for fallback message
      const invoiceAmount = invoice.items.reduce((sum, item) => {
        return sum + (item.amount || (item.qty * item.rate));
      }, 0);
      
      // Fallback to showing calculated values
      creditLimitData.value = {
        customer: typeof invoice.customer === 'object' ? invoice.customer.label : invoice.customer,
        company: invoice.supplier?.label || '',
        creditLimit: "Unknown",
        currentBalance: "Unknown",
        draftInvoices: "0.00",
        draftPayments: "0.00",
        totalBalance: "Unknown",
        invoiceAmount: formatCurrency(invoiceAmount),
        totalExposure: "Unknown",
        excessAmount: "Unknown"
      };
      
      showCreditLimitDialog.value = true;
      return true;
    }
  }
  
  // Not a credit limit error
  return false;
};


const extractHtmlFromError = (errorMessage) => {
  // Try to parse as JSON if it's a JSON string
  let processedMessage = errorMessage;
  
  try {
    if (typeof errorMessage === 'string' && errorMessage.startsWith('[') && errorMessage.endsWith(']')) {
      const parsed = JSON.parse(errorMessage);
      processedMessage = parsed[0] || errorMessage;
    }
  } catch (e) {
    // Not JSON, continue with original message
  }
  
  // Look for HTML content in the message
  if (typeof processedMessage === 'string') {
    // Check for div with specific styling that indicates credit limit error
    if (processedMessage.includes('<div style="font-family: Arial, sans-serif;">')) {
      return processedMessage;
    }
    
    // Fallback regex to extract any HTML content
    const htmlMatch = processedMessage.match(/<div[^>]*>([\s\S]*?)<\/div>/i);
    if (htmlMatch && htmlMatch[0]) {
      return htmlMatch[0];
    }
  }
  
  return null;
};


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

.compact-toast {
  max-width: 320px;
  pointer-events: none;
}

:deep(.compact-toast .p-toast-message) {
  margin: 0.35rem;
  padding: 0.35rem 0.6rem;
  font-size: 0.85rem;
  line-height: 1.25;
}

:deep(.compact-toast .p-toast-summary) {
  margin: 0;
  font-weight: 600;
  line-height: 1.2;
}
</style>