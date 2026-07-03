export const DEFAULT_ROUTE = '/dashboard'

export const NAV_ITEMS = [
  { key: 'dashboard', label: '仪表盘', path: '/dashboard', icon: 'dashboard', caption: '整体运行态势' },
  { key: 'questions', label: '题库', path: '/questions', icon: 'questions', caption: '题目维护与检索' },
  { key: 'tags', label: '标签', path: '/tags', icon: 'tags', caption: '标签体系管理' },
  { key: 'ocr-records', label: 'OCR 记录', path: '/ocr-records', icon: 'ocr', caption: '识别质量与修正' },
  { key: 'papers', label: '试卷', path: '/papers', icon: 'papers', caption: '组卷结果与导出' },
  { key: 'users', label: '用户', path: '/users', icon: 'users', caption: '用户归属与活跃' },
  { key: 'cost-monitor', label: '成本监控', path: '/cost-monitor', icon: 'cost', caption: 'OCR 调用成本' },
  { key: 'system-status', label: '系统状态', path: '/system-status', icon: 'system', caption: '环境与健康摘要' },
]
