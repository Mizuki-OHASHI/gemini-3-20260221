import { useState, useCallback } from 'react'
import { api } from '../api/client'
import { useGame } from '../contexts/GameContext'
import type { TurnResponse } from '../api/model'

interface UseGameTurnReturn {
  playTurn: (capture: () => string | null) => Promise<void>
  isLoading: boolean
  lastResult: TurnResponse | null
  capturedImage: string | null
  error: string | null
  dismissResult: () => void
}

function dataURLtoBlob(dataURL: string): Blob {
  const [header, data] = dataURL.split(',')
  const mime = header.match(/:(.*?);/)?.[1] ?? 'image/jpeg'
  const binary = atob(data)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return new Blob([bytes], { type: mime })
}

export function useGameTurn(): UseGameTurnReturn {
  const { gameId, updateFromTurn } = useGame()
  const [isLoading, setIsLoading] = useState(false)
  const [lastResult, setLastResult] = useState<TurnResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)

  const playTurn = useCallback(
    async (capture: () => string | null) => {
      if (!gameId || isLoading) return

      setError(null)
      setIsLoading(true)

      try {
        const dataURL = capture()
        if (!dataURL) {
          setError('写真の撮影に失敗しました')
          setIsLoading(false)
          return
        }
        setCapturedImage(dataURL)

        const blob = dataURLtoBlob(dataURL)
        const res = await api.playTurnGameGameIdTurnPost(gameId, { file: blob })
        setLastResult(res.data)
        updateFromTurn(res.data)
      } catch (e) {
        if (e instanceof Error) {
          setError(e.message)
        } else {
          setError('エラーが発生しました')
        }
      } finally {
        setIsLoading(false)
      }
    },
    [gameId, isLoading, updateFromTurn],
  )

  const dismissResult = useCallback(() => {
    setLastResult(null)
    setCapturedImage(null)
    setError(null)
  }, [])

  return { playTurn, isLoading, lastResult, capturedImage, error, dismissResult }
}
