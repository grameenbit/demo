export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col items-center justify-center p-6">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full text-center shadow-2xl">
        <div className="w-16 h-16 bg-purple-600/20 border border-purple-500/40 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl font-black text-purple-400">👋</span>
        </div>
        <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">Hello World</h1>
        <p className="text-slate-400 text-sm">Welcome to your clean React + Vite + Tailwind application.</p>
      </div>
    </div>
  )
}