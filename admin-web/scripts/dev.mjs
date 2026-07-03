import { createServer } from '../../frontend/node_modules/vite/dist/node/index.js'

import { createAdminViteConfig } from '../config.shared.mjs'

const server = await createServer(createAdminViteConfig())
await server.listen()
server.printUrls()
