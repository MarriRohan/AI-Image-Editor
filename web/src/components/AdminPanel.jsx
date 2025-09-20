import { useEffect, useState } from 'react'
import { api } from '../utils/api'
import { notify } from '../utils/notify'

export default function AdminPanel() {
  const [items, setItems] = useState([])
  const [busyId, setBusyId] = useState(null)

  async function load() {
    try {
      const res = await api.get('/events')
      setItems(res.data.items)
    } catch (e) {
      setItems([])
    }
  }

  async function approve(item) {
    try {
      setBusyId(item.id)
      const payload = {
        violations: [{ type: item.type, score: item.score }],
        plate: { text: item.plate_text, confidence: item.plate_conf },
        evidence: item.meta
      }
      const res = await api.post('/issue-fine', payload)
      notify('e-Challan issued (mock)', 'success')
    } catch (e) {
      notify('Failed to issue e-challan (backend not running)', 'error')
    } finally {
      setBusyId(null)
    }
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
          <button className="px-3 py-2 rounded bg-blue-600 text-white disabled:opacity-60 flex items-center gap-2" disabled={busyId===it.id} onClick={()=>approve(it)}>
            {busyId===it.id && <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>}
            Approve & Issue e-Challan
          </button>
        </div>
      ))}
    </div>
  )
}
