import { preview } from '../../frontend/node_modules/vite/dist/node/index.js'

import { createAdminViteConfig } from '../config.shared.mjs'

const server = await preview(createAdminViteConfig())
server.printUrls()
