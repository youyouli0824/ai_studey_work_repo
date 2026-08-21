/**
 * 全局未读私聊状态(供侧边栏「私聊」菜单红点显示)
 */
import { reactive } from 'vue'

export const unreadState = reactive({
  total: 0
})
