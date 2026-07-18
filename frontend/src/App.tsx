import { NavLink, Route, Routes } from 'react-router-dom'
import PropertiesPage from './pages/PropertiesPage'
import PropertyDetailPage from './pages/PropertyDetailPage'
import MapPage from './pages/MapPage'
import AdminPage from './pages/AdminPage'

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🏠 Real Estate Investor</h1>
        <nav>
          <NavLink to="/" end>
            Properties
          </NavLink>
          <NavLink to="/map">Map</NavLink>
          <NavLink to="/admin">Admin</NavLink>
        </nav>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<PropertiesPage />} />
          <Route path="/properties/:id" element={<PropertyDetailPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </main>
    </div>
  )
}
