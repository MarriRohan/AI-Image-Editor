import { useEffect, useRef, useState } from 'react'
import { api } from '../utils/api'
import { notify } from '../utils/notify'

export default function LiveView() {
  const fileRef = useRef(null)
  const [result, setResult] = useState(null)
  const [uploading, setUploading] = useState(false)

  async function onUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    setUploading(true)
    try {
      const res = await api.post('/inference/frame', form)
      setResult(res.data)
      notify('Frame processed', 'success')
    } catch (e) {
      setResult({ error: 'Backend not reachable or unauthorized' })
      notify('Backend not reachable or unauthorized', 'error')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <input ref={fileRef} type="file" accept="image/*" onChange={onUpload} className="block" disabled={uploading} />
        {uploading && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="inline-block w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></span>
            Uploading...
          </div>
        )}
      </div>
      {result && (
        <pre className="bg-white p-4 rounded shadow overflow-auto text-xs">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  )
}
