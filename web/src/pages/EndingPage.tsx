import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useGame } from '../contexts/GameContext'

type EndingKind = 'success' | 'escape'

export function EndingPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { gameSolved, resetGame } = useGame()
  const [isResetting, setIsResetting] = useState(false)

  const param = searchParams.get('result')
  const ending: EndingKind = param === 'success' || (param !== 'escape' && gameSolved) ? 'success' : 'escape'

  const handleRestart = async () => {
    if (isResetting) return
    setIsResetting(true)
    await resetGame()
    navigate('/', { replace: true })
  }

  return (
    <div className="min-h-full p-4 flex items-center">
      <section className="w-full rounded-2xl border border-[var(--color-mist)] bg-[var(--color-dusk)] p-6 space-y-5 animate-spirit-reveal">
        {ending === 'success' ? (
          <>
            <p className="text-xs tracking-[0.2em] uppercase text-[var(--color-spirit)]">Good Ending</p>
            <h1 className="text-2xl font-bold text-[var(--color-frost)]">真相は暴かれた</h1>
            <p className="text-sm leading-relaxed text-[var(--color-whisper)]">
              犯人は見つかり、ついに逮捕された。<br />
              失われた時間は戻らない。<br />
              それでもあなたは、澪の声を最後まで受け取ることができた。
            </p>
          </>
        ) : (
          <>
            <p className="text-xs tracking-[0.2em] uppercase text-[var(--color-blood)]">Bad Ending</p>
            <h1 className="text-2xl font-bold text-[var(--color-frost)]">犯人は逃げ切った</h1>
            <p className="text-sm leading-relaxed text-[var(--color-whisper)]">
              手がかりは足りず、決定打は見つからなかった。<br />
              犯人は街のどこかへ姿を消した。<br />
              部屋に残ったのは、あなたを見つめる澪の気配だけだった。
            </p>
          </>
        )}

        <div className="space-y-3">
          <button
            onClick={handleRestart}
            disabled={isResetting}
            className="w-full rounded-full border border-[var(--color-mist)] bg-[var(--color-shadow)] px-5 py-3 text-sm font-semibold text-[var(--color-frost)] disabled:opacity-60"
          >
            {isResetting ? 'リセット中...' : '最初からやり直す'}
          </button>
          <button
            onClick={() => navigate('/context')}
            className="w-full rounded-full border border-[var(--color-mist)] px-5 py-3 text-sm text-[var(--color-ash)]"
          >
            記憶を確認する
          </button>
        </div>
      </section>
    </div>
  )
}
