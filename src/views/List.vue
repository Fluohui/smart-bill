<template>
  <a-card title="记账">
    <a-space>
      <a-input v-model:value="item" placeholder="事项" />
      <a-input-number v-model:value="amount" :min="0" :precision="2" />
      <a-select v-model:value="category" style="width:120px">
        <a-select-option value="餐饮">餐饮</a-select-option>
        <a-select-option value="交通">交通</a-select-option>
        <a-select-option value="购物">购物</a-select-option>
      </a-select>
      <a-button type="primary" @click="add">保存</a-button>
    </a-space>
  </a-card>

  <a-card style="margin-top:16px" title="最近账单">
    <a-list bordered :data-source="bills">
      <template #renderItem="{ item }">
        <a-list-item>
          <span>{{ item.item }}</span>
          <span style="color:red">￥{{ item.amount }}</span>
          <a-button size="small" danger @click="del(item.id)">删</a-button>
        </a-list-item>
      </template>
    </a-list>
  </a-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/api/http'

const item = ref('')
const amount = ref(0)
const category = ref('餐饮')
const bills = ref([])

async function load() {
  const { data } = await http.get('/bill')
  bills.value = data.list
}
async function add() {
  await http.post('/bill', { item: item.value, amount: amount.value, category: category.value })
  item.value = ''
  amount.value = 0
  load()
}
async function del(id) {
  await http.delete(`/bill/${id}`)
  load()
}

onMounted(load)
</script>