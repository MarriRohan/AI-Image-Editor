import { useState } from 'react'
import LiveView from './components/LiveView'
import ViolationFeed from './components/ViolationFeed'
import AdminPanel from './components/AdminPanel'

export default function App() {
  const [tab, setTab] = useState('live')
  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="flex gap-4 p-4 bg-white shadow">
        <button className={`px-3 py-2 rounded ${tab==='live'?'bg-blue-600 text-white':'bg-gray-200'}`} onClick={()=>setTab('live')}>Live</button>
        <button className={`px-3 py-2 rounded ${tab==='feed'?'bg-blue-600 text-white':'bg-gray-200'}`} onClick={()=>setTab('feed')}>Violations</button>
        <button className={`px-3 py-2 rounded ${tab==='admin'?'bg-blue-600 text-white':'bg-gray-200'}`} onClick={()=>setTab('admin')}>Admin</button>
      </nav>
      <main className="p-4">
        {tab==='live' && <LiveView />}
        {tab==='feed' && <ViolationFeed />}
        {tab==='admin' && <AdminPanel />}
      </main>
    </div>
  )
}
