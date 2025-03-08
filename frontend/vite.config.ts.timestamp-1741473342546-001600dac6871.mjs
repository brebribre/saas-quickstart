// vite.config.ts
import { defineConfig } from "file:///Users/bryanalvin/stratigo-job/frontend/node_modules/vite/dist/node/index.js";
import react from "file:///Users/bryanalvin/stratigo-job/frontend/node_modules/@vitejs/plugin-react-swc/index.mjs";
import path from "path";
var __vite_injected_original_dirname = "/Users/bryanalvin/stratigo-job/frontend";
var vite_config_default = defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 3e3
  },
  plugins: [
    react()
  ],
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src")
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          "react-vendor": ["react", "react-dom", "react-router-dom"]
        }
      }
    }
  }
}));
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMvYnJ5YW5hbHZpbi9zdHJhdGlnby1qb2IvZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIi9Vc2Vycy9icnlhbmFsdmluL3N0cmF0aWdvLWpvYi9mcm9udGVuZC92aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vVXNlcnMvYnJ5YW5hbHZpbi9zdHJhdGlnby1qb2IvZnJvbnRlbmQvdml0ZS5jb25maWcudHNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tIFwidml0ZVwiO1xuaW1wb3J0IHJlYWN0IGZyb20gXCJAdml0ZWpzL3BsdWdpbi1yZWFjdC1zd2NcIjtcbmltcG9ydCBwYXRoIGZyb20gXCJwYXRoXCI7XG5cbi8vIGh0dHBzOi8vdml0ZWpzLmRldi9jb25maWcvXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoKHsgbW9kZSB9KSA9PiAoe1xuICBzZXJ2ZXI6IHtcbiAgICBob3N0OiBcIjo6XCIsXG4gICAgcG9ydDogMzAwMCxcbiAgfSxcbiAgcGx1Z2luczogW1xuICAgIHJlYWN0KCksXG4gIF0sXG4gIHJlc29sdmU6IHtcbiAgICBhbGlhczoge1xuICAgICAgXCJAXCI6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsIFwiLi9zcmNcIiksXG4gICAgfSxcbiAgfSxcbiAgYnVpbGQ6IHtcbiAgICByb2xsdXBPcHRpb25zOiB7XG4gICAgICBvdXRwdXQ6IHtcbiAgICAgICAgbWFudWFsQ2h1bmtzOiB7XG4gICAgICAgICAgJ3JlYWN0LXZlbmRvcic6IFsncmVhY3QnLCAncmVhY3QtZG9tJywgJ3JlYWN0LXJvdXRlci1kb20nXSxcbiAgICAgICAgfSxcbiAgICAgIH0sXG4gICAgfSxcbiAgfSxcbn0pKTtcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBdVMsU0FBUyxvQkFBb0I7QUFDcFUsT0FBTyxXQUFXO0FBQ2xCLE9BQU8sVUFBVTtBQUZqQixJQUFNLG1DQUFtQztBQUt6QyxJQUFPLHNCQUFRLGFBQWEsQ0FBQyxFQUFFLEtBQUssT0FBTztBQUFBLEVBQ3pDLFFBQVE7QUFBQSxJQUNOLE1BQU07QUFBQSxJQUNOLE1BQU07QUFBQSxFQUNSO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxNQUFNO0FBQUEsRUFDUjtBQUFBLEVBQ0EsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLE1BQ0wsS0FBSyxLQUFLLFFBQVEsa0NBQVcsT0FBTztBQUFBLElBQ3RDO0FBQUEsRUFDRjtBQUFBLEVBQ0EsT0FBTztBQUFBLElBQ0wsZUFBZTtBQUFBLE1BQ2IsUUFBUTtBQUFBLFFBQ04sY0FBYztBQUFBLFVBQ1osZ0JBQWdCLENBQUMsU0FBUyxhQUFhLGtCQUFrQjtBQUFBLFFBQzNEO0FBQUEsTUFDRjtBQUFBLElBQ0Y7QUFBQSxFQUNGO0FBQ0YsRUFBRTsiLAogICJuYW1lcyI6IFtdCn0K
