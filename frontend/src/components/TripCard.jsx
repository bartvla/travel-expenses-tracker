/** Jedna podroz na liscie. Pola opcjonalne pomijamy, gdy sa puste. */
function TripCard({ trip }) {
  const dates = trip.end_date
    ? `${trip.start_date} - ${trip.end_date}`
    : `od ${trip.start_date}`

  return (
    <li className="card">
      <div className="card-head">
        <h2>{trip.name}</h2>
        {trip.budget !== null && (
          <span className="budget">
            {trip.budget} {trip.currency}
          </span>
        )}
      </div>

      <p className="meta">
        {trip.destination && <span>{trip.destination}</span>}
        <span>{dates}</span>
      </p>

      {trip.notes && <p className="notes">{trip.notes}</p>}
    </li>
  )
}

export default TripCard
