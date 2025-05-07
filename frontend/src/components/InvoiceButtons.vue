<!-- components/InvoiceButtons.vue -->
<template>
  <div class="mt-6">
    <!-- <Button 
      v-if="canSave"
      :label="isInvoiceNew ? $t('saveInvoice') : $t('update')" 
      icon="pi pi-save"
      @click="$emit('save')" 
      class="w-full" 
    /> -->

    <Button 
      v-if="!isInvoiceNew && canDelete" 
      :label="$t('deleteInvoice')" 
      icon="pi pi-trash" 
      severity="danger"
      @click="$emit('delete')" 
      class="w-full mt-2" 
    />

    <Button 
      v-if="!isInvoiceNew && canSubmit" 
      :label="$t('submitInvoice')" 
      icon="pi pi-check" 
      severity="success"
      @click="$emit('submit')" 
      class="w-full mt-2" 
    />
  </div>
</template>

<script setup>
import Button from 'primevue/button';

const props = defineProps({
  isInvoiceNew: {
    type: Boolean,
    required: true
  },
  canSave: {
    type: Boolean,
    default: true
  },
  canDelete: {
    type: Boolean,
    default: true
  },
  canSubmit: {
    type: Boolean,
    default: true
  }
});

defineEmits(['save', 'delete', 'submit']);
</script>

<style scoped>
:deep(.p-button) {
  max-width: 500px !important;
  margin: 10px auto;
}
</style>