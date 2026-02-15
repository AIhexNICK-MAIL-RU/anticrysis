import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { anticrisis } from '../api'

const balanceFields = [
  { key: 'noncurrent_assets', label: 'Внеоборотные активы' },
  { key: 'current_assets', label: 'Оборотные активы' },
  { key: 'equity', label: 'Собственный капитал' },
  { key: 'long_term_liabilities', label: 'Долгосрочные обязательства' },
  { key: 'short_term_liabilities', label: 'Краткосрочные обязательства' },
  { key: 'receivables', label: 'Дебиторская задолженность' },
  { key: 'payables', label: 'Кредиторская задолженность' },
  { key: 'cash', label: 'Денежные средства' },
]
const bdrFields = [
  { key: 'revenue', label: 'Выручка' },
  { key: 'cost_of_sales', label: 'Себестоимость продаж' },
  { key: 'operating_expenses', label: 'Операционные расходы' },
  { key: 'other_income', label: 'Прочие доходы' },
  { key: 'other_expenses', label: 'Прочие расходы' },
]
const bddsFields = [
  { key: 'cash_begin', label: 'Остаток на начало' },
  { key: 'inflows_operating', label: 'Поступления (операционная)' },
  { key: 'outflows_operating', label: 'Выплаты (операционная)' },
  { key: 'cash_end', label: 'Остаток на конец' },
]

export default function PeriodForm() {
  const { orgId, periodId } = useParams<{ orgId: string; periodId?: string }>()
  const org = orgId ? parseInt(orgId, 10) : 0
  const period = periodId ? parseInt(periodId, 10) : null
  const [periods, setPeriods] = useState<{ id: number; label: string }[]>([])
  const [balance, setBalance] = useState<Record<string, number>>({})
  const [bdr, setBDR] = useState<Record<string, number>>({})
  const [bdds, setBDDS] = useState<Record<string, number>>({})
  const [coefficients, setCoefficients] = useState<Record<string, number> | null>(null)
  const [crisis, setCrisis] = useState<{ crisis_type_name: string; confidence: number; reasoning: string } | null>(null)
  const [saving, setSaving] = useState(false)
  const [newLabel, setNewLabel] = useState('')
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    if (!org) return
    anticrisis.periods(org).then(setPeriods).catch(() => setPeriods([]))
  }, [org])

  const currentPeriodId = period || (periods[0]?.id)
  useEffect(() => {
    if (!org || !currentPeriodId) return
    anticrisis.coefficients(org, currentPeriodId).then(setCoefficients).catch(() => setCoefficients(null))
    anticrisis.crisis(org, currentPeriodId).then(setCrisis).catch(() => setCrisis(null))
  }, [org, currentPeriodId])

  const saveBalance = async () => {
    if (!org || !currentPeriodId) return
    setSaving(true)
    try {
      await anticrisis.updateBalance(org, currentPeriodId, balance)
      const c = await anticrisis.coefficients(org, currentPeriodId)
      setCoefficients(c)
      const cr = await anticrisis.crisis(org, currentPeriodId)
      setCrisis(cr)
    } finally {
      setSaving(false)
    }
  }
  const saveBDR = async () => {
    if (!org || !currentPeriodId) return
    setSaving(true)
    try {
      await anticrisis.updateBDR(org, currentPeriodId, bdr)
      const c = await anticrisis.coefficients(org, currentPeriodId)
      setCoefficients(c)
      const cr = await anticrisis.crisis(org, currentPeriodId)
      setCrisis(cr)
    } finally {
      setSaving(false)
    }
  }
  const saveBDDS = async () => {
    if (!org || !currentPeriodId) return
    setSaving(true)
    try {
      await anticrisis.updateBDDS(org, currentPeriodId, bdds)
    } finally {
      setSaving(false)
    }
  }

  const createPeriod = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!org) return
    setCreating(true)
    try {
      const start = new Date()
      const end = new Date(start.getFullYear(), start.getMonth() + 1, 0)
      await anticrisis.createPeriod(org, {
        period_type: 'month',
        period_start: start.toISOString(),
        period_end: end.toISOString(),
        label: newLabel || `Период ${start.toLocaleDateString('ru')}`,
      })
      setNewLabel('')
      const p = await anticrisis.periods(org)
      setPeriods(p)
    } finally {
      setCreating(false)
    }
  }

  if (!org) return null

  return (
    <div>
      <p><Link to="/">← Дашборд</Link></p>
      <h1>Отчётность и коэффициенты</h1>

      <div className="card">
        <h2>Период</h2>
        <select
          value={currentPeriodId ?? ''}
          onChange={(e) => (window.location.href = `/orgs/${org}/periods/${e.target.value}`)}
        >
          {periods.map((p) => (
            <option key={p.id} value={p.id}>{p.label || `Период ${p.id}`}</option>
          ))}
        </select>
        <form onSubmit={createPeriod} style={{ marginTop: '1rem' }}>
          <input
            placeholder="Новый период (название)"
            value={newLabel}
            onChange={(e) => setNewLabel(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={creating}>Добавить период</button>
        </form>
      </div>

      {currentPeriodId && (
        <>
          <div className="card">
            <h2>Баланс</h2>
            {balanceFields.map((f) => (
              <div key={f.key} className="form-group" style={{ display: 'inline-block', marginRight: '1rem', width: 220 }}>
                <label>{f.label}</label>
                <input
                  type="number"
                  step="any"
                  value={balance[f.key] ?? ''}
                  onChange={(e) => setBalance((b) => ({ ...b, [f.key]: parseFloat(e.target.value) || 0 }))}
                />
              </div>
            ))}
            <br />
            <button type="button" className="btn btn-primary" onClick={saveBalance} disabled={saving}>Сохранить баланс</button>
          </div>

          <div className="card">
            <h2>БДР (доходы и расходы)</h2>
            {bdrFields.map((f) => (
              <div key={f.key} className="form-group" style={{ display: 'inline-block', marginRight: '1rem', width: 220 }}>
                <label>{f.label}</label>
                <input
                  type="number"
                  step="any"
                  value={bdr[f.key] ?? ''}
                  onChange={(e) => setBDR((b) => ({ ...b, [f.key]: parseFloat(e.target.value) || 0 }))}
                />
              </div>
            ))}
            <br />
            <button type="button" className="btn btn-primary" onClick={saveBDR} disabled={saving}>Сохранить БДР</button>
          </div>

          <div className="card">
            <h2>БДДС (денежные средства)</h2>
            {bddsFields.map((f) => (
              <div key={f.key} className="form-group" style={{ display: 'inline-block', marginRight: '1rem', width: 220 }}>
                <label>{f.label}</label>
                <input
                  type="number"
                  step="any"
                  value={bdds[f.key] ?? ''}
                  onChange={(e) => setBDDS((b) => ({ ...b, [f.key]: parseFloat(e.target.value) || 0 }))}
                />
              </div>
            ))}
            <br />
            <button type="button" className="btn btn-primary" onClick={saveBDDS} disabled={saving}>Сохранить БДДС</button>
          </div>

          {coefficients && (
            <div className="card">
              <h2>Коэффициенты</h2>
              <table style={{ width: '100%' }}>
                <tbody>
                  <tr><td>Текущая ликвидность</td><td>{coefficients.current_ratio?.toFixed(2)}</td></tr>
                  <tr><td>Быстрая ликвидность</td><td>{coefficients.quick_ratio?.toFixed(2)}</td></tr>
                  <tr><td>Абсолютная ликвидность</td><td>{coefficients.absolute_liquidity?.toFixed(2)}</td></tr>
                  <tr><td>Автономия</td><td>{coefficients.autonomy?.toFixed(2)}</td></tr>
                  <tr><td>Соотношение заёмных и собственных</td><td>{coefficients.debt_to_equity?.toFixed(2)}</td></tr>
                  <tr><td>ROA</td><td>{coefficients.roa?.toFixed(2)}</td></tr>
                  <tr><td>ROE</td><td>{coefficients.roe?.toFixed(2)}</td></tr>
                  <tr><td>Рентабельность продаж</td><td>{coefficients.profit_margin?.toFixed(2)}</td></tr>
                </tbody>
              </table>
            </div>
          )}

          {crisis && (
            <div className="card">
              <h2>Карта кризиса</h2>
              <p><strong>{crisis.crisis_type_name}</strong> (уверенность: {(crisis.confidence * 100).toFixed(0)}%)</p>
              <p>{crisis.reasoning}</p>
              <p><Link to={`/orgs/${org}/plans`} className="btn btn-primary">Перейти к планам мероприятий</Link></p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
