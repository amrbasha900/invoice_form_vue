<template>
  <div class="invoice-form max-w-2xl mx-auto p-4">
    <form @submit.prevent="saveInvoice">
      <!-- Display Invoice Name -->
      <div class="mb-4">
        <h3 v-if="invoiceName" class="font-semibold text-lg">
          Invoice Name: {{ invoiceName }}
        </h3>
      </div>
      <!-- Two columns on small+ screens -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <!-- Supplier -->
        <div class="w-full">
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
            <label for="supplier">Supplier</label>
          </FloatLabel>
          <span v-if="validationErrors.supplier" class="text-sm text-red-500 validationErrors">
              Supplier is required
            </span>
        </div>

        <!-- Customer -->
        <div class="w-full">
          <FloatLabel variant="on" class="w-full block">
            <AutoComplete
              v-model="invoice.customer"
              inputId="customer"
              :suggestions="customerSuggestions"
              optionLabel="label"
              @complete="searchCustomer"
              :forceSelection="true"
              :completeOnFocus="true"
              class="w-full"
            />
            <label for="customer">Customer</label>
          </FloatLabel>
        </div>
      </div>

      <div class="mt-6">
        <DataTable
          :value="invoice.items"
          class="w-full mt-6 text-lg"
          responsiveLayout="scroll"
          @row-click="onRowClick"
        >
          <Column field="item" header="Item" />
          <Column field="qty" header="Qty" />
          <Column field="rate" header="Rate" />
          <Column field="amount" header="Amount">
            <template #body="slotProps">
              {{ formatCurrency(slotProps.data.amount) }}
            </template>
          </Column>

          <!-- Customer (custom render) -->
          <Column header="Customer">
            <template #body="slotProps">
              {{ slotProps.data.customer?.label || slotProps.data.customer }}
            </template>
          </Column>
        </DataTable>
      </div>
      <div class="mt-6">
        <Button label="Add Item" icon="pi pi-plus" @click="openAddDialog" />
      </div>
      <!-- Submit -->
      <!-- Buttons: Save, Update, Delete, Submit -->
      <div class="mt-6">
        <Button
          v-if="isInvoiceNew"
          label="Save Invoice"
          @click="handleSaveInvoice"
          class="w-full"
        />
        <Button
          v-if="!isInvoiceNew"
          label="Update"
          @click="handleSaveInvoice"
          class="w-full mt-2"
        />

        <Button
          v-if="!isInvoiceNew"
          label="Delete Invoice"
          icon="pi pi-trash"
          severity="danger"
          @click="deleteInvoice"
          class="w-full mt-2"
        />

        <Button
          v-if="!isInvoiceNew"
          label="Submit Invoice"
          icon="pi pi-check"
          severity="success"
          @click="submitInvoice"
          class="w-full mt-2"
        />
      </div>
    </form>

    <!-- Add Item Dialog -->
    <Dialog
      header="Add Item"
      v-model:visible="showItemDialog"
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
      <div class="mt-1">
        <FloatLabel variant="on" class="w-full block">
          <AutoComplete
            v-model="newItem.item"
            inputId="item"
            :suggestions="itemSuggestions"
            optionLabel="label"
            @complete="searchItem"
            :forceSelection="true"
            :completeOnFocus="true"
            class="w-full"
          />
          <label for="item">Item Code</label>
        </FloatLabel>
        <span v-if="validationErrors.item" class="text-sm text-red-500 validationErrors">
          Item Code is required
        </span>
        <div class="grid grid-cols-3 sm:grid-cols-3 gap-x-6 gap-y-4 mb-4">
          <div>
          <FloatLabel variant="on">
            <InputText
              v-model="qtyInput"
              inputId="qty"
              class="w-full"
              inputmode="numeric"
            />
            <label for="qty">Qty</label>
          </FloatLabel>
          <span v-if="validationErrors.qty" class="text-sm text-red-500 validationErrors">
              Qty is required
            </span>
          </div>
          <div>
          <FloatLabel variant="on">
            <InputText
              v-model="rateInput"
              inputId="rate"
              class="w-full"
              inputmode="numeric"
            />
            <label for="rate">Rate</label>
          </FloatLabel>
<span v-if="validationErrors.rate" class="text-sm text-red-500 validationErrors">
              Rate is required
            </span>
          </div>
          <FloatLabel variant="on" class="w-full">
            <InputText
              v-model="newItem.amount"
              inputId="amount"
              class="w-full"
              :disabled="true"
              mode="currency"
              currency="SAR"
            />
            <label for="amount">Total Amount</label>
          </FloatLabel>
        </div>
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
          <label for="item">Customer</label>
        </FloatLabel>
<span v-if="validationErrors.customer" class="text-sm text-red-500 validationErrors">
              Customer is required
            </span>
        <div class="flex flex-wrap items-center justify-center gap-10">
          <Button
            :label="editIndex !== null ? 'Update' : 'Add'"
            @click="saveItem"
            class="w-full my-50px"
          />
          <div class="h-3"></div>
          <Button
            v-if="editIndex !== null"
            label="Delete"
            icon="pi pi-trash"
            severity="danger"
            @click="handleDelete"
            class="w-full"
          />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, watch , computed} from "vue";
import { useRoute } from "vue-router";
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

// Calculate amount when qty or rate changes
const calculateAmount = () => {
  newItem.amount = (newItem.qty || 0) * (newItem.rate || 0);
};

// Format currency for display
const formatCurrency = (value) => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "SAR",
  }).format(value);
};

//Handle Arabic Numbers
const rateInput = computed({
  get() {
    // Return current value as string
    return newItem.rate === 0 && !newItem.rateEditing ? '' : newItem.rate.toString();
  },
  set(value) {
    // Flag to track if we're editing (to handle empty state better)
    newItem.rateEditing = true;
    
    // Handle Arabic numerals
    const westernValue = value.replace(/[٠١٢٣٤٥٦٧٨٩]/g, (d) => {
      return String.fromCharCode(d.charCodeAt(0) - 1632 + 48);
    });
    
    // If empty, set to 0 but keep track that we're editing
    if (westernValue === '') {
      newItem.rate = 0;
      calculateAmount();
      return;
    }
    
    // Only update if it's a valid number
    const numValue = parseFloat(westernValue);
    if (!isNaN(numValue)) {
      newItem.rate = numValue;
      calculateAmount();
    }
  }
});
// Also need to do the same for qty
const qtyInput = computed({
  get() {
    return newItem.qty === 0 && !newItem.qtyEditing ? '' : newItem.qty.toString();
  },
  set(value) {
    newItem.qtyEditing = true;
    
    const westernValue = value.replace(/[٠١٢٣٤٥٦٧٨٩]/g, (d) => {
      return String.fromCharCode(d.charCodeAt(0) - 1632 + 48);
    });
    
    if (westernValue === '') {
      newItem.qty = 0;
      calculateAmount();
      return;
    }
    
    const numValue = parseFloat(westernValue);
    if (!isNaN(numValue)) {
      newItem.qty = numValue;
      calculateAmount();
    }
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
const saveItem = () => {
  if (!validateDialog()) return;
  const itemData = {
    item: newItem.item.code,
    qty: newItem.qty,
    rate: newItem.rate,
    amount: newItem.qty * newItem.rate,
    customer: newItem.customer,
  };

  if (editIndex.value !== null) {
    invoice.items[editIndex.value] = itemData;
  } else {
    invoice.items.push(itemData);
  }

  toast.add({
    severity: editIndex.value !== null ? "success" : "info",
    summary: editIndex.value !== null ? "Item Updated" : "Item Added",
    detail: `Item ${
      editIndex.value !== null ? "updated" : "added"
    } successfully`,
    life: 2000,
  });

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

// Load all options
onMounted(async () => {
  try {
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
</style>