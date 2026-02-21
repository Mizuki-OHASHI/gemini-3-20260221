import { useState } from "react";
import { suspects } from "../constants/characters";
import { useGame } from "../contexts/GameContext";

interface Props {
  onCorrect: () => void;
  onClose: () => void;
}

export function AccusationOverlay({ onCorrect, onClose }: Props) {
  const { accuse } = useGame();
  const [selectedSuspect, setSelectedSuspect] = useState<string | null>(null);
  const [reason, setReason] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!selectedSuspect || !reason.trim() || isLoading) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const result = await accuse(selectedSuspect, reason);
      if (result.correct) {
        onCorrect();
      } else {
        setErrorMessage(result.message);
      }
    } catch {
      setErrorMessage("送信中にエラーが発生しました。もう一度お試しください。");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-[var(--color-void)]/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[var(--color-dusk)] border border-[var(--color-mist)] rounded-2xl p-5 w-full max-w-md max-h-[90vh] overflow-y-auto space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-bold text-[var(--color-frost)]">
            犯人を指名する
          </h2>
          <button
            onClick={onClose}
            className="text-[var(--color-ash)] text-xl leading-none"
          >
            &times;
          </button>
        </div>

        <div className="space-y-2">
          <p className="text-xs text-[var(--color-ash)]">容疑者を選択</p>
          {suspects.map((s) => (
            <button
              key={s.name}
              onClick={() => setSelectedSuspect(s.name)}
              className={`w-full text-left p-3 rounded-xl border transition-all ${
                selectedSuspect === s.name
                  ? "border-[var(--color-phantom)] bg-[var(--color-phantom)]/10"
                  : "border-[var(--color-mist)] bg-[var(--color-shadow)]"
              }`}
            >
              <span className="text-sm font-bold text-[var(--color-frost)]">
                {s.name}
              </span>
              <span className="text-xs text-[var(--color-ash)] ml-2">
                {s.relation}
              </span>
            </button>
          ))}
        </div>

        <div className="space-y-2">
          <p className="text-xs text-[var(--color-ash)]">犯人だと思う理由</p>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="手がかりをもとに推理を書いてください..."
            className="w-full h-24 bg-[var(--color-shadow)] border border-[var(--color-mist)] rounded-xl p-3 text-sm text-[var(--color-frost)] placeholder:text-[var(--color-ash)]/50 resize-none outline-none focus:border-[var(--color-phantom)]"
          />
        </div>

        {errorMessage && (
          <div className="text-sm text-[var(--color-blood)] bg-[var(--color-blood)]/10 rounded-xl p-3">
            {errorMessage}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={!selectedSuspect || !reason.trim() || isLoading}
          className="w-full py-3 rounded-full bg-[var(--color-phantom)] text-[var(--color-frost)] font-bold text-sm disabled:opacity-40 transition-opacity"
        >
          {isLoading ? "判定中..." : "告発する"}
        </button>
      </div>
    </div>
  );
}
