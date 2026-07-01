import { defineConfig } from 'vite'
import uniPlugin from '@dcloudio/vite-plugin-uni'

// @dcloudio/vite-plugin-uni 是 CJS 模块，在 ESM (package.json "type": "module")
// 下 Node 原生 loader 不识别 __esModule 标志，会把整个 exports 对象当默认导出，
// 所以必须显式取 .default
const uni = uniPlugin.default || uniPlugin

export default defineConfig({
  plugins: [uni()]
})
