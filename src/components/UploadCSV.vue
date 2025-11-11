<template>
  <a-upload :before-upload="beforeUpload" accept=".csv">
    <a-button>导入微信/支付宝 CSV</a-button>
  </a-upload>
  <span style="margin-left:8px;color:#666">仅支持 *.csv，自动识别格式</span>
</template>

<script setup>
import http from '@/api/http'
import { message } from 'ant-design-vue'

async function beforeUpload(file) {
  const form = new FormData()
  form.append('file', file)
  try {
    const { data } = await http.post('/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    message.success(`成功导入 ${data.count} 条记录`)
    setTimeout(() => location.reload(), 800) // 简单刷新看结果
  } catch (e) {
    message.error(e.response?.data?.error || '导入失败')
  }
  return false // 手动上传
}
</script>