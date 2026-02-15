import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { orgs } from '../api'

export default function Organizations() {
  const [list, setList] = useState<{ id: number; name: string }[]>([])
  const [name, setName] = useState('')
  const [error, setError] = useState('')

  const load = () => orgs.list().then(setList).catch(() => setList([]))

  useEffect(() => { load() }, [])

  const create = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await orgs.create(name)
      setName('')
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    }
  }

  return (
    <div>
      <h1>Организации</h1>
      <div className="card">
        <h2>Новая организация</h2>
        <form onSubmit={create}>
          <div className="form-group">
            <label>Название</label>
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          {error && <p style={{ color: '#d32f2f' }}>{error}</p>}
          <button type="submit" className="btn btn-primary">Создать</button>
        </form>
      </div>
      <div className="card">
        <h2>Мои организации</h2>
        {list.length === 0 ? (
          <p>Нет организаций. Создайте первую выше.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {list.map((o) => (
              <li key={o.id} style={{ marginBottom: '0.5rem' }}>
                <Link to={`/orgs/${o.id}/periods`}>{o.name}</Link>
                {' — '}
                <Link to={`/orgs/${o.id}/plans`}>Планы</Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
