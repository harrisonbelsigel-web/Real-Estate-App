import { FormEvent, useCallback, useEffect, useState } from 'react'
import { api, formatCapRate } from '../api'
import type { Area, ScrapingJob } from '../types'

const emptyForm = {
  name: '',
  city: '',
  state: '',
  center_latitude: '',
  center_longitude: '',
  radius_miles: '5',
}

export default function AdminPage() {
  const [areas, setAreas] = useState<Area[]>([])
  const [jobs, setJobs] = useState<ScrapingJob[]>([])
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const refresh = useCallback(() => {
    api.listAreas().then(setAreas).catch(() => {})
    api.listScrapingJobs().then(setJobs).catch(() => {})
  }, [])

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 15000)
    return () => clearInterval(interval)
  }, [refresh])

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    const payload = {
      name: form.name,
      city: form.city,
      state: form.state.toUpperCase(),
      center_latitude: Number(form.center_latitude),
      center_longitude: Number(form.center_longitude),
      radius_miles: Number(form.radius_miles),
    }
    try {
      if (editingId) {
        await api.updateArea(editingId, payload)
        setMessage(`Updated ${payload.name}`)
      } else {
        await api.createArea(payload)
        setMessage(`Created ${payload.name}`)
      }
      setForm(emptyForm)
      setEditingId(null)
      refresh()
    } catch (err: any) {
      setMessage(err?.response?.data?.detail ?? 'Request failed')
    }
  }

  const startEdit = (area: Area) => {
    setEditingId(area.id)
    setForm({
      name: area.name,
      city: area.city,
      state: area.state,
      center_latitude: String(area.center_latitude),
      center_longitude: String(area.center_longitude),
      radius_miles: String(area.radius_miles),
    })
  }

  const remove = async (area: Area) => {
    if (!confirm(`Delete area "${area.name}"?`)) return
    await api.deleteArea(area.id)
    refresh()
  }

  const scrape = async (area: Area) => {
    try {
      const res = await api.triggerScrape(area.id)
      setMessage(res.detail)
      refresh()
    } catch (err: any) {
      setMessage(err?.response?.data?.detail ?? 'Failed to start scrape')
    }
  }

  return (
    <div>
      {message && (
        <div className="card" style={{ borderColor: '#0ea5e9' }}>
          {message}
        </div>
      )}

      <div className="card">
        <h2>{editingId ? 'Edit Area' : 'Add New Area'}</h2>
        <form className="area-form" onSubmit={submit}>
          <label>
            Name
            <input
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Ithaca, NY"
            />
          </label>
          <label>
            City
            <input
              required
              value={form.city}
              onChange={(e) => setForm({ ...form, city: e.target.value })}
            />
          </label>
          <label>
            State
            <input
              required
              maxLength={2}
              value={form.state}
              onChange={(e) => setForm({ ...form, state: e.target.value })}
              placeholder="NY"
            />
          </label>
          <label>
            Latitude
            <input
              required
              type="number"
              step="any"
              value={form.center_latitude}
              onChange={(e) => setForm({ ...form, center_latitude: e.target.value })}
            />
          </label>
          <label>
            Longitude
            <input
              required
              type="number"
              step="any"
              value={form.center_longitude}
              onChange={(e) => setForm({ ...form, center_longitude: e.target.value })}
            />
          </label>
          <label>
            Radius (miles)
            <input
              required
              type="number"
              step="0.5"
              value={form.radius_miles}
              onChange={(e) => setForm({ ...form, radius_miles: e.target.value })}
            />
          </label>
          <button type="submit" className="btn">
            {editingId ? 'Save Changes' : 'Add Area'}
          </button>
          {editingId && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                setEditingId(null)
                setForm(emptyForm)
              }}
            >
              Cancel
            </button>
          )}
        </form>
      </div>

      <div className="card">
        <h2>Tracked Areas ({areas.length})</h2>
        <table className="property-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>City</th>
              <th>Radius</th>
              <th>Median Cap Rate</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {areas.map((a) => (
              <tr key={a.id} style={{ cursor: 'default' }}>
                <td>{a.name}</td>
                <td>
                  {a.city}, {a.state}
                </td>
                <td>{a.radius_miles} mi</td>
                <td>{formatCapRate(a.median_cap_rate)}</td>
                <td style={{ display: 'flex', gap: '0.4rem' }}>
                  <button className="btn" onClick={() => scrape(a)}>
                    Scrape
                  </button>
                  <button className="btn btn-secondary" onClick={() => startEdit(a)}>
                    Edit
                  </button>
                  <button className="btn btn-danger" onClick={() => remove(a)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Scraping Jobs</h2>
        {jobs.length === 0 ? (
          <p style={{ color: '#64748b' }}>No scraping jobs yet.</p>
        ) : (
          <table className="property-table">
            <thead>
              <tr>
                <th>Area</th>
                <th>Status</th>
                <th>Found</th>
                <th>Qualified (≥6%)</th>
                <th>Started</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id} style={{ cursor: 'default' }}>
                  <td>{j.area_name}</td>
                  <td>
                    <span className={`status-pill status-${j.status}`}>{j.status}</span>
                  </td>
                  <td>{j.properties_found}</td>
                  <td>{j.properties_analyzed}</td>
                  <td>{new Date(j.started_at).toLocaleString()}</td>
                  <td>{j.error_message ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
