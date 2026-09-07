import { createClient, type SupabaseClient } from '@supabase/supabase-js'

let client: SupabaseClient | null = null

export function useSupabase() {
  const config = useRuntimeConfig()
  const configured = Boolean(config.public.supabaseUrl && config.public.supabaseAnonKey)
  if (configured && !client) client = createClient(config.public.supabaseUrl, config.public.supabaseAnonKey)
  return { client, configured }
}
