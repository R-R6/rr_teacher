import { createRouter, createWebHashHistory } from 'vue-router'

import { DEFAULT_ROUTE } from '@/config/navigation.js'
import { useAuthStore } from '@/stores/auth.js'

import ControlShell from '@/layouts/ControlShell.vue'
import CostMonitorPage from '@/pages/CostMonitorPage.vue'
import DashboardPage from '@/pages/DashboardPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import OcrRecordsPage from '@/pages/OcrRecordsPage.vue'
import PapersPage from '@/pages/PapersPage.vue'
import QuestionsPage from '@/pages/QuestionsPage.vue'
import SystemStatusPage from '@/pages/SystemStatusPage.vue'
import TagsPage from '@/pages/TagsPage.vue'
import UsersPage from '@/pages/UsersPage.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/login', component: LoginPage, meta: { public: true, title: '后台登录' } },
    {
      path: '/',
      component: ControlShell,
      children: [
        { path: '', redirect: DEFAULT_ROUTE },
        { path: 'dashboard', component: DashboardPage, meta: { title: '仪表盘', subtitle: '从运行态势到风险提示，一屏看清今天的产品状态。' } },
        { path: 'questions', component: QuestionsPage, meta: { title: '题库管理', subtitle: '按作者、题型和难度定位题目，并在桌面端完成修订。' } },
        { path: 'tags', component: TagsPage, meta: { title: '标签管理', subtitle: '维护教材、知识点、题型和难度体系。' } },
        { path: 'ocr-records', component: OcrRecordsPage, meta: { title: 'OCR 记录', subtitle: '查看识别结果、原图和人工修正，追踪质量问题。' } },
        { path: 'papers', component: PapersPage, meta: { title: '试卷管理', subtitle: '跟踪组卷结果和导出产物，清理不需要的试卷。' } },
        { path: 'users', component: UsersPage, meta: { title: '用户查看', subtitle: '核对用户归属、内容产出和 OCR 使用情况。' } },
        { path: 'cost-monitor', component: CostMonitorPage, meta: { title: '成本监控', subtitle: '从引擎、日期和用户维度核对 OCR 资源消耗。' } },
        { path: 'system-status', component: SystemStatusPage, meta: { title: '系统状态', subtitle: '查看环境摘要、健康状态和关键运行开关。' } },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const { isAuthenticated } = useAuthStore()
  if (!to.meta.public && !isAuthenticated.value) {
    return '/login'
  }
  if (to.path === '/login' && isAuthenticated.value) {
    return DEFAULT_ROUTE
  }
  return true
})

export default router
