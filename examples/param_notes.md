# Day 8 推理参数实验笔记

> 实验工具：`examples/param_lab.py`
> 原始数据已跑好（2026-09-30 19:33，共 12 次请求 / 1123 tokens），对照文件：
>
> | 实验 | 结果文件 |
> |---|---|
> | 一 · temperature | `examples/param_results.md`（9 行） |
> | 二 · max_tokens 截断 | `examples/param_results_exp2.md` |
> | 三 · system prompt | `examples/param_results_exp3a.md`（诗人）/ `exp3b.md`（JSON 接口） |
>
> 这份笔记记录的是"我观察到了什么 → 我推断出什么规则"——**结论用自己的话写，禁止抄资料**。

---

## 实验一 · temperature

**运行命令**（数据已在 `param_results.md`，想重跑随时可跑）：

```bash
uv run --env-file .env python examples/param_lab.py --temps 0 0.7 1.5 --runs 3
```

**观察填空**（**逐字比对**同一温度的 3 行回复，不是扫一眼）：

1. temp=0.0 的 3 次输出：一致 / 不一致？
2. temp=0.7 与 1.5：不一致的字出现在句子的**哪个位置**——开头、中段，还是结尾？这个位置本身说明了什么？
3. 三种温度的**回复内容本身**差异在哪？0.0 和 0.7 讲的是同一件事吗？谁更具体？
4. token 数和耗时随温度有明显变化吗？还是说差异另有来源？
5. 我的推断：temperature 控制的到底是什么？（一句话，自己说）

## 实验二 · max_tokens 截断

**运行命令**：

```bash
uv run --env-file .env python examples/param_lab.py --prompt "详细解释什么是梯度下降" --max-tokens 20 --temps 0 --runs 1
```

**观察填空**：

1. 回复是被"完整讲完"还是"说一半就停"？最后两个字是什么？这句话算说完了吗？
2. 回复 total_tokens = 45。prompt 和 completion 各占多少？差值说明了什么？
3. 从而推断：max_tokens 限制的是**输入**还是**输出**？模型"想说完"的意愿和这个上限冲突时，谁赢？

## 实验三 · system prompt 的力量

**运行命令**（同一个问题，只换 system，跑两次对比）：

```bash
uv run --env-file .env python examples/param_lab.py \
  --system "你是一个爱用比喻的诗人" --temps 0 --runs 1 \
  --prompt "解释什么是缓存" --out examples/param_results_exp3a.md
uv run --env-file .env python examples/param_lab.py \
  --system "你是一个只输出 JSON 的接口，格式为 {\"answer\": string}" --temps 0 --runs 1 \
  --prompt "解释什么是缓存" --out examples/param_results_exp3b.md
```

**观察填空**：

1. 两次的回答风格/格式差异有多大？各用一句话描述两者的差别。
2. 第二次它真的遵守了 JSON 约定吗？**动手验证**：把 exp3b 的回复原文粘进下面代码跑一次——

```python
import json

raw = r"<把 exp3b 的回复原文粘到这里>"
print(json.loads(raw))
```

   报错了吗？报什么错？为什么这段文本不是合法 JSON？
3. 结合实验二一起想：如果这是 agent 的一次工具调用，模型返回了这种回复，你的代码会发生什么？
4. 我的推断：system prompt 在对话中的地位和 user 消息有何不同？

## 花费记录

| 实验 | 请求数 | tokens |
|---|---|---|
| 一 | 9 | 822 |
| 二 | 1 | 45 |
| 三 | 2 | 256 |
| **合计** | **12** | **1123** |

## 最重要的一行结论

> 用一句话写下今天最大的发现（写给三天后的自己看）：
