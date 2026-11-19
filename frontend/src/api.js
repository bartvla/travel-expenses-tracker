/** Wywolania HTTP do backendu. Ksztalt danych odpowiada schemas.py po stronie API. */

async function request(path, init) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })

  if (!res.ok) {
    throw new Error(await errorMessage(res))
  }

  return res.json()
}

/** FastAPI zwraca detail jako string (HTTPException) albo liste bledow walidacji. */
async function errorMessage(res) {
  try {
    const body = await res.json()
    const detail = body.detail

    if (typeof detail === 'string') {
      return detail
    }

    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg ?? 'Blad walidacji').join(', ')
    }
  } catch {
    // brak ciala odpowiedzi albo nie JSON - zostaje ogolny komunikat
  }

  return `Blad ${res.status}`
}

export function listTrips() {
  return request('/trips')
}

export function createTrip(payload) {
  return request('/trips', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function listExpenses(tripId) {
  return request(`/trips/${tripId}/expenses`)
}

export function createExpense(tripId, payload) {
  return request(`/trips/${tripId}/expenses`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}