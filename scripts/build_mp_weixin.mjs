import fs from 'node:fs/promises'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const FRONTEND = path.join(ROOT, 'frontend')
const OUTPUT = path.join(FRONTEND, 'dist/build/mp-weixin')
const CLOUD_SRC = path.join(FRONTEND, 'cloudfunctions')
const CLOUD_DST = path.join(OUTPUT, 'cloudfunctions')
const PROFILE_WXML = path.join(OUTPUT, 'pages/profile/profile.wxml')

const UNI_CLI = path.join(FRONTEND, 'node_modules', '@dcloudio', 'vite-plugin-uni', 'bin', 'uni.js')

function run(command, args, cwd) {
  const result = spawnSync(command, args, {
    cwd,
    stdio: 'inherit',
    shell: false,
  })
  if (result.error) {
    console.error(`执行失败: ${command} ${args.join(' ')}`)
    console.error(result.error.message)
    process.exit(1)
  }
  if (result.status !== 0) {
    console.error(`命令退出码 ${result.status}: ${command} ${args.join(' ')}`)
    process.exit(result.status ?? 1)
  }
}

async function pathExists(target) {
  try {
    await fs.access(target)
    return true
  } catch {
    return false
  }
}

async function copyDir(src, dst) {
  await fs.mkdir(dst, { recursive: true })
  const entries = await fs.readdir(src, { withFileTypes: true })
  for (const entry of entries) {
    const sourcePath = path.join(src, entry.name)
    const targetPath = path.join(dst, entry.name)
    if (entry.isDirectory()) {
      await copyDir(sourcePath, targetPath)
      continue
    }
    await fs.copyFile(sourcePath, targetPath)
  }
}

async function patchProjectConfig() {
  const configPath = path.join(OUTPUT, 'project.config.json')
  const config = JSON.parse(await fs.readFile(configPath, 'utf8'))
  if (!config.cloudfunctionRoot) {
    config.cloudfunctionRoot = 'cloudfunctions/'
    await fs.writeFile(configPath, JSON.stringify(config, null, 2))
  }
}

async function main() {
  if (!(await pathExists(path.join(FRONTEND, 'node_modules')))) {
    console.error('缺少 frontend/node_modules，请先在 frontend 目录执行 npm install')
    process.exit(1)
  }

  if (!(await pathExists(UNI_CLI))) {
    console.error(`缺少 uni CLI: ${UNI_CLI}`)
    console.error('请先在 frontend 目录执行 npm install')
    process.exit(1)
  }

  console.log('==> Building WeChat mini program (mp-weixin)...')
  run(process.execPath, [UNI_CLI, 'build', '-p', 'mp-weixin'], FRONTEND)

  if (!(await pathExists(path.join(OUTPUT, 'app.json')))) {
    console.error(`构建失败，未找到: ${path.join(OUTPUT, 'app.json')}`)
    process.exit(1)
  }

  console.log('==> Syncing cloudfunctions...')
  await copyDir(CLOUD_SRC, CLOUD_DST)
  await patchProjectConfig()

  if (!(await pathExists(PROFILE_WXML))) {
    console.error(`构建失败，未找到: ${PROFILE_WXML}`)
    process.exit(1)
  }

  console.log('==> Done.')
  console.log(`    输出目录: ${path.relative(ROOT, OUTPUT)}`)
  console.log('    下一步: 打开微信开发者工具，导入 frontend/ 目录，点击「编译」')
  console.log('    开发模式（改代码自动重新编译）: cd frontend && npm run dev:mp-weixin')
}

await main()
