import { useState, useRef, useEffect } from 'react'
import type { FormEvent } from 'react'
import { api, isApiError } from '../lib/api'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition'

// ─── Types ────────────────────────────────────────────────────────────────────

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface ChatResponse {
  response: string
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  const { transcript, isListening, startListening, stopListening, isSupported } =
    useSpeechRecognition()

  // When the speech recognition produces a transcript, put it in the input box.
  useEffect(() => {
    if (transcript) setInput(transcript)
  }, [transcript])

  // Auto-scroll to the latest message.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  async function sendMessage(text: string) {
    if (!text.trim()) return
    setError('')
    const userMessage: Message = { role: 'user', content: text.trim() }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const data = await api.post<ChatResponse>('/api/chat', { message: text.trim() })
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response }])
    } catch (err) {
      setError(isApiError(err) ? err.message : 'Failed to get a response')
    } finally {
      setIsLoading(false)
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    sendMessage(input)
  }

  function toggleMic() {
    if (isListening) {
      stopListening()
    } else {
      setInput('')
      startListening()
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 60px)' }}>

      {/* Message list */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem 1rem' }}>
        <div style={{ maxWidth: 720, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {messages.length === 0 && (
            <p style={{ color: 'var(--color-text-muted)', textAlign: 'center', marginTop: '4rem' }}>
              Start a conversation — type a message or press the mic.
            </p>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '75%',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-md)',
                backgroundColor:
                  msg.role === 'user' ? 'var(--color-accent-dark)' : 'var(--color-surface)',
                border: msg.role === 'assistant' ? '1px solid var(--color-border)' : 'none',
                lineHeight: 1.5,
                whiteSpace: 'pre-wrap',
              }}
            >
              {msg.content}
            </div>
          ))}

          {isLoading && (
            <div
              style={{
                alignSelf: 'flex-start',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-surface)',
                border: '1px solid var(--color-border)',
                color: 'var(--color-text-muted)',
                fontStyle: 'italic',
              }}
            >
              Thinking…
            </div>
          )}

          {error && <p className="form-error" style={{ textAlign: 'center' }}>{error}</p>}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input bar */}
      <div style={{ borderTop: '1px solid var(--color-border)', padding: '1rem', backgroundColor: 'var(--color-bg)' }}>
        <form
          onSubmit={handleSubmit}
          style={{ maxWidth: 720, margin: '0 auto', display: 'flex', gap: '0.5rem' }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? 'Listening…' : 'Type a message…'}
            disabled={isLoading}
            style={{ flex: 1 }}
          />

          {isSupported && (
            <button
              type="button"
              className="btn btn-ghost"
              onClick={toggleMic}
              title={isListening ? 'Stop recording' : 'Start voice input'}
              style={{ borderColor: isListening ? 'var(--color-accent)' : undefined }}
            >
              {isListening ? '⏹' : '🎤'}
            </button>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
