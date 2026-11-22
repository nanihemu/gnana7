import { useState } from 'react'
import { api, errMsg } from '../api'

interface Msg {
  role: 'user' | 'bot'
  text: string
  sources?: { id: number; title: string; score: number }[]
}

export default function Chatbot() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)

  async function ask(e: React.FormEvent) {
    e.preventDefault()
    const q = input.trim()
    if (!q || busy) return
    const history = messages
      .slice(-6)
      .map((m) => ({ role: m.role, content: m.text }))
    setMessages((ms) => [...ms, { role: 'user', text: q }])
    setInput('')
    setBusy(true)
    try {
      const { data } = await api.post<{
        answer: string
        grounded: boolean
        sources?: { id: number; title: string; score: number }[]
      }>('/chat/', { question: q, history })
      setMessages((ms) => [
        ...ms,
        { role: 'bot', text: data.answer, sources: data.sources || [] },
      ])
    } catch (e) {
      setMessages((ms) => [...ms, { role: 'bot', text: errMsg(e) }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      {open && (
        <div className="chat-panel">
          <header>
            <span>AI Tutor 🤖</span>
            <button
              className="btn sm secondary"
              style={{ padding: '2px 8px' }}
              onClick={() => setOpen(false)}
            >
              ✕
            </button>
          </header>
          <div className="chat-msgs">
            {messages.length === 0 && (
              <p className="muted" style={{ padding: 8 }}>
                Ask about anything in your school's learning material — topics,
                quizzes, science, maths…
              </p>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`m ${m.role}`}>
                {m.text}
                {m.sources && m.sources.length > 0 && (
                  <div className="chat-sources">
                    Sources: {m.sources.map((s) => s.title).join(', ')}
                  </div>
                )}
              </div>
            ))}
            {busy && <div className="m bot muted">Thinking…</div>}
          </div>
          <form onSubmit={ask}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about a topic…"
            />
            <button className="btn sm" type="submit" disabled={busy || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      )}
      {!open && (
        <button className="chat-fab" onClick={() => setOpen(true)} aria-label="Open AI tutor">
          💬
        </button>
      )}
    </>
  )
}
