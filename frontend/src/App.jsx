import { useCallback, useEffect, useState } from 'react'
import { createTrip, listTrips } from './api.js'
import TripCard from './components/TripCard.jsx'
import TripForm from './components/TripForm.jsx'

function App() {
  const [trips, setTrips] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [formOpen, setFormOpen] = useState(false)

  const loadTrips = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      setTrips(await listTrips())
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Brak polaczenia z API')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadTrips()
  }, [loadTrips])

  /** Po zapisie zamykamy formularz i pobieramy liste jeszcze raz z backendu. */
  async function handleCreate(payload) {
    await createTrip(payload)
    setFormOpen(false)
    await loadTrips()
  }

  return (
    <>
      <header className="topbar">
        <span className="brand">Travel Expenses Tracker</span>
        <button type="button" onClick={() => setFormOpen((open) => !open)}>
          {formOpen ? 'Zamknij' : '+ Nowa podroz'}
        </button>
      </header>

      <main>
        {formOpen && (
          <TripForm onSubmit={handleCreate} onCancel={() => setFormOpen(false)} />
        )}

        {loading && <p className="muted">Wczytywanie...</p>}
        {error && <p className="error">{error}</p>}

        {!loading && !error && trips.length === 0 && (
          <p className="muted">Brak podrozy. Dodaj pierwsza.</p>
        )}

        {trips.length > 0 && (
          <ul className="list">
            {trips.map((trip) => (
              <TripCard key={trip.id} trip={trip} />
            ))}
          </ul>
        )}
      </main>
    </>
  )
}

export default App
