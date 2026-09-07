export function useApi() {
  const config = useRuntimeConfig()
  const { client } = useSupabase()

  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    if (!client) {
      throw new Error('Authentication is not configured yet.')
    }
    const { data } = await client.auth.getSession()
    if (!data.session) throw new Error('Please sign in before creating a source.')

    const response = await fetch(`${config.public.apiBaseUrl}${path}`, {
      ...options,
      headers: { Authorization: `Bearer ${data.session.access_token}`, ...(options.headers || {}) }
    })
    const payload = await response.json()
    if (!response.ok) throw new Error(payload.error?.message || 'We could not save your source right now.')
    return payload.data as T
  }

  return { request }
}
