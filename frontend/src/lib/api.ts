/**
 * api.ts — thin fetch() wrapper for all Flask API calls.
 *
 * All requests go to /api/* which Vite proxies to Flask in dev,
 * and Flask serves directly in production.
 */

export interface ApiError {
  name: 'ApiError'
  status: number
  message: string
}

export function isApiError(err: unknown): err is ApiError {
  return (
    typeof err === 'object' &&
    err !== null &&
    (err as ApiError).name === 'ApiError'
  )
}

function makeApiError(status: number, message: string): ApiError {
  return { name: 'ApiError', status, message }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const res = await fetch(path, {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // send session cookie with every request
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let message = res.statusText
    try {
      const data = await res.json() as Record<string, string>
      message = data['error'] ?? data['message'] ?? message
    } catch {
      // response wasn't JSON — use status text as-is
    }
    throw makeApiError(res.status, message)
  }

  // 204 No Content — return undefined cast to T
  if (res.status === 204) return undefined as T

  return res.json() as Promise<T>
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body: unknown) => request<T>('POST', path, body),
  put: <T>(path: string, body: unknown) => request<T>('PUT', path, body),
  delete: <T>(path: string) => request<T>('DELETE', path),
}
