import { Outlet, Link, useNavigate } from 'react-router-dom'

export default function Layout() {
  const navigate = useNavigate()
  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }
  return (
    <>
      <nav>
        <Link to="/">Дашборд</Link>
        <Link to="/orgs">Организации</Link>
        <button type="button" onClick={handleLogout} className="btn btn-secondary" style={{ marginLeft: 'auto' }}>
          Выход
        </button>
      </nav>
      <main className="container">
        <Outlet />
      </main>
    </>
  )
}
