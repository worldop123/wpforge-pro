import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    // 代码分割优化
    rollupOptions: {
      output: {
        // 手动分包，将第三方库分离到独立 chunk
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'element-plus': ['element-plus'],
          'utils-vendor': ['axios', 'lodash']
        },
        // chunk 文件名添加 hash，便于 CDN 缓存
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        // 移除 console 和 debugger
        drop_console: true,
        drop_debugger: true,
        // 移除纯函数调用
        pure_funcs: ['console.log', 'console.info']
      },
      format: {
        // 移除注释
        comments: false
      }
    },
    // 提高 chunk 大小警告阈值
    chunkSizeWarningLimit: 1000,
    // CSS 代码分割
    cssCodeSplit: true
  }
})
