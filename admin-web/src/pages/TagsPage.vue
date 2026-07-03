<template>
  <div class="page-stack">
    <div v-if="feedback" :class="feedbackTone === 'error' ? 'error-banner' : 'success-banner'">{{ feedback }}</div>

    <PanelCard title="新增标签" eyebrow="Taxonomy Create">
      <div class="filters">
        <div class="field-group field-group--grow">
          <label class="field-label">标签名称</label>
          <input v-model.trim="createForm.name" class="text-input" />
        </div>
        <div class="field-group">
          <label class="field-label">标签类型</label>
          <select v-model="createForm.tag_type" class="select-input">
            <option value="book">教材版本</option>
            <option value="knowledge">知识点</option>
            <option value="type">题型</option>
            <option value="difficulty">难度</option>
          </select>
        </div>
        <div class="field-group">
          <label class="field-label">排序值</label>
          <input v-model.number="createForm.sort_order" class="text-input" type="number" min="1" />
        </div>
        <div class="actions-row">
          <button class="primary-button" @click="createTag">创建标签</button>
        </div>
      </div>
    </PanelCard>

    <PanelCard title="标签列表" eyebrow="Tag Ledger">
      <ListStateSummary
        :title="resultMeta.totalLabel"
        :subtitle="`${resultMeta.rangeLabel} · ${resultMeta.filterLabel}`"
        :chips="activeFilterItems"
      />

      <div class="filters" style="margin-bottom: 18px;">
        <div class="field-group">
          <label class="field-label">查看类型</label>
          <select v-model="filterType" class="select-input" @change="loadTags">
            <option value="">全部</option>
            <option value="book">教材版本</option>
            <option value="knowledge">知识点</option>
            <option value="type">题型</option>
            <option value="difficulty">难度</option>
          </select>
        </div>
      </div>

      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>标签</th>
              <th>类型</th>
              <th>排序</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tag in tags" :key="tag.id">
              <td><strong>{{ tag.name }}</strong></td>
              <td>{{ typeLabels[tag.tag_type] }}</td>
              <td>{{ tag.sort_order }}</td>
              <td>
                <div class="table-actions">
                  <button @click="openEditor(tag)">编辑</button>
                  <button @click="removeTag(tag)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="showEmptyState" class="empty-panel">
        <strong>{{ emptyState.title }}</strong>
        <p>{{ emptyState.detail }}</p>
      </div>
    </PanelCard>

    <DrawerPanel :open="drawerOpen" title="编辑标签" eyebrow="Taxonomy Edit" @close="drawerOpen = false">
      <div v-if="editingTag" class="modal-form">
        <div class="field-group">
          <label class="field-label">标签名称</label>
          <input v-model.trim="editForm.name" class="text-input" />
        </div>
        <div class="field-group">
          <label class="field-label">排序值</label>
          <input v-model.number="editForm.sort_order" class="text-input" type="number" min="1" />
        </div>
        <div class="actions-row">
          <button class="primary-button" @click="saveTag">保存标签</button>
        </div>
      </div>
    </DrawerPanel>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { adminApi } from '@/api/admin.js'
import DrawerPanel from '@/components/DrawerPanel.vue'
import ListStateSummary from '@/components/ListStateSummary.vue'
import PanelCard from '@/components/PanelCard.vue'
import { buildEmptyState, buildResultMeta, describeActiveFilters } from '@/utils/list-state.js'

const typeLabels = {
  book: '教材版本',
  knowledge: '知识点',
  type: '题型',
  difficulty: '难度',
}

const tags = ref([])
const filterType = ref('')
const drawerOpen = ref(false)
const editingTag = ref(null)
const feedback = ref('')
const feedbackTone = ref('success')
const createForm = reactive({
  name: '',
  tag_type: 'knowledge',
  sort_order: 1,
})
const editForm = reactive({
  name: '',
  sort_order: 1,
})

const activeFilterItems = computed(() =>
  describeActiveFilters(
    { filterType: filterType.value },
    {
      filterType: {
        label: '标签类型',
        format: (value) => typeLabels[value] || value,
      },
    }
  )
)

const resultMeta = computed(() =>
  buildResultMeta({
    total: tags.value.length,
    page: 1,
    pageSize: tags.value.length || 1,
    noun: '个标签',
    activeFilterCount: activeFilterItems.value.length,
  })
)

const emptyState = computed(() =>
  buildEmptyState({
    noun: '标签',
    hasFilters: activeFilterItems.value.length > 0,
    defaultHint:
      activeFilterItems.value.length > 0
        ? '当前类型下暂无标签，可以切换其他分类或直接新建。'
        : '当前还没有标签数据，可以先创建教材版本、知识点或难度标签。',
  })
)

const showEmptyState = computed(() => feedbackTone.value !== 'error' && tags.value.length === 0)

function applyFeedback(message, tone = 'success') {
  feedback.value = message
  feedbackTone.value = tone
}

async function loadTags() {
  const data = await adminApi.listTags({ tag_type: filterType.value || undefined })
  tags.value = Array.isArray(data) ? data : []
}

async function createTag() {
  try {
    await adminApi.createTag({
      name: createForm.name,
      tag_type: createForm.tag_type,
      sort_order: Number(createForm.sort_order),
    })
    applyFeedback('标签创建成功。')
    createForm.name = ''
    await loadTags()
  } catch (error) {
    applyFeedback(error.message || '标签创建失败。', 'error')
  }
}

function openEditor(tag) {
  editingTag.value = tag
  editForm.name = tag.name
  editForm.sort_order = tag.sort_order
  drawerOpen.value = true
}

async function saveTag() {
  try {
    await adminApi.updateTag(editingTag.value.id, {
      name: editForm.name,
      sort_order: Number(editForm.sort_order),
    })
    applyFeedback('标签更新成功。')
    drawerOpen.value = false
    await loadTags()
  } catch (error) {
    applyFeedback(error.message || '标签更新失败。', 'error')
  }
}

async function removeTag(tag) {
  if (!window.confirm(`确定删除标签「${tag.name}」吗？若被题目引用会被后端拦截。`)) return
  try {
    await adminApi.deleteTag(tag.id)
    applyFeedback('标签已删除。')
    await loadTags()
  } catch (error) {
    applyFeedback(error.message || '标签删除失败。', 'error')
  }
}

onMounted(async () => {
  try {
    await loadTags()
  } catch (error) {
    applyFeedback(error.message || '标签列表加载失败。', 'error')
  }
})
</script>
