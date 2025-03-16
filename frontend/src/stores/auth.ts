import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/lib/supabase'
import type { User } from '@supabase/supabase-js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(true)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!user.value)

  // Initialize auth state
  const initialize = async () => {
    loading.value = true
    error.value = null

    try {
      // Check if user is already logged in
      const { data } = await supabase.auth.getSession()
      
      if (data.session) {
        user.value = data.session.user
      }

      // Set up auth state change listener
      supabase.auth.onAuthStateChange((_, session) => {
        user.value = session?.user || null
      })
    } catch (err: any) {
      console.error('Failed to initialize auth:', err)
      error.value = err.message || 'Failed to initialize authentication'
    } finally {
      loading.value = false
    }
  }

  // Sign up with email and password
  const signUp = async (email: string, password: string) => {
    loading.value = true
    error.value = null

    try {
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password
      })

      if (signUpError) throw signUpError
      
      return { success: true, data }
    } catch (err: any) {
      console.error('Sign up failed:', err)
      error.value = err.message || 'Sign up failed'
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Sign in with email and password
  const signIn = async (email: string, password: string) => {
    loading.value = true
    error.value = null

    try {
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (signInError) throw signInError
      
      user.value = data.user
      return { success: true, data }
    } catch (err: any) {
      console.error('Sign in failed:', err)
      error.value = err.message || 'Sign in failed'
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Sign in with OAuth provider
  const signInWithOAuth = async (provider: 'google' | 'github' | 'facebook') => {
    loading.value = true
    error.value = null

    try {
      const { data, error: oauthError } = await supabase.auth.signInWithOAuth({
        provider
      })

      if (oauthError) throw oauthError
      
      return { success: true, data }
    } catch (err: any) {
      console.error('OAuth sign in failed:', err)
      error.value = err.message || 'OAuth sign in failed'
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Sign out
  const signOut = async () => {
    loading.value = true
    error.value = null

    try {
      const { error: signOutError } = await supabase.auth.signOut()
      
      if (signOutError) throw signOutError
      
      user.value = null
      return { success: true }
    } catch (err: any) {
      console.error('Sign out failed:', err)
      error.value = err.message || 'Sign out failed'
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }

  // Get user profile
  const getUserProfile = async () => {
    if (!user.value) return null

    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.value.id)
        .single()

      if (error) throw error
      
      return data
    } catch (err: any) {
      console.error('Failed to get user profile:', err)
      return null
    }
  }

  // Update user profile
  const updateUserProfile = async (profile: any) => {
    if (!user.value) return { success: false, error: 'Not authenticated' }

    try {
      const { error } = await supabase
        .from('profiles')
        .upsert({
          id: user.value.id,
          updated_at: new Date(),
          ...profile
        })

      if (error) throw error
      
      return { success: true }
    } catch (err: any) {
      console.error('Failed to update profile:', err)
      return { success: false, error: err.message }
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    initialize,
    signUp,
    signIn,
    signInWithOAuth,
    signOut,
    getUserProfile,
    updateUserProfile
  }
}) 