import { useState } from 'react'

/** Formularz nowego wydatku dla wybranej podrozy. */
function ExpenseForm({ currency, defaultDate, onSubmit, onCancel }) {
  const [form, setForm] = useState({
    description: '',
    amount: '',
    spent_on: defaultDate || '',
  })
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
        description: form.description.trim() || null,
        amount: form.amount,
        spent_on: form.spent_on,
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
        Opis wydatku
        <input
          maxLength={255}
          placeholder="np. Bilety lotnicze, nocleg, obiad"
          value={form.description}
          onChange={(event) => update('description', event.target.value)}
        />
      </label>

      <div className="form-row">
        <label>
          Kwota ({currency})
          <input
            required
            type="number"
            min="0.01"
            step="0.01"
            value={form.amount}
            onChange={(event) => update('amount', event.target.value)}
          />
        </label>

        <label>
          Data wydatku
          <input
            required
            type="date"
            value={form.spent_on}
            onChange={(event) => update('spent_on', event.target.value)}
          />
        </label>
      </div>

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

export default ExpenseForm