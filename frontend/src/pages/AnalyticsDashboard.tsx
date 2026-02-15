import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
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
  cost_of_sales: 'Себестоимость',
  operating_expenses: 'Операционные расходы',
  other_income: 'Прочие доходы',
  other_expenses: 'Прочие расходы',
  profit: 'Прибыль',
}

const bddsLabels: Record<string, string> = {
  cash_begin: 'Остаток на начало',
  inflows_operating: 'Поступления (опер.)',
  outflows_operating: 'Выплаты (опер.)',
  inflows_investing: 'Поступления (инв.)',
  outflows_investing: 'Выплаты (инв.)',
  inflows_financing: 'Поступления (фин.)',
  outflows_financing: 'Выплаты (фин.)',
  cash_end: 'Остаток на конец',
}

const coefLabels: Record<string, string> = {
  current_ratio: 'Текущая ликвидность',
  quick_ratio: 'Быстрая ликвидность',
  absolute_liquidity: 'Абсолютная ликвидность',
  autonomy: 'Автономия',
  debt_to_equity: 'Заёмные/собственные',
  roa: 'ROA',
  roe: 'ROE',
  profit_margin: 'Рентабельность продаж',
}

const finModelLabels: Record<string, string> = {
  total_assets: 'Всего активов',
  total_liabilities: 'Всего обязательств',
  equity_ratio: 'Доля собственного капитала',
  profit: 'Прибыль',
  profit_margin: 'Рентабельность продаж',
  gross_profit: 'Валовая прибыль',
  gross_margin: 'Валовая маржа',
  break_even_revenue: 'Выручка ТБУ',
  operating_cash_flow: 'ДП (опер.)',
  investing_cash_flow: 'ДП (инв.)',
  financing_cash_flow: 'ДП (фин.)',
  net_cash_flow: 'Чистое изменение денег',
  cash_end_calculated: 'Остаток на конец (расч.)',
}

const CHART_COLORS = ['#2563eb', '#16a34a', '#ca8a04', '#dc2626', '#9333ea', '#0d9488', '#ea580c', '#4f46e5']

function formatNum(v: number): string {
  if (v === undefined || v === null) return '—'
  return Number(v).toLocaleString('ru', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

export default function AnalyticsDashboard() {
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
    crisis: { crisis_type_code: string; crisis_type_name: string; confidence: number; reasoning: string }
    fin_model?: Record<string, number>
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

  const exportJson = () => {
    if (!data) return
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `anticrisis_org${org}_period${data.period.id}_${data.period.label || 'export'}.json`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  const exportCsv = () => {
    if (!data) return
    const rows: string[][] = []
    const enc = (s: string) => `"${String(s).replace(/"/g, '""')}"`
    rows.push(['Раздел', 'Показатель', 'Значение'])
    Object.entries(data.balance).forEach(([k, v]) => rows.push(['Баланс', balanceLabels[k] ?? k, String(v)]))
    Object.entries(data.bdr).forEach(([k, v]) => rows.push(['БДР', bdrLabels[k] ?? k, String(v)]))
    Object.entries(data.bdds).forEach(([k, v]) => rows.push(['БДДС', bddsLabels[k] ?? k, String(v)]))
    Object.entries(data.coefficients).forEach(([k, v]) => rows.push(['Коэффициенты', coefLabels[k] ?? k, String(v)]))
    if (data.fin_model) {
      Object.entries(data.fin_model).forEach(([k, v]) => rows.push(['Фин. модель', finModelLabels[k] ?? k, String(v)]))
    }
    rows.push(['Кризис', 'Тип', data.crisis.crisis_type_name])
    rows.push(['Кризис', 'Уверенность', String(data.crisis.confidence)])
    rows.push(['Кризис', 'Обоснование', data.crisis.reasoning])
    const csv = rows.map((r) => r.map(enc).join(';')).join('\n')
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `anticrisis_org${org}_period${data.period.id}.csv`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  if (!org) return null

  const balanceChartData = data ? Object.entries(data.balance).map(([k, v]) => ({ name: balanceLabels[k] ?? k, value: v })) : []
  const bdrChartData = data ? Object.entries(data.bdr).filter(([, v]) => v !== undefined).map(([k, v]) => ({ name: bdrLabels[k] ?? k, value: v })) : []
  const bddsChartData = data ? Object.entries(data.bdds).filter(([, v]) => v !== undefined).map(([k, v]) => ({ name: bddsLabels[k] ?? k, value: v })) : []
  const coefChartData = data ? Object.entries(data.coefficients).map(([k, v]) => ({ name: coefLabels[k] ?? k, value: v })) : []
  const finModelChartData = data?.fin_model ? Object.entries(data.fin_model).map(([k, v]) => ({ name: finModelLabels[k] ?? k, value: v })) : []
  const crisisPieData = data
    ? [
        { name: data.crisis.crisis_type_name, value: Math.round(data.crisis.confidence * 100) },
        { name: 'Прочее', value: Math.max(0, 100 - Math.round(data.crisis.confidence * 100)) },
      ]
    : []

  return (
    <div style={{ maxWidth: 1200 }}>
      <p><Link to="/">← Дашборд</Link></p>
      <h1 style={{ marginTop: 0 }}>Дашборд аналитики</h1>
      <p style={{ color: '#666' }}>
        Визуализация расчётов по периоду и выгрузка всех данных (JSON / CSV).
      </p>

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
          <Link to={`/orgs/${org}/table`}>Расчётная таблица</Link>
          {' · '}
          <Link to={`/orgs/${org}/periods`}>Ввод данных</Link>
          {' · '}
          <Link to={`/orgs/${org}/plans`}>Планы мероприятий</Link>
        </p>
      </div>

      {error && <div className="card" style={{ borderColor: 'var(--danger, #c00)' }}><p>{error}</p></div>}
      {loading && <p>Загрузка...</p>}

      {data && !loading && (
        <>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <h3 style={{ marginTop: 0 }}>Выгрузка данных</h3>
            <p>Скачать все данные по выбранному периоду для отчётов или анализа во внешних инструментах.</p>
            <button type="button" className="btn btn-primary" onClick={exportJson} style={{ marginRight: 8 }}>
              Скачать JSON
            </button>
            <button type="button" className="btn btn-secondary" onClick={exportCsv}>
              Скачать CSV
            </button>
          </div>

          <div className="card" style={{ marginBottom: '1rem' }}>
            <h3 style={{ marginTop: 0 }}>Баланс (структура)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={balanceChartData} margin={{ top: 8, right: 8, left: 8, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-25} textAnchor="end" height={60} tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={(v: number) => formatNum(v)} />
                <Tooltip formatter={(v: number) => formatNum(v)} />
                <Bar dataKey="value" fill={CHART_COLORS[0]} name="Сумма" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card" style={{ marginBottom: '1rem' }}>
            <h3 style={{ marginTop: 0 }}>БДР (доходы и расходы)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={bdrChartData} margin={{ top: 8, right: 8, left: 8, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-25} textAnchor="end" height={60} tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={(v: number) => formatNum(v)} />
                <Tooltip formatter={(v: number) => formatNum(v)} />
                <Bar dataKey="value" fill={CHART_COLORS[1]} name="Сумма" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {bddsChartData.length > 0 && (
            <div className="card" style={{ marginBottom: '1rem' }}>
              <h3 style={{ marginTop: 0 }}>БДДС (денежные потоки)</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={bddsChartData} margin={{ top: 8, right: 8, left: 8, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-25} textAnchor="end" height={60} tick={{ fontSize: 11 }} />
                  <YAxis tickFormatter={(v: number) => formatNum(v)} />
                  <Tooltip formatter={(v: number) => formatNum(v)} />
                  <Bar dataKey="value" fill={CHART_COLORS[2]} name="Сумма" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="card" style={{ marginBottom: '1rem' }}>
            <h3 style={{ marginTop: 0 }}>Коэффициенты</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={coefChartData} layout="vertical" margin={{ top: 8, right: 40, left: 120, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(v: number) => Number(v).toFixed(2)} />
                <YAxis type="category" dataKey="name" width={115} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => Number(v).toFixed(4)} />
                <Bar dataKey="value" fill={CHART_COLORS[3]} name="Значение" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {finModelChartData.length > 0 && (
            <div className="card" style={{ marginBottom: '1rem' }}>
              <h3 style={{ marginTop: 0 }}>Финансовая модель (расчёт по данным периода)</h3>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={finModelChartData} layout="vertical" margin={{ top: 8, right: 40, left: 140, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" tickFormatter={(v: number) => formatNum(v)} />
                  <YAxis type="category" dataKey="name" width={135} tick={{ fontSize: 10 }} />
                  <Tooltip formatter={(v: number) => formatNum(Number(v))} />
                  <Bar dataKey="value" fill={CHART_COLORS[5]} name="Значение" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="card" style={{ marginBottom: '1rem', display: 'flex', flexWrap: 'wrap', gap: '1.5rem', alignItems: 'flex-start' }}>
            <div>
              <h3 style={{ marginTop: 0 }}>Карта кризиса</h3>
              <ResponsiveContainer width={260} height={200}>
                <PieChart>
                  <Pie
                    data={crisisPieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={70}
                    label={({ name, value }: { name: string; value: number }) => `${name}: ${value}%`}
                  >
                    {crisisPieData.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? CHART_COLORS[4] : '#e5e7eb'} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: number) => `${v}%`} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div style={{ flex: 1, minWidth: 200 }}>
              <p><strong>{data.crisis.crisis_type_name}</strong></p>
              <p>Уверенность: {(data.crisis.confidence * 100).toFixed(0)}%</p>
              <p>{data.crisis.reasoning}</p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
