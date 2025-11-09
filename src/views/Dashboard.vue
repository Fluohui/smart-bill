<template>
  <a-row :gutter="16">
    <a-col :span="8">
      <a-card title="本月支出">
        <div style="font-size:24px;color:#ff4d4f">￥ {{ monthTotal }}</div>
      </a-card>
    </a-col>
    <a-col :span="16">
      <a-card title="分类占比">
        <div ref="pie" style="height:260px"></div>
      </a-card>
    </a-col>
  </a-row>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import http from '@/api/http'

const monthTotal = ref(0)
const pie = ref(null)
let chart

async function loadData() {
  const { data } = await http.get('/bill')
  monthTotal.value = data.monthTotal
  // 饼图数据
  const catMap = {}
  data.list.forEach(b => {
    catMap[b.category] = (catMap[b.category] || 0) + b.amount
  })
  const pieData = Object.keys(catMap).map(k => ({ name: k, value: catMap[k] }))
  chart.setOption({
    tooltip: { show: true },
    series: [{
      type: 'pie',
      radius: '60%',
      data: pieData
    }]
  })
}

onMounted(() => {
  chart = echarts.init(pie.value)
  loadData()
})
</script>