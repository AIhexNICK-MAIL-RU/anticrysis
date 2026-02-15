import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { anticrisis } from '../api'

const balanceLabels: Record<string, string> = {
  noncurrent_assets: 'Внеоборотные активы',
  current_assets: 'Оборотные активы',
  equity: 'Собственный капитал',
  long_term_liabilities: 'Долгосрочные обязательства',
  short_term_liabilities: 'Краткосрочные обязательства',
  receivables: 'Дебиторская задолженность',
  payables: 'Кредиторская задолженность',
  cash: 'Денежные средства',
}

const bdrLabels: Record<string, string> = {
  revenue: 'Выручка',
  cost_of_sales: 'Себестоимость продаж',
  operating_expenses: 'Операционные расходы',
  other_income: 'Прочие доходы',
  other_expenses: 'Прочие расходы',
  profit: 'Прибыль',
}

const bddsLabels: Record<string, string> = {
  cash_begin: 'Остаток на начало',
  inflows_operating: 'Поступления (операционная)',
  outflows_operating: 'Выплаты (операционная)',
  inflows_investing: 'Поступления (инвестиционная)',
  outflows_investing: 'Выплаты (инвестиционная)',
  inflows_financing: 'Поступления (финансовая)',
  outflows_financing: 'Выплаты (финансовая)',
  cash_end: 'Остаток на конец',
}

const coefLabels: Record<string, string> = {
  current_ratio: 'Текущая ликвидность',
  quick_ratio: 'Быстрая ликвидность',
  absolute_liquidity: 'Абсолютная ликвидность',
  autonomy: 'Автономия',
  debt_to_equity: 'Соотношение заёмных и собственных',
  roa: 'ROA',
  roe: 'ROE',
  profit_margin: 'Рентабельность продаж',
}

function formatNum(v: number): string {
  if (v === undefined || v === null) return '—'
  return Number(v).toLocaleString('ru', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function TableBlock({ title, rows }: { title: string; rows: [string, number][] }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <table style={{ width: '100%', maxWidth: 480 }}>
        <tbody>
          {rows.map(([label, value]) => (
            <tr key={label}>
              <td>{label}</td>
              <td style={{ textAlign: 'right' }}>{formatNum(value)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function CalculationTable() {
  const { orgId } = useParams<{ orgId: string }>()
  const org = orgId ? parseInt(orgId, 10) : 0
  const [periods, setPeriods] = useState<{ id: number; label: string }[]>([])
  const [periodId, setPeriodId] = useState<number | null>(null)
  const [data, setData] = useState<{
    period: { id: number; label: string }
    balance: Record<string, number>
    bdr: Record<string, number>
    bdds: Record<string, number>
    coefficients: Record<string, number>
    crisis: { crisis_type_name: string; confidence: number; reasoning: string }
  } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!org) return
    anticrisis.periods(org).then((p) => {
      setPeriods(p)
      if (p.length && !periodId) setPeriodId(p[0].id)
    }).catch(() => setPeriods([]))
  }, [org])

  useEffect(() => {
    if (!org || !periodId) {
      setData(null)
      return
    }
    setLoading(true)
    setError(null)
    anticrisis.periodTable(org, periodId)
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [org, periodId])

  if (!org) return null

  return (
    <div>
      <p><Link to="/">← Дашборд</Link></p>
      <h1>Расчётная таблица</h1>
      <p className="muted">Баланс, БДР, БДДС, коэффициенты и карта кризиса по выбранному периоду.</p>

      <div className="card">
        <div className="form-group">
          <label>Период</label>
          <select
            value={periodId ?? ''}
            onChange={(e) => setPeriodId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">— Выберите —</option>
            {periods.map((p) => (
              <option key={p.id} value={p.id}>{p.label || `Период ${p.id}`}</option>
            ))}
          </select>
        </div>
        <p>
          <Link to={`/orgs/${org}/periods`}>Ввод данных (баланс, БДР, БДДС)</Link>
          {' · '}
          <Link to={`/orgs/${org}/plans`}>Планы мероприятий</Link>
        </p>
      </div>

      {error && <div className="card" style={{ borderColor: 'var(--danger, #c00)' }}><p>{error}</p></div>}
      {loading && <p>Загрузка...</p>}

      {data && !loading && (
        <>
          <TableBlock
            title="Баланс (ББЛ)"
            rows={Object.entries(data.balance).map(([k, v]) => [balanceLabels[k] ?? k, v])}
          />
          <TableBlock
            title="БДР (доходы и расходы)"
            rows={Object.entries(data.bdr).map(([k, v]) => [bdrLabels[k] ?? k, v])}
          />
          {Object.keys(data.bdds).length > 0 && (
            <TableBlock
              title="БДДС (денежные потоки)"
              rows={Object.entries(data.bdds).map(([k, v]) => [bddsLabels[k] ?? k, v])}
            />
          )}
          <TableBlock
            title="Коэффициенты"
            rows={Object.entries(data.coefficients).map(([k, v]) => [coefLabels[k] ?? k, v])}
          />
          <div className="card">
            <h2>Карта кризиса</h2>
            <p><strong>{data.crisis.crisis_type_name}</strong> (уверенность: {(data.crisis.confidence * 100).toFixed(0)}%)</p>
            <p>{data.crisis.reasoning}</p>
            <p><Link to={`/orgs/${org}/plans`} className="btn btn-primary">Планы мероприятий</Link></p>
          </div>
        </>
      )}
    </div>
  )
}
