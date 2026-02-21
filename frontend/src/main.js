import { createApp } from 'vue'
import App from './App.vue'
import './styles/main.css'

if ('scrollRestoration' in window.history) {
  window.history.scrollRestoration = 'manual'
}

function resetScrollToTop() {
  const root = document.documentElement
  const previousBehavior = root.style.scrollBehavior
  root.style.scrollBehavior = 'auto'

  window.scrollTo(0, 0)
  root.scrollTop = 0
  if (document.body) {
    document.body.scrollTop = 0
  }

  requestAnimationFrame(() => {
    window.scrollTo(0, 0)
    root.scrollTop = 0
    if (document.body) {
      document.body.scrollTop = 0
    }
    root.style.scrollBehavior = previousBehavior
  })
}

resetScrollToTop()
window.addEventListener('load', resetScrollToTop, { once: true })
window.addEventListener('pageshow', resetScrollToTop)

createApp(App).mount('#app')
