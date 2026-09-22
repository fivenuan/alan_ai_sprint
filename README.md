# alan_ai_sprint

> 我的 1 个月 AI Agent 转型 sprint · 从广告算法工程师到 AI Agent 工程 + 强化学习

## 我是谁

alan，985 数学本科，前广告算法工程师（竞价 / CTR 预估），正在转型 AI Agent 工程。

## 为什么转

对 agent 系统、工作流和强化学习感兴趣，想把算法背景用在 agent harness 与反馈机制工程上。

## 这个仓库的目标

1 个月全职冲刺（8h/天）：Python 工程纪律 + LLM 工程 + Harness + 第一个 production-quality agent demo。

## 已完成的项目

| Day | 项目 | 学到的核心 |
|---|---|---|
| 1 | 工程管线接入 | pytest / ruff / mypy strict / pre-commit / uv 工作流 |
| 2 | [pydantic JSON parser](src/alan_ai_sprint/parser.py) | 强类型数据验证、两步解析分离语法/Schema 错误、TDD、退出码约定 |
| 3 | [并发 URL 抓取器](src/alan_ai_sprint/fetcher.py) | asyncio 协程 / gather / Semaphore 限流 / monkeypatch 打桩测试（22 测试全绿，不打真网） |

```bash
# 快速上手
uv sync
uv run pytest                      # 22 个测试
uv run parse-json data/sample_response.json
uv run fetch-urls data/urls.txt    # 并发抓取，4 成功 / 2 失败路径演示
```

## 进度

- [x] Day 0: 仓库创建，防刷环境搭建
- [x] Day 1: 工程纪律接入（pytest + ruff + mypy + pre-commit + 首个 commit）
- [x] Day 2: pydantic JSON parser + 工程纪律真实应用
- [x] Day 3: asyncio 并发抓取器（gather + Semaphore + 打桩测试）
- [ ] Week 1: Python 工程纪律补课（进行中）
- [ ] Week 2: LLM 工程底座
- [ ] Week 3: Harness 雏形
- [ ] Day 30: 对外可见 demo + 简历锚点

## 如何联系

- GitHub Issues / Discussions 欢迎交流

## License

MIT
