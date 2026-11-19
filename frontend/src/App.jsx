import { useCallback, useEffect, useState } from 'react'
import { createTrip, listTrips } from './api.js'
import TripCard from './components/TripCard.jsx'
import TripDetails from './components/TripDetails.jsx'
import TripForm from './components/TripForm.jsx'

function App() {
  const [trips, setTrips] = useState([])
  const [selectedTrip, setSelectedTrip] = useState(null)
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

  function handleSelectTrip(trip) {
    setFormOpen(false)
    setSelectedTrip(trip)
  }

  function handleBackToTrips() {
    setFormOpen(false)
    setSelectedTrip(null)
  }

  return (
    <>
      <header className="topbar">
        <span
          className="brand"
          onClick={handleBackToTrips}
          style={{ cursor: 'pointer' }}
        >
          Travel Expenses Tracker
        </span>
        <button type="button" onClick={() => setFormOpen((open) => !open)}>
          {formOpen
            ? 'Zamknij'
            : selectedTrip
              ? '+ Nowy wydatek'
              : '+ Nowa podroz'}
        </button>
      </header>

      <main>
        {selectedTrip ? (
          <TripDetails
            trip={selectedTrip}
            formOpen={formOpen}
            onCloseForm={() => setFormOpen(false)}
            onBack={handleBackToTrips}
          />
        ) : (
          <>
            {formOpen && (
              <TripForm
                onSubmit={handleCreate}
                onCancel={() => setFormOpen(false)}
              />
            )}

            {loading && <p className="muted">Wczytywanie...</p>}
            {error && <p className="error">{error}</p>}

            {!loading && !error && trips.length === 0 && (
              <p className="muted">Brak podrozy. Dodaj pierwsza.</p>
            )}

            {trips.length > 0 && (
              <ul className="list">
                {trips.map((trip) => (
                  <TripCard
                    key={trip.id}
                    trip={trip}
                    onSelect={handleSelectTrip}
                  />
                ))}
              </ul>
            )}
          </>
        )}
      </main>
    </>
  )
}

export default App
