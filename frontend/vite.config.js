import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  // Backend API target:
  // - In development: falls back to http://127.0.0.1:8000
  // - In production: set VITE_API_BASE_URL
  const API_TARGET = env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

  return {
    plugins: [react()],

    build: {
      chunkSizeWarningLimit: 1500, // Increase from default 500kB to 1.5MB
      rollupOptions: {
        output: {
          manualChunks(id) {
            const path = id.replace(/\\/g, "/");

            if (path.includes("/node_modules/")) {
              if (path.includes("/recharts/")) {
                return "vendor-charts";
              }
              if (path.includes("/papaparse/")) {
                return "vendor-csv";
              }
              return "vendor";
            }

            return undefined;
          },
        },
      },
    },

    // IMPORTANT: alias to support "@/components/..." "@/pages/..." etc.
    resolve: {
      alias: {
        "@": "/src",
      },
    },

    server: {
      host: "127.0.0.1",   // Force IPv4 to avoid localhost DNS issues
      port: 5173,
      open: true,
      strictPort: true,
      proxy: {
        "/vizion/": { target: API_TARGET, changeOrigin: true, secure: false },
        "/health/": { target: API_TARGET, changeOrigin: true, secure: false },
        "/shipments/": { target: API_TARGET, changeOrigin: true, secure: false },
        "/ai/": { target: API_TARGET, changeOrigin: true, secure: false },
        "/reports/": { target: API_TARGET, changeOrigin: true, secure: false },
        "/api/": { target: API_TARGET, changeOrigin: true, secure: false },
        "/auth/": { target: API_TARGET, changeOrigin: true, secure: false },
        "/ws": { target: API_TARGET, changeOrigin: true, ws: true, secure: false },
      },
    },
  };
});
