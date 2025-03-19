<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { copyToClipboard } from '@/utils/copyToClipboard';

const props = defineProps<{
  content: string; // The JSON string to display
}>();

const formattedJson = ref('');
const isValidJson = ref(true);
const copySuccess = ref(false);

// Function to handle copying JSON to clipboard
const handleCopy = async () => {
  const success = await copyToClipboard(props.content);
  if (success) {
    copySuccess.value = true;
    // Reset copy success state after 2 seconds
    setTimeout(() => {
      copySuccess.value = false;
    }, 2000);
  }
};

// Function to add syntax highlighting to JSON
const formatJsonWithHighlighting = (json: string): string => {
  // Replace keys with highlighted keys
  let highlighted = json.replace(
    /"([^"]+)":/g, 
    '<span class="json-key">"$1"</span>:'
  );
  
  // Highlight string values
  highlighted = highlighted.replace(
    /: "([^"]*)"/g, 
    ': <span class="json-string">"$1"</span>'
  );
  
  // Highlight numbers
  highlighted = highlighted.replace(
    /: (\d+\.?\d*)/g,
    ': <span class="json-number">$1</span>'
  );
  
  // Highlight booleans
  highlighted = highlighted.replace(
    /: (true|false)/g, 
    ': <span class="json-boolean">$1</span>'
  );
  
  // Highlight null
  highlighted = highlighted.replace(
    /: null/g, 
    ': <span class="json-null">null</span>'
  );
  
  return highlighted;
};

// Format the JSON with proper indentation and syntax highlighting
onMounted(() => {
  try {
    // Parse and re-stringify the JSON with indentation
    const parsed = JSON.parse(props.content);
    const formatted = JSON.stringify(parsed, null, 2);
    formattedJson.value = formatJsonWithHighlighting(formatted);
    isValidJson.value = true;
  } catch (e) {
    // If parsing fails, show original content and error state
    formattedJson.value = props.content;
    isValidJson.value = false;
  }
});
</script>

<template>
  <div class="json-container" :class="{ 'error': !isValidJson }">
    <div class="json-header">
      <span>JSON</span>
      <button 
        class="copy-btn" 
        @click="handleCopy"
        title="Copy to clipboard"
      >
        {{ copySuccess ? 'Copied!' : 'Copy' }}
      </button>
    </div>
    <pre class="json-content"><code v-html="formattedJson"></code></pre>
  </div>
</template>

<style scoped>
.json-container {
  background-color: #1e1e1e;
  border-radius: 6px;
  margin: 8px 0;
  overflow: hidden;
  font-family: monospace;
  font-size: 12px; /* Smaller font size */
  width: 100%; /* Take available space */
}

.json-header {
  background-color: #333;
  padding: 4px 10px;
  color: #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.copy-btn {
  background-color: #555;
  border: none;
  color: white;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 10px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.copy-btn:hover {
  background-color: #777;
}

.copy-btn:active {
  background-color: #3a3a3a;
}

.json-content {
  color: #e0e0e0;
  padding: 10px;
  margin: 0;
  overflow-x: auto;
  white-space: pre; /* Use 'pre' to preserve formatting and enable horizontal scrolling */
  line-height: 1.4;
  max-width: 100%;
  /* Remove word-break to prevent line wrapping */
}

/* Add a subtle scrollbar indicator */
.json-content::-webkit-scrollbar {
  height: 6px;
}

.json-content::-webkit-scrollbar-thumb {
  background-color: #555;
  border-radius: 3px;
}

.json-content::-webkit-scrollbar-track {
  background-color: #2a2a2a;
}

/* Adjust styling for small screens */
@media (max-width: 480px) {
  .json-container {
    font-size: 11px; /* Even smaller font on mobile */
    max-width: 300px; /* Fixed width only on mobile */
  }
  
  .json-content {
    padding: 8px;
  }
  
  .json-header {
    padding: 3px 8px;
    font-size: 10px;
  }
  
  .copy-btn {
    font-size: 9px;
    padding: 2px 6px;
  }
}

/* JSON syntax highlighting colors */
:deep(.json-key) {
  color: #9cdcfe;
}

:deep(.json-string) {
  color: #ce9178;
}

:deep(.json-number) {
  color: #b5cea8;
}

:deep(.json-boolean) {
  color: #569cd6;
}

:deep(.json-null) {
  color: #569cd6;
}

.error {
  border: 1px solid #e8454e;
}

.error .json-header {
  background-color: #932a30;
}
</style> 