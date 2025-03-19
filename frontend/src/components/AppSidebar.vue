<script setup lang="ts">
import {
  Home,
  Inbox,
  User,
  LogOut,
  Mail,
  BotIcon
} from 'lucide-vue-next'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter
} from '@/components/ui/sidebar'
import { useRouter } from 'vue-router'
import { onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'

const router = useRouter()
const authStore = useAuthStore()

// Define the type for menu items
interface MenuItem {
  title: string
  route: string
  icon: any
  requiresAuth?: boolean
}

// Menu items with proper routes
const items: MenuItem[] = [
  {
    title: 'Dashboard',
    route: '/dashboard',
    icon: Home
  },
  {
    title: 'Inbox',
    route: '/inbox',
    icon: Inbox,
    requiresAuth: true
  },
  {
    title: 'Agents',
    route: '/agents',
    icon: BotIcon,
    requiresAuth: true
  },
]

const filteredItems = computed(() => {
  return items.filter(item => !item.requiresAuth || authStore.isAuthenticated)
})

const navigateTo = (route: string) => {
  router.push(route)
}

const handleSignIn = async () => {
  router.push('/login')
}

const handleSignUp = async () => {
  router.push('/register')
}

const handleSignOut = async () => {
  const { success } = await authStore.signOut()
  if (success) {
    router.push('/')
  }
}

// We don't need to initialize auth here since it's done in main.ts
// onMounted(() => {
//   authStore.initialize()
// })
</script>

<template>
  <Sidebar>
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Application</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in filteredItems" :key="item.title">
              <SidebarMenuButton class="cursor-pointer" asChild @click="navigateTo(item.route)">
                <div class="flex items-center">
                  <component :is="item.icon" class="mr-2" />
                  <span>{{ item.title }}</span>
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    
    <!-- User profile area at the bottom -->
    <SidebarFooter>
      <div class="p-4 border-t">
        <div v-if="authStore.isAuthenticated" class="space-y-3">
          <div 
            class="flex items-center justify-between rounded-md transition-colors hover:bg-accent p-2"
            @click="navigateTo('/profile')"
          >
            <div class="flex items-center gap-2">
              <Avatar class="h-8 w-8">
                <AvatarImage :src="authStore.user?.user_metadata?.avatar_url" />
                <AvatarFallback>
                  <User class="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <div>
                <p class="text-sm font-medium">{{ authStore.user?.email }}</p>
                <p class="text-xs text-muted-foreground">
                  {{ authStore.user?.user_metadata?.full_name || 'User' }}
                </p>
              </div>
            </div>
          </div>
          
          <Button 
            @click="handleSignOut" 
            variant="outline"
            class="w-full justify-start"
          >
            <LogOut class="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
        
        <div v-else class="space-y-2">
          <Button 
            @click="handleSignIn" 
            class="w-full justify-start"
          >
            <Mail class="h-4 w-4 mr-2" />
            Sign In
          </Button>
          
          <Button 
            @click="handleSignUp" 
            variant="secondary"
            class="w-full justify-start"
          >
            <User class="h-4 w-4 mr-2" />
            Sign Up
          </Button>
        </div>
      </div>
    </SidebarFooter>
  </Sidebar>
</template>
