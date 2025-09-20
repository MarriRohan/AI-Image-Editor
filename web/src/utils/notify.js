export function notify(message, type = 'info', timeout = 2500) {
  let root = document.getElementById('toast-root')
  if (!root) {
    root = document.createElement('div')
    root.id = 'toast-root'
    document.body.appendChild(root)
  }
  const el = document.createElement('div')
  el.className = `app-toast ${type === 'success' ? 'success' : type === 'error' ? 'error' : ''}`
  el.textContent = message
  root.appendChild(el)
  const remove = () => {
    el.style.animation = 'toast-out 160ms ease-in forwards'
    setTimeout(() => el.remove(), 180)
  }
  setTimeout(remove, timeout)
  return remove
}
