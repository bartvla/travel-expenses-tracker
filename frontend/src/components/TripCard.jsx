/** Jedna podroz na liscie. Klikniecie otwiera jej wydatki. */
function TripCard({ trip, onSelect }) {
  const dates = trip.end_date
    ? `${trip.start_date} - ${trip.end_date}`
    : `od ${trip.start_date}`

  return (
    <li
      className="card"
      onClick={() => onSelect(trip)}
      style={{ cursor: 'pointer' }}
    >
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
