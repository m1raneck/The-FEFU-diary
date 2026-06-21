import { apiGet } from './api'

export async function getSchedule() {
  return apiGet('/api/schedule')
}
