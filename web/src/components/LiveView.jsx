import { useEffect, useRef, useState } from 'react'
import { api } from '../utils/api'

export default function LiveView() {
  const fileRef = useRef(null)
  const [result, setResult] = useState(null)

  async function onUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    const res = await api.post('/inference/frame', form)
    setResult(res.data)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <input ref={fileRef} type="file" accept="image/*" onChange={onUpload} className="block" />
      </div>
      {result && (
        <pre className="bg-white p-4 rounded shadow overflow-auto text-xs">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  )
}
