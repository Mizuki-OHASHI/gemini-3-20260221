import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCamera } from "../hooks/useCamera";
import { useGameTurn } from "../hooks/useGameTurn";
import { useGame } from "../contexts/GameContext";
import { ProgressIndicator } from "../components/ProgressIndicator";
import { PreludePage } from "./PreludePage";

const PRELUDE_SEEN_KEY = "prelude_seen_v1";

export function MainPage() {
  const navigate = useNavigate();
  const [showPrelude, setShowPrelude] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.sessionStorage.getItem(PRELUDE_SEEN_KEY) !== "1";
  });
  const {
    videoRef,
    isActive,
    error: cameraError,
    start,
    capture,
  } = useCamera();
  const {
    playTurn,
    isLoading,
    lastResult,
    error: turnError,
    dismissResult,
  } = useGameTurn();
  const { gameId, clearedItems, gameSolved, isInitializing } = useGame();

  // gameId がない場合（リセット後など）も PreludePage を表示
  const needsPrelude = showPrelude || !gameId;

  useEffect(() => {
    if (!needsPrelude) {
      start();
    }
  }, [needsPrelude, start]);

  useEffect(() => {
    if (gameSolved) {
      navigate("/ending?result=success", { replace: true });
    }
  }, [gameSolved, navigate]);

  if (needsPrelude) {
    return (
      <PreludePage
        onComplete={() => {
          window.sessionStorage.setItem(PRELUDE_SEEN_KEY, "1");
          setShowPrelude(false);
        }}
      />
    );
  }

  const handleShutter = () => {
    if (lastResult) {
      dismissResult();
      return;
    }
    playTurn(capture);
  };

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-[var(--color-ash)] animate-ghost-pulse">
          ゲームを読み込み中...
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full p-4 gap-3">
      <ProgressIndicator clearedItems={clearedItems} />

      <div className="relative aspect-[3/4] bg-[var(--color-dusk)] border border-[var(--color-mist)] rounded-2xl overflow-hidden">
        {/* カメラフィード */}
        {isActive ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-[var(--color-ash)] gap-3">
            <p>カメラを起動できませんでした</p>
            <button
              onClick={start}
              className="px-4 py-2 bg-[var(--color-phantom)] text-[var(--color-frost)] rounded-lg text-sm"
            >
              カメラ起動
            </button>
          </div>
        )}

        {/* ローディングオーバーレイ */}
        {isLoading && (
          <div className="absolute inset-0 bg-[var(--color-void)]/70 flex flex-col items-center justify-center gap-3">
            <div className="w-10 h-10 border-4 border-[var(--color-spirit)]/30 border-t-[var(--color-spirit)] rounded-full animate-spin animate-shimmer" />
            <p className="text-[var(--color-spirit)] text-sm font-medium animate-ghost-pulse">
              霊感知中...
            </p>
          </div>
        )}

        {/* 結果表示 */}
        {lastResult && !isLoading && (
          <div className="absolute inset-0 flex flex-col">
            {lastResult.ghost_url ? (
              <img
                src={lastResult.ghost_url}
                alt="幽霊合成写真"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full bg-[var(--color-dusk)]" />
            )}
            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[var(--color-void)]/90 to-transparent">
              <div className="bg-[var(--color-shadow)]/90 border border-[var(--color-mist)] rounded-xl p-3 backdrop-blur-sm">
                <p className="text-[var(--color-whisper)] text-sm leading-relaxed">
                  {lastResult.message}
                </p>
                {lastResult.ghost_message && (
                  <p className="text-[var(--color-spirit)] text-sm mt-2 italic">
                    「{lastResult.ghost_message}」
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* エラー表示 */}
      {(cameraError || turnError) && (
        <p className="text-sm text-[var(--color-blood)] text-center">
          {cameraError || turnError}
        </p>
      )}

      {/* シャッターボタン */}
      {!gameSolved && (
        <div className="flex flex-col items-center py-2 gap-3">
          <button
            onClick={handleShutter}
            disabled={isLoading || !isActive}
            className={`w-16 h-16 rounded-full border-4 transition-all ${
              isLoading || !isActive
                ? "border-[var(--color-mist)] bg-[var(--color-dusk)] cursor-not-allowed"
                : lastResult
                  ? "border-[var(--color-phantom)] bg-[var(--color-phantom)]/20 shadow-[var(--glow-phantom)] active:bg-[var(--color-phantom)]/40"
                  : "border-[var(--color-mist)] bg-[var(--color-shadow)] active:bg-[var(--color-dusk)] active:scale-95"
            } flex items-center justify-center`}
          >
            {lastResult ? (
              <span className="text-[var(--color-frost)] text-xs font-bold">
                再撮影
              </span>
            ) : (
              <div className="w-12 h-12 rounded-full bg-[var(--color-shadow)] border-2 border-[var(--color-mist)]" />
            )}
          </button>
          <button
            onClick={() => navigate("/ending?result=escape")}
            className="text-xs text-[var(--color-ash)] underline underline-offset-4"
          >
            捜査を打ち切る
          </button>
        </div>
      )}
    </div>
  );
}
