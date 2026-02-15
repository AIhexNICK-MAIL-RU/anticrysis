import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { auth } from '../api'

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await auth.register(email, password, fullName)
      const { access_token } = await auth.login(email, password)
      localStorage.setItem('token', access_token)
      navigate('/')
    } catch (err) {
      const msg = err instanceof Error ? err.message : typeof err === 'object' && err !== null ? JSON.stringify(err) : 'Ошибка регистрации'
      setError(msg)
    }
  }

  return (
    <div className="container" style={{ maxWidth: 400, marginTop: '3rem' }}>
      <div className="card">
        <h1 style={{ marginTop: 0 }}>Регистрация</h1>
        <form onSubmit={submit}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>ФИО</label>
            <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Пароль</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <p style={{ color: '#d32f2f' }}>{error}</p>}
          <button type="submit" className="btn btn-primary">Зарегистрироваться</button>
        </form>
        <p style={{ marginTop: '1rem' }}>
          Уже есть аккаунт? <Link to="/login">Вход</Link>
        </p>
      </div>
    </div>
  )
}
