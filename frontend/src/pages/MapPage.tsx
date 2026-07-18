import { useEffect, useMemo, useState } from 'react'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import L from 'leaflet'
import { Link } from 'react-router-dom'
import { api, formatCapRate, formatCurrency } from '../api'
import type { Area, PropertyDetail, PropertyListItem } from '../types'

// Fix default marker icons under bundlers
const markerIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

type MappedProperty = PropertyListItem & { latitude: number; longitude: number }

export default function MapPage() {
  const [areas, setAreas] = useState<Area[]>([])
  const [areaId, setAreaId] = useState<number | undefined>(undefined)
  const [properties, setProperties] = useState<MappedProperty[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.listAreas().then(setAreas).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    api
      .listProperties({ area_id: areaId, limit: 200 })
      .then(async (res) => {
        // The list endpoint doesn't include coordinates; fetch details for mapped pins.
        const detailed = await Promise.all(
          res.items.slice(0, 100).map((p) => api.getProperty(p.id).catch(() => null)),
        )
        const mapped: MappedProperty[] = []
        detailed.forEach((d: PropertyDetail | null, i) => {
          if (d && d.latitude != null && d.longitude != null) {
            mapped.push({ ...res.items[i], latitude: d.latitude, longitude: d.longitude })
          }
        })
        setProperties(mapped)
      })
      .finally(() => setLoading(false))
  }, [areaId])

  const center = useMemo<[number, number]>(() => {
    if (areaId) {
      const area = areas.find((a) => a.id === areaId)
      if (area) return [area.center_latitude, area.center_longitude]
    }
    if (properties.length > 0) return [properties[0].latitude, properties[0].longitude]
    return [39.5, -84.5] // roughly centered on tracked markets
  }, [areaId, areas, properties])

  return (
    <div>
      <div className="filters">
        <label>
          Area
          <select
            value={areaId ?? ''}
            onChange={(e) => setAreaId(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">All areas</option>
            {areas.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </label>
        {loading && <span style={{ color: '#64748b' }}>Loading pins…</span>}
        <span style={{ color: '#64748b' }}>{properties.length} properties with coordinates</span>
      </div>

      <div className="map-container">
        <MapContainer center={center} zoom={areaId ? 11 : 5} style={{ height: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {properties.map((p) => (
            <Marker key={p.id} position={[p.latitude, p.longitude]} icon={markerIcon}>
              <Popup>
                <strong>{p.address}</strong>
                <br />
                {formatCurrency(p.selling_price)} · {formatCapRate(p.calculated_cap_rate)} cap
                <br />
                <Link to={`/properties/${p.id}`}>View details</Link>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  )
}
