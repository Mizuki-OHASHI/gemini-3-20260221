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
  avatarUrl: string | null
  clearedItems: string[]
  gameSolved: boolean
  hints: HintInfo[]
  isInitializing: boolean
  hideBottomNav: boolean
}

interface GameContextValue extends GameState {
  updateFromTurn: (turn: TurnResponse) => void
  resetGame: () => Promise<void>
  createGame: (ghostDescription?: string) => Promise<string>
  generateAvatar: (gameId?: string) => Promise<string>
  setHideBottomNav: (hide: boolean) => void
}

const GameContext = createContext<GameContextValue | null>(null)

const LS_GAME_ID = 'ghost_whisper_game_id'

async function restoreHintsFromServer(gameId: string): Promise<{ avatarUrl: string | null; hints: HintInfo[]; clearedItems: string[]; gameSolved: boolean }> {
  const [gameRes, photosRes, hintsRes] = await Promise.all([
    api.getGameGameGameIdGet(gameId),
    api.listPhotosGameGameIdPhotosGet(gameId),
    api.listHintMessagesEndpointScenarioHintsGet(),
  ])

  const avatarUrl = gameRes.data.avatar_url ?? null
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

  return { avatarUrl, hints, clearedItems, gameSolved }
}

export function GameProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<GameState>({
    gameId: null,
    avatarUrl: null,
    clearedItems: [],
    gameSolved: false,
    hints: [],
    isInitializing: true,
    hideBottomNav: false,
  })

  const setHideBottomNav = useCallback((hide: boolean) => {
    setState((s) => ({ ...s, hideBottomNav: hide }))
  }, [])

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
          const { avatarUrl, hints, clearedItems, gameSolved } = await restoreHintsFromServer(gameId)
          if (cancelled) return
          setState({
            gameId,
            avatarUrl,
            clearedItems,
            gameSolved,
            hints,
            isInitializing: false,
          })
          return
        } catch {
          // Game not found, will need new game via PreludePage
          gameId = null
        }
      }

      // No saved game — don't auto-create; let PreludePage handle it
      if (!cancelled) {
        setState((s) => ({ ...s, isInitializing: false }))
      }
    }

    init()
    return () => { cancelled = true }
  }, [])

  const createGame = useCallback(async (ghostDescription?: string) => {
    const res = await api.createGameGamePost({
      player_name: 'player',
      ...(ghostDescription ? { ghost_description: ghostDescription } : {}),
    })
    const gameId = res.data.id
    try { localStorage.setItem(LS_GAME_ID, gameId) } catch { /* noop */ }
    setState((s) => ({ ...s, gameId }))
    return gameId
  }, [])

  const generateAvatar = useCallback(async (gameIdOverride?: string) => {
    const id = gameIdOverride ?? state.gameId
    if (!id) throw new Error('Game not created yet')
    const res = await api.generateAvatarGameGameIdAvatarPost(id)
    const avatarUrl = res.data.avatar_url
    setState((s) => ({ ...s, avatarUrl }))
    return avatarUrl
  }, [state.gameId])

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
    try { sessionStorage.removeItem('prelude_seen_v1') } catch { /* noop */ }
    setState({
      gameId: null,
      avatarUrl: null,
      clearedItems: [],
      gameSolved: false,
      hints: [],
      isInitializing: false,
    })
  }, [])

  return (
    <GameContext.Provider value={{ ...state, updateFromTurn, resetGame, createGame, generateAvatar, setHideBottomNav }}>
      {children}
    </GameContext.Provider>
  )
}

export function useGame() {
  const ctx = useContext(GameContext)
  if (!ctx) throw new Error('useGame must be used within GameProvider')
  return ctx
}
