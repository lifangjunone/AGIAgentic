import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueDevTools from "vite-plugin-vue-devtools";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
        // 对于流式响应，需要特殊处理
        configure: (proxy, _options) => {
          proxy.on("proxyReq", (proxyReq, req, res) => {
            // 确保流式响应不被缓冲
            if (req.url.includes("/stream")) {
              proxyReq.setHeader("Connection", "keep-alive");
            }
          });
        },
      },
    },
  },
});
