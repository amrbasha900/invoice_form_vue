// Enhanced CreditLimitDialog.vue with better handling of values

<template>
  <Dialog 
    :visible="visible" 
    @update:visible="$emit('update:visible', $event)"
    :style="{ width: '90vw', maxWidth: '550px' }"
    :modal="true"
    :closable="false"
    :header="title"
    :draggable="false"
    class="credit-limit-dialog"
  >
    <div class="error-content">
      <!-- Customer Details -->
      <div class="customer-info">
        <div class="customer-name">{{ customer }}</div>
        <div v-if="company" class="company-name">{{ company }}</div>
      </div>
      
      <!-- Credit Limit Table -->
      <table class="credit-table">
        <tr>
          <td class="label">Credit Limit:</td>
          <td class="value">{{ creditLimit }}</td>
        </tr>
        <tr>
          <td class="label">Current Balance:</td>
          <td class="value">{{ currentBalance }}</td>
        </tr>
        <tr>
          <td class="label">Draft Invoices:</td>
          <td class="value">{{ draftInvoices }}</td>
        </tr>
        <tr>
          <td class="label">Draft Payments:</td>
          <td class="value">{{ draftPayments }}</td>
        </tr>
        <tr class="highlight-row">
          <td class="label"><strong>Total Current Balance:</strong></td>
          <td class="value"><strong>{{ totalBalance }}</strong></td>
        </tr>
        <tr>
          <td class="label">Current Invoice Amount:</td>
          <td class="value">{{ invoiceAmount }}</td>
        </tr>
        <tr class="warning-row">
          <td class="label"><strong>Total Exposure:</strong></td>
          <td class="value"><strong>{{ totalExposure }}</strong></td>
        </tr>
        <tr class="error-row">
          <td class="label"><strong>Excess Amount:</strong></td>
          <td class="value"><strong>{{ excessAmount }}</strong></td>
        </tr>
      </table>
      
      <!-- Message -->
      <div class="warning-message">
        {{ $t('pleaseAdjustInvoice') || 'Please adjust the invoice amounts to be within the customer\'s credit limit.' }}
      </div>
    </div>
    
    <!-- Footer -->
    <template #footer>
      <Button 
        :label="$t('understand') || 'I Understand'" 
        @click="close" 
        :autofocus="true"
        class="p-button-primary" 
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: 'Credit Limit Exceeded'
  },
  data: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['update:visible', 'close']);

// Extract data properties with defaults
const customer = computed(() => props.data.customer || 'Unknown Customer');
const company = computed(() => props.data.company || '');
const creditLimit = computed(() => props.data.creditLimit || '0.00');
const currentBalance = computed(() => props.data.currentBalance || '0.00');
const draftInvoices = computed(() => props.data.draftInvoices || '0.00');
const draftPayments = computed(() => props.data.draftPayments || '0.00');
const totalBalance = computed(() => props.data.totalBalance || '0.00');
const invoiceAmount = computed(() => props.data.invoiceAmount || '0.00');
const totalExposure = computed(() => props.data.totalExposure || '0.00');
const excessAmount = computed(() => props.data.excessAmount || '0.00');

const close = () => {
  emit('update:visible', false);
  emit('close');
};
</script>

<style scoped>
.credit-limit-dialog {
  font-family: Arial, sans-serif;
}

.error-content {
  padding: 0 1rem;
}

.customer-info {
  margin-bottom: 1.5rem;
  text-align: center;
}

.customer-name {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.company-name {
  font-size: 0.9rem;
  color: #666;
}

.credit-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
}

.credit-table tr {
  border-bottom: 1px solid #e2e8f0;
}

.credit-table tr:last-child {
  border-bottom: none;
}

.credit-table td {
  padding: 8px 12px;
}

.credit-table .label {
  width: 50%;
  font-weight: 500;
  color: #4b5563;
}

.credit-table .value {
  text-align: right;
  font-weight: 500;
}

.highlight-row {
  background-color: #f8fafc;
}

.warning-row {
  background-color: #fff7ed;
}

.error-row {
  background-color: #fef2f2;
  color: #dc2626;
}

.warning-message {
  margin: 1.5rem 0;
  padding: 12px;
  background-color: #fef2f2;
  border-left: 4px solid #dc2626;
  color: #dc2626;
  font-weight: 500;
}
</style>