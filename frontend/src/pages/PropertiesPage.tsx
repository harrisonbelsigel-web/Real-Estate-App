import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, formatCapRate, formatCurrency } from '../api'
import type { Area, PropertyFilters, PropertyListResponse } from '../types'

const PAGE_SIZE = 25

export default function PropertiesPage() {
  const navigate = useNavigate()
  const [areas, setAreas] = useState<Area[]>([])
  const [data, setData] = useState<PropertyListResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(0)
  const [filters, setFilters] = useState<PropertyFilters>({
    min_cap_rate: 6,
    sort_by: 'cap_rate',
    order: 'desc',
  })

  useEffect(() => {
    api.listAreas().then(setAreas).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    api
      .listProperties({ ...filters, skip: page * PAGE_SIZE, limit: PAGE_SIZE })
      .then(setData)
      .catch((e) => setError(e?.message ?? 'Failed to load properties'))
      .finally(() => setLoading(false))
  }, [filters, page])

  const update = (patch: Partial<PropertyFilters>) => {
    setPage(0)
    setFilters((f) => ({ ...f, ...patch }))
  }

  const toggleSort = (col: 'cap_rate' | 'price' | 'rent') => {
    if (filters.sort_by === col) {
      update({ order: filters.order === 'desc' ? 'asc' : 'desc' })
    } else {
      update({ sort_by: col, order: 'desc' })
    }
  }

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0

  return (
    <div>
      <div className="filters">
        <label>
          Area
          <select
            value={filters.area_id ?? ''}
            onChange={(e) =>
              update({ area_id: e.target.value ? Number(e.target.value) : undefined })
            }
          >
            <option value="">All areas</option>
            {areas.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Min cap rate %
          <input
            type="number"
            step="0.5"
            value={filters.min_cap_rate ?? 6}
            onChange={(e) => update({ min_cap_rate: Number(e.target.value) })}
          />
        </label>
        <label>
          Min price
          <input
            type="number"
            placeholder="Any"
            value={filters.min_price ?? ''}
            onChange={(e) =>
              update({ min_price: e.target.value ? Number(e.target.value) : undefined })
            }
          />
        </label>
        <label>
          Max price
          <input
            type="number"
            placeholder="Any"
            value={filters.max_price ?? ''}
            onChange={(e) =>
              update({ max_price: e.target.value ? Number(e.target.value) : undefined })
            }
          />
        </label>
        <label>
          Beds
          <input
            type="number"
            placeholder="Any"
            value={filters.bedrooms ?? ''}
            onChange={(e) =>
              update({ bedrooms: e.target.value ? Number(e.target.value) : undefined })
            }
          />
        </label>
        <label>
          Above area median
          <select
            value={filters.meets_area_threshold ? 'yes' : 'no'}
            onChange={(e) => update({ meets_area_threshold: e.target.value === 'yes' })}
          >
            <option value="no">All (≥ 6%)</option>
            <option value="yes">Only above median</option>
          </select>
        </label>
      </div>

      {error && <div className="empty-state">⚠️ {error}</div>}
      {loading && <div className="empty-state">Loading…</div>}

      {!loading && data && data.items.length === 0 && (
        <div className="empty-state">
          No properties found. Run a scrape from the Admin page to collect listings.
        </div>
      )}

      {!loading && data && data.items.length > 0 && (
        <>
          <table className="property-table">
            <thead>
              <tr>
                <th>Address</th>
                <th>City</th>
                <th onClick={() => toggleSort('price')}>
                  Price {filters.sort_by === 'price' ? (filters.order === 'desc' ? '▼' : '▲') : ''}
                </th>
                <th>Beds</th>
                <th>Baths</th>
                <th onClick={() => toggleSort('rent')}>
                  Est. Rent{' '}
                  {filters.sort_by === 'rent' ? (filters.order === 'desc' ? '▼' : '▲') : ''}
                </th>
                <th onClick={() => toggleSort('cap_rate')}>
                  Cap Rate{' '}
                  {filters.sort_by === 'cap_rate' ? (filters.order === 'desc' ? '▼' : '▲') : ''}
                </th>
                <th>Vs. Median</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((p) => (
                <tr key={p.id} onClick={() => navigate(`/properties/${p.id}`)}>
                  <td>{p.address}</td>
                  <td>
                    {p.city}, {p.state}
                  </td>
                  <td>{formatCurrency(p.selling_price)}</td>
                  <td>{p.bedrooms ?? '—'}</td>
                  <td>{p.bathrooms ?? '—'}</td>
                  <td>{formatCurrency(p.rental_estimate)}/mo</td>
                  <td className="cap-rate">{formatCapRate(p.calculated_cap_rate)}</td>
                  <td>
                    {p.meets_area_threshold ? (
                      <span className="badge badge-green">Above median</span>
                    ) : (
                      <span className="badge badge-gray">Below median</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="pagination">
            <button
              className="btn btn-secondary"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </button>
            <span>
              Page {page + 1} of {Math.max(totalPages, 1)} ({data.total} properties)
            </span>
            <button
              className="btn btn-secondary"
              disabled={page + 1 >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}
