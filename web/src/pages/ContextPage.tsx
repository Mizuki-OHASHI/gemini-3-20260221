import { useGame } from "../contexts/GameContext";

const ALL_ITEMS = [
  { key: "bookshelf", label: "本棚", chapter: 1 },
  { key: "clock", label: "時計", chapter: 2 },
  { key: "mirror", label: "鏡", chapter: 3 },
];

export function ContextPage() {
  const { chapters, clearedItems, gameSolved } = useGame();

  return (
    <div className="flex flex-col p-4 gap-4">
      <h1 className="text-xl font-bold text-[var(--color-frost)]">
        記憶の断片
      </h1>

      <p className="text-sm text-[var(--color-ash)]">
        手がかり {clearedItems.length}/3
      </p>

      <div className="space-y-4">
        {ALL_ITEMS.map((item) => {
          const cleared = clearedItems.includes(item.key);
          const chapterData = chapters.find((c) => c.chapter === item.chapter);

          if (cleared && chapterData) {
            return (
              <div
                key={item.key}
                className="bg-[var(--color-dusk)] border border-[var(--color-mist)] rounded-2xl p-5 space-y-3 animate-spirit-reveal"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs bg-[var(--color-phantom)] text-[var(--color-frost)] px-2 py-0.5 rounded-full">
                    第{item.chapter}章
                  </span>
                  <span className="text-sm text-[var(--color-ember)] font-medium">
                    {item.label}
                  </span>
                </div>
                <p className="text-[var(--color-whisper)] leading-relaxed text-sm">
                  {chapterData.story}
                </p>
              </div>
            );
          }

          return (
            <div
              key={item.key}
              className="bg-[var(--color-dusk)]/50 rounded-2xl p-5 space-y-2"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs bg-[var(--color-mist)] text-[var(--color-ash)] px-2 py-0.5 rounded-full">
                  第{item.chapter}章
                </span>
                <span className="text-sm text-[var(--color-ash)] animate-flicker">
                  ???
                </span>
              </div>
              <p className="text-[var(--color-ash)]/60 text-sm">
                まだ発見されていません
              </p>
            </div>
          );
        })}
      </div>

      {gameSolved && (
        <div className="bg-[var(--color-dusk)] border border-[var(--color-mist)] rounded-2xl p-5 space-y-3">
          <h2 className="text-lg font-semibold text-[var(--color-spirit)]">
            終章
          </h2>
          <p className="text-[var(--color-whisper)] leading-relaxed text-sm">
            犯人は見つかり逮捕された。
            でも澪はもう帰ってこない。
          </p>
          <p className="text-[var(--color-ash)] text-xs italic">
            ──これからも部屋で見守ってくれるのだろうか。
          </p>
        </div>
      )}
    </div>
  );
}
