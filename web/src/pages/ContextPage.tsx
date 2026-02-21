import { useState } from "react";
import { useGame } from "../contexts/GameContext";
import { suspects } from "../constants/characters";

const ALL_ITEMS = [
  { key: "cup", label: "コップ" },
  { key: "air_conditioner", label: "エアコン" },
  { key: "clock", label: "時計" },
];

const SUSPECT_ACCENTS = ["#dc2626", "#d97706", "#7c3aed", "#0891b2"];

export function ContextPage() {
  const { hints, clearedItems, gameSolved } = useGame();
  const [openSuspect, setOpenSuspect] = useState<string | null>(null);

  return (
    <div className="flex flex-col p-4 gap-6 pb-8">
      {/* 記憶の断片 */}
      <section>
        <h1 className="text-xl font-bold text-[var(--color-frost)]">
          記憶の断片
        </h1>
        <p className="text-sm text-[var(--color-ash)] mt-1">
          手がかり {clearedItems.length}/3
        </p>

        <div className="space-y-4 mt-4">
          {ALL_ITEMS.map((item) => {
            const cleared = clearedItems.includes(item.key);
            const hintData = hints.find((h) => h.item === item.key);
            const clueNum = clearedItems.indexOf(item.key);

            if (cleared) {
              return (
                <div
                  key={item.key}
                  className="bg-[var(--color-dusk)] border border-[var(--color-mist)] rounded-2xl p-5 space-y-3 animate-spirit-reveal"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs bg-[var(--color-phantom)] text-[var(--color-frost)] px-2 py-0.5 rounded-full">
                      手がかり{clueNum + 1}
                    </span>
                    <span className="text-sm text-[var(--color-ember)] font-medium">
                      {item.label}
                    </span>
                  </div>
                  {hintData?.ghostUrl && (
                    <img
                      src={hintData.ghostUrl}
                      alt={`${item.label}の手がかり`}
                      className="w-full rounded-xl"
                    />
                  )}
                  {hintData?.message && (
                    <p className="text-[var(--color-whisper)] leading-relaxed text-sm">
                      {hintData.message}
                    </p>
                  )}
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
                    手がかり
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
      </section>

      {/* 容疑者ファイル */}
      <section>
        <div className="text-center mb-4">
          <p className="text-[var(--color-blood)] text-xs tracking-widest font-bold mb-1">
            ── 容疑者ファイル ──
          </p>
          <h2 className="text-lg font-bold text-[var(--color-frost)]">
            SUSPECTS
          </h2>
          <p className="text-xs text-[var(--color-ash)]/60 mt-0.5">
            恋人を殺した犯人は、この中にいる。
          </p>
        </div>

        <div className="space-y-3">
          {suspects.map((s, i) => {
            const accent = SUSPECT_ACCENTS[i];
            const isOpen = openSuspect === s.name;

            return (
              <div
                key={s.name}
                onClick={() => setOpenSuspect(isOpen ? null : s.name)}
                className="bg-[var(--color-dusk)] rounded-xl p-4 cursor-pointer transition-shadow"
                style={{
                  borderLeft: `4px solid ${accent}`,
                  boxShadow: isOpen
                    ? `0 0 0 1px ${accent}, 0 4px 20px rgba(0,0,0,0.3)`
                    : undefined,
                }}
              >
                <div className="flex items-center gap-3">
                  <img
                    src={`/${s.imagePath}`}
                    alt={s.name}
                    className="w-20 h-20 rounded-full shrink-0 object-cover"
                    style={{ border: `2px solid ${accent}` }}
                  />

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className="text-[0.65rem] font-bold px-1.5 py-0.5 rounded"
                        style={{
                          background: `${accent}20`,
                          color: accent,
                        }}
                      >
                        容疑者 {String(i + 1).padStart(2, "0")}
                      </span>
                    </div>

                    <h3 className="text-[var(--color-frost)] font-bold text-sm leading-tight">
                      {s.name}
                    </h3>
                    <p className="text-[var(--color-ash)] text-xs">
                      {s.nameReading}
                    </p>
                    <p className="text-[var(--color-ash)]/60 text-xs mt-0.5">
                      {s.age}歳 / {s.occupation}
                    </p>
                    <p
                      className="text-xs font-semibold mt-1"
                      style={{ color: accent }}
                    >
                      {s.relation}
                    </p>
                  </div>
                </div>

                {isOpen && (
                  <div className="mt-3 pt-3 border-t border-[var(--color-mist)] space-y-3">
                    <div>
                      <p className="text-[0.65rem] text-[var(--color-ash)]/60 font-bold tracking-wider mb-1">
                        自分から見た印象
                      </p>
                      <p className="text-[var(--color-whisper)] text-xs leading-relaxed">
                        {s.impression}
                      </p>
                    </div>
                    <div>
                      <p className="text-[0.65rem] text-[var(--color-ash)]/60 font-bold tracking-wider mb-1">
                        アリバイ
                      </p>
                      <p className="text-[var(--color-whisper)] text-xs leading-relaxed">
                        {s.aribai}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {gameSolved && (
        <div className="bg-[var(--color-dusk)] border border-[var(--color-mist)] rounded-2xl p-5 space-y-3">
          <h2 className="text-lg font-semibold text-[var(--color-spirit)]">
            終章
          </h2>
          <p className="text-[var(--color-whisper)] leading-relaxed text-sm">
            犯人は見つかり逮捕された。 でも澪はもう帰ってこない。
          </p>
          <p className="text-[var(--color-ash)] text-xs italic">
            ──これからも部屋で見守ってくれるのだろうか。
          </p>
        </div>
      )}
    </div>
  );
}
