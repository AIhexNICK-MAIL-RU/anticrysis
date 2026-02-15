import { useState, useEffect } from 'react'
import { calc } from '../api'

type ModelMeta = {
  sheets: { name: string; visibility: string; file: string }[]
  active_sheet: string
  has_model: boolean
}

export default function CalcModel() {
  const [meta, setMeta] = useState<ModelMeta | null>(null)
  const [inputs, setInputs] = useState<Record<string, string>>({})
  const [cells, setCells] = useState<Record<string, number | string | null> | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    calc.model().then(setMeta).catch(() => setMeta({ sheets: [], active_sheet: '', has_model: false }))
  }, [])

  const run = async () => {
    setError('')
    setCells(null)
    const numInputs: Record<string, number> = {}
    for (const [k, v] of Object.entries(inputs)) {
      const n = parseFloat(String(v).replace(',', '.'))
      if (!Number.isNaN(n)) numInputs[k] = n
    }
    setLoading(true)
    try {
      const res = await calc.run(numInputs)
      setCells(res.cells || {})
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка расчёта')
    } finally {
      setLoading(false)
    }
  }

  const addInput = () => {
    const key = prompt('Адрес ячейки (например B2 или Данные!B2):')?.trim()
    if (key) setInputs((prev) => ({ ...prev, [key]: '' }))
  }

  if (!meta) return <p>Загрузка...</p>

  return (
    <div className="card" style={{ maxWidth: 900 }}>
      <h1 style={{ marginTop: 0 }}>Расчётная модель</h1>
      <p style={{ color: '#666' }}>
        Модель загружается из экспорта Excel (JSON). Задайте значения входных ячеек и нажмите «Рассчитать».
      </p>
      {meta.sheets.length > 0 && (
        <p>
          Листы: {meta.sheets.map((s) => s.name).join(', ')}. Активный: {meta.active_sheet || '—'}
        </p>
      )}
      {!meta.has_model && (
        <p style={{ color: '#b8860b' }}>
          Модель не загружена. Запустите скрипт экспорта из корня проекта:{' '}
          <code>python backend/scripts/export_excel_to_json.py "Рабочая тетрадь_Фин модель.xlsx"</code>
        </p>
      )}

      <div style={{ marginTop: '1rem' }}>
        <strong>Входные ячейки</strong>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
          {Object.entries(inputs).map(([key]) => (
            <span key={key} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <label>
                {key}
                <input
                  type="text"
                  value={inputs[key]}
                  onChange={(e) => setInputs((prev) => ({ ...prev, [key]: e.target.value }))}
                  placeholder="0"
                  style={{ width: 80, marginLeft: 4 }}
                />
              </label>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: '2px 6px' }}
                onClick={() => setInputs((prev) => { const n = { ...prev }; delete n[key]; return n })}
              >
                ×
              </button>
            </span>
          ))}
          <button type="button" className="btn btn-secondary" onClick={addInput}>
            + ячейка
          </button>
        </div>
      </div>

      <div style={{ marginTop: '1rem' }}>
        <button type="button" className="btn btn-primary" onClick={run} disabled={loading}>
          {loading ? 'Расчёт…' : 'Рассчитать'}
        </button>
      </div>

      {error && <p style={{ color: '#d32f2f' }}>{error}</p>}

      {cells && Object.keys(cells).length > 0 && (
        <div style={{ marginTop: '1.5rem' }}>
          <strong>Результаты (ячейки)</strong>
          <table style={{ width: '100%', marginTop: '0.5rem', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #ddd' }}>
                <th style={{ textAlign: 'left', padding: 6 }}>Ячейка</th>
                <th style={{ textAlign: 'right', padding: 6 }}>Значение</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(cells)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([coord, value]) => (
                  <tr key={coord} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: 6 }}>{coord}</td>
                    <td style={{ padding: 6, textAlign: 'right' }}>
                      {value === null || value === undefined ? '—' : String(value)}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
