/**
 * speech-recognition.d.ts
 *
 * Type declarations for the Web Speech API.
 * The standard `lib.dom.d.ts` includes these but they are not always
 * exposed under the correct global names in all TypeScript versions.
 */

interface SpeechRecognition extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start(): void
  stop(): void
  abort(): void
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
  onend: (() => void) | null
}

interface SpeechRecognitionEvent extends Event {
  readonly resultIndex: number
  readonly results: SpeechRecognitionResultList
}

interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string
  readonly message: string
}

declare var SpeechRecognition: {
  new (): SpeechRecognition
}

declare var webkitSpeechRecognition: {
  new (): SpeechRecognition
}
