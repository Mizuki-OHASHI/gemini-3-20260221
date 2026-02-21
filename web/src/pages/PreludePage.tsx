import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGame } from "../contexts/GameContext";

const START_DIALOG = [
  "付き合って、1年が経った。",
  "最初のデートは水族館だった。暗い館内を2人で歩きながら、出口近くのショップでお揃いのコップを買った。",
  "「これで毎朝コーヒー飲もう」と恋人が言って、あなたは笑いながら頷いた。",
  "それから季節が4つ過ぎて、気がつけば同じ部屋で眠るようになっていた。",
  "幸せだった。本当に、それだけだった。",
];

const EXPLAIN_RULE = [
  "恋人は目の前にはいない。声も聞こえない。",
  "でも写真には映るようだ。",
  "写真を使えば恋人の伝えたいことがわかるかもしれない。",
];

const DEATH_DIALOG = "朝倉澪さんが、亡くなりました。";
const MESSAGE_FROM_HELL = "ただいま";

const HAIR_COLORS = [
  { id: "black", label: "黒" },
  { id: "brown", label: "茶" },
  { id: "blonde", label: "金" },
  { id: "silver", label: "銀" },
];

const HAIR_LENGTHS = [
  { id: "short", label: "ショート" },
  { id: "medium", label: "ミディアム" },
  { id: "long", label: "ロング" },
];

const HAIR_COLOR_MAP: Record<string, string> = {
  black: "黒髪",
  brown: "茶髪",
  blonde: "金髪",
  silver: "銀髪",
};

const HAIR_LENGTH_MAP: Record<string, string> = {
  short: "ショートヘア",
  medium: "ミディアムヘア",
  long: "ロングヘア",
};

type PreludePageProps = {
  onComplete?: () => void;
};

export function PreludePage({ onComplete }: PreludePageProps) {
  const navigate = useNavigate();
  const { createGame, generateAvatar, setHideBottomNav } = useGame();

  useEffect(() => {
    setHideBottomNav(true);
    return () => setHideBottomNav(false);
  }, [setHideBottomNav]);
  const [step, setStep] = useState(0);
  const [hairColor, setHairColor] = useState<string | null>(null);
  const [hairLength, setHairLength] = useState<string | null>(null);
  const [partnerName, setPartnerName] = useState("澪");
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [isGeneratingAvatar, setIsGeneratingAvatar] = useState(false);
  const [avatarError, setAvatarError] = useState<string | null>(null);
  const [blackout, setBlackout] = useState(false);

  const goDark = () => {
    setBlackout(true);
    window.setTimeout(() => {
      setStep(2);
      setBlackout(false);
    }, 900);
  };

  const canGenerateAvatar = Boolean(
    hairColor && hairLength && partnerName.trim(),
  );

  const handleGenerateAvatar = async () => {
    if (!canGenerateAvatar || isGeneratingAvatar || !hairColor || !hairLength) {
      return;
    }

    setAvatarError(null);
    setIsGeneratingAvatar(true);
    setAvatarUrl(null);

    try {
      // 髪色/長さから ghost_description を構築
      const ghostDescription = `${HAIR_COLOR_MAP[hairColor]}の${HAIR_LENGTH_MAP[hairLength]}の少女。白いワンピースを着て、悲しげな表情をしている。`;

      // ゲーム作成 → アバター生成
      const newGameId = await createGame(ghostDescription);
      const url = await generateAvatar(newGameId);
      setAvatarUrl(url);
    } catch (error) {
      setAvatarError(`アバター生成に失敗しました。(${String(error)})`);
    } finally {
      setIsGeneratingAvatar(false);
    }
  };

  return (
    <div className="relative min-h-dvh overflow-hidden">
      {step < 2 ? (
        <div className="min-h-dvh p-4 bg-gradient-to-b from-[#f6e8c5] via-[#f2d7b5] to-[#d9b99b] text-[#2d1e18]">
          {step === 0 && (
            <section className="space-y-5 animate-spirit-reveal">
              <div className="rounded-2xl border border-[#c99569] bg-[#fff8ea]/90 p-5 shadow-[0_10px_30px_rgba(121,70,35,0.15)]">
                <p className="text-xs tracking-[0.2em] text-[#8a4a2b] uppercase">
                  Game Start
                </p>
                <h1 className="mt-2 text-2xl font-bold">
                  恋人のアバターを作成
                </h1>
                <p className="mt-2 text-sm text-[#5f3b2e]">
                  最初の思い出は明るかった。髪の色と長さを選んで、あなたの中の「恋人」を生成してください。
                </p>
              </div>

              <div className="rounded-2xl border border-[#d8b493] bg-[#fff9ef] p-4 space-y-4">
                <div className="space-y-2">
                  <p className="text-xs font-medium text-[#8a4a2b]">髪の色</p>
                  <div className="grid grid-cols-4 gap-2">
                    {HAIR_COLORS.map((option) => (
                      <button
                        key={option.id}
                        onClick={() => setHairColor(option.id)}
                        className={`rounded-xl border px-2 py-2 text-xs font-semibold ${
                          hairColor === option.id
                            ? "border-[#8a4a2b] bg-[#f3dfc8] text-[#5f3b2e]"
                            : "border-[#d8b493] bg-white text-[#6e4a3b]"
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-medium text-[#8a4a2b]">髪の長さ</p>
                  <div className="grid grid-cols-3 gap-2">
                    {HAIR_LENGTHS.map((option) => (
                      <button
                        key={option.id}
                        onClick={() => setHairLength(option.id)}
                        className={`rounded-xl border px-2 py-2 text-xs font-semibold ${
                          hairLength === option.id
                            ? "border-[#8a4a2b] bg-[#f3dfc8] text-[#5f3b2e]"
                            : "border-[#d8b493] bg-white text-[#6e4a3b]"
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <div className="rounded-2xl border border-[#d8b493] bg-[#fff9ef] p-4">
                <label
                  htmlFor="partner-name"
                  className="text-xs font-medium text-[#8a4a2b]"
                >
                  恋人の名前
                </label>
                <input
                  id="partner-name"
                  value={partnerName}
                  onChange={(event) => setPartnerName(event.target.value)}
                  className="mt-2 w-full rounded-xl border border-[#d8b493] bg-white px-3 py-2 text-sm text-[#2d1e18] outline-none focus:border-[#8a4a2b]"
                  maxLength={20}
                />
              </div>

              <button
                onClick={handleGenerateAvatar}
                disabled={!canGenerateAvatar || isGeneratingAvatar}
                className="w-full rounded-full bg-[#8a4a2b] px-5 py-3 text-sm font-semibold text-[#fff2e0] disabled:cursor-not-allowed disabled:bg-[#bb9a82]"
              >
                {isGeneratingAvatar ? "生成中..." : "アバターを生成する"}
              </button>

              {avatarError && (
                <p className="text-sm text-[#7c2d12]">{avatarError}</p>
              )}

              {avatarUrl && (
                <div className="rounded-2xl border border-[#d8b493] bg-[#fff9ef] p-4 space-y-3 animate-spirit-reveal">
                  <p className="text-xs font-medium text-[#8a4a2b]">
                    生成結果プレビュー
                  </p>
                  <img
                    src={avatarUrl}
                    alt="生成した恋人のアバター"
                    className="aspect-square w-full rounded-2xl object-cover bg-white"
                  />
                  <button
                    onClick={() => setStep(1)}
                    className="w-full rounded-full bg-[#8a4a2b] px-5 py-3 text-sm font-semibold text-[#fff2e0]"
                  >
                    思い出へ進む
                  </button>
                </div>
              )}
            </section>
          )}

          {step === 1 && (
            <section className="space-y-4 animate-spirit-reveal">
              <div className="rounded-2xl border border-[#c99569] bg-[#fff8ea]/95 p-5">
                <p className="text-xs tracking-[0.18em] text-[#8a4a2b] uppercase">
                  Memory
                </p>
                <h2 className="mt-2 text-2xl font-bold">
                  {partnerName}との楽しかった思い出
                </h2>
              </div>

              <div className="rounded-2xl border border-[#d8b493] bg-[#fff9ef] p-4 space-y-4 text-sm">
                {START_DIALOG.map((line, index) => (
                  <p key={index} className="leading-relaxed">
                    {line}
                  </p>
                ))}
              </div>

              <button
                onClick={goDark}
                className="w-full rounded-full bg-[#8a4a2b] px-5 py-3 text-sm font-semibold text-[#fff2e0]"
              >
                その朝の知らせを見る
              </button>
            </section>
          )}
        </div>
      ) : (
        <div className="min-h-dvh bg-[var(--color-void)] p-4 text-[var(--color-whisper)]">
          <section className="space-y-4 animate-spirit-reveal">
            <div className="rounded-2xl border border-[var(--color-mist)] bg-[var(--color-dusk)] p-5">
              <p className="text-xs tracking-[0.22em] text-[var(--color-blood)] uppercase">
                Breaking News
              </p>
              <h2 className="mt-2 text-2xl font-bold text-[var(--color-frost)]">
                {DEATH_DIALOG}
              </h2>
              {/* <p className="mt-4 text-lg text-[var(--color-spirit)]">
                「{MESSAGE_FROM_HELL}」
              </p> */}
            </div>

            <div className="rounded-2xl border border-[var(--color-mist)] bg-[var(--color-shadow)] p-4 text-sm space-y-3">
              {EXPLAIN_RULE.map((line, index) => (
                <p key={index} className="leading-relaxed">
                  {line}
                </p>
              ))}
            </div>

            <button
              onClick={() => {
                if (onComplete) {
                  onComplete();
                  return;
                }
                navigate("/", { replace: true });
              }}
              className="w-full rounded-full border border-[var(--color-mist)] bg-[var(--color-shadow)] px-5 py-3 text-sm font-semibold text-[var(--color-frost)]"
            >
              調査を開始する
            </button>
          </section>
        </div>
      )}

      <div
        className={`pointer-events-none absolute inset-0 bg-[var(--color-void)] transition-opacity duration-900 ${
          blackout ? "opacity-100" : "opacity-0"
        }`}
      />
    </div>
  );
}
