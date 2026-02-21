import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { MainPage } from './pages/MainPage'
import { ContextPage } from './pages/ContextPage'
import { GameProvider } from './contexts/GameContext'

function App() {
  return (
    <GameProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<MainPage />} />
            <Route path="context" element={<ContextPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </GameProvider>
  )
}

export default App
