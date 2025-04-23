<template>
  <div class="invoice-form max-w-2xl mx-auto p-4">
    <form @submit.prevent="saveInvoice">
      <!-- Display Invoice Name -->
      <div class="mb-4">
        <h3 v-if="invoiceName" class="font-semibold text-lg">
          {{ $t('invoiceName') }}: {{ invoiceName }}
        </h3>
      </div>
      <!-- Two columns on small+ screens -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <!-- Supplier -->
        <!-- Supplier field with grid layout and red active trash button -->
<div class="w-full">
  <div class="grid grid-cols-12 gap-1">
    <div class="col-span-11">
      <FloatLabel variant="on" class="w-full block">
        <AutoComplete
          v-model="invoice.supplier"
          inputId="supplier"
          :suggestions="supplierSuggestions"
          optionLabel="label"
          @complete="searchSupplier"
          :forceSelection="true"
          :completeOnFocus="true"
          class="w-full"
        />
        <label for="supplier">{{ $t('supplier') }}</label>
      </FloatLabel>
    </div>
    <div class="col-span-1 flex items-center justify-center">
      <Button 
        icon="pi pi-trash" 
        :class="[
          'p-button-rounded p-button-text',
          invoice.supplier ? 'p-button-danger' : ''
        ]"
        @click="clearSupplier"
        type="button"
        aria-label="Clear supplier"
        :disabled="!invoice.supplier"
      />
    </div>
  </div>
  <span v-if="validationErrors.supplier" class="text-sm text-red-500 validationErrors">
    {{ $t('supplierIsRequired') }}
  </span>
</div>
        <!-- Customer -->
        <div class="w-full">
          <div class="grid grid-cols-12 gap-1">
            <div class="col-span-11">
              <FloatLabel variant="on" class="w-full block">
                <AutoComplete v-model="invoice.customer" inputId="customer" :suggestions="customerSuggestions"
                  optionLabel="label" @complete="searchCustomer" :forceSelection="true" :completeOnFocus="true"
                  class="w-full" />
                <label for="customer">{{ $t('customer') }}</label>
              </FloatLabel>
            </div>
            <div class="col-span-1 flex items-center justify-center">
              <Button icon="pi pi-trash" :class="[
          'p-button-rounded p-button-text',
          invoice.customer ? 'p-button-danger' : ''
        ]" @click="clearMainCustomer" type="button"
                aria-label="Clear customer" :disabled="!invoice.customer" />
            </div>
          </div>
        </div>
      </div>

      <div class="mt-6">
        <DataTable :value="invoice.items" class="w-full mt-6 text-lg" responsiveLayout="scroll" @row-click="onRowClick">
          <Column field="item" :header="$t('item')" />
          <Column field="qty" :header="$t('qty')" />
          <Column field="rate" :header="$t('rate')" />
          <Column field="amount" :header="$t('amount')">
            <template #body="slotProps">
              {{ formatCurrency(slotProps.data.amount) }}
            </template>
          </Column>

          <!-- Customer (custom render) -->
          <Column :header="$t('customer')">
            <template #body="slotProps">
              {{ slotProps.data.customer?.label || slotProps.data.customer }}
            </template>
          </Column>
        </DataTable>
      </div>
      <div class="mt-6">
        <Button :label="$t('addItem')" icon="pi pi-plus" @click="openAddDialog" />
      </div>
      <!-- Submit -->
      <!-- Buttons: Save, Update, Delete, Submit -->
      <div class="mt-6">
        <Button v-if="isInvoiceNew" :label="$t('saveInvoice')" @click="handleSaveInvoice" class="w-full" />
        <Button v-if="!isInvoiceNew" :label="$t('update')" @click="handleSaveInvoice" class="w-full mt-2" />

        <Button v-if="!isInvoiceNew" :label="$t('deleteInvoice')" icon="pi pi-trash" severity="danger"
          @click="deleteInvoice" class="w-full mt-2" />

        <Button v-if="!isInvoiceNew" :label="$t('submitInvoice')" icon="pi pi-check" severity="success"
          @click="submitInvoice" class="w-full mt-2" />
      </div>
    </form>

    <!-- Add Item Dialog -->
    <Dialog :header="$t('addItem')" v-model:visible="showItemDialog" modal :dismissableMask="true" :style="{
        width: '100%',
        maxWidth: '400px',
        position: 'fixed',
        top: '2%',
        left: '50%',
        transform: 'translateX(-50%)',
      }" :breakpoints="{ '960px': '95vw', '640px': '100vw' }">
      <div class="mt-1">
        <FloatLabel variant="on" class="w-full block">
          <AutoComplete v-model="newItem.item" inputId="item" :suggestions="itemSuggestions" optionLabel="label"
            @complete="searchItem" :forceSelection="true" :completeOnFocus="true" class="w-full" />
          <label for="item">{{ $t('itemCode') }}</label>
        </FloatLabel>
        <span v-if="validationErrors.item" class="text-sm text-red-500 validationErrors">
          {{ $t('itemCodeIsRequired') }}
        </span>
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
  />
              <label for="qty">{{ $t('qty') }}</label>
            </FloatLabel>
            <span v-if="validationErrors.qty" class="text-sm text-red-500 validationErrors">
              {{ $t('qtyIsRequired') }}
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
                
              />
              <label for="rate">{{ $t('rate') }}</label>
            </FloatLabel>
            <span v-if="validationErrors.rate" class="text-sm text-red-500 validationErrors">
              {{ $t('rateIsRequired') }}
            </span>
          </div>
          <FloatLabel variant="on" class="w-full">
            <InputText v-model="newItem.amount" inputId="amount" class="w-full" :disabled="true" mode="currency"
              currency="SAR" />
            <label for="amount">{{ $t('totalAmount') }}</label>
          </FloatLabel>
        </div>
        <div class="w-full">
  <div class="grid grid-cols-12 gap-1">
    <div class="col-span-11">
      <FloatLabel variant="on" class="w-full block">
        <AutoComplete
          v-model="newItem.customer"
          inputId="Customer"
          :suggestions="customerSuggestions"
          optionLabel="label"
          @complete="searchCustomer"
          :forceSelection="true"
          :completeOnFocus="true"
          class="w-full"
        />
        <label for="Customer">{{ $t('customer') }}</label>
      </FloatLabel>
    </div>
    <div class="col-span-1 flex items-center justify-center">
      <Button 
        icon="pi pi-trash" 
        :class="[
          'p-button-rounded p-button-text',
          newItem.customer ? 'p-button-danger' : ''
        ]" 
        @click="clearCustomer"
        type="button"
        aria-label="Clear customer"
        :disabled="!newItem.customer"
      />
    </div>
  </div>
  <span v-if="validationErrors.customer" class="text-sm text-red-500 validationErrors">
    {{ $t('customerIsRequired') }}
  </span>
</div>
        <div class="flex flex-wrap items-center justify-center gap-10">
          <Button :label="editIndex !== null ? $t('update') : $t('add')" @click="saveItem" class="w-full my-50px" />
          <div class="h-3"></div>
          <Button v-if="editIndex !== null" :label="$t('delete')" icon="pi pi-trash" severity="danger"
            @click="handleDelete" class="w-full" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, watch , computed} from "vue";
import { useRoute, onBeforeRouteLeave } from "vue-router";
const route = useRoute();
import axios from "axios";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";

const toast = useToast();
const confirm = useConfirm();

// State
const showItemDialog = ref(false);
const editIndex = ref(null);
const isInvoiceNew = ref(true); // Track if the invoice is new
const invoiceName = ref(null);
const invoice = reactive({
  supplier: "",
  customer: "",
  items: [],
});

// Form item
const newItem = reactive({
  item: "",
  qty: null,
  qtyEditing: false,
  rate: null,
  rateEditing: false,
  amount: null,
  customer: "",
});
const isDirty = ref(false);

// Calculate amount when qty or rate changes
const calculateAmount = () => {
  // Calculate raw amount
  const rawAmount = (newItem.qty || 0) * (newItem.rate || 0);
  
  // Format to 2 decimal places using toFixed and convert back to number
  newItem.amount = parseFloat(rawAmount.toFixed(2));
};

// Format currency for display
const formatCurrency = (value) => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "SAR",
  }).format(value);
};

//Handle Arabic Numbers
// Updated rateInput computed property with deletion support
const rateInput = computed({
  get() {
    return newItem.rate === 0 && !newItem.rateEditing ? '' : newItem.rate.toString();
  },
  set(value) {
    newItem.rateEditing = true;
    
    // If the field is being cleared (empty or just a decimal point), allow it
    if (value === '' || value === '.' || value === '،' || value === '٫') {
      newItem.rate = 0;
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
      newItem.rate = 0;
    } else {
      const numValue = parseFloat(westernValue);
      if (!isNaN(numValue)) {
        newItem.rate = numValue;
      }
    }
    
    calculateAmount();
  }
});



const clearSupplier = () => {
  invoice.supplier = "";
  // Mark the form as dirty since we made a change
  isDirty.value = true;
};
const clearCustomer = () => {
  newItem.customer = "";
};

const clearMainCustomer = () => {
  invoice.customer = "";
  // Mark the form as dirty since we made a change
  isDirty.value = true;
};

// Also need to do the same for qty
// Updated qtyInput computed property with comprehensive Arabic handling
// Updated qtyInput computed property with deletion support
const qtyInput = computed({
  get() {
    return newItem.qty === 0 && !newItem.qtyEditing ? '' : newItem.qty.toString();
  },
  set(value) {
    newItem.qtyEditing = true;
    
    // If the field is being cleared (empty or just a decimal point), allow it
    if (value === '' || value === '.' || value === '،' || value === '٫') {
      newItem.qty = 0;
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
      newItem.qty = 0;
    } else {
      const numValue = parseFloat(westernValue);
      if (!isNaN(numValue)) {
        newItem.qty = numValue;
      }
    }
    
    calculateAmount();
  }
});

// Required field keys

const requiredFields = ["item", "qty", "rate", "customer"];
const requiredMainFields = ["supplier"];
const validationErrors = reactive({});

// Suggestions
const allSuppliers = ref([]);
const allCustomers = ref([]);
const allItems = ref([]);
const supplierSuggestions = ref([]);
const customerSuggestions = ref([]);
const itemSuggestions = ref([]);

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

const validateSupplier  = () => {
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
// Watch for changes to qty or rate to update amount
watch(
  () => [newItem.qty, newItem.rate],
  () => {
    calculateAmount();
  },
  { deep: true }
);

// Search methods
const searchSupplier = (event) => {
  const query = event.query.toLowerCase();
  supplierSuggestions.value = allSuppliers.value.filter((s) =>
    s.label.toLowerCase().includes(query)
  );
};

const searchCustomer = (event) => {
  const query = event.query?.toLowerCase() || "";
  customerSuggestions.value = !query
    ? allCustomers.value.slice(0, 5)
    : allCustomers.value.filter((c) => c.label.toLowerCase().includes(query));
};

const searchItem = (event) => {
  const query = event.query.toLowerCase();
  itemSuggestions.value = allItems.value.filter((i) =>
    i.label.toLowerCase().includes(query)
  );
};

// Open add dialog
const openAddDialog = () => {
  resetDialog();
  if (invoice.customer) {
    newItem.customer = invoice.customer;
  }
  showItemDialog.value = true;
};

// Open edit dialog from row
const onRowClick = (event) => {
  const row = event.data;
  editIndex.value = event.index;
  Object.assign(newItem, {
    item: { label: row.item, code: row.item },
    qty: row.qty,
    rate: row.rate,
    customer: row.customer,
    amount: row.amount,
  });
  showItemDialog.value = true;
};

// Save item (add or update)
// Updated saveItem function with auto-save logic
const saveItem = async () => {
  if (!validateDialog()) return;
  
  // Create item data object from form
  const itemData = {
    item: newItem.item.code,
    qty: newItem.qty,
    rate: newItem.rate,
    amount: newItem.qty * newItem.rate,
    customer: newItem.customer,
  };

  // Add or update item in the items array
  if (editIndex.value !== null) {
    invoice.items[editIndex.value] = itemData;
  } else {
    invoice.items.push(itemData);
  }

  // If this is a new invoice that hasn't been saved yet, auto-save it first
  if (isInvoiceNew.value && !invoiceName.value) {
    try {
      // Make sure supplier (required field) is present
      if (!validateSupplier()) {
        toast.add({
          severity: "error",
          summary: "Error",
          detail: "Please select a supplier before adding items",
          life: 3000,
        });
        return;
      }

      // Auto-save the invoice
      await handleSaveInvoice();
      
      toast.add({
        severity: "success",
        summary: "Invoice Created",
        detail: `Invoice ${invoiceName.value} has been created with the item`,
        life: 3000,
      });
    } catch (error) {
      console.error("Failed to auto-save invoice:", error);
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to save the invoice. Please try again.",
        life: 3000,
      });
      return;
    }
  } 
  // If this is an existing invoice, update it
  else if (!isInvoiceNew.value && invoiceName.value) {
    try {
      await handleSaveInvoice();
      
      toast.add({
        severity: editIndex.value !== null ? "success" : "info",
        summary: editIndex.value !== null ? "Item Updated" : "Item Added",
        detail: `Item ${editIndex.value !== null ? "updated" : "added"} to invoice ${invoiceName.value}`,
        life: 3000,
      });
    } catch (error) {
      console.error("Failed to update invoice:", error);
      toast.add({
        severity: "error",
        summary: "Error",
        detail: "Failed to update the invoice. Please try again.",
        life: 3000,
      });
      return;
    }
  }
  // If we're not auto-saving (just working with a new unsaved invoice)
  else {
    toast.add({
      severity: editIndex.value !== null ? "success" : "info",
      summary: editIndex.value !== null ? "Item Updated" : "Item Added",
      detail: `Item ${editIndex.value !== null ? "updated" : "added"} successfully`,
      life: 2000,
    });
  }

  // Close dialog and reset form
  resetDialog();
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

// Delete item
const handleDelete = () => {
  confirm.require({
    message: "Are you sure you want to delete this item?",
    header: "Confirm Delete",
    icon: "pi pi-exclamation-triangle",
    acceptClass: "p-button-danger",
    acceptLabel: "Yes, Delete",
    rejectLabel: "Cancel",
    accept: () => {
      invoice.items.splice(editIndex.value, 1);
      toast.add({
        severity: "success",
        summary: "Deleted",
        detail: "Item removed",
        life: 2000,
      });
      resetDialog();
      isDirty.value = false;
      showItemDialog.value = false;
    },
    reject: () => {
      toast.add({
        severity: "info",
        summary: "Cancelled",
        detail: "Delete cancelled",
        life: 2000,
      });
    },
  });
};

// Save Invoice Logic
const handleSaveInvoice = async () => {
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
    console.log(response);
    invoiceName.value = response.message.invoice_name; // Show the invoice name after save/update
    toast.add({
      severity: "success",
      summary: isInvoiceNew.value ? "Invoice Created" : "Invoice Updated",
      detail: `The invoice has been ${
        isInvoiceNew.value ? "created" : "updated"
      } successfully.`,
      life: 2000,
    });

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
      detail: `$${err} : Failed to save/update invoice.`,
      life: 2000,
    });
    throw new Error(
      error.response?.data?.message || "An unknown error occurred"
    );
  }
};

const deleteInvoice = async () => {
  try {
    confirm.require({
      message: "Are you sure you want to delete this invoice?",
      header: "Confirm Delete",
      icon: "pi pi-exclamation-triangle",
      acceptClass: "p-button-danger",
      acceptLabel: "Yes, Delete",
      rejectLabel: "Cancel",
      accept: async () => {
        // Assuming an API to delete the invoice
        const response = await axios.post(
          "/api/method/invoice_form_vue.api.delete_invoice",
          { invoice_name: invoiceName.value }
        );
        toast.add({
          severity: "success",
          summary: "Invoice Deleted",
          detail: "The invoice has been deleted.",
          life: 2000,
        });
        resetInvoiceForm();
        isDirty.value = false;
      },
    });
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Error",
      detail: "Failed to delete invoice.",
    });
  }
};

const submitInvoice = async () => {
  try {
    // Assuming an API to submit the invoice
    const response = await axios.post(
      "/api/method/invoice_form_vue.api.remove_from_invoice",
      { invoice_name: invoiceName.value }
    );
    toast.add({
      severity: "success",
      summary: "Invoice Submitted",
      detail: "The invoice has been submitted.",
      life: 2000,
    });
    resetInvoiceForm();
    isDirty.value = false;
  } catch (error) {
    toast.add({
      severity: "error",
      summary: "Error",
      detail: "Failed to submit invoice.",
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

watch(
  () => [invoice.supplier, invoice.customer, invoice.items],
  () => {
    isDirty.value = true;
  },
  { deep: true }
);
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

onMounted(async () => {
  try {
    fixDropdownWidth()
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

    supplierSuggestions.value = [...allSuppliers.value];
    customerSuggestions.value = [...allCustomers.value];
    itemSuggestions.value = [...allItems.value];

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
}

/* Force FloatLabel children to full width */
:deep(.p-float-label) {
  display: block;
  width: 100%;
  margin-bottom: 1.5rem;
}

/* ✅ Force AutoComplete & DatePicker input wrappers to be full width */
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
}

/* Ensure PrimeVue input wrappers play nice */
:deep(.p-autocomplete),
:deep(.p-inputnumber) {
  max-width: 500px !important;
  display: flex;
  width: 100% !important;
  margin-bottom: 10px !important;
  margin-top: 10px !important;
}
:deep(.p-datatable) {
   max-width: 500px !important;
}
:deep(.p-button) {
   max-width: 500px !important;
   margin: 10px auto;
}
.validationErrors{
  font-size: 12px;
  color: red;
}

[dir="rtl"] .p-autocomplete-option {
  text-align: right;
}
.p-autocomplete-overlay {
  max-width: 200px !important;
}
</style>