<script setup lang="ts">
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import AppSidebar from '@/components/AppSidebar.vue'
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <main class="mx-2 my-3 w-full">
      <SidebarTrigger />
      <RouterView />
    </main>
  </SidebarProvider>
</template>
