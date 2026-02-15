import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { orgs, anticrisis } from '../api'

export default function Dashboard() {
  const [organizations, setOrganizations] = useState<{ id: number; name: string }[]>([])
  const [selectedOrgId, setSelectedOrgId] = useState<number | null>(null)
  const [periods, setPeriods] = useState<{ id: number; label: string }[]>([])
  const [crisis, setCrisis] = useState<{ crisis_type_name: string; confidence: number; reasoning: string } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    orgs.list().then(setOrganizations).catch(() => setOrganizations([])).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedOrgId) {
      setPeriods([])
      setCrisis(null)
      return
    }
    anticrisis.periods(selectedOrgId).then((p) => {
      setPeriods(p)
      const last = p[0]
      if (last) {
        anticrisis.crisis(selectedOrgId, last.id).then(setCrisis).catch(() => setCrisis(null))
      } else setCrisis(null)
    }).catch(() => setPeriods([]))
  }, [selectedOrgId])

  if (loading) return <p>Загрузка...</p>

  return (
    <div>
      <h1>Дашборд</h1>
      <div className="card">
        <div className="form-group">
          <label>Организация</label>
          <select
            value={selectedOrgId ?? ''}
            onChange={(e) => setSelectedOrgId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">— Выберите —</option>
            {organizations.map((o) => (
              <option key={o.id} value={o.id}>{o.name}</option>
            ))}
          </select>
        </div>
        {selectedOrgId && (
          <p>
            <Link to={`/orgs/${selectedOrgId}/periods`}>Отчётность и коэффициенты</Link>
            {' · '}
            <Link to={`/orgs/${selectedOrgId}/table`}>Расчётная таблица</Link>
            {' · '}
            <Link to={`/orgs/${selectedOrgId}/plans`}>Планы мероприятий</Link>
          </p>
        )}
      </div>

      {selectedOrgId && periods.length > 0 && (
        <div className="card">
          <h2>Периоды</h2>
          <ul>
            {periods.slice(0, 5).map((p) => (
              <li key={p.id}>
                <Link to={`/orgs/${selectedOrgId}/periods/${p.id}`}>{p.label || `Период ${p.id}`}</Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {crisis && (
        <div className="card">
          <h2>Карта кризиса</h2>
          <p><strong>{crisis.crisis_type_name}</strong> (уверенность: {(crisis.confidence * 100).toFixed(0)}%)</p>
          <p>{crisis.reasoning}</p>
        </div>
      )}

      {organizations.length === 0 && (
        <div className="card">
          <p>Создайте организацию в разделе <Link to="/orgs">Организации</Link> и добавьте период отчётности.</p>
        </div>
      )}
    </div>
  )
}
