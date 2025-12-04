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
          <!-- <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
            <input type="checkbox" v-model="showAllLogs" />
            <span>显示所有日志（调试）</span>
          </label> -->
        </div>
      </div>
    </div>

    <div class="content">
      <!-- 执行状态概览 -->
      <div class="status-overview" v-if="executionStatus || logs.length > 0">
        <div class="status-card">
          <div class="status-item">
            <span class="label">状态:</span>
            <span :class="['status-badge', executionStatus?.status || 'unknown']">
              {{ executionStatus?.statusText || '等待中' }}
            </span>
          </div>
          <div class="status-item" v-if="executionStatus?.totalTime">
            <span class="label">总耗时:</span>
            <span class="value">{{ executionStatus.totalTime }}秒</span>
          </div>
          <div class="status-item" v-if="executionStatus?.completedSteps">
            <span class="label">完成步骤:</span>
            <span class="value">{{ executionStatus.completedSteps }}/{{ executionStatus.totalSteps }}</span>
          </div>
          <div class="status-item">
            <span class="label">日志总数:</span>
            <span class="value">{{ logs.length }}</span>
          </div>
          <div class="status-item">
            <span class="label">显示日志:</span>
            <span class="value">{{ filteredLogs.length }}</span>
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
          <!-- 调试信息 -->
          <div v-if="logs.length > 0" style="background: #f0f0f0; padding: 10px; margin-bottom: 10px; border-radius: 4px; font-size: 12px;">
            <strong>调试信息:</strong><br>
            总日志数: {{ logs.length }} | 
            过滤后日志数: {{ filteredLogs.length }} | 
            启用过滤器: {{ logFilters.filter(f => f.enabled).map(f => f.type).join(', ') }}
          </div>
          
          <div
            v-for="(log, index) in filteredLogs"
            :key="`log-${index}-${log.eventType}-${log.timestamp}-${Date.now()}`"
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
              <div class="log-data" v-if="log.data && Object.keys(log.data).length > 0">
                <div class="data-section" v-if="log.data.step || log.step">
                  <strong>步骤:</strong> {{ log.data.step || log.step }}
                </div>
                <div class="data-section" v-if="log.data.node || log.node">
                  <strong>节点:</strong> {{ log.data.node || log.node }}
                </div>
                <div class="data-section" v-if="log.data.agent || (log.data.data && log.data.data.agent)">
                  <strong>代理:</strong> {{ log.data.agent || (log.data.data && log.data.data.agent) }}
                </div>
                <div class="data-section" v-if="log.data.tool || (log.data.data && log.data.data.tool)">
                  <strong>工具:</strong> {{ log.data.tool || (log.data.data && log.data.data.tool) }}
                </div>
                <div class="data-section" v-if="log.data.message && log.data.message !== log.message">
                  <strong>消息:</strong> {{ log.data.message }}
                </div>
                <div
                  class="data-section execution-result"
                  v-if="log.data.execution_result || (log.data.data && log.data.data.execution_result)"
                >
                  <strong>执行结果:</strong>
                  <div class="result-content" v-html="formatResult(log.data.execution_result || (log.data.data && log.data.data.execution_result))"></div>
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
                  v-if="log.data.task_analysis || (log.data.data && log.data.data.task_analysis)"
                >
                  <strong>任务分析:</strong>
                  <div class="result-content">{{ log.data.task_analysis || (log.data.data && log.data.data.task_analysis) }}</div>
                </div>
                <div
                  class="data-section"
                  v-if="log.data.execution_plans || (log.data.data && log.data.data.execution_plans)"
                >
                  <strong>执行计划:</strong>
                  <div class="plans-list">
                    <div
                      v-for="(plan, idx) in (log.data.execution_plans || (log.data.data && log.data.data.execution_plans) || [])"
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
                  <pre style="background: #f5f5f5; padding: 8px; border-radius: 4px; overflow-x: auto; font-size: 11px; margin-top: 8px; white-space: pre-wrap;">{{ typeof log.rawData === 'string' ? log.rawData : JSON.stringify(log.rawData, null, 2) }}</pre>
                </details>
              </div>
            </div>
          </div>
          <div v-if="filteredLogs.length === 0 && logs.length > 0" class="empty-logs">
            <div style="color: #ff9800; margin-bottom: 10px;">
              ⚠️ 日志已过滤，请检查过滤器设置
            </div>
            <div style="font-size: 12px; color: #666;">
              当前日志总数: {{ logs.length }}<br>
              已启用过滤器: {{ logFilters.filter(f => f.enabled).map(f => f.label).join(', ') }}<br>
              日志类型分布: {{ Object.entries(logs.reduce((acc, log) => { acc[log.eventType] = (acc[log.eventType] || 0) + 1; return acc; }, {})).map(([type, count]) => `${type}: ${count}`).join(', ') }}
            </div>
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
import { ref, computed, nextTick, onMounted, watch } from 'vue'

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
  { type: 'ping', label: '心跳', enabled: false },
  { type: 'error', label: '错误', enabled: true },
  { type: 'unknown', label: '未知', enabled: true }
])

const executionStatus = ref(null)
const showAllLogs = ref(false) // 调试模式：显示所有日志

const filteredLogs = computed(() => {
  // 如果启用"显示所有日志"，直接返回所有日志
  if (showAllLogs.value) {
    console.log('🔓 调试模式：显示所有日志，总数:', logs.value.length)
    return logs.value
  }
  
  const enabledTypes = logFilters.value
    .filter(f => f.enabled)
    .map(f => f.type)
  const filtered = logs.value.filter(log => {
    const matches = enabledTypes.includes(log.eventType)
    if (!matches) {
      console.log('❌ 日志被过滤:', { eventType: log.eventType, enabledTypes, log })
    }
    return matches
  })
  console.log('📊 过滤日志计算:', { 
    total: logs.value.length, 
    filtered: filtered.length, 
    enabledTypes,
    logTypes: logs.value.map(l => l.eventType),
    filteredLogTypes: filtered.map(l => l.eventType)
  })
  return filtered
})

// 监听logs变化，强制触发更新
watch(() => logs.value.length, (newLength, oldLength) => {
  console.log('🔄 logs数组长度变化:', { oldLength, newLength })
  if (newLength > oldLength) {
    console.log('✅ 新日志已添加，当前总数:', newLength)
    console.log('📋 最新日志:', logs.value[logs.value.length - 1])
    nextTick(() => {
      console.log('🔍 nextTick后过滤日志数:', filteredLogs.value.length)
    })
  }
}, { immediate: true })

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
    let chunkCount = 0
    let totalBytesReceived = 0

    console.log('🚀 开始读取流式数据...')

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        console.log('✅ 流式数据读取完成，总共收到', chunkCount, '个数据块，', totalBytesReceived, '字节')
        break
      }

      chunkCount++
      totalBytesReceived += value.length
      const decoded = decoder.decode(value, { stream: true })
      buffer += decoded
      
      console.log(`📦 收到数据块 #${chunkCount}, 大小: ${value.length} 字节, 累计: ${totalBytesReceived} 字节, buffer长度: ${buffer.length}`)
      
      // 定义处理SSE数据的函数（在使用之前定义）
      const processSSEData = (dataStr, eventType) => {
        if (!dataStr) return

        console.log('📨 处理SSE数据:', { 
          eventType, 
          hasDataStr: !!dataStr,
          dataStrLength: dataStr ? dataStr.length : 0,
          preview: dataStr ? dataStr.substring(0, 100) : null
        })

        // 处理ping心跳消息
        if (dataStr && (dataStr.startsWith('ping') || dataStr.startsWith(': ping'))) {
          // ping消息单独处理，不添加到日志
          if (eventType === 'ping' || !eventType) {
            console.log('💓 收到ping心跳，跳过')
            return
          }
        }
        
        if (dataStr) {
          console.log('📥 收到原始数据:', { 
            eventType, 
            eventTypeType: typeof eventType,
            eventTypeValue: eventType,
            dataStrLength: dataStr.length, 
            preview: dataStr.substring(0, 200),
            fullDataStr: dataStr // 临时输出完整数据用于调试
          })
          
          // 临时：输出完整数据到控制台，方便调试
          if (dataStr.length < 1000) {
            console.log('📋 完整数据字符串:', dataStr)
          }
          
          try {
            let data
            
            // 改进的Python字典到JSON转换函数
            // 注意：实际数据中字符串值可能使用双引号，只有键使用单引号
            const pythonDictToJson = (pythonStr) => {
              let jsonStr = pythonStr.trim()
              
              // 1. 先处理Python关键字（必须在替换引号之前）
              jsonStr = jsonStr.replace(/:\s*True\b/g, ': true')
              jsonStr = jsonStr.replace(/:\s*False\b/g, ': false')
              jsonStr = jsonStr.replace(/:\s*None\b/g, ': null')
              
              // 2. 先保护双引号字符串（临时替换为占位符）
              const stringPlaceholders = []
              let placeholderIndex = 0
              
              // 匹配双引号字符串（包括转义的双引号）
              jsonStr = jsonStr.replace(/"(?:[^"\\]|\\.)*"/g, (match) => {
                const placeholder = `__STRING_PLACEHOLDER_${placeholderIndex}__`
                stringPlaceholders.push(match)
                placeholderIndex++
                return placeholder
              })
              
              // 3. 处理字典键：'key': -> "key":
              jsonStr = jsonStr.replace(/'([^']*)':\s*/g, '"$1": ')
              
              // 4. 处理单引号字符串值：: 'value' -> : "value"
              jsonStr = jsonStr.replace(/:\s*'([^']*)'(?=\s*[,}\]])/g, ': "$1"')
              
              // 5. 处理数组中的单引号字符串值
              jsonStr = jsonStr.replace(/\[\s*'([^']*)'\s*\]/g, '["$1"]')
              jsonStr = jsonStr.replace(/,\s*'([^']*)'\s*(?=[,\]])/g, ', "$1"')
              
              // 6. 处理剩余的单引号（嵌套字典的键等）
              jsonStr = jsonStr.replace(/'/g, '"')
              
              // 7. 恢复双引号字符串
              stringPlaceholders.forEach((original, index) => {
                jsonStr = jsonStr.replace(`__STRING_PLACEHOLDER_${index}__`, original)
              })
              
              return jsonStr
            }
            
            // 安全地解析Python字典格式：只使用JSON.parse，不执行任意代码
            try {
              let jsonStr = pythonDictToJson(dataStr)
              
              console.log('🔄 转换后的JSON字符串:', jsonStr.substring(0, 500))
              
              // 只使用JSON.parse，这是安全的，不会执行任意代码
              data = JSON.parse(jsonStr)
              
              // 验证结果必须是对象
              if (typeof data !== 'object' || data === null) {
                throw new Error('解析结果不是对象')
              }
              
              console.log('✅ JSON解析成功:', data)
            } catch (parseError) {
              // 如果JSON解析失败，尝试更宽松的转换
              console.warn('⚠️ JSON解析失败，尝试备用方法:', parseError.message)
              try {
                // 备用方法：使用相同的保护双引号字符串逻辑
                let jsonStr = dataStr.trim()
                
                // 处理Python关键字
                jsonStr = jsonStr.replace(/:\s*True\b/g, ': true')
                jsonStr = jsonStr.replace(/:\s*False\b/g, ': false')
                jsonStr = jsonStr.replace(/:\s*None\b/g, ': null')
                
                // 保护双引号字符串
                const stringPlaceholders = []
                let placeholderIndex = 0
                jsonStr = jsonStr.replace(/"(?:[^"\\]|\\.)*"/g, (match) => {
                  const placeholder = `__STRING_PLACEHOLDER_${placeholderIndex}__`
                  stringPlaceholders.push(match)
                  placeholderIndex++
                  return placeholder
                })
                
                // 处理字典键
                jsonStr = jsonStr.replace(/'([^']*)':\s*/g, '"$1": ')
                
                // 处理剩余的单引号
                jsonStr = jsonStr.replace(/'/g, '"')
                
                // 恢复双引号字符串
                stringPlaceholders.forEach((original, index) => {
                  jsonStr = jsonStr.replace(`__STRING_PLACEHOLDER_${index}__`, original)
                })
                
                console.log('🔄 备用方法转换后的JSON:', jsonStr.substring(0, 500))
                
                data = JSON.parse(jsonStr)
                
                if (typeof data !== 'object' || data === null) {
                  throw new Error('备用方法解析结果不是对象')
                }
                
                console.log('✅ 备用方法解析成功:', data)
              } catch (backupError) {
                console.error('❌ 所有解析方法都失败')
                console.error('原始数据长度:', dataStr.length)
                console.error('原始数据前500字符:', dataStr.substring(0, 500))
                console.error('主方法错误:', parseError.message)
                console.error('备用方法错误:', backupError.message)
                throw new Error(`数据解析失败: ${parseError.message}`)
              }
            }
            
            // 成功解析后处理数据
            console.log('🚀 准备处理数据:', { 
              eventType, 
              eventTypeType: typeof eventType,
              eventTypeValue: eventType,
              dataKeys: Object.keys(data), 
              step: data.step, 
              message: data.message,
              hasData: !!data.data,
              dataDataKeys: data.data ? Object.keys(data.data) : [],
              fullData: data
            })
            
            // 确保eventType存在且有效
            if (!eventType || typeof eventType !== 'string' || !eventType.trim()) {
              console.warn('⚠️ eventType无效:', eventType, '使用默认值on_chain_stream')
              eventType = 'on_chain_stream'
            } else {
              eventType = eventType.trim()
              console.log('✅ eventType有效:', eventType)
            }
            
            console.log('🎯 调用handleStreamData，参数:', { data, eventType })
            // 保存原始字符串到data对象中，以便在handleStreamData中使用
            data._rawString = dataStr
            handleStreamData(data, eventType, dataStr)
          } catch (e) {
            console.error('❌ 解析失败:', e)
            console.error('错误详情:', {
              message: e.message,
              stack: e.stack,
              name: e.name
            })
            console.error('原始数据:', dataStr)
            console.error('原始数据长度:', dataStr.length)
            console.error('eventType:', eventType)
            
            // 即使解析失败，也添加日志条目显示原始数据
            const fallbackEventType = eventType ? String(eventType) : 'on_chain_stream'
            const errorLog = {
              eventType: fallbackEventType,
              message: '数据解析失败: ' + e.message,
              timestamp: new Date().toLocaleTimeString(),
              data: { 
                raw: dataStr.substring(0, 500), // 只保存前500字符
                error: e.message,
                errorStack: e.stack,
                eventType: eventType
              },
              rawData: dataStr.substring(0, 1000) // 保存更多原始数据
            }
            logs.value.push(errorLog)
            logs.value = [...logs.value] // 强制更新
            console.log('⚠️ 错误日志已添加:', errorLog)
            console.log('📊 当前日志总数:', logs.value.length)
            scrollToBottom()
          }
        }
      }
      
      // SSE格式：event: xxx\n\ndata: xxx\n\n
      // 检查buffer内容，看看实际格式（只在第一次或buffer较大时检查）
      if ((chunkCount === 1 || chunkCount % 10 === 0) && buffer.length > 0) {
        const preview = buffer.substring(0, Math.min(300, buffer.length))
        console.log(`🔍 buffer内容预览 (长度: ${buffer.length}):`, preview.replace(/\n/g, '\\n').replace(/\r/g, '\\r'))
        console.log(`🔍 buffer包含\\n\\n:`, buffer.includes('\n\n'))
        console.log(`🔍 buffer包含\\r\\n\\r\\n:`, buffer.includes('\r\n\r\n'))
        console.log(`🔍 buffer包含单个\\n:`, buffer.includes('\n'))
        console.log(`🔍 buffer包含单个\\r:`, buffer.includes('\r'))
      }
      
      // 尝试多种分隔符
      let chunks = []
      let usedSeparator = ''
      
      // 先尝试标准的 \n\n
      if (buffer.includes('\n\n')) {
        chunks = buffer.split('\n\n')
        usedSeparator = '\\n\\n'
      } 
      // 再尝试 \r\n\r\n
      else if (buffer.includes('\r\n\r\n')) {
        chunks = buffer.split('\r\n\r\n')
        usedSeparator = '\\r\\n\\r\\n'
      }
      // 再尝试 \r\r
      else if (buffer.includes('\r\r')) {
        chunks = buffer.split('\r\r')
        usedSeparator = '\\r\\r'
      }
      // 如果都没有，但buffer很大，可能是数据还没完整，先不处理
      else {
        if (buffer.length > 5000) {
          console.warn(`⚠️ buffer很大 (${buffer.length}) 但没有找到分隔符，可能数据格式不对`)
          // 尝试查找 "event:" 和 "data:" 模式
          const eventMatches = buffer.match(/event:\s*([^\n\r]+)/g)
          const dataMatches = buffer.match(/data:\s*([^\n\r]+)/g)
          if (eventMatches || dataMatches) {
            console.log('🔍 找到event/data模式，但分隔符可能不对')
            console.log('event匹配:', eventMatches?.slice(0, 3))
            console.log('data匹配:', dataMatches?.slice(0, 3))
          }
        }
        // 继续等待更多数据
        continue
      }
      
      buffer = chunks.pop() || ''
      
      if (chunks.length > 0) {
        console.log(`✅ 使用 ${usedSeparator} 分隔符解析到 ${chunks.length} 个完整块，剩余buffer长度: ${buffer.length}`)
        
        // 处理每个完整块
        for (let i = 0; i < chunks.length; i++) {
          const chunk = chunks[i]
          if (!chunk.trim()) {
            console.log(`⏭️ 跳过空块 #${i + 1}`)
            continue
          }
          
          console.log(`🔍 处理块 #${i + 1}, 长度: ${chunk.length}, 内容预览: ${chunk.substring(0, 100)}`)
          
          const lines = chunk.split(/\r?\n/)
          let eventType = null
          let dataLines = []

          for (const line of lines) {
            const trimmed = line.trim()
            if (trimmed.startsWith('event:')) {
              eventType = trimmed.replace('event:', '').trim()
            } else if (trimmed.startsWith('data:')) {
              // 收集所有data行（SSE格式支持多行data）
              dataLines.push(trimmed.replace('data:', '').trim())
            } else if (trimmed.startsWith(':')) {
              // 注释行，忽略
              continue
            } else if (dataLines.length > 0 && trimmed) {
              // 如果已经有data行，后续的非空行也作为data的一部分（多行data）
              dataLines.push(trimmed)
            }
          }
          
          // 合并所有data行为一个字符串
          const dataStr = dataLines.length > 0 ? dataLines.join(' ') : null
          
          // 调用处理函数
          if (dataStr) {
            processSSEData(dataStr, eventType)
          }
        }
      }
    }
  } catch (error) {
    console.error('❌ Execution error:', error)
    console.error('错误详情:', {
      message: error.message,
      stack: error.stack,
      name: error.name
    })
    
    const errorLog = {
      eventType: 'error',
      message: `执行失败: ${error.message}`,
      timestamp: new Date().toLocaleTimeString(),
      data: {
        error: error.message,
        stack: error.stack,
        name: error.name
      },
      rawData: { error: error.message }
    }
    
    logs.value.push(errorLog)
    logs.value = [...logs.value] // 强制更新
    console.log('⚠️ 错误日志已添加:', errorLog)
    console.log('📊 当前日志总数:', logs.value.length)
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

const handleStreamData = (data, eventTypeFromStream = null, rawString = null) => {
  console.log('🔍 handleStreamData 调用:', { 
    data, 
    eventTypeFromStream,
    eventTypeFromStreamType: typeof eventTypeFromStream,
    eventTypeFromStreamValue: eventTypeFromStream,
    hasRawString: !!rawString,
    rawStringLength: rawString ? rawString.length : 0
  })
  
  // 优先使用流中的event类型（如果存在且有效）
  let eventType = null
  
  if (eventTypeFromStream && typeof eventTypeFromStream === 'string' && eventTypeFromStream.trim()) {
    // 如果流中有明确的event类型，优先使用
    eventType = eventTypeFromStream.trim()
    console.log('✅ 使用流中的eventType:', eventType)
  } else {
    console.log('⚠️ eventTypeFromStream无效，尝试推断:', { 
      eventTypeFromStream, 
      type: typeof eventTypeFromStream,
      trimmed: eventTypeFromStream ? String(eventTypeFromStream).trim() : null
    })
    // 否则从data.step推断
    const stepValue = data?.step || data?.data?.step || null
    if (stepValue) {
      eventType = getEventTypeFromStep(String(stepValue))
      console.log('🔄 从step推断eventType:', { step: stepValue, eventType })
    } else {
      // 默认使用on_chain_stream
      eventType = 'on_chain_stream'
      console.log('⚠️ 无法推断eventType，使用默认值:', eventType)
    }
  }
  
  // 确保eventType有on_前缀，以匹配过滤器
  if (!eventType || typeof eventType !== 'string' || !eventType.startsWith('on_')) {
    const inferredType = getEventTypeFromStep(eventType || 'unknown')
    console.log('🔄 补充on_前缀:', { from: eventType, to: inferredType })
    eventType = inferredType
  }
  
  // 最终验证eventType
  if (!eventType || typeof eventType !== 'string') {
    console.error('❌ eventType仍然无效，强制设置为on_chain_stream:', eventType)
    eventType = 'on_chain_stream'
  }
  
  console.log('✅ 最终确定的eventType:', eventType, '类型:', typeof eventType)

  console.log('📋 最终eventType:', eventType, '数据:', { 
    step: data?.step, 
    message: data?.message,
    hasData: !!data?.data,
    dataKeys: data?.data ? Object.keys(data.data) : []
  })

  // 合并data和data.data，确保所有字段都能访问到
  const logData = { ...data, ...(data.data || {}) }
  
  console.log('📦 合并后的logData keys:', Object.keys(logData))
  console.log('📦 logData内容预览:', {
    step: logData.step,
    message: logData.message,
    hasExecutionResult: !!logData.execution_result,
    hasTaskAnalysis: !!logData.task_analysis,
    hasExecutionPlans: !!logData.execution_plans,
    executionResultType: typeof logData.execution_result
  })
  
  // 准备rawData，优先使用传入的rawString，否则使用完整的data对象
  const rawDataToSave = rawString || data._rawString || data
  
  const logEntry = {
    eventType: String(eventType), // 确保是字符串
    message: data.message || '',
    timestamp: new Date().toLocaleTimeString(),
    data: logData,
    // 保存原始数据用于调试：优先保存原始字符串，否则保存完整data对象
    rawData: rawDataToSave
  }
  
  // 清理临时字段
  if (data._rawString) {
    delete data._rawString
  }
  
  console.log('📝 准备添加日志条目:', {
    eventType: logEntry.eventType,
    eventTypeType: typeof logEntry.eventType,
    message: logEntry.message,
    dataKeys: Object.keys(logEntry.data),
    logEntry: logEntry
  })

  // 直接push到数组
  const beforeLength = logs.value.length
  logs.value.push(logEntry)
  
  // 强制触发响应式更新 - 使用展开运算符创建新数组
  logs.value = [...logs.value]
  
  console.log('✅ 日志已添加到数组:', {
    beforeLength,
    afterLength: logs.value.length,
    eventType: logEntry.eventType,
    message: logEntry.message,
    dataKeys: Object.keys(logEntry.data),
    totalLogs: logs.value.length
  })
  console.log('📊 当前日志总数:', logs.value.length, '最新日志eventType:', logEntry.eventType)
  console.log('🔍 检查最新日志:', logs.value[logs.value.length - 1])
  
  // 在nextTick中检查过滤后的日志
  nextTick(() => {
    const enabledTypes = logFilters.value.filter(f => f.enabled).map(f => f.type)
    const willBeShown = enabledTypes.includes(logEntry.eventType)
    console.log('🔍 检查过滤器:', {
      enabledTypes,
      logEventType: logEntry.eventType,
      willBeShown,
      filteredLogsCount: filteredLogs.value.length,
      allLogEventTypes: logs.value.map(l => l.eventType),
      filteredLogEventTypes: filteredLogs.value.map(l => l.eventType)
    })
    
    if (!willBeShown) {
      console.warn('⚠️ 警告：日志不会被显示，因为eventType不在启用的过滤器中！')
      console.warn('启用过滤器:', enabledTypes)
      console.warn('日志eventType:', logEntry.eventType)
    }
  })

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
