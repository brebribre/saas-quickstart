<script setup lang="ts">
import { ref, onMounted } from 'vue';
import MarkdownIt from 'markdown-it';

const props = defineProps<{
  content: string; // The markdown content to display
}>();

const renderedContent = ref('');

// Initialize markdown-it with options
const md = new MarkdownIt({
  html: false, // Disable HTML tags in source
  xhtmlOut: false, // Use '/' to close single tags (<br />)
  breaks: true, // Convert \n in paragraphs into <br>
  linkify: true, // Autoconvert URL-like text to links
  typographer: true, // Enable smartquotes and other typographic replacements
});

// Add a custom renderer for table cells to force padding
const defaultRender = md.renderer.rules.td_open || function(tokens, idx, options, env, self) {
  return self.renderToken(tokens, idx, options);
};

md.renderer.rules.td_open = function(tokens, idx, options, env, self) {
  // Add inline style to ensure padding
  tokens[idx].attrJoin('style', 'padding: 0.75rem; border: 1px solid #e5e7eb;');
  return defaultRender(tokens, idx, options, env, self);
};

// Do the same for table headers
const thDefaultRender = md.renderer.rules.th_open || function(tokens, idx, options, env, self) {
  return self.renderToken(tokens, idx, options);
};

md.renderer.rules.th_open = function(tokens, idx, options, env, self) {
  // Add inline style to ensure padding and background
  tokens[idx].attrJoin('style', 'padding: 0.75rem; border: 1px solid #e5e7eb; background-color: #f9fafb; font-weight: 600;');
  return thDefaultRender(tokens, idx, options, env, self);
};

onMounted(() => {
  // Render markdown to HTML
  renderedContent.value = md.render(props.content);
});
</script>

<template>
  <div class="markdown-content" v-html="renderedContent"></div>
</template>

<style scoped>
/* Using non-scoped CSS as a fallback to ensure styles are applied */
.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
  border: 1px solid #d1d5db;
}

.markdown-content table th,
.markdown-content table td {
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
  text-align: left;
}

.markdown-content table th {
  background-color: #f9fafb;
  font-weight: 600;
}

.markdown-content {
  font-size: 0.875rem; /* text-sm equivalent */
  line-height: 1.5;
  overflow-wrap: break-word;
  padding: 0.5rem 0; /* Vertical padding only */
  width: 100%; /* Take available space */
}

/* Adjust styling for small screens */
@media (max-width: 480px) {
  .markdown-content {
    font-size: 0.8125rem; /* Slightly smaller font on mobile */
  }
}

/* Style for markdown elements */
:deep(p) {
  margin: 0 0 0.75rem 0;
}

:deep(p:last-child) {
  margin-bottom: 0;
}

:deep(strong) {
  font-weight: 600;
}

:deep(em) {
  font-style: italic;
}

:deep(a) {
  color: #3b82f6; /* blue-500 */
  text-decoration: underline;
}

:deep(code) {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.875em;
  padding: 0.2em 0.4em;
  color: #e83e8c;
}

:deep(pre) {
  background-color: #f8f8f8;
  border-radius: 6px;
  padding: 0.75rem;
  overflow-x: auto;
  margin: 0.75rem 0;
}

:deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
  display: block;
}

/* Base list styles */
:deep(ul, ol) {
  margin: 0.5rem 0 1rem 0;
  padding: 0;
  list-style-position: outside;
}

/* Unordered lists */
:deep(ul) {
  padding-left: 1.5rem;
  list-style-type: disc;
}

/* Ordered lists - specifically adjusted for alignment */
:deep(ol) {
  padding-left: 1.5rem;
  list-style-type: decimal;
}

/* Direct child ordered lists (first level) */
:deep(> ol) {
  padding-left: 1.2rem;  /* Slightly less to align with text */
}

:deep(li) {
  margin-bottom: 0.5rem;
}

:deep(li:last-child) {
  margin-bottom: 0.75rem;
}

:deep(li > ul, li > ol) {
  margin: 0.5rem 0 0 0;
  padding-left: 1.5rem;
}

/* Add extra space for two-digit numbers in ordered lists */
:deep(ol li:nth-child(n+10)) {
  margin-left: 0.25rem;
}

:deep(h1, h2, h3, h4, h5, h6) {
  margin-top: 1.25rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  line-height: 1.25;
}

:deep(h1:first-child, h2:first-child, h3:first-child, h4:first-child, h5:first-child, h6:first-child) {
  margin-top: 0;
}

:deep(h1) { font-size: 1.5rem; margin-bottom: 0.5rem; margin-top: 1rem; }
:deep(h2) { font-size: 1.25rem; margin-bottom: 0.5rem; margin-top: 1rem; }
:deep(h3) { font-size: 1.125rem; margin-bottom: 0.5rem; margin-top: 1rem; }
:deep(h4) { font-size: 1rem; margin-bottom: 0.5rem; margin-top: 1rem; }
:deep(h5, h6) { font-size: 0.875rem; margin-bottom: 0.5rem; margin-top: 1rem; }

:deep(blockquote) {
  border-left: 4px solid #e5e7eb; /* gray-200 */
  padding-left: 1rem;
  margin: 1rem 0;
  margin-left: 0;
  margin-right: 0;
  font-style: italic;
  color: #6b7280; /* gray-500 */
}

:deep(hr) {
  margin: 1rem 0;
  border: 0;
  border-top: 1px solid #e5e7eb; /* gray-200 */
}

/* Table styles with !important */
:deep(table) {
  border-collapse: collapse !important;
  width: 100% !important;
  margin: 1rem 0 !important;
  border: 1px solid #d1d5db !important;
}

:deep(table th),
:deep(table td) {
  border: 1px solid #e5e7eb !important;
  padding: 0.25rem !important;
  text-align: left !important;
}

:deep(table th) {
  background-color: #f9fafb !important;
  font-weight: 600 !important;
}

/* Additional table row styling */
:deep(table tr) {
  border-bottom: 1px solid #e5e7eb !important;
}

:deep(table tr:nth-child(even)) {
  background-color: #f9fafb !important;
}
</style> 