import axios from 'axios'
import { getGameAPI } from './endpoints/gameAPI'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})

export const api = getGameAPI(apiClient)
