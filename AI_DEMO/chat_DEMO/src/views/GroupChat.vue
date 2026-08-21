<template>
  <div class="chat-page">
    <!-- 左: 群列表 -->
    <div class="chat-list">
      <div class="list-title">
        <span>我的群聊</span>
      </div>
      <div
        v-for="g in groups"
        :key="g.group_type"
        class="chat-item"
        :class="{ active: isActive(g) }"
        @click="switchGroup(g)"
      >
        <div class="chat-item-icon">
          <el-icon :size="20"><component :is="g.group_type === 'ALL' ? 'ChatDotSquare' : 'OfficeBuilding'" /></el-icon>
        </div>
        <div class="chat-item-main">
          <div class="chat-item-name">{{ g.name }}</div>
          <div class="chat-item-last">
            {{ g.last_message || '暂无消息' }}
          </div>
        </div>
        <div class="chat-item-meta">
          <div class="chat-item-count">{{ g.member_count }}人</div>
          <div class="chat-item-time">{{ shortTime(g.last_time) }}</div>
        </div>
      </div>
    </div>

    <!-- 右: 聊天窗口 -->
    <div class="chat-window">
      <template v-if="activeGroup">
        <div class="window-header">
          <span class="window-name">{{ activeGroup.name }}</span>
          <span class="window-meta">{{ activeGroup.member_count }} 名成员</span>
        </div>

        <div ref="msgBox" class="message-box">
          <div v-if="hasMore" class="load-more">
            <el-button text type="primary" :loading="loadingMore" @click="loadOlder">
              加载更早的消息
            </el-button>
          </div>
          <div v-for="m in messages" :key="m.message_id" class="message-row" :class="{ mine: isMine(m) }">
            <el-avatar :size="36" :src="m.sender_avatar || undefined" class="msg-avatar">
              {{ (m.sender_name || '?').charAt(0) }}
            </el-avatar>
            <div class="msg-body">
              <div class="msg-meta">
                <span class="msg-name">{{ m.sender_name }}</span>
                <span class="msg-time">{{ formatTime(m.created_at) }}</span>
              </div>
              <div class="msg-bubble">{{ m.content }}</div>
            </div>
          </div>
          <div v-if="!messages.length && !loading" class="empty-tip">
            还没有消息，来说点什么吧~
          </div>
        </div>

        <div class="input-area">
          <el-input
            v-model="draft"
            type="textarea"
            :rows="2"
            resize="none"
            maxlength="2000"
            show-word-limit
            placeholder="输入消息，Enter 发送，Shift+Enter 换行"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <div class="input-actions">
            <el-button type="primary" :loading="sending" @click="sendMessage">发送</el-button>
          </div>
        </div>
      </template>
      <div v-else class="window-empty">请选择一个群聊</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { chatApi } from '@/api'
import { authState } from '@/store/auth'

const PAGE_SIZE = 20
const groups = ref([])
const activeGroup = ref(null)

const messages = ref([])
const page = ref(0)
const total = ref(0)
const loading = ref(false)
const loadingMore = ref(false)
const sending = ref(false)
const draft = ref('')

const msgBox = ref()
let pollTimer = null
let lastMessageId = 0

function isActive(g) {
  return activeGroup.value && activeGroup.value.group_type === g.group_type
}

function isMine(m) {
  return Number(m.sender_id) === Number(authState.user?.EMPLOYEE_ID)
}

function shortTime(t) {
  if (!t) return ''
  return t.slice(5, 16) // MM-DD HH:MM
}

function formatTime(t) {
  if (!t) return ''
  return t.slice(5, 16)
}

async function loadMyGroups() {
  try {
    const data = await chatApi.myGroups()
    groups.value = data.groups
    if (data.groups.length) switchGroup(data.groups[0])
  } catch (e) {
    ElMessage.error(e.message || '加载群聊失败')
  }
}

function switchGroup(g) {
  activeGroup.value = g
  messages.value = []
  page.value = 0
  total.value = 0
  lastMessageId = 0
  draft.value = ''
  loadMessages()
}

/** 分页拉取历史消息 */
async function loadMessages() {
  if (!activeGroup.value) return
  loading.value = true
  try {
    const params = { page: page.value + 1, page_size: PAGE_SIZE }
    const data =
      activeGroup.value.group_type === 'ALL'
        ? await chatApi.allMessages(params)
        : await chatApi.deptMessages(params)
    // 追加到历史之前
    messages.value = [...data.items, ...messages.value]
    total.value = data.total
    page.value += 1
    lastMessageId = Math.max(lastMessageId, ...data.items.map((m) => Number(m.message_id)))
    if (page.value === 1) scrollToBottom()
  } catch (e) {
    ElMessage.error(e.message || '加载消息失败')
  } finally {
    loading.value = false
  }
}

async function loadOlder() {
  if (loadingMore.value) return
  loadingMore.value = true
  try {
    await loadMessages()
  } finally {
    loadingMore.value = false
  }
}

const hasMore = computed(() => messages.value.length < total.value)

/** 轮询获取新消息(仅增量追加) */
async function pollNewMessages() {
  if (!activeGroup.value || loading.value) return
  try {
    const params = { page: 1, page_size: PAGE_SIZE }
    const data =
      activeGroup.value.group_type === 'ALL'
        ? await chatApi.allMessages(params)
        : await chatApi.deptMessages(params)
    const fresh = data.items.filter((m) => Number(m.message_id) > lastMessageId)
    if (fresh.length) {
      const known = new Set(messages.value.map((m) => Number(m.message_id)))
      const uniq = fresh.filter((m) => !known.has(Number(m.message_id)))
      if (uniq.length) {
        messages.value.push(...uniq)
        lastMessageId = Math.max(lastMessageId, ...uniq.map((m) => Number(m.message_id)))
        total.value = data.total
        scrollToBottom()
      }
    }
  } catch (_) {
    /* 轮询失败静默,下一轮重试 */
  }
}

async function sendMessage() {
  const content = draft.value.trim()
  if (!content) return
  sending.value = true
  try {
    const isAll = activeGroup.value.group_type === 'ALL'
    if (isAll) await chatApi.sendAll(content)
    else await chatApi.sendDept(content)
    draft.value = ''
    await pollNewMessages()
  } catch (e) {
    ElMessage.error(e.message || '发送失败')
  } finally {
    sending.value = false
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  })
}

onMounted(() => {
  loadMyGroups()
  pollTimer = setInterval(pollNewMessages, 5000)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 60px);
  display: flex;
  background: #fff;
}

/* 群列表 */
.chat-list {
  width: 300px;
  border-right: 1px solid #eef2f7;
  overflow-y: auto;
  flex-shrink: 0;
}

.list-title {
  padding: 14px 16px 8px;
  font-size: 13px;
  color: #94a3b8;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.15s;
}

.chat-item:hover {
  background: #f5f7fa;
}

.chat-item.active {
  background: #eef4ff;
}

.chat-item-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-item-main {
  flex: 1;
  min-width: 0;
}

.chat-item-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-item-last {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 3px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-item-meta {
  text-align: right;
  flex-shrink: 0;
}

.chat-item-count {
  font-size: 11px;
  color: #94a3b8;
}

.chat-item-time {
  font-size: 11px;
  color: #c0c8d2;
  margin-top: 2px;
}

/* 聊天窗口 */
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.window-header {
  padding: 14px 20px;
  border-bottom: 1px solid #eef2f7;
  display: flex;
  align-items: center;
  gap: 12px;
}

.window-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.window-meta {
  font-size: 12px;
  color: #94a3b8;
}

.message-box {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  background: #f8fafc;
}

.load-more {
  text-align: center;
  margin-bottom: 6px;
}

.message-row {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}

.message-row.mine {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
  background: #2563eb;
  color: #fff;
}

.message-row.mine .msg-avatar {
  background: #10b981;
}

.msg-body {
  max-width: 60%;
}

.message-row.mine .msg-body {
  text-align: right;
}

.msg-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 4px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.message-row.mine .msg-meta {
  justify-content: flex-end;
}

.msg-name {
  color: #64748b;
  font-weight: 500;
}

.msg-bubble {
  display: inline-block;
  padding: 9px 14px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #e2e8f0;
  color: #1e293b;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
  white-space: pre-wrap;
  text-align: left;
}

.message-row.mine .msg-bubble {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}

.empty-tip {
  text-align: center;
  color: #c0c8d2;
  padding-top: 80px;
}

.window-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c8d2;
}

/* 输入区 */
.input-area {
  border-top: 1px solid #eef2f7;
  padding: 10px 16px 12px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
</style>
