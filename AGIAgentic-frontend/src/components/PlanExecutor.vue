<template>
  <div class="plan-executor">
    <div class="header">
      <h1>🎯 计划执行器</h1>
      <div class="input-section">
        <textarea
          v-model="userTask"
          placeholder="请输入任务描述..."
          class="task-input"
          rows="3"
        ></textarea>
        <div class="controls">
          <input
            v-model="userId"
            type="text"
            placeholder="用户ID"
            class="user-id-input"
          />
          <button
            @click="startExecution"
            :disabled="isExecuting"
            class="start-btn"
          >
            {{ isExecuting ? '执行中...' : '🚀 开始执行' }}
          </button>
          <button
            @click="clearLogs"
            :disabled="isExecuting"
            class="clear-btn"
          >
            🗑️ 清空日志
          </button>
        </div>
      </div>
    </div>

    <div class="content">
      <!-- 执行状态概览 -->
      <div class="status-overview" v-if="executionStatus">
        <div class="status-card">
          <div class="status-item">
            <span class="label">状态:</span>
            <span :class="['status-badge', executionStatus.status]">
              {{ executionStatus.statusText }}
            </span>
          </div>
          <div class="status-item" v-if="executionStatus.totalTime">
            <span class="label">总耗时:</span>
            <span class="value">{{ executionStatus.totalTime }}秒</span>
          </div>
          <div class="status-item" v-if="executionStatus.completedSteps">
            <span class="label">完成步骤:</span>
            <span class="value">{{ executionStatus.completedSteps }}/{{ executionStatus.totalSteps }}</span>
          </div>
        </div>
      </div>

      <!-- 执行日志 -->
      <div class="logs-container">
        <div class="logs-header">
          <h2>📋 执行日志</h2>
          <div class="log-filters">
            <label
              v-for="filter in logFilters"
              :key="filter.type"
              class="filter-checkbox"
            >
              <input
                type="checkbox"
                v-model="filter.enabled"
                @change="filterLogs"
              />
              <span>{{ filter.label }}</span>
            </label>
          </div>
        </div>
        <div class="logs" ref="logsContainer">
          <div
            v-for="(log, index) in filteredLogs"
            :key="index"
            :class="['log-item', `log-${log.eventType}`]"
          >
            <div class="log-header">
              <span class="log-icon">{{ getEventIcon(log.eventType) }}</span>
              <span class="log-event">{{ log.eventType }}</span>
              <span class="log-time">{{ log.timestamp }}</span>
            </div>
            <div class="log-content">
              <div class="log-message" v-if="log.message">
                {{ log.message }}
              </div>
              <div class="log-data" v-if="log.data">
                <div class="data-section" v-if="log.data.step || log.step">
                  <strong>步骤:</strong> {{ log.data.step || log.step }}
                </div>
                <div class="data-section" v-if="log.data.node || log.node">
                  <strong>节点:</strong> {{ log.data.node || log.node }}
                </div>
                <div class="data-section" v-if="log.data.agent">
                  <strong>代理:</strong> {{ log.data.agent }}
                </div>
                <div class="data-section" v-if="log.data.tool">
                  <strong>工具:</strong> {{ log.data.tool }}
                </div>
                <div
                  class="data-section execution-result"
                  v-if="log.data.execution_result"
                >
                  <strong>执行结果:</strong>
                  <div class="result-content" v-html="formatResult(log.data.execution_result)"></div>
                </div>
                <div
                  class="data-section"
                  v-if="log.data.step_results"
                >
                  <strong>步骤结果:</strong>
                  <div class="step-results">
                    <div
                      v-for="(stepResult, idx) in log.data.step_results"
                      :key="idx"
                      class="step-result-item"
                    >
                      <div class="step-header">步骤 {{ stepResult.step }}</div>
                      <div class="step-content" v-html="formatResult(stepResult.execution_result)"></div>
                      <div class="step-status" :class="stepResult.status">
                        状态: {{ stepResult.status === 'completed' ? '已完成' : stepResult.status }}
                      </div>
                    </div>
                  </div>
                </div>
                <div
                  class="data-section"
                  v-if="log.data.task_analysis"
                >
                  <strong>任务分析:</strong>
                  <div class="result-content">{{ log.data.task_analysis }}</div>
                </div>
                <div
                  class="data-section"
                  v-if="log.data.execution_plans"
                >
                  <strong>执行计划:</strong>
                  <div class="plans-list">
                    <div
                      v-for="(plan, idx) in log.data.execution_plans"
                      :key="idx"
                      class="plan-item"
                    >
                      <div class="plan-step">步骤 {{ plan.step }}: {{ plan.description }}</div>
                      <div class="plan-result">预期结果: {{ plan.expected_result }}</div>
                    </div>
                  </div>
                </div>
                <div
                  class="data-section"
                  v-if="log.data.response"
                >
                  <strong>最终响应:</strong>
                  <div class="result-content" v-html="formatMarkdown(log.data.response)"></div>
                </div>
                <!-- 显示原始数据（如果解析失败） -->
                <div class="data-section" v-if="log.data && log.data.raw && log.data.error">
                  <strong>⚠️ 原始数据（解析失败）:</strong>
                  <div class="result-content" style="background: #fff3cd; color: #856404;">
                    <pre style="white-space: pre-wrap; word-break: break-all;">{{ log.data.raw }}</pre>
                    <div style="margin-top: 8px; color: #dc3545;">错误: {{ log.data.error }}</div>
                  </div>
                </div>
                <!-- 调试信息：显示原始数据 -->
                <details class="data-section debug-info" v-if="log.rawData">
                  <summary style="cursor: pointer; color: #999; font-size: 12px;">🔍 调试信息（展开查看原始数据）</summary>
                  <pre style="background: #f5f5f5; padding: 8px; border-radius: 4px; overflow-x: auto; font-size: 11px; margin-top: 8px; white-space: pre-wrap;">{{ JSON.stringify(log.rawData, null, 2) }}</pre>
                </details>
              </div>
            </div>
          </div>
          <div v-if="filteredLogs.length === 0 && logs.length > 0" class="empty-logs">
            日志已过滤，请检查过滤器设置（当前日志总数: {{ logs.length }}）
          </div>
          <div v-if="logs.length === 0 && !isExecuting" class="empty-logs">
            暂无日志数据
          </div>
          <div v-if="isExecuting && logs.length === 0" class="empty-logs">
            正在接收数据...
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'

const userTask = ref('调用工具帮我算下命，出生时间2011年10月19日8点，不需要让我确认信息')
const userId = ref('0002')
const isExecuting = ref(false)
const logs = ref([])
const logsContainer = ref(null)

const logFilters = ref([
  { type: 'on_chain_start', label: '链开始', enabled: true },
  { type: 'on_chain_stream', label: '流式数据', enabled: true },
  { type: 'on_chain_end', label: '链结束', enabled: true },
  { type: 'on_tool_start', label: '工具开始', enabled: true },
  { type: 'on_tool_end', label: '工具结束', enabled: true },
  { type: 'ping', label: '心跳', enabled: false }
])

const executionStatus = ref(null)

const filteredLogs = computed(() => {
  const enabledTypes = logFilters.value
    .filter(f => f.enabled)
    .map(f => f.type)
  const filtered = logs.value.filter(log => enabledTypes.includes(log.eventType))
  console.log('过滤日志:', { 
    total: logs.value.length, 
    filtered: filtered.length, 
    enabledTypes,
    logTypes: logs.value.map(l => l.eventType)
  })
  return filtered
})

const getEventIcon = (eventType) => {
  const icons = {
    'on_chain_start': '🚀',
    'on_chain_stream': '📊',
    'on_chain_end': '✅',
    'on_tool_start': '🔧',
    'on_tool_end': '✔️',
    'ping': '💓'
  }
  return icons[eventType] || '📝'
}

const formatResult = (result) => {
  if (typeof result === 'string') {
    return formatMarkdown(result)
  }
  if (typeof result === 'object') {
    if (result.execution_result) {
      return formatMarkdown(result.execution_result)
    }
    // 如果是对象，尝试格式化显示
    if (Object.keys(result).length > 0) {
      let formatted = ''
      for (const [key, value] of Object.entries(result)) {
        if (typeof value === 'string' && value.length > 50) {
          formatted += `<div><strong>${key}:</strong> ${formatMarkdown(value)}</div>`
        } else if (typeof value === 'object') {
          formatted += `<div><strong>${key}:</strong> ${JSON.stringify(value, null, 2)}</div>`
        } else {
          formatted += `<div><strong>${key}:</strong> ${value}</div>`
        }
      }
      return formatted || JSON.stringify(result, null, 2)
    }
    return JSON.stringify(result, null, 2)
  }
  return String(result)
}

const formatMarkdown = (text) => {
  if (!text) return ''
  // 简单的markdown格式化
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/### (.*?)\n/g, '<h3>$1</h3>')
    .replace(/## (.*?)\n/g, '<h2>$1</h2>')
    .replace(/# (.*?)\n/g, '<h1>$1</h1>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const filterLogs = () => {
  // 触发重新计算
}

const startExecution = async () => {
  if (!userTask.value.trim()) {
    alert('请输入任务描述')
    return
  }

  isExecuting.value = true
  logs.value = []
  executionStatus.value = {
    status: 'running',
    statusText: '执行中...'
  }

  try {
    const response = await fetch('/api/v1/plan_executor/stream', {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_task: userTask.value,
        user_id: userId.value
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentEvent = null

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      
      // SSE格式：event: xxx\n\ndata: xxx\n\n
      const chunks = buffer.split('\n\n')
      buffer = chunks.pop() || ''

      for (const chunk of chunks) {
        if (!chunk.trim()) continue
        
        const lines = chunk.split('\n')
        let eventType = null
        let dataStr = null

        for (const line of lines) {
          const trimmed = line.trim()
          if (trimmed.startsWith('event:')) {
            eventType = trimmed.replace('event:', '').trim()
          } else if (trimmed.startsWith('data:')) {
            dataStr = trimmed.replace('data:', '').trim()
          } else if (trimmed.startsWith(':')) {
            // 注释行，忽略
            continue
          }
        }

        if (dataStr && !dataStr.startsWith('ping') && !dataStr.startsWith(': ping')) {
          console.log('收到数据:', { eventType, dataStr: dataStr.substring(0, 150) })
          try {
            let data
            
            // 方法1: 尝试使用Function构造器直接解析Python字典（最可靠）
            try {
              // 先处理Python关键字，避免被当作变量名
              let processedStr = dataStr
                .replace(/:\s*True\b/g, ': true')
                .replace(/:\s*False\b/g, ': false')
                .replace(/:\s*None\b/g, ': null')
                .replace(/'/g, '"') // 将单引号替换为双引号
              
              // 使用Function构造器安全解析
              const func = new Function('return ' + processedStr)
              data = func()
              
              // 验证结果
              if (typeof data !== 'object' || data === null) {
                throw new Error('解析结果不是对象')
              }
              
              console.log('Function解析成功:', data)
            } catch (funcError) {
              // 方法2: 尝试JSON解析（如果Function失败）
              console.warn('Function解析失败，尝试JSON:', funcError.message)
              try {
                let jsonStr = dataStr
                  .replace(/:\s*True\b/g, ': true')
                  .replace(/:\s*False\b/g, ': false')
                  .replace(/:\s*None\b/g, ': null')
                  .replace(/'/g, '"')
                
                data = JSON.parse(jsonStr)
                console.log('JSON解析成功:', data)
              } catch (jsonError) {
                throw new Error(`Function和JSON解析都失败: ${funcError.message}, ${jsonError.message}`)
              }
            }
            
            // 成功解析后处理数据
            handleStreamData(data, eventType)
          } catch (e) {
            console.error('解析失败:', e.message)
            console.error('原始数据:', dataStr)
            // 即使解析失败，也添加日志条目显示原始数据
            const fallbackEventType = eventType || getEventTypeFromStep('unknown')
            logs.value.push({
              eventType: fallbackEventType,
              message: '数据解析失败: ' + e.message,
              timestamp: new Date().toLocaleTimeString(),
              data: { 
                raw: dataStr, 
                error: e.message,
                eventType: eventType
              },
              rawData: { raw: dataStr }
            })
            scrollToBottom()
          }
        }
      }
    }
  } catch (error) {
    console.error('Execution error:', error)
    logs.value.push({
      eventType: 'error',
      message: `执行失败: ${error.message}`,
      timestamp: new Date().toLocaleTimeString(),
      data: {}
    })
  } finally {
    isExecuting.value = false
    executionStatus.value = {
      ...executionStatus.value,
      status: 'completed',
      statusText: '执行完成'
    }
    scrollToBottom()
  }
}

const handleStreamData = (data, eventTypeFromStream = null) => {
  // 优先使用流中的event类型，否则从data.step推断
  let eventType = eventTypeFromStream || data.step || 'unknown'
  
  // 确保eventType有on_前缀，以匹配过滤器
  if (eventType.startsWith('on_')) {
    // 已经是on_开头，直接使用
    eventType = eventType
  } else {
    // 从step推断，确保返回带on_前缀的类型
    eventType = getEventTypeFromStep(eventType)
  }

  console.log('处理数据:', { eventType, eventTypeFromStream, step: data.step, message: data.message })

  // 合并data和data.data，确保所有字段都能访问到
  const logData = { ...data, ...(data.data || {}) }
  
  const logEntry = {
    eventType: eventType,
    message: data.message || '',
    timestamp: new Date().toLocaleTimeString(),
    data: logData,
    // 也保存原始数据用于调试
    rawData: data
  }

  logs.value.push(logEntry)
  console.log('日志已添加，当前日志数量:', logs.value.length)

  // 更新执行状态
  if (data.step === 'completed' || (data.data && data.data.step === 'completed')) {
    const stepData = data.data || data
    executionStatus.value = {
      status: 'completed',
      statusText: '执行完成',
      totalTime: stepData.timing_info?.response_generation_duration || 
                 (stepData.message && stepData.message.match(/总耗时:\s*([\d.]+)秒/)?.[1]) || 0,
      completedSteps: stepData.completed_nodes || 0,
      totalSteps: stepData.total_nodes || 0
    }
  }

  scrollToBottom()
}

const getEventTypeFromStep = (step) => {
  if (!step) return 'on_chain_stream'
  const stepStr = String(step).toLowerCase()
  if (stepStr.includes('chain_start') || stepStr === 'agent_start') return 'on_chain_start'
  if (stepStr.includes('chain_stream') || stepStr.includes('step_')) return 'on_chain_stream'
  if (stepStr.includes('chain_end') || stepStr.includes('complete') || stepStr === 'agent_complete') return 'on_chain_end'
  if (stepStr.includes('tool_start')) return 'on_tool_start'
  if (stepStr.includes('tool_complete') || stepStr.includes('tool_end')) return 'on_tool_end'
  if (stepStr === 'ping') return 'ping'
  return 'on_chain_stream'
}

const scrollToBottom = () => {
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}

const clearLogs = () => {
  logs.value = []
  executionStatus.value = null
}

onMounted(() => {
  // 组件挂载后的初始化
})
</script>

<style scoped>
.plan-executor {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 28px;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  transition: border-color 0.3s;
}

.task-input:focus {
  outline: none;
  border-color: #667eea;
}

.controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.user-id-input {
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  width: 120px;
}

.start-btn,
.clear-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.start-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.start-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.start-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.clear-btn {
  background: #f5f5f5;
  color: #666;
}

.clear-btn:hover:not(:disabled) {
  background: #e0e0e0;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.status-overview {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.status-card {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-weight: 600;
  color: #666;
}

.value {
  color: #333;
  font-weight: 500;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.running {
  background: #e3f2fd;
  color: #1976d2;
}

.status-badge.completed {
  background: #e8f5e9;
  color: #388e3c;
}

.logs-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 300px);
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.logs-header h2 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.log-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
}

.logs {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
  max-height: calc(100vh - 400px);
}

.log-item {
  margin-bottom: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.log-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.log-on_chain_start {
  border-left-color: #2196f3;
}

.log-on_chain_stream {
  border-left-color: #4caf50;
}

.log-on_chain_end {
  border-left-color: #ff9800;
}

.log-on_tool_start {
  border-left-color: #9c27b0;
}

.log-on_tool_end {
  border-left-color: #00bcd4;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.log-icon {
  font-size: 18px;
}

.log-event {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.log-time {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.log-message {
  margin-bottom: 8px;
  color: #555;
  font-size: 14px;
  line-height: 1.6;
}

.log-data {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.data-section {
  margin-bottom: 12px;
  font-size: 13px;
  line-height: 1.6;
}

.data-section strong {
  color: #667eea;
  margin-right: 8px;
}

.result-content {
  margin-top: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  color: #333;
  line-height: 1.8;
}

.result-content :deep(h1),
.result-content :deep(h2),
.result-content :deep(h3) {
  margin: 12px 0 8px 0;
  color: #333;
}

.result-content :deep(strong) {
  color: #667eea;
}

.result-content :deep(code) {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.plans-list {
  margin-top: 8px;
}

.plan-item {
  padding: 10px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #667eea;
}

.plan-step {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.plan-result {
  font-size: 12px;
  color: #666;
}

.execution-result {
  background: #fff3cd;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #ffc107;
}

.step-results {
  margin-top: 8px;
}

.step-result-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #667eea;
}

.step-header {
  font-weight: 600;
  color: #667eea;
  margin-bottom: 8px;
  font-size: 14px;
}

.step-content {
  margin-bottom: 8px;
  color: #333;
  line-height: 1.6;
}

.step-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.step-status.completed {
  background: #e8f5e9;
  color: #388e3c;
}

.empty-logs {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 14px;
}

/* 滚动条样式 */
.logs::-webkit-scrollbar {
  width: 8px;
}

.logs::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.logs::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.logs::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
