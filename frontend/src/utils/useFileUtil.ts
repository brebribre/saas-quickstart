import { ref, reactive } from 'vue'
import { useToast } from '@/components/ui/toast/use-toast'

export function useFileUtil() {
  const { toast } = useToast()
  
  // Use reactive state instead of individual refs
  const state = reactive({
    selectedFiles: [] as File[],
    uploadError: '',
    isDraggingFile: false
  })
  
  // Keep fileInput as ref since it's a DOM element reference
  const fileInput = ref<HTMLInputElement | null>(null)

  // Check if file type is allowed
  const isFileTypeAllowed = (file: File): boolean => {
    const allowedTypes = [
      // Documents
      'application/pdf', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain', 'application/json',
      // Images
      'image/jpeg', 'image/png', 'image/gif'
    ]
    
    return allowedTypes.includes(file.type)
  }

  // Format file size for display
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    
    const units = ['B', 'KB', 'MB', 'GB']
    const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
    
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`
  }

  // Validate files and separate into supported, unsupported, and oversized arrays
  const validateFiles = (files: File[]): {
    supportedFiles: File[],
    unsupportedFiles: string[],
    oversizedFiles: string[]
  } => {
    const supportedFiles: File[] = []
    const unsupportedFiles: string[] = []
    const oversizedFiles: string[] = []
    
    // Validate files
    files.forEach(file => {
      if (file.size > 50 * 1024 * 1024) { // 50MB
        oversizedFiles.push(file.name)
      } else if (!isFileTypeAllowed(file)) {
        unsupportedFiles.push(file.name)
      } else {
        supportedFiles.push(file)
      }
    })

    return { supportedFiles, unsupportedFiles, oversizedFiles }
  }

  // Process validation results and show appropriate toast notifications
  const processValidationResults = (
    supportedFiles: File[],
    unsupportedFiles: string[],
    oversizedFiles: string[]
  ) => {
    // Handle errors for oversized files
    if (oversizedFiles.length > 0) {
      const fileNames = oversizedFiles.length > 3 
        ? `${oversizedFiles.slice(0, 3).join(', ')} and ${oversizedFiles.length - 3} more` 
        : oversizedFiles.join(', ')
      
      state.uploadError = `File${oversizedFiles.length > 1 ? 's' : ''} exceeding 50MB size limit: ${fileNames}`
      
      toast({
        title: 'Files too large',
        description: `${oversizedFiles.length} file${oversizedFiles.length > 1 ? 's' : ''} exceed the 50MB size limit`,
        variant: 'destructive',
      })
    }
    
    // Handle unsupported file types
    if (unsupportedFiles.length > 0) {
      const fileNames = unsupportedFiles.length > 3 
        ? `${unsupportedFiles.slice(0, 3).join(', ')} and ${unsupportedFiles.length - 3} more` 
        : unsupportedFiles.join(', ')
      
      if (!oversizedFiles.length) {
        state.uploadError = `Unsupported file type${unsupportedFiles.length > 1 ? 's' : ''}: ${fileNames}`
      }
      
      toast({
        title: 'Unsupported file type',
        description: `${unsupportedFiles.length} file${unsupportedFiles.length > 1 ? 's' : ''} of unsupported type were removed`,
        variant: 'destructive',
      })
    }
    
    // Add supported files to selection
    if (supportedFiles.length > 0) {
      // Only clear error if we have valid files to add
      if (supportedFiles.length === (supportedFiles.length + unsupportedFiles.length + oversizedFiles.length)) {
        state.uploadError = ''
      }
      state.selectedFiles.push(...supportedFiles)
      
      // Show toast if some files were accepted
      if (unsupportedFiles.length > 0 || oversizedFiles.length > 0) {
        toast({
          title: 'Files added',
          description: `${supportedFiles.length} file${supportedFiles.length > 1 ? 's' : ''} were added successfully`,
        })
      }
    }
  }

  // Handle file selection from input
  const handleFileSelect = (event: Event) => {
    const target = event.target as HTMLInputElement
    if (!target.files?.length) return
    
    const files = Array.from(target.files)
    const { supportedFiles, unsupportedFiles, oversizedFiles } = validateFiles(files)
    
    processValidationResults(supportedFiles, unsupportedFiles, oversizedFiles)
    
    // Reset file input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }

  // Drag and drop handlers
  const handleDragEnter = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    state.isDraggingFile = true
  }

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    // Only set dragging to false if leaving the main container
    if (e.currentTarget === e.target) {
      state.isDraggingFile = false
    }
  }

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    state.isDraggingFile = false
    
    const droppedFiles = e.dataTransfer?.files
    if (!droppedFiles?.length) return
    
    const files = Array.from(droppedFiles)
    const { supportedFiles, unsupportedFiles, oversizedFiles } = validateFiles(files)
    
    processValidationResults(supportedFiles, unsupportedFiles, oversizedFiles)
  }

  // Remove file from selection
  const removeFile = (index: number) => {
    state.selectedFiles = state.selectedFiles.filter((_, i) => i !== index)
  }

  // Clear all selected files
  const clearFiles = () => {
    state.selectedFiles = []
    state.uploadError = ''
  }

  // Get file list label
  const getFileListLabel = () => {
    if (state.selectedFiles.length === 0) return ''
    return `Selected Files (${state.selectedFiles.length})`
  }

  return {
    // Expose the reactive state properties directly
    ...state,
    fileInput,
    isFileTypeAllowed,
    formatFileSize,
    handleFileSelect,
    handleDragEnter,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    removeFile,
    clearFiles,
    getFileListLabel
  }
}
