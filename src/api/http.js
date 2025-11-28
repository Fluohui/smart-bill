import axios from 'axios'
export default axios.create({
  baseURL: 'https://smart-bill-backend-production.up.railway.app/api'
})