import type { Session } from '@supabase/supabase-js'

const session = ref<Session | null>(null)
const initialized = ref(false)

export function useAuth() {
  const { client, configured } = useSupabase()
  async function initialize() {
    if (!client || initialized.value) return
    session.value = (await client.auth.getSession()).data.session
    client.auth.onAuthStateChange((_event, nextSession) => { session.value = nextSession })
    initialized.value = true
  }
  async function signIn(email: string, password: string) {
    if (!client) throw new Error('Authentication is not configured.')
    const { error } = await client.auth.signInWithPassword({ email, password })
    if (error) throw error
  }
  async function signUp(email: string, password: string) {
    if (!client) throw new Error('Authentication is not configured.')
    const { data, error } = await client.auth.signUp({ email, password })
    if (error) throw error
    return Boolean(data.user && !data.session)
  }
  async function signOut() { if (client) { const { error } = await client.auth.signOut(); if (error) throw error } }
  return { configured, session, initialize, signIn, signUp, signOut }
}
