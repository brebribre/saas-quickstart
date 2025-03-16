<script setup lang="ts">
import {
  Calendar,
  Home,
  Inbox,
  Search,
  Settings,
  AudioWaveform,
  BookOpen,
  Bot,
  Command,
  Frame,
  GalleryVerticalEnd,
  Map,
  PieChart,
  Settings2,
  SquareTerminal
} from 'lucide-vue-next'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem
} from '@/components/ui/sidebar'
import { useRouter } from 'vue-router'

const router = useRouter()

// Define the type for menu items
interface MenuItem {
  title: string
  route: string
  icon: any
}

// Menu items with proper routes
const items: MenuItem[] = [
  {
    title: 'Home',
    route: '/',
    icon: Home
  },
  {
    title: 'Inbox',
    route: '/inbox',
    icon: Inbox
  }
]

// Handle navigation
const navigateTo = (route: string) => {
  router.push(route)
}
</script>

<template>
  <Sidebar>
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Application</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in items" :key="item.title">
              <SidebarMenuButton asChild @click="navigateTo(item.route)">
                <div class="flex items-center cursor-pointer">
                  <component :is="item.icon" class="mr-2" />
                  <span>{{ item.title }}</span>
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
  </Sidebar>
</template>
