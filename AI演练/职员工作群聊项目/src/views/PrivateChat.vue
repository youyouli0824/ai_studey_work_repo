<template>
  <div class="chat-page">
    <!-- 左: 会话 + 通讯录 -->
    <div class="chat-list">
      <el-tabs v-model="activeTab" class="list-tabs">
        <el-tab-pane label="会话" name="conv">
          <div class="list-body">
            <div
              v-for="conv in conversations"
              :key="conv.EMPLOYEE_ID"
              class="chat-item"
              :class="{ active: isActive(conv) }"
              @click="selectConversation(conv)"
            >
              <el-badge :value="conv.unread_count" :hidden="conv.unread_count === 0" :max="99" class="conv-badge">
                <el-avatar :size="40" :src="conv.avatar || undefined" class="chat-item-icon-avatar">
                  {{ (conv.name || '?').charAt(0) }}
                </el-avatar>
              </el-badge>
              <div class="chat-item-main">
                <div class="chat-item-name">
                  {{ conv.name }}
                  <el-tag v-if="conv.role !== 'STAFF'" size="small" :type="roleTagType(conv.role)" effect="plain">
                    {{ roleShort(conv.role) }}
                  </el-tag>
                </div>
                <div class="chat-item-last">{{ conv.last_message || '暂无消息' }}</div>
              </div>
              <div class="chat-item-meta">
                <div class="chat-item-time">{{ shortTime(conv.last_time) }}</div>
              </div>
            </div>
            <div v-if="!conversations.length" class="empty-tip">还没有会话，去通讯录找人聊聊吧</div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="通讯录" name="contact">
          <div class="list-search">
            <el-input v-model="keyword" placeholder="搜索职员姓名" clearable :prefix-icon="Search" />
          </div>
          <div class="list-body">
            <div
              v-for="c in filteredContacts"
              :key="c.EMPLOYEE_ID"
              class="chat-item"
              :class="{ active: isActive(c) }"
              @click="selectContact(c)"
            >
              <el-avatar :size="40" :src="c.avatar || undefined" class="chat-item-icon-avatar">
                {{ (c.name || '?').charAt(0) }}
              </el-avatar>
              <div class="chat-item-main">
                <div class="chat-item-name">
                  {{ c.name }}
                  <el-tag v-if="c.role !== 'STAFF'" size="small" :type="roleTagType(c.role)" effect="plain">
                    {{ roleShort(c.role) }}
                  </el-tag>
                </div>
                <div class="chat-item-last">{{ departmentLabel(c.DEPARTMENT_ID) || '未分配部门' }}</div>
              </div>
            </div>
            <div v-if="!filteredContacts.length" class="empty-tip">未找到相关职员</div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 右: 聊天窗口 -->
    <div class="chat-window">
      <template v-if="activeContact">
        <div class="window-header">
          <el-avatar :size="36" :src="activeContact.avatar || undefined" class="header-avatar">
            {{ (activeContact.name || '?').charAt(0) }}
          </el-avatar>
          <span class="window-name">{{ activeContact.name }}</span>
          <span class="window-meta">{{ departmentLabel(activeContact.DEPARTMENT_ID) || '未分配部门' }}</span>
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
            还没有消息，发送第一条打个招呼吧~
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
      <div v-else class="window-empty">从左侧选择一个会话或职员开始私聊</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { chatApi } from '@/api'
import { authState } from '@/store/auth'
import { departmentLabel } from '@/utils/labels'

const PAGE_SIZE = 20

/* 左侧列表 */
const activeTab = ref('conv')
const conversations = ref([])
const contacts = ref([])
const keyword = ref('')

const activeContact = ref(null)

/* 聊天窗口 */
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

const filteredContacts = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return contacts.value
  return contacts.value.filter((c) => c.name.toLowerCase().includes(kw))
})

function roleShort(role) {
  return role === 'PRESIDENT' ? '总裁' : '管理层'
}
function roleTagType(role) {
  return role === 'PRESIDENT' ? 'danger' : 'warning'
}

function isActive(x) {
  return activeContact.value && Number(activeContact.value.EMPLOYEE_ID) === Number(x.EMPLOYEE_ID)
}

function isMine(m) {
  return Number(m.sender_id) === Number(authState.user?.EMPLOYEE_ID)
}

function shortTime(t) {
  if (!t) return ''
  return t.slice(5, 16)
}
function formatTime(t) {
  if (!t) return ''
  return t.slice(5, 16)
}

async function loadContacts() {
  try {
    contacts.value = await chatApi.contacts()
  } catch (e) {
    ElMessage.error(e.message || '加载联系人失败')
  }
}

/** 打开聊天窗口(重置消息) */
function openChat(c) {
  activeContact.value = c
  messages.value = []
  page.value = 0
  total.value = 0
  lastMessageId = 0
  draft.value = ''
  loadMessages()
}

/** 点会话: 打开并标记已读,刷新列表去掉红点 */
async function selectConversation(conv) {
  activeTab.value = 'conv'
  openChat({
    EMPLOYEE_ID: conv.EMPLOYEE_ID,
    name: conv.name,
    avatar: conv.avatar,
    DEPARTMENT_ID: conv.DEPARTMENT_ID,
    role: conv.role
  })
  await chatApi.markRead(conv.EMPLOYEE_ID).catch(() => {})
  refreshConversations()
}

/** 点通讯录联系人: 打开(可能无历史,成为新会话) */
function selectContact(c) {
  openChat(c)
  chatApi.markRead(c.EMPLOYEE_ID).catch(() => {})
}

/** 会话列表(含未读数,服务端按最近消息置顶) */
async function refreshConversations() {
  try {
    conversations.value = await chatApi.conversations()
    // 正在查看的会话保持已读
    if (activeContact.value) {
      const cur = conversations.value.find(
        (x) => Number(x.EMPLOYEE_ID) === Number(activeContact.value.EMPLOYEE_ID)
      )
      if (cur && cur.unread_count > 0) {
        cur.unread_count = 0
        await chatApi.markRead(cur.EMPLOYEE_ID).catch(() => {})
      }
    }
  } catch (_) {
    /* 静默 */
  }
}

async function loadMessages() {
  if (!activeContact.value) return
  loading.value = true
  try {
    const data = await chatApi.privateMessages({
      contact_id: activeContact.value.EMPLOYEE_ID,
      page: page.value + 1,
      page_size: PAGE_SIZE
    })
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

async function pollNewMessages() {
  if (!activeContact.value || loading.value) return
  try {
    const data = await chatApi.privateMessages({
      contact_id: activeContact.value.EMPLOYEE_ID,
      page: 1,
      page_size: PAGE_SIZE
    })
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
    /* 静默 */
  }
}

async function sendMessage() {
  const content = draft.value.trim()
  if (!content || !activeContact.value) return
  sending.value = true
  try {
    await chatApi.sendPrivate({
      receiver_id: activeContact.value.EMPLOYEE_ID,
      content
    })
    draft.value = ''
    await pollNewMessages()
    refreshConversations()
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
  loadContacts()
  refreshConversations()
  pollTimer = setInterval(() => {
    pollNewMessages()
    refreshConversations()
  }, 5000)
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

.chat-list {
  width: 300px;
  border-right: 1px solid #eef2f7;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.list-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 4px;
}
.list-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
  padding: 0 12px;
}
.list-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  display: flex;
}
.list-tabs :deep(.el-tab-pane) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-search {
  padding: 10px 12px 6px;
}

.list-body {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.chat-item:hover {
  background: #f5f7fa;
}

.chat-item.active {
  background: #eef4ff;
}

.conv-badge :deep(.el-badge__content) {
  border: 2px solid #fff;
}

.chat-item-icon-avatar {
  flex-shrink: 0;
  background: #64748b;
  color: #fff;
  font-weight: 600;
}

.chat-item-main {
  flex: 1;
  min-width: 0;
}

.chat-item-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
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

.chat-item-time {
  font-size: 11px;
  color: #c0c8d2;
}

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

.header-avatar {
  background: #64748b;
  color: #fff;
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
  padding-top: 40px;
}

.window-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c8d2;
}

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
