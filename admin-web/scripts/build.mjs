import fs from 'node:fs/promises'
import path from 'node:path'

import { build } from '../../frontend/node_modules/vite/dist/node/index.js'

import { createAdminViteConfig } from '../config.shared.mjs'

const config = createAdminViteConfig()
const buildConfig = {
  ...config,
  build: {
    ...config.build,
    write: false,
  },
}

const result = await build(buildConfig)
const outputs = Array.isArray(result) ? result : [result]
const outDir = config.build.outDir

await fs.mkdir(outDir, { recursive: true })

for (const outputGroup of outputs) {
  for (const file of outputGroup.output) {
    const target = path.join(outDir, file.fileName)
    const source = file.type === 'asset' ? file.source : file.code
    await fs.writeFile(target, source)
  }
}
