# 阶段收尾记录

## 已完成修改
1. 新增默声模式文本对话后端接口，支持文本直连 LLM（不依赖 STT/TTS）。
2. 前端增加默声输入框与发送按钮，支持回车发送。
3. 新增语音模式/默声模式切换，默声模式下阻断麦克风静音自动触发逻辑。
4. Live2D 动作触发做了保底策略，避免看起来“无动作”。
5. 情绪分析模型从固定模型改为可配置，默认跟随当前 AI 模型。
6. 默认模型策略调整为本地可用且支持视觉链路的模型。
7. 摄像头链路已实测通过（camera-state / video-frame 成功）。

## 已做但未完全闭环
1. 已把 TTS 切到硅基流动并填入配置，但实际调用曾出现 403，需要后续按账号权限/额度继续排查。
2. 已切到原版 Whisper 基础端点，但 WHISPER_API_KEY 仍未配置，语音识别未完成闭环。
3. qwen3.5-9b 在当前本地环境可见但加载失败，暂未修复到可稳定运行状态。

## 计划中但还没做
1. 增加模型可用性探测与自动回退（例如 9b 失败自动回退到 8b/4b）。
2. 增加 Live2D 动作进一步随机化保底（连续 neutral 时自动轮换 random 动作）。
3. 增加前端对 API 配置有效性的可视化健康检查（LLM/STT/TTS 一键体检）。
4. 进一步优化本地模式稳定性（减少 Model reloaded 抖动带来的“卡住”感）。

## 接下来需要做
1. 补齐语音识别配置：
   - 填 WHISPER_API_KEY
   - 验证 WHISPER_BASE_URL 对应服务可用
2. 修复 TTS 403：
   - 检查硅基流动 key 权限与余额
   - 核对 voice id 可用性
3. 确认最终部署路线（官方 API 路线）：
   - 本地 WebSocket 服务保持
   - LLM/ASR/TTS 使用官方或兼容外部 API
4. 做一次完整验收：
   - 语音模式：说话 -> 识别 -> 回复 -> 播放
   - 默声模式：输入 -> 回复 -> 动作
   - 摄像头模式：开关与帧处理

## 注意事项
1. 对话中明文出现过 API key，建议立刻在平台侧轮换新 key。
2. 当前 Node 版本与 service 声明版本有 warning（可跑但有潜在兼容风险）。
3. 多次 server.py exit code 1 很多是端口占用导致的重复启动，不是同一个功能性崩溃。
4. 前端保存了本地配置（localStorage），调试模型时要注意旧配置覆盖默认值的问题。

## 如何运行项目（本地 WebSocket + 外部 API）
1. 准备环境
   - Node.js 建议 18（当前 24 可运行，但会有 engine warning）。
   - pnpm 已安装。
   - Python 3.10+，并确保 `service/webrtc/.venv` 可用。

2. 填写后端配置（`service/webrtc/.env`）
   - LLM：`LLM_BASE_URL`、`LLM_API_KEY`、`AI_MODEL`
   - ASR：`WHISPER_BASE_URL`、`WHISPER_API_KEY`、`WHISPER_MODEL`
   - TTS：`TTS_BASE_URL`、`TTS_API_KEY`、`TTS_VOICE`（或 `SILICONFLOW_*`）
   - 可选：`MEM0_API_KEY`

3. 安装依赖
   - 根目录：`pnpm install`
   - service 目录：`pnpm install`
   - webrtc 目录（首次）：创建并安装 Python 依赖

4. 启动三个服务（分别开三个终端）
   - 终端 A（WebRTC）：
     - `cd service/webrtc`
     - `d:\Regular-dev\amadeus\service\webrtc\.venv\Scripts\python.exe server.py`
   - 终端 B（Node 代理）：
     - `cd service`
     - `pnpm dev`
   - 终端 C（前端）：
     - `cd .`
     - `pnpm dev`

5. 访问与检查
   - 前端地址：`http://localhost:1002`
   - 代理端口：`3002`
   - WebRTC 端口：`8001`
   - 快速检查命令：
     - `Test-NetConnection 127.0.0.1 -Port 1002`
     - `Test-NetConnection 127.0.0.1 -Port 3002`
     - `Test-NetConnection 127.0.0.1 -Port 8001`

6. 使用方式
   - 默声模式：输入框直接发文字对话。
   - 语音模式：点击“麦克风”，允许浏览器麦克风权限后使用。
   - 摄像头：点击视频按钮并允许权限，后端会接收 `camera-state` / `video-frame`。

7. 常见故障
   - `server.py` 启动失败但端口是通的：通常是端口已被旧进程占用，先杀掉 8001 占用进程再启动。
   - TTS 403：优先检查 API Key 权限、余额、voice id。
   - STT 无结果：优先检查 `WHISPER_API_KEY` 和 `WHISPER_BASE_URL`。

