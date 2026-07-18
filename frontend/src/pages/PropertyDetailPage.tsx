import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, formatCapRate, formatCurrency } from '../api'
import type { PropertyDetail } from '../types'

export default function PropertyDetailPage() {
  const { id } = useParams()
  const [property, setProperty] = useState<PropertyDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    api
      .getProperty(Number(id))
      .then(setProperty)
      .catch((e) => setError(e?.message ?? 'Failed to load property'))
  }, [id])

  if (error) return <div className="empty-state">⚠️ {error}</div>
  if (!property) return <div className="empty-state">Loading…</div>

  const a = property.analysis

  return (
    <div>
      <Link to="/">← Back to properties</Link>
      <div className="card" style={{ marginTop: '1rem' }}>
        <h2>
          {property.address}, {property.city}, {property.state} {property.zip_code}
        </h2>
        <p style={{ color: '#64748b', marginBottom: '0.75rem' }}>
          {property.bedrooms ?? '?'} bd · {property.bathrooms ?? '?'} ba ·{' '}
          {property.square_feet ? `${property.square_feet.toLocaleString()} sqft` : '? sqft'} ·{' '}
          {property.property_type.replace('_', ' ')}
        </p>
        <a
          className="listing-link"
          href={property.listing_url}
          target="_blank"
          rel="noopener noreferrer"
        >
          View original listing ↗
        </a>
      </div>

      <div className="card">
        <h2>Investment Metrics</h2>
        <div className="metric-grid">
          <div className="metric">
            <div className="label">Selling Price</div>
            <div className="value">{formatCurrency(property.selling_price)}</div>
          </div>
          <div className="metric">
            <div className="label">Cap Rate</div>
            <div className="value cap-rate">{formatCapRate(a?.calculated_cap_rate)}</div>
          </div>
          <div className="metric">
            <div className="label">Potential Rent</div>
            <div className="value">{formatCurrency(a?.rental_estimate)}/mo</div>
          </div>
          <div className="metric">
            <div className="label">Annual Rental Income</div>
            <div className="value">{formatCurrency(a?.annual_rental_income)}</div>
          </div>
          <div className="metric">
            <div className="label">Property Taxes (est/yr)</div>
            <div className="value">
              {formatCurrency(property.property_taxes ?? a?.property_tax_annual)}
            </div>
          </div>
          <div className="metric">
            <div className="label">Insurance (est/yr)</div>
            <div className="value">{formatCurrency(a?.insurance_estimate)}</div>
          </div>
          <div className="metric">
            <div className="label">Vs. Area Median</div>
            <div className="value">
              {a?.cap_rate_vs_median != null
                ? `${a.cap_rate_vs_median >= 0 ? '+' : ''}${a.cap_rate_vs_median.toFixed(2)} pts`
                : '—'}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Rental Comparables ({property.rental_comparables.length})</h2>
        {property.rental_comparables.length === 0 ? (
          <p style={{ color: '#64748b' }}>No rental comparables recorded.</p>
        ) : (
          <table className="property-table">
            <thead>
              <tr>
                <th>Address</th>
                <th>Distance</th>
                <th>Monthly Rent</th>
                <th>Beds</th>
                <th>Baths</th>
              </tr>
            </thead>
            <tbody>
              {property.rental_comparables.map((c) => (
                <tr key={c.id} style={{ cursor: 'default' }}>
                  <td>{c.comparable_address}</td>
                  <td>{c.distance_miles?.toFixed(1)} mi</td>
                  <td>{formatCurrency(c.monthly_rent)}</td>
                  <td>{c.bedrooms ?? '—'}</td>
                  <td>{c.bathrooms ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
