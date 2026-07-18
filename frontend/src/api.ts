import axios from 'axios'
import type {
  Area,
  AreaSummary,
  PropertyDetail,
  PropertyFilters,
  PropertyListResponse,
  ScrapingJob,
} from './types'

const client = axios.create({ baseURL: '/' })

export const api = {
  // Properties
  async listProperties(filters: PropertyFilters = {}): Promise<PropertyListResponse> {
    const { data } = await client.get('/api/properties', { params: filters })
    return data
  },

  async getProperty(id: number): Promise<PropertyDetail> {
    const { data } = await client.get(`/api/properties/${id}`)
    return data
  },

  async getAreaSummary(areaId: number): Promise<AreaSummary> {
    const { data } = await client.get(`/api/properties/area/${areaId}/summary`)
    return data
  },

  // Areas
  async listAreas(): Promise<Area[]> {
    const { data } = await client.get('/api/areas')
    return data
  },

  async createArea(area: {
    name: string
    city: string
    state: string
    center_latitude: number
    center_longitude: number
    radius_miles: number
  }): Promise<Area> {
    const { data } = await client.post('/api/areas', area)
    return data
  },

  async updateArea(id: number, area: Partial<Area>): Promise<Area> {
    const { data } = await client.put(`/api/areas/${id}`, area)
    return data
  },

  async deleteArea(id: number): Promise<void> {
    await client.delete(`/api/areas/${id}`)
  },

  // Scraping
  async triggerScrape(areaId: number): Promise<{ detail: string }> {
    const { data } = await client.post(`/admin/scrape/${areaId}`)
    return data
  },

  async listScrapingJobs(): Promise<ScrapingJob[]> {
    const { data } = await client.get('/admin/scraping-jobs')
    return data
  },
}

export function formatCurrency(value: number | null | undefined): string {
  if (value == null) return '—'
  return value.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  })
}

export function formatCapRate(value: number | null | undefined): string {
  if (value == null) return '—'
  return `${value.toFixed(2)}%`
}
