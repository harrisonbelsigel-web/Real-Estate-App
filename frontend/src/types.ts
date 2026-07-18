export interface PropertyListItem {
  id: number
  address: string
  city: string
  state: string
  selling_price: number
  bedrooms: number | null
  bathrooms: number | null
  calculated_cap_rate: number | null
  rental_estimate: number | null
  meets_minimum_threshold: boolean
  meets_area_threshold: boolean
}

export interface PropertyListResponse {
  total: number
  skip: number
  limit: number
  items: PropertyListItem[]
}

export interface RentalComparable {
  id: number
  comparable_address: string
  comparable_latitude: number
  comparable_longitude: number
  distance_miles: number
  monthly_rent: number
  bedrooms: number | null
  bathrooms: number | null
}

export interface InvestmentAnalysis {
  id: number
  calculated_cap_rate: number | null
  rental_estimate: number | null
  annual_rental_income: number | null
  cap_rate_vs_median: number | null
  insurance_estimate: number | null
  property_tax_annual: number | null
  meets_minimum_threshold: boolean
  meets_area_threshold: boolean
}

export interface PropertyDetail {
  id: number
  address: string
  city: string
  state: string
  zip_code: string
  latitude: number | null
  longitude: number | null
  selling_price: number
  property_taxes: number | null
  bedrooms: number | null
  bathrooms: number | null
  square_feet: number | null
  property_type: string
  listing_url: string
  created_at: string
  last_updated: string
  analysis: InvestmentAnalysis | null
  rental_comparables: RentalComparable[]
}

export interface Area {
  id: number
  name: string
  city: string
  state: string
  center_latitude: number
  center_longitude: number
  radius_miles: number
  median_cap_rate: number | null
  median_rent: number | null
  created_at: string
  last_updated: string
}

export interface AreaSummary {
  area_id: number
  area_name: string
  total_properties: number
  median_cap_rate: number | null
  median_price: number | null
  median_rent: number | null
  average_cap_rate: number | null
}

export interface ScrapingJob {
  id: number
  area_id: number | null
  area_name: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  properties_found: number
  properties_analyzed: number
  error_message: string | null
  started_at: string
  completed_at: string | null
}

export interface PropertyFilters {
  area_id?: number
  min_cap_rate?: number
  max_price?: number
  min_price?: number
  bedrooms?: number
  meets_area_threshold?: boolean
  sort_by?: 'cap_rate' | 'price' | 'rent'
  order?: 'asc' | 'desc'
  skip?: number
  limit?: number
}
