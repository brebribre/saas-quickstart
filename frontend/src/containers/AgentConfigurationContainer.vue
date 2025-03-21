<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useFiles, type FileRecord } from '@/hooks/useFiles'
import { useAuthStore } from '@/stores/auth'
import { useAgents, type Agent } from '@/hooks/useAgents'
import { useToast } from '@/components/ui/toast/use-toast'
import { 
  Table, 
  TableBody, 
  TableCaption, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  ArrowLeft, 
  File as FileIcon, 
  ExternalLink, 
  Trash2, 
  FileText, 
  FileSpreadsheet,
  Image as FileImage,
  FileType2 as FilePdf,
  FileJson
} from 'lucide-vue-next'

const route = useRoute()
const agentId = route.params.agentId as string
const { toast } = useToast()
const authStore = useAuthStore()
const { getAgent } = useAgents()
const { 
  listAgentFiles, 
  getFileUrl, 
  deleteFile, 
  formatFileSize,
  loading: filesLoading 
} = useFiles()

const agent = ref<Agent | null>(null)
const files = ref<FileRecord[]>([])
const isLoading = ref(false)

// Get appropriate icon for file type
const getFileIcon = (mimeType: string) => {
  if (mimeType.startsWith('image/')) {
    return FileImage
  } else if (mimeType.includes('spreadsheet') || mimeType.includes('excel') || mimeType.includes('csv')) {
    return FileSpreadsheet
  } else if (mimeType.includes('pdf')) {
    return FilePdf
  } else if (mimeType.includes('json')) {
    return FileJson
  } else {
    return FileText
  }
}

// Format date for display
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// Load agent files
const loadFiles = async () => {
  if (!authStore.user) return
  
  try {
    isLoading.value = true
    files.value = await listAgentFiles(agentId, authStore.user.id)
  } catch (error) {
    toast({
      title: 'Error loading files',
      description: error instanceof Error ? error.message : 'Failed to load agent files',
      variant: 'destructive'
    })
  } finally {
    isLoading.value = false
  }
}

// Open file in new window
const openFile = async (fileId: string) => {
  if (!authStore.user) return
  
  try {
    isLoading.value = true
    const fileUrl = await getFileUrl(fileId, authStore.user.id)
    
    if (fileUrl && fileUrl.signedUrl) {
      window.open(fileUrl.signedUrl, '_blank')
    } else {
      throw new Error('Failed to get file URL')
    }
  } catch (error) {
    toast({
      title: 'Error opening file',
      description: error instanceof Error ? error.message : 'Failed to open file',
      variant: 'destructive'
    })
  } finally {
    isLoading.value = false
  }
}

// Delete file
const handleDeleteFile = async (fileId: string) => {
  if (!authStore.user) return
  
  try {
    isLoading.value = true
    const success = await deleteFile(fileId, authStore.user.id)
    
    if (success) {
      // Remove file from list
      files.value = files.value.filter(file => file.id !== fileId)
      
      toast({
        title: 'File deleted',
        description: 'File has been successfully deleted',
      })
    } else {
      throw new Error('Failed to delete file')
    }
  } catch (error) {
    toast({
      title: 'Error deleting file',
      description: error instanceof Error ? error.message : 'Failed to delete file',
      variant: 'destructive'
    })
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  if (authStore.user) {
    agent.value = await getAgent(agentId)
    await loadFiles()
  }
})
</script>

<template>
  <div class="p-4">
    <div class="flex items-center gap-2 mb-6">
      <Button variant="ghost" size="icon" @click="$router.push('/agents')" class="shrink-0">
        <ArrowLeft class="h-4 w-4" />
      </Button>
      <h1 class="text-2xl font-bold">Agent Configuration</h1>
    </div>
    
    <Card class="mb-8">
      <CardHeader>
        <CardTitle>{{ agent?.name }} Documents</CardTitle>
        <CardDescription>
          Manage all the documents uploaded to this agent
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div v-if="isLoading" class="py-4 text-center text-muted-foreground">
          Loading files...
        </div>
        
        <div v-else-if="files.length === 0" class="py-8 text-center text-muted-foreground">
          <FileIcon class="mx-auto h-12 w-12 mb-3 opacity-50" />
          <p>No documents have been uploaded to this agent yet.</p>
          <p class="text-sm mt-2">
            You can upload documents during chat by dragging files or using the file button.
          </p>
        </div>
        
        <Table v-else>
          <TableCaption>A list of documents uploaded to this agent.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Size</TableHead>
              <TableHead>Uploaded At</TableHead>
              <TableHead class="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="file in files" :key="file.id">
              <TableCell class="font-medium flex items-center gap-2">
                <component :is="getFileIcon(file.mime_type)" class="h-4 w-4 opacity-70" /> 
                <span class="truncate max-w-[150px]">{{ file.filename }}</span>
              </TableCell>
              <TableCell>{{ file.mime_type.split('/')[1].toUpperCase() }}</TableCell>
              <TableCell>{{ formatFileSize(file.file_size) }}</TableCell>
              <TableCell>{{ formatDate(file.uploaded_at) }}</TableCell>
              <TableCell class="text-right">
                <div class="flex justify-end gap-2">
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    @click="openFile(file.id)"
                    title="View file"
                  >
                    <ExternalLink class="h-4 w-4" />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    @click="handleDeleteFile(file.id)"
                    title="Delete file"
                    class="text-destructive"
                  >
                    <Trash2 class="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  </div>
</template>

<style scoped>
.table :deep(th) {
  font-weight: 600;
  color: var(--foreground);
}

.table :deep(tr:last-child) {
  border-bottom: none;
}
</style>
