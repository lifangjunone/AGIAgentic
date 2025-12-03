# astream_events — API Reference

[English](#english) | [中文](#chinese) <!-- clickable links; default view is English (English section first) -->

<h2 id="english">English</h2>

Short, canonical reference for runtime streaming events emitted by the system. All events follow a 3‑phase lifecycle pattern where applicable: _start_ → one or more _stream_ / _data_ events → _end_. Events are delivered over Server-Sent Events (SSE) by default (each transmission uses the SSE "data" field with a JSON payload), but the same payloads apply to WebSocket or other streaming transports.

General envelope (every SSE data payload)
{
"event": string, // canonical event name (see list below)
"timestamp": string, // ISO8601 UTC timestamp, e.g. "2025-12-03T10:15:30Z"
"run_id": string, // unique id for the current run/task
"data": object // event-specific payload (detailed per event)
}

Notes / guarantees

- Ordering: For a given run_id, start → stream\* → end ordering is preserved by the emitter. Concurrent tools/models may interleave events; each event includes context metadata (e.g., node_id, tool_id).
- Multiplicity: stream/data events can occur multiple times (chunked outputs). Start and end occur once per invocation.
- Payloads must be JSON-serializable (primitives, dicts, lists). Do not include runtime objects (e.g., langchain HumanMessage) in events.
- Error reporting: errors appear in the relevant end event payload (see examples) and/or in a global "on_error" event if fatal.

Event categories and payload schemas

1. LangGraph lifecycle events

- on_chain_start
  - data: { "chain_name": string, "node_id": string, "metadata": object|null }
  - meaning: a chain or graph node execution started.
- on_chain_stream
  - data: { "node_id": string, "chunk": string|object, "progress": number|null }
  - meaning: intermediate streaming output from the chain/node.
- on_chain_end
  - data: { "node_id": string, "result": object|null, "error": string|null, "duration_ms": int }
  - meaning: chain/node finished; if error != null the execution failed.

2. Chat / model events

- on_chat_model_start
  - data: { "model": string, "model_version": string|null, "prompt_id": string|null }
  - meaning: model invocation started.
- on_chat_model_stream
  - data: { "model": string, "chunk": string, "token_index": int|null }
  - meaning: partial model output (text chunk).
- on_chat_model_end
  - data: { "model": string, "final_text": string|null, "error": string|null, "duration_ms": int }
  - meaning: model finished; error populated on failure.

3. Tool events

- on_tool_start
  - data: { "tool_id": string, "tool_name": string, "input": object|null }
  - meaning: tool execution began.
- on_tool_stream (optional)
  - data: { "tool_id": string, "chunk": object|string }
  - meaning: streaming output from the tool.
- on_tool_end
  - data: { "tool_id": string, "output": object|null, "error": string|null, "duration_ms": int }
  - meaning: tool finished; output holds final result.

4. Global / control events

- on_error
  - data: { "phase": string, "message": string, "details": object|null }
  - meaning: non-recoverable or top-level error outside a single node/tool.
- on_progress
  - data: { "percent": number, "message": string|null }
  - meaning: generic progress update.

Examples

- Chain start
  {
  "event": "on_chain_start",
  "timestamp": "2025-12-03T10:15:30Z",
  "run_id": "run-abc123",
  "data": { "chain_name": "plan_and_execute", "node_id": "check_and_execute", "metadata": null }
  }

- Model stream chunk (SSE data payload)
  {
  "event": "on_chat_model_stream",
  "timestamp": "2025-12-03T10:15:31Z",
  "run_id": "run-abc123",
  "data": { "model": "gpt-x", "chunk": "李白 was born in ", "token_index": 12 }
  }

- Tool end with error
  {
  "event": "on_tool_end",
  "timestamp": "2025-12-03T10:15:45Z",
  "run_id": "run-abc123",
  "data": { "tool_id": "bing_search", "output": null, "error": "HTTP 429 Too Many Requests", "duration_ms": 1200 }
  }

Best practices for consumers

- Always parse the top-level envelope and check run_id and event before using data.
- Treat stream events as partial; only the end event guarantees final result.
- Implement deduplication and idempotency using node_id/tool_id where applicable.
- Keep event handlers robust to unknown future fields: ignore unrecognized keys and prefer schema‑based parsing.
- If using SSE, parse each "data:" line as a standalone JSON object; do not expect a single JSON array.

If you want, I can:

- add TypeScript interfaces for each payload,
- provide example SSE client code (curl, JS EventSource),
- or extend the docs with a sequence diagram for a full plan execution flow.

<h2 id="chinese">中文</h2>

简明规范：本文件列出系统运行时发出的流式事件（streaming events）。事件通常遵循三阶段生命周期：开始（start）→ 若干流/数据事件（stream/data）→ 结束（end）。默认通过 Server-Sent Events (SSE) 发送（每次使用 SSE 的 "data" 字段，载荷为 JSON）；同样的载荷也适用于 WebSocket 或其他流式传输。

通用包裹（每个 SSE data 载荷）
{
"event": string, // 规范事件名（见下表）
"timestamp": string, // ISO8601 UTC 时间戳，如 "2025-12-03T10:15:30Z"
"run_id": string, // 当前运行/任务的唯一 id
"data": object // 事件特定的载荷（见下文）
}

说明 / 保证

- 顺序性：对于同一 run_id，发射端保证 start → stream\* → end 的顺序。并发工具/模型可能产生交错事件；每个事件包含上下文元数据（如 node_id、tool_id）。
- 重复性：stream/data 事件可多次出现（分块输出）。start 与 end 各自仅出现一次。
- 载荷必须可 JSON 序列化（基本类型、字典、列表）。不要在事件中包含运行时对象（例如 langchain 的 HumanMessage）。
- 错误报告：错误通常出现在对应的 end 事件的 payload 中（见示例），或作为全局 "on_error" 事件上报（严重错误）。

事件分类与字段规范

1. LangGraph 生命周期事件

- on_chain_start
  - data: { "chain_name": string, "node_id": string, "metadata": object|null }
  - 含义：某个链或图节点开始执行。
- on_chain_stream
  - data: { "node_id": string, "chunk": string|object, "progress": number|null }
  - 含义：链/节点的中间流式输出。
- on_chain_end
  - data: { "node_id": string, "result": object|null, "error": string|null, "duration_ms": int }
  - 含义：链/节点执行结束；若 error != null 则表示失败。

2. 聊天/模型事件

- on_chat_model_start
  - data: { "model": string, "model_version": string|null, "prompt_id": string|null }
  - 含义：模型调用开始。
- on_chat_model_stream
  - data: { "model": string, "chunk": string, "token_index": int|null }
  - 含义：模型的部分输出（文本分片）。
- on_chat_model_end
  - data: { "model": string, "final_text": string|null, "error": string|null, "duration_ms": int }
  - 含义：模型完成；出错时 error 有值。

3. 工具事件

- on_tool_start
  - data: { "tool_id": string, "tool_name": string, "input": object|null }
  - 含义：工具开始执行。
- on_tool_stream（可选）
  - data: { "tool_id": string, "chunk": object|string }
  - 含义：工具的流式输出。
- on_tool_end
  - data: { "tool_id": string, "output": object|null, "error": string|null, "duration_ms": int }
  - 含义：工具完成；output 为最终结果。

4. 全局 / 控制事件

- on_error
  - data: { "phase": string, "message": string, "details": object|null }
  - 含义：不可恢复或跨节点的顶级错误。
- on_progress
  - data: { "percent": number, "message": string|null }
  - 含义：通用进度更新。

示例

- 链开始
  {
  "event": "on_chain_start",
  "timestamp": "2025-12-03T10:15:30Z",
  "run_id": "run-abc123",
  "data": { "chain_name": "plan_and_execute", "node_id": "check_and_execute", "metadata": null }
  }

- 模型流分片（SSE data 载荷）
  {
  "event": "on_chat_model_stream",
  "timestamp": "2025-12-03T10:15:31Z",
  "run_id": "run-abc123",
  "data": { "model": "gpt-x", "chunk": "李白 was born in ", "token_index": 12 }
  }

- 工具结束并出错
  {
  "event": "on_tool_end",
  "timestamp": "2025-12-03T10:15:45Z",
  "run_id": "run-abc123",
  "data": { "tool_id": "bing_search", "output": null, "error": "HTTP 429 Too Many Requests", "duration_ms": 1200 }
  }

最佳实践（消费者侧）

- 解析顶层包裹并先检查 run_id 与 event 字段再使用 data。
- 将 stream 事件视为部分结果；仅以对应的 end 事件作为最终结果确认。
- 使用 node_id/tool_id 实现幂等与去重。
- 对未知字段保持兼容：忽略非识别键，采用基于 schema 的解析方法。
- 使用 SSE 时，按行解析每个 "data:" 行为一个独立 JSON 对象；不要假设返回的是单一 JSON 数组。

还可以提供（按需）

- TypeScript 接口定义
- SSE 客户端示例（curl / JS EventSource）
- 全流程的时序图 / 序列示例
