import { useEffect, useState } from 'react'
import { api } from '../utils/api'

export default function ViolationFeed() {
  const [items, setItems] = useState([])

  async function load(page=1) {
    try {
      const res = await api.get('/events', { params: { page }})
      setItems(res.data.items)
    } catch (e) {
      setItems([])
    }
  }

  useEffect(()=>{ load() },[])

  return (
    <div className="grid gap-4">
      {items.map(it => (
        <div key={it.id} className="bg-white p-4 rounded shadow">
          <div className="flex gap-4">
            <img src={it.evidence_path ? ('/evidence/' + it.evidence_path.split('/').pop()) : ''} alt="evidence" className="w-56 h-32 object-cover rounded" />
            <div className="text-sm">
              <div className="font-semibold">{it.type} • score {it.score?.toFixed(2)}</div>
              <div>Plate: {it.plate_text} ({(it.plate_conf||0).toFixed(2)})</div>
              <div>Speed: {(it.speed_kph||0).toFixed(1)} km/h</div>
              <div className="text-gray-500">{it.created_at}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
