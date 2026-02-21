import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react'
import { api } from '../api/client'
import type { TurnResponse } from '../api/model'

interface HintInfo {
  item: string
  message: string
  ghostUrl: string | null
}

interface GameState {
  gameId: string | null
  clearedItems: string[]
  gameSolved: boolean
  hints: HintInfo[]
  isInitializing: boolean
}

interface GameContextValue extends GameState {
  updateFromTurn: (turn: TurnResponse) => void
  resetGame: () => Promise<void>
}

const GameContext = createContext<GameContextValue | null>(null)

const LS_GAME_ID = 'ghost_whisper_game_id'
const LS_CLEARED = 'ghost_whisper_cleared_items'
const LS_HINTS = 'ghost_whisper_hints'
const LS_SOLVED = 'ghost_whisper_solved'

function loadFromStorage(): Partial<GameState> {
  try {
    return {
      gameId: localStorage.getItem(LS_GAME_ID),
      clearedItems: JSON.parse(localStorage.getItem(LS_CLEARED) || '[]'),
      hints: JSON.parse(localStorage.getItem(LS_HINTS) || '[]'),
      gameSolved: localStorage.getItem(LS_SOLVED) === 'true',
    }
  } catch {
    return {}
  }
}

function saveToStorage(state: Pick<GameState, 'gameId' | 'clearedItems' | 'hints' | 'gameSolved'>) {
  if (state.gameId) localStorage.setItem(LS_GAME_ID, state.gameId)
  localStorage.setItem(LS_CLEARED, JSON.stringify(state.clearedItems))
  localStorage.setItem(LS_HINTS, JSON.stringify(state.hints))
  localStorage.setItem(LS_SOLVED, String(state.gameSolved))
}

function clearStorage() {
  localStorage.removeItem(LS_GAME_ID)
  localStorage.removeItem(LS_CLEARED)
  localStorage.removeItem(LS_HINTS)
  localStorage.removeItem(LS_SOLVED)
}

async function createNewGame(): Promise<string> {
  const res = await api.createGameGamePost({ player_name: 'player' })
  return res.data.id
}

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<GameState>({
    gameId: null,
    clearedItems: [],
    gameSolved: false,
    hints: [],
    isInitializing: true,
  })

  useEffect(() => {
    let cancelled = false

    async function init() {
      const stored = loadFromStorage()
      let gameId = stored.gameId ?? null

      if (gameId) {
        try {
          const res = await api.getGameGameGameIdGet(gameId)
          if (cancelled) return
          setState({
            gameId,
            clearedItems: res.data.cleared_items ?? stored.clearedItems ?? [],
            gameSolved: res.data.status === 'solved',
            hints: stored.hints ?? [],
            isInitializing: false,
          })
          return
        } catch {
          // Game not found, create new
          gameId = null
        }
      }

      try {
        gameId = await createNewGame()
        if (cancelled) return
        const newState: GameState = {
          gameId,
          clearedItems: [],
          gameSolved: false,
          hints: [],
          isInitializing: false,
        }
        saveToStorage(newState)
        setState(newState)
      } catch {
        if (cancelled) return
        setState((s) => ({ ...s, isInitializing: false }))
      }
    }

    init()
    return () => { cancelled = true }
  }, [])

  const updateFromTurn = useCallback((turn: TurnResponse) => {
    setState((prev) => {
      const hints = [...prev.hints]
      if (turn.detected_item && turn.hint_message) {
        const exists = hints.some((h) => h.item === turn.detected_item)
        if (!exists) {
          hints.push({
            item: turn.detected_item,
            message: turn.hint_message,
            ghostUrl: turn.ghost_url ?? null,
          })
        }
      }

      const next: GameState = {
        ...prev,
        clearedItems: turn.cleared_items,
        gameSolved: turn.game_solved,
        hints,
      }
      saveToStorage(next)
      return next
    })
  }, [])

  const resetGame = useCallback(async () => {
    clearStorage()
    setState((s) => ({ ...s, isInitializing: true }))
    try {
      const gameId = await createNewGame()
      const newState: GameState = {
        gameId,
        clearedItems: [],
        gameSolved: false,
        hints: [],
        isInitializing: false,
      }
      saveToStorage(newState)
      setState(newState)
    } catch {
      setState((s) => ({ ...s, isInitializing: false }))
    }
  }, [])

  return (
    <GameContext.Provider value={{ ...state, updateFromTurn, resetGame }}>
      {children}
    </GameContext.Provider>
  )
}

export function useGame() {
  const ctx = useContext(GameContext)
  if (!ctx) throw new Error('useGame must be used within GameProvider')
  return ctx
}
