import { useState } from 'react'

const emptyForm = {
  name: '',
  destination: '',
  start_date: '',
  end_date: '',
  currency: 'PLN',
  budget: '',
  notes: '',
}

/** Formularz nowej podrozy. Puste pola opcjonalne wysylamy jako null. */
function TripForm({ onSubmit, onCancel }) {
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  function update(field, value) {
    setForm((previous) => ({ ...previous, [field]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSaving(true)
    setError(null)

    try {
      await onSubmit({
        name: form.name.trim(),
        destination: form.destination.trim() || null,
        start_date: form.start_date,
        end_date: form.end_date || null,
        currency: form.currency.trim().toUpperCase(),
        budget: form.budget || null,
        notes: form.notes.trim() || null,
      })
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Nie udalo sie zapisac')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <label>
        Nazwa
        <input
          required
          maxLength={120}
          value={form.name}
          onChange={(event) => update('name', event.target.value)}
        />
      </label>

      <label>
        Cel podrozy
        <input
          maxLength={120}
          value={form.destination}
          onChange={(event) => update('destination', event.target.value)}
        />
      </label>

      <div className="form-row">
        <label>
          Data od
          <input
            required
            type="date"
            value={form.start_date}
            onChange={(event) => update('start_date', event.target.value)}
          />
        </label>

        <label>
          Data do
          <input
            type="date"
            value={form.end_date}
            onChange={(event) => update('end_date', event.target.value)}
          />
        </label>
      </div>

      <div className="form-row">
        <label>
          Waluta
          <input
            required
            minLength={3}
            maxLength={3}
            value={form.currency}
            onChange={(event) => update('currency', event.target.value)}
          />
        </label>

        <label>
          Budzet
          <input
            type="number"
            min="0"
            step="0.01"
            value={form.budget}
            onChange={(event) => update('budget', event.target.value)}
          />
        </label>
      </div>

      <label>
        Notatki
        <textarea
          rows={3}
          value={form.notes}
          onChange={(event) => update('notes', event.target.value)}
        />
      </label>

      {error && <p className="error">{error}</p>}

      <div className="form-actions">
        <button type="button" className="button-ghost" onClick={onCancel}>
          Anuluj
        </button>
        <button type="submit" disabled={saving}>
          {saving ? 'Zapisywanie...' : 'Zapisz'}
        </button>
      </div>
    </form>
  )
}

export default TripForm
