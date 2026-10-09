import { useEffect, useState } from 'react'

function App() {
  const [message, setMessage] = useState('Loading...')

  useEffect(() => {
    fetch('/api/message')
      .then((res) => res.json())
      .then((data: { message: string }) => setMessage(data.message))
      .catch(() => setMessage('Failed to reach the backend.'))
  }, [])

  return (
    <main>
      <h1>{message}</h1>
    </main>
  )
}

export default App
