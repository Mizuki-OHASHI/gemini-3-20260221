const ITEMS = [
  { key: 'bookshelf', label: '本棚', icon: '📚' },
  { key: 'clock', label: '時計', icon: '🕰️' },
  { key: 'mirror', label: '鏡', icon: '🪞' },
]

export function ProgressIndicator({ clearedItems }: { clearedItems: string[] }) {
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
    </div>
  )
}
