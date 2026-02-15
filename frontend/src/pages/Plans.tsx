import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { anticrisis } from '../api'

type Plan = {
  id: number
  title: string
  crisis_type_code: string
  items: { id: number; title: string; status: string; completed: boolean }[]
}

export default function Plans() {
  const { orgId } = useParams<{ orgId: string }>()
  const org = orgId ? parseInt(orgId, 10) : 0
  const [plans, setPlans] = useState<Plan[]>([])
  const [crisisTypes, setCrisisTypes] = useState<{ code: string; name: string }[]>([])
  const [newTitle, setNewTitle] = useState('')
  const [newCrisisCode, setNewCrisisCode] = useState('')
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!org) return
    anticrisis.plans(org).then(setPlans).catch(() => setPlans([]))
    anticrisis.crisisTypes().then(setCrisisTypes).catch(() => setCrisisTypes([]))
  }, [org])

  const createPlan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!org) return
    setError('')
    setCreating(true)
    try {
      const templateItems = [
        { title: 'Оптимизация структуры имущества', stage: 'Имущество' },
        { title: 'Управление дебиторской и кредиторской задолженностью', stage: 'Задолженность' },
        { title: 'Управление финансами', stage: 'Финансы' },
        { title: 'Управление продажами', stage: 'Продажи' },
        { title: 'Активизация основной деятельности', stage: 'Активизация' },
      ]
      await anticrisis.createPlan(org, {
        crisis_type_code: newCrisisCode,
        title: newTitle || 'План антикризисных мероприятий',
        items: templateItems,
      })
      setNewTitle('')
      const p = await anticrisis.plans(org)
      setPlans(p)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setCreating(false)
    }
  }

  const toggleItem = async (planId: number, itemId: number, completed: boolean) => {
    if (!org) return
    try {
      await anticrisis.updatePlanItem(org, planId, itemId, { completed, status: completed ? 'done' : 'in_progress' })
      const p = await anticrisis.plans(org)
      setPlans(p)
    } catch (_) {}
  }

  if (!org) return null

  return (
    <div>
      <p><Link to="/">← Дашборд</Link></p>
      <h1>Планы антикризисных мероприятий</h1>

      <div className="card">
        <h2>Новый план</h2>
        <form onSubmit={createPlan}>
          <div className="form-group">
            <label>Название</label>
            <input value={newTitle} onChange={(e) => setNewTitle(e.target.value)} placeholder="План антикризисных мероприятий" />
          </div>
          <div className="form-group">
            <label>Тип кризиса</label>
            <select value={newCrisisCode} onChange={(e) => setNewCrisisCode(e.target.value)}>
              <option value="">—</option>
              {crisisTypes.map((t) => (
                <option key={t.code} value={t.code}>{t.name}</option>
              ))}
            </select>
          </div>
          {error && <p style={{ color: '#d32f2f' }}>{error}</p>}
          <button type="submit" className="btn btn-primary" disabled={creating}>Создать план</button>
        </form>
      </div>

      <div className="card">
        <h2>Мои планы</h2>
        {plans.length === 0 ? (
          <p>Планов пока нет. Создайте план выше (по умолчанию добавятся типовые этапы из курса).</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {plans.map((plan) => (
              <li key={plan.id} style={{ marginBottom: '1.5rem', borderBottom: '1px solid #eee', paddingBottom: '1rem' }}>
                <h3>{plan.title}</h3>
                {plan.crisis_type_code && (
                  <p style={{ color: '#666', fontSize: '0.9rem' }}>Тип кризиса: {crisisTypes.find((t) => t.code === plan.crisis_type_code)?.name ?? plan.crisis_type_code}</p>
                )}
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {plan.items.map((item) => (
                    <li key={item.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <input
                        type="checkbox"
                        checked={item.completed}
                        onChange={(e) => toggleItem(plan.id, item.id, e.target.checked)}
                      />
                      <span style={{ textDecoration: item.completed ? 'line-through' : 'none' }}>{item.title}</span>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
