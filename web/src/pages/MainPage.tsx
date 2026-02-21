import { useCamera } from '../hooks/useCamera'

export function MainPage() {
  const { videoRef, isActive, error, start, stop } = useCamera()

  return (
    <div className="flex flex-col h-full p-4 gap-4">
      <h1 className="text-xl font-bold text-gray-900">謎解きカメラ</h1>

      <div className="relative aspect-[3/4] bg-gray-900 rounded-2xl overflow-hidden">
        {isActive ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            <p>カメラを起動してください</p>
          </div>
        )}
      </div>

      {error && (
        <p className="text-sm text-red-500 text-center">{error}</p>
      )}

      <button
        onClick={isActive ? stop : start}
        className={`w-full py-3 rounded-xl font-semibold text-white transition-colors ${
          isActive
            ? 'bg-red-500 active:bg-red-600'
            : 'bg-indigo-600 active:bg-indigo-700'
        }`}
      >
        {isActive ? 'カメラ停止' : 'カメラ起動'}
      </button>
    </div>
  )
}
