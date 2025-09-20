import axios from 'axios'

const token = () => localStorage.getItem('token') || ''
const baseURL = import.meta.env.VITE_API_BASE_URL || ''
const useMock = (!baseURL || baseURL === '/') && (import.meta.env.VITE_MOCK_API ?? 'true') !== 'false'

if (!useMock) {
  export const api = axios.create({ baseURL })
  api.interceptors.request.use((cfg)=>{
    const t = token()
    if (t) cfg.headers['Authorization'] = `Bearer ${t}`
    return cfg
  })
} else {
  const wait = (ms)=> new Promise(r=>setTimeout(r, ms))
  const mockEvents = []
  const apiImpl = {
    async post(path, body) {
      if (path.startsWith('/inference/frame')) {
        await wait(200)
        const ts = Date.now()
        const event = {
          id: mockEvents.length+1,
          type: 'no_helmet',
          score: 0.82,
          plate_text: 'AP09AB1234',
          plate_conf: 0.93,
          speed_kph: 64.5,
          evidence_path: '/evidence/sample.jpg',
          evidence_plate_path: '/evidence/sample_plate.jpg',
          meta: { timestamp_ms: ts, speed_kph: 64.5, bboxes: [[10,10,100,100]] },
          created_at: new Date(ts).toISOString()
        }
        mockEvents.unshift(event)
        return { data: { result: { violations: [{ type: 'no_helmet', score: 0.82 }], plate: { text: 'AP09AB1234', confidence: 0.93 }, evidence: event.meta }, verified: [{ type: 'no_helmet', score: 0.82 }], challan: { status: 'mock' } } }
      }
      if (path.startsWith('/issue-fine')) {
        await wait(150)
        return { data: { status: 'mock', ok: true } }
      }
      throw new Error('Unknown mock POST '+path)
    },
    async get(path, { params } = {}) {
      if (path.startsWith('/events')) {
        await wait(150)
        const page = params?.page || 1
        const pageSize = params?.page_size || 20
        const items = mockEvents.slice((page-1)*pageSize, page*pageSize)
        return { data: { total: mockEvents.length, page, page_size: pageSize, items } }
      }
      throw new Error('Unknown mock GET '+path)
    }
  }
  export const api = apiImpl
  if (!localStorage.getItem('mock-banner-shown')) {
    console.info('API is running in MOCK mode. Set VITE_API_BASE_URL to call real backend.')
    localStorage.setItem('mock-banner-shown', '1')
  }
}
