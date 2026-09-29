# alan_ai_sprint

![CI](https://github.com/fivenuan/alan_ai_sprint/actions/workflows/ci.yml/badge.svg)

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
| 3 | [并发 URL 抓取器](src/alan_ai_sprint/fetcher.py) | asyncio 协程 / gather / Semaphore 限流 / monkeypatch 打桩测试（不打真网） |
| 4 | [可复用装饰器](src/alan_ai_sprint/decorators.py) | 装饰器工厂三层结构 / PEP 695 ParamSpec 泛型 / `@async_retry` 横切重试 / 生成器惰性读取 |
| 5 | 打包与版本管理 | dependencies vs dev 组 / semver / `uv build` 产物与 wheel 元数据 / 镜像瘦身 439→318MB |
| 6 | [Docker 化](Dockerfile) | 分层缓存（依赖层与代码层分离）/ uv `--no-install-project` / 退出码透传到容器 / compose 编排 |

```bash
# 快速上手
uv sync
uv run pytest                      # 29 个测试
uv run parse-json data/sample_response.json
uv run fetch-urls data/urls.txt    # 并发抓取，4 成功 / 2 失败路径演示
```

## Docker

```bash
docker build -t alan-fetcher:0.1.1 .
docker run --rm alan-fetcher:0.1.1        # 退出码 0=全成功 / 1=输入错误 / 2=部分失败

docker compose up --abort-on-container-exit --exit-code-from fetcher
```

分层设计：`pyproject.toml` + `uv.lock` + `README.md` 先行（依赖层，几乎不变），`src/` 后拷（代码层，常变）——改代码时依赖层命中缓存，重建秒级。镜像 318MB（dev 工具已迁出主依赖）。

## 进度

- [x] Day 0: 仓库创建，防刷环境搭建
- [x] Day 1: 工程纪律接入（pytest + ruff + mypy + pre-commit + 首个 commit）
- [x] Day 2: pydantic JSON parser + 工程纪律真实应用
- [x] Day 3: asyncio 并发抓取器（gather + Semaphore + 打桩测试）
- [x] Day 4: 装饰器工厂 + async_retry 横切重试 + 生成器（29 测试全绿）
- [x] Day 5: 打包与版本管理（dev 依赖迁移 / semver 0.1.1 / uv build / 镜像瘦身）
- [x] Day 6: Docker 化（分层缓存 + compose 单服务跑通）
- [ ] Day 7: CI/CD（GitHub Actions 自动测试）
- [ ] Week 1: Python 工程纪律补课（Day 7 收尾）
- [ ] Week 2: LLM 工程底座
- [ ] Week 3: Harness 雏形
- [ ] Day 30: 对外可见 demo + 简历锚点

## 如何联系

- GitHub Issues / Discussions 欢迎交流

## License

MIT
