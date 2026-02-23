import { useState, useEffect, useCallback, useRef } from 'react'

interface SpeechRecognitionResult {
  transcript: string
  isListening: boolean
  isSupported: boolean
  startListening: () => void
  stopListening: () => void
  error: string | null
}


/**
 * useSpeechRecognition
 *
 * Wraps the browser's Web Speech API (SpeechRecognition / webkitSpeechRecognition).
 * Returns a transcript string that updates in real time as the user speaks.
 * `isSupported` is false on browsers that don't implement the API (Firefox, Safari < 14.1).
 */
export function useSpeechRecognition(): SpeechRecognitionResult {
  const [transcript, setTranscript] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const recognitionRef = useRef<SpeechRecognition | null>(null)

  const SpeechRecognitionAPI =
    window.SpeechRecognition ?? window.webkitSpeechRecognition

  const isSupported = Boolean(SpeechRecognitionAPI)

  useEffect(() => {
    if (!SpeechRecognitionAPI) return

    const recognition = new SpeechRecognitionAPI()
    recognition.continuous = false       // stop after first pause
    recognition.interimResults = true    // stream partial results
    recognition.lang = 'en-US'

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = ''
      let final = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const text = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          final += text
        } else {
          interim += text
        }
      }
      setTranscript(final || interim)
    }

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      setError(event.error)
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognitionRef.current = recognition

    return () => {
      recognition.abort()
    }
  }, [SpeechRecognitionAPI])

  const startListening = useCallback(() => {
    if (!recognitionRef.current) return
    setTranscript('')
    setError(null)
    setIsListening(true)
    recognitionRef.current.start()
  }, [])

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return
    recognitionRef.current.stop()
    setIsListening(false)
  }, [])

  return { transcript, isListening, isSupported, startListening, stopListening, error }
}
