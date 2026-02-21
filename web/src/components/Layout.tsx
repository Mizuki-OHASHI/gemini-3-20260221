import { NavLink, Outlet } from 'react-router-dom'
import { useGame } from '../contexts/GameContext'

export function Layout() {
  const { hideBottomNav } = useGame()
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex-1 flex flex-col items-center gap-1 py-3 text-xs font-medium transition-colors ${
      isActive ? 'text-[var(--color-spirit)]' : 'text-[var(--color-ash)]'
    }`

  return (
    <div className="max-w-md mx-auto min-h-dvh flex flex-col bg-[var(--color-void)] relative">
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>

      {!hideBottomNav && (
        <nav className="sticky bottom-0 flex border-t border-[var(--color-mist)] bg-[var(--color-shadow)]/80 backdrop-blur-sm safe-bottom">
          <NavLink to="/" className={linkClass}>
            <svg xmlns="http://www.w3.org/2000/svg" className="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Z" />
            </svg>
            <span>撮影</span>
          </NavLink>
          <NavLink to="/context" className={linkClass}>
            <svg xmlns="http://www.w3.org/2000/svg" className="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" />
            </svg>
            <span>記憶</span>
          </NavLink>
        </nav>
      )}
    </div>
  )
}
