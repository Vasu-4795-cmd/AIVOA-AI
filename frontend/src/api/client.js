import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
})

axios.post(
    `${import.meta.env.VITE_API_URL}/api/copilot/parse`,
    formData
);

export default api
