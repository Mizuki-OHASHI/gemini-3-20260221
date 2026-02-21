export function ContextPage() {
  return (
    <div className="flex flex-col p-4 gap-6">
      <h1 className="text-xl font-bold text-gray-900">ストーリー</h1>

      <div className="bg-gray-50 rounded-2xl p-5 space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Chapter 1</h2>
        <p className="text-gray-600 leading-relaxed">
          ここにパズルの背景ストーリーやヒントが表示されます。
          カメラで周囲を探索し、隠された謎を解き明かしましょう。
        </p>
      </div>

      <div className="bg-indigo-50 rounded-2xl p-5 space-y-3">
        <h2 className="text-lg font-semibold text-indigo-800">ヒント</h2>
        <ul className="space-y-2 text-indigo-700 text-sm">
          <li className="flex gap-2">
            <span>1.</span>
            <span>ヒントがここに表示されます</span>
          </li>
        </ul>
      </div>
    </div>
  )
}
