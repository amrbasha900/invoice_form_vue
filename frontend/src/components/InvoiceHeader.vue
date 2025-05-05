<!-- components/InvoiceHeader.vue -->
<template>
  <div>
    <!-- Display Invoice Name -->
    <div class="mb-4">
      <h3 v-if="invoiceName" class="font-semibold text-lg">
        {{ $t('invoiceName') }}: {{ invoiceName }}
      </h3>
    </div>
    
    <!-- Two columns on small+ screens -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
      <!-- Supplier -->
      <div class="w-full">
        <div class="grid grid-cols-12 gap-1">
          <div class="col-span-11">
            <FloatLabel variant="on" class="w-full block">
              <AutoComplete
                v-model="localSupplier"
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
                localSupplier ? 'p-button-danger' : ''
              ]"
              @click="clearSupplier"
              type="button"
              aria-label="Clear supplier"
              :disabled="!localSupplier"
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
              <AutoComplete 
                v-model="localCustomer" 
                inputId="customer" 
                :suggestions="customerSuggestions"
                optionLabel="label" 
                @complete="searchCustomer" 
                :forceSelection="true" 
                :completeOnFocus="true"
                class="w-full" 
              />
              <label for="customer">{{ $t('customer') }}</label>
            </FloatLabel>
          </div>
          <div class="col-span-1 flex items-center justify-center">
            <Button 
              icon="pi pi-trash" 
              :class="[
                'p-button-rounded p-button-text',
                localCustomer ? 'p-button-danger' : ''
              ]" 
              @click="clearMainCustomer" 
              type="button"
              aria-label="Clear customer" 
              :disabled="!localCustomer" 
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import FloatLabel from 'primevue/floatlabel';
import AutoComplete from 'primevue/autocomplete';
import Button from 'primevue/button';

// Props
const props = defineProps({
  supplier: {
    type: [Object, String],
    default: ""
  },
  customer: {
    type: [Object, String],
    default: ""
  },
  invoiceName: {
    type: String,
    default: null
  },
  allSuppliers: {
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
  }
});

// Emits
const emit = defineEmits(['update:supplier', 'update:customer', 'clear-supplier', 'clear-customer']);

// Local reactive data
const supplierSuggestions = ref([]);
const customerSuggestions = ref([]);

// Computed properties for two-way binding
const localSupplier = computed({
  get() {
    return props.supplier;
  },
  set(value) {
    emit('update:supplier', value);
    emit('clear-supplier'); // To mark the form as dirty
  }
});

const localCustomer = computed({
  get() {
    return props.customer;
  },
  set(value) {
    emit('update:customer', value);
    emit('clear-customer'); // To mark the form as dirty
  }
});

// Methods
const searchSupplier = (event) => {
  const query = event.query.toLowerCase();
  supplierSuggestions.value = props.allSuppliers.filter((s) =>
    s.label.toLowerCase().includes(query)
  );
};

const searchCustomer = (event) => {
  const query = event.query?.toLowerCase() || "";
  customerSuggestions.value = !query
    ? props.allCustomers.slice(0, 5)
    : props.allCustomers.filter((c) => c.label.toLowerCase().includes(query));
};

const clearSupplier = () => {
  emit('update:supplier', "");
  emit('clear-supplier');
};

const clearMainCustomer = () => {
  emit('update:customer', "");
  emit('clear-customer');
};
</script>

<style scoped>
.validationErrors {
  font-size: 12px;
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
  font-size: 0.9rem !important; /* Reduced font size from 0.9rem to 0.75rem */
}

:deep(.p-autocomplete),
:deep(.p-inputnumber) {
  max-width: 500px !important;
  display: flex;
  width: 100% !important;
  margin-bottom: 10px !important;
  margin-top: 10px !important;
  font-size: 0.9rem !important; /* Reduced font size from 0.9rem to 0.75rem */
}

/* Additional styles for dropdown items and label text */
:deep(.p-autocomplete-item) {
  font-size: 0.9rem !important; /* Reduce font size of dropdown items */
  padding: 0.3rem 0.5rem !important; /* Reduce padding for dropdown items */
}

:deep(.p-float-label label) {
  font-size: 0.9rem !important; /* Reduce the font size of floating labels */
}

/* Reduce padding in autocomplete input */
:deep(.p-autocomplete .p-autocomplete-input) {
  padding: 0.3rem 0.5rem !important;
}

/* Make dropdown panel more compact */
:deep(.p-autocomplete-panel .p-autocomplete-items) {
  padding: 0.2rem !important;
}
</style>