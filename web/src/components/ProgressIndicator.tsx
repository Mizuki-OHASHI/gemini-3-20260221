const ITEMS = [
  { key: 'cup', label: 'コップ', icon: '☕' },
  { key: 'air_conditioner', label: 'エアコン', icon: '❄️' },
  { key: 'clock', label: '時計', icon: '🕰️' },
]

const FINAL_ITEM = { key: 'earring', label: '証拠品', icon: '💍' }

export function ProgressIndicator({ clearedItems }: { clearedItems: string[] }) {
  const allPhase1Cleared = ITEMS.every((item) => clearedItems.includes(item.key))
  const earringCleared = clearedItems.includes(FINAL_ITEM.key)

  return (
    <div className="flex justify-center gap-4 py-2">
      {ITEMS.map((item, index) => {
        const cleared = clearedItems.includes(item.key)
        return (
          <div key={item.key} className="flex flex-col items-center gap-1">
            <div
              className={`w-12 h-12 rounded-full flex items-center justify-center text-lg transition-colors ${
                cleared
                  ? 'bg-[var(--color-phantom)] text-[var(--color-frost)] shadow-[var(--glow-phantom)] animate-spirit-reveal'
                  : 'border-2 border-[var(--color-mist)] text-[var(--color-ash)] animate-flicker'
              }`}
            >
              {cleared ? item.icon : '?'}
            </div>
            <span className={`text-xs ${cleared ? 'text-[var(--color-phantom)] font-semibold animate-spirit-reveal' : 'text-[var(--color-ash)]'}`}>
              {cleared ? item.label : `手がかり${index + 1}`}
            </span>
          </div>
        )
      })}

      {allPhase1Cleared && (
        <div className="flex flex-col items-center gap-1 animate-spirit-reveal">
          <div
            className={`w-12 h-12 rounded-full flex items-center justify-center text-lg transition-colors ${
              earringCleared
                ? 'bg-[var(--color-phantom)] text-[var(--color-frost)] shadow-[var(--glow-phantom)]'
                : 'border-2 border-[var(--color-spirit)] text-[var(--color-spirit)] animate-ghost-pulse'
            }`}
          >
            {earringCleared ? FINAL_ITEM.icon : '?'}
          </div>
          <span className={`text-xs ${earringCleared ? 'text-[var(--color-phantom)] font-semibold' : 'text-[var(--color-spirit)]'}`}>
            {earringCleared ? FINAL_ITEM.label : '最後の手がかり'}
          </span>
        </div>
      )}
    </div>
  )
}
