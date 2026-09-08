export function useApi() {
  const config = useRuntimeConfig()
  const { client } = useSupabase()

  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    if (!client) {
      throw new Error('Authentication is not configured yet.')
    }
    const { data } = await client.auth.getSession()
    if (!data.session) throw new Error('Please sign in before completing this action.')

    const response = await fetch(`${config.public.apiBaseUrl}${path}`, {
      ...options,
      headers: { Authorization: `Bearer ${data.session.access_token}`, ...(options.headers || {}) }
    })

    if (response.status === 204) {
      return null as T
    }

    const text = await response.text()
    let payload: any = {}
    if (text) {
      try {
        payload = JSON.parse(text)
      } catch {
        payload = { error: { message: text } }
      }
    }

    if (!response.ok) {
      throw new Error(payload.error?.message || 'We could not complete this request right now.')
    }
    return payload.data as T
  }

  return { request }
}
