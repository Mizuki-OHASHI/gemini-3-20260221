import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { MainPage } from './pages/MainPage'
import { ContextPage } from './pages/ContextPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<MainPage />} />
          <Route path="context" element={<ContextPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
