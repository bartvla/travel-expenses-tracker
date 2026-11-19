import { useCallback, useEffect, useState } from 'react'
import { createExpense, listExpenses } from '../api.js'
import ExpenseForm from './ExpenseForm.jsx'

/** Drugi ekran: szczegoly podrozy i lista jej wydatkow. */
function TripDetails({ trip, formOpen, onCloseForm, onBack }) {
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadExpenses = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      setExpenses(await listExpenses(trip.id))
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Brak polaczenia z API')
    } finally {
      setLoading(false)
    }
  }, [trip.id])

  useEffect(() => {
    void loadExpenses()
  }, [loadExpenses])

  async function handleCreate(payload) {
    await createExpense(trip.id, payload)
    onCloseForm()
    await loadExpenses()
  }

  const totalSpent = expenses.reduce(
    (sum, item) => sum + Number(item.amount),
    0
  )

  return (
    <>
      <div style={{ marginBottom: '1.25rem' }}>
        <button type="button" className="button-ghost" onClick={onBack}>
          ← Wszystkie podroze
        </button>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-head">
          <h2>{trip.name}</h2>
          <span className="budget">
            Wydano: {totalSpent.toFixed(2)} {trip.currency}
            {trip.budget !== null && ` / ${trip.budget} ${trip.currency}`}
          </span>
        </div>
        <p className="meta">
          {trip.destination && <span>{trip.destination}</span>}
          <span>
            {trip.end_date
              ? `${trip.start_date} - ${trip.end_date}`
              : `od ${trip.start_date}`}
          </span>
        </p>
        {trip.notes && <p className="notes">{trip.notes}</p>}
      </div>

      {formOpen && (
        <ExpenseForm
          currency={trip.currency}
          defaultDate={trip.start_date}
          onSubmit={handleCreate}
          onCancel={onCloseForm}
        />
      )}

      {loading && <p className="muted">Wczytywanie...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && !error && expenses.length === 0 && (
        <p className="muted">Brak wydatkow dla tej podrozy. Dodaj pierwszy.</p>
      )}

      {expenses.length > 0 && (
        <ul className="list">
          {expenses.map((expense) => (
            <li key={expense.id} className="card">
              <div className="card-head">
                <h2>{expense.description || 'Wydatek'}</h2>
                <span className="budget">
                  {Number(expense.amount).toFixed(2)} {trip.currency}
                </span>
              </div>
              <p className="meta">
                <span>{expense.spent_on}</span>
              </p>
            </li>
          ))}
        </ul>
      )}
    </>
  )
}

export default TripDetails