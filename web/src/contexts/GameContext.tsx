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

async function createNewGame(): Promise<string> {
  const res = await api.createGameGamePost({ player_name: 'player' })
  return res.data.id
}

async function restoreHintsFromServer(gameId: string): Promise<{ hints: HintInfo[]; clearedItems: string[]; gameSolved: boolean }> {
  const [gameRes, photosRes, hintsRes] = await Promise.all([
    api.getGameGameGameIdGet(gameId),
    api.listPhotosGameGameIdPhotosGet(gameId),
    api.listHintMessagesScenarioHintsGet(),
  ])

  const clearedItems = gameRes.data.cleared_items ?? []
  const gameSolved = gameRes.data.status === 'solved'

  const hintMap: Record<string, string> = {}
  for (const h of hintsRes.data) {
    hintMap[h.item] = h.message
  }

  const hints: HintInfo[] = photosRes.data.photos
    .filter((p) => p.detected_item)
    .map((p) => ({
      item: p.detected_item!,
      message: hintMap[p.detected_item!] ?? '',
      ghostUrl: p.ghost_url ?? null,
    }))

  return { hints, clearedItems, gameSolved }
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
      let gameId: string | null = null
      try {
        gameId = localStorage.getItem(LS_GAME_ID)
      } catch {
        // localStorage unavailable
      }

      if (gameId) {
        try {
          const { hints, clearedItems, gameSolved } = await restoreHintsFromServer(gameId)
          if (cancelled) return
          setState({
            gameId,
            clearedItems,
            gameSolved,
            hints,
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
        try { localStorage.setItem(LS_GAME_ID, gameId) } catch { /* noop */ }
        setState({
          gameId,
          clearedItems: [],
          gameSolved: false,
          hints: [],
          isInitializing: false,
        })
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

      return {
        ...prev,
        clearedItems: turn.cleared_items,
        gameSolved: turn.game_solved,
        hints,
      }
    })
  }, [])

  const resetGame = useCallback(async () => {
    try { localStorage.removeItem(LS_GAME_ID) } catch { /* noop */ }
    setState((s) => ({ ...s, isInitializing: true }))
    try {
      const gameId = await createNewGame()
      try { localStorage.setItem(LS_GAME_ID, gameId) } catch { /* noop */ }
      setState({
        gameId,
        clearedItems: [],
        gameSolved: false,
        hints: [],
        isInitializing: false,
      })
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
