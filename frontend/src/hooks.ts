import { useCallback, useEffect, useState } from 'react'
import { api, errMsg } from './api'

export { api, errMsg }

function unwrap(body: unknown): unknown {
  if (body && typeof body === 'object' && !Array.isArray(body)) {
    const rec = body as Record<string, unknown>
    if (Array.isArray(rec.results)) return rec.results
  }
  return body
}

/** GET a list/resource and expose loading + error + reload. Pass null to disable fetching. */
export function useFetch<T>(url: string | null, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [tick, setTick] = useState(0)

  useEffect(() => {
    if (!url) {
      setLoading(false)
      return
    }
    let mounted = true
    setLoading(true)
    api
      .get<T>(url)
      .then((r) => {
        if (mounted) {
          // Transparently unwrap DRF pagination: {count, next, previous, results}.
          // Every API on this backend returns either a list/object directly or a
          // paginated envelope whose only array key is "results".
          setData(unwrap(r.data) as T)
          setError('')
        }
      })
      .catch((e) => mounted && setError(errMsg(e)))
      .finally(() => mounted && setLoading(false))
    return () => {
      mounted = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, tick, ...deps])

  const reload = useCallback(() => setTick((t) => t + 1), [])
  return { data, error, loading, reload, setData }
}

/** Simple POST/PUT/DELETE wrapper with busy/error state. */
export function useMutate<T = unknown>(url: string, method: 'post' | 'put' | 'patch' | 'delete' = 'post') {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const run = useCallback(
    async (payload?: unknown, params?: Record<string, unknown>): Promise<T | null> => {
      setBusy(true)
      setError('')
      try {
        const r = await api[method]<T>(url, payload, {
          ...(params ? { params } : {}),
        })
        return r.data
      } catch (e) {
        setError(errMsg(e))
        return null
      } finally {
        setBusy(false)
      }
    },
    [url, method],
  )

  return { run, busy, error, setError }
}
