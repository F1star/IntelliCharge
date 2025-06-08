<template>
  <div class="bill-view">
    <h1>充电详单</h1>
    <BillList />
  </div>
</template>

<script setup>
import BillList from '../components/chargingSystem/BillList.vue'
</script>

<style scoped>
.bill-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}
</style> 