import { useEffect, useState } from 'react'
import { api } from '../utils/api'

export default function AdminPanel() {
  const [items, setItems] = useState([])

  async function load() {
    const res = await api.get('/events')
    setItems(res.data.items)
  }

  async function approve(item) {
    const payload = {
      violations: [{ type: item.type, score: item.score }],
      plate: { text: item.plate_text, confidence: item.plate_conf },
      evidence: item.meta
    }
    const res = await api.post('/issue-fine', payload)
    alert(JSON.stringify(res.data))
  }

  useEffect(()=>{ load() },[])

  return (
    <div className="space-y-3">
      {items.map(it => (
        <div key={it.id} className="bg-white p-4 rounded shadow flex items-center justify-between">
          <div>
            <div className="font-semibold">{it.type} • {it.plate_text}</div>
            <div className="text-xs text-gray-500">{it.created_at}</div>
          </div>
          <button className="px-3 py-2 rounded bg-blue-600 text-white" onClick={()=>approve(it)}>Approve & Issue e-Challan</button>
        </div>
      ))}
    </div>
  )
}
