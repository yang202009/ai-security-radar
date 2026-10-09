# AI Security Radar｜AI 安全雷达

[English](README.en.md) · [使用流程](SKILL.md) · [信源清单](references/sources.json) · [MIT License](LICENSE)

为具备网页检索能力的 AI 助手提供一套 AI 网络安全研究流程：发现近期事件、追溯原文、核验攻击条件和修复状态，再给出企业影响、客户问答与候选选题。默认用简体中文交付。

适合安全研究者、企业安全团队、售前与方案人员，以及需要技术证据的内容作者。

## 研究范围

| 方向 | 重点 |
|---|---|
| 保护 AI 系统 | 提示注入、Agent 越权、MCP 工具投毒、RAG／记忆污染、供应链与凭证泄露 |
| 攻击者使用 AI | 钓鱼、社工、恶意代码、自动化入侵；区分观察、推测与确认事件 |
| AI 用于防御 | 漏洞发现、代码审计、SOC 与响应自动化；检查评测条件、效果和限制 |

泛产品发布、融资和缺乏安全证据的营销稿不占重点条目。

## 你会得到什么

- 有原文链接的事件简报：日期、影响条件、修复状态、证据等级。
- 对企业决策有用的待确认问题，以及有证据关联的写作切入点。
- 实际检索覆盖记录：未查、零匹配、部分返回和访问失败分别说明。
- 事件去重与增量跟进：新增、实质更新、更正和重复分开。

仓库包含 97 个信源入口、三档检索预设和八个专题包。来源质量分用于安排检索，单篇报道仍须重新核验；多个平台转述同一研究不算独立证据。

## 使用前提

**Skill 是供 AI 助手执行的研究说明。** 实际研究需要宿主提供网页搜索与正文读取工具；本仓库没有自带联网爬虫、平台账号、搜索 API 或定时服务。

Python 助手可选，使用 Python 3.10+ 和标准库，无需安装依赖。它只输出 JSON 检索计划，不联网、不确认事件，也不写入文件。本仓库本身不要求 API Key；宿主工具及可选社区引擎可能有自己的配置要求。

## 安装与开始

将仓库放入宿主支持的 Skill 目录。下面以项目级 `.agents/skills/` 为例；在目标项目根目录运行，目录已存在时先检查，避免重复安装：

```powershell
git clone https://github.com/yang202009/ai-security-radar.git .agents/skills/ai-security-radar
```

使用宿主的 Skill 加载方式调用 `ai-security-radar`。如果宿主支持 `$skill-name`，可以这样提问：

```text
用 $ai-security-radar 查最近 30 天 AI 安全事件，重点看 Agent、MCP 和提示注入，核对攻击条件与修复，给我企业影响和实际覆盖缺口。
```

也可以让助手读取本仓库 `SKILL.md` 并按其中的流程执行。仅克隆仓库不会启动研究或定时任务。

更多请求示例：

```text
做一份最近 7 天的 AI 安全周报，只保留有可读原始证据的事件。
深挖 Claude Code 的提示注入问题，区分研究演示和真实利用，核对当前修复状态。
把已有报告改成客户交流版，沿用原核验截止，不重新全量搜索。
与上次报告比较，只给新增、实质更新和更正，附变化证据。
```

## 默认值与定制

| 项目 | 默认值／选项 |
|---|---|
| 时间 | 最近 30 个自然日，含今天；Asia/Shanghai |
| 深度 | `balanced`；可选 `quick`、`deep` |
| 重点事件 | 通常 5—8 条；证据不足时少给 |
| 输出 | 聊天中交付；只有要求保存时才写报告 |
| 研究 | 原文优先，按需补公开社区线索 |

参数可用自然语言给出。过去 24 小时按滚动窗口核验；日报、周报和本周至今分别按其日历范围处理。说明你的角色、主题和用途即可调整排序；公开版不预设个人背景或客户环境。

## 离线检索计划

在本仓库根目录运行：

```powershell
python -B -X utf8 scripts/plan_search.py --days 30 --depth balanced
python -B -X utf8 scripts/plan_search.py --days 7 --entity 'Claude Code' --topic 'prompt injection' --depth deep
python -B -X utf8 scripts/plan_search.py --days 30 --lane china
python -B -X utf8 scripts/plan_search.py --days 7 --sources thn,embrace,gtig --community off
python -B -X utf8 scripts/plan_search.py --days 7 --as-of 2026-10-09
```

最后一条是固定历史窗口示例；省略 `--as-of` 时使用北京时间当天。计划包含 `queries`、`discovery_queries`、`community_queries` 和初始为 `not-run` 的 `coverage_template`。日期筛选仅帮助发现线索，不能证明正文发布日期。

专题包：`secure-ai`、`ai-assisted-attack`、`ai-defense`、`china`、`frameworks`、`papers`、`industry`、`news`。`--sources` 优先于专题包和深度预设。`--alias`、`--exclude` 可重复传入；别名和排除词仍需助手核对，不是自动身份确认或硬过滤。完整参数见：

```powershell
python -B -X utf8 scripts/plan_search.py --help
```

## 报告结构与证据标准

报告按需要提供结论、重点事件、候选选题／客户问答、优先深读和覆盖缺口。每条具体事实链接到支持它的原文，建议与事实分开。

| 等级 | 含义 |
|---|---|
| 强 | 原始报告有方法或复现条件，关键事实有公告、独立复现或可检查材料支持 |
| 中 | 原文可读，但缺独立核验，或官方观察缺少方法细节 |
| 待核 | 仅标题或转述、原文受限，或关键事实冲突 |

未说明真实利用时保留“研究演示”或“尚无公开利用证据”。没有合格事件时交付简短结论与覆盖缺口。

## 可选社区协作

用户明确要求原生社区数据时，可与单独安装的 [last30days](https://github.com/mvanhorn/last30days-skill) 协作，按其当前文档确认运行条件。该引擎不是必需依赖，也没有随本仓库分发。详见[协作说明](references/last30days-bridge.md)。本助手的 JSON 不能直接作为该引擎的 `--plan`。

## 目录

```text
SKILL.md                       研究入口与交付规则
agents/openai.yaml             宿主界面元数据
references/research-protocol.md 检索、日期与证据核验
references/sources.json         信源入口、评分、预设与专题包
references/source-review.md     信源评分方法与维护边界
references/followups.md         复用与增量研究
references/last30days-bridge.md  可选原生社区协作
scripts/plan_search.py          标准库离线计划助手
tests/test_plan_search.py       日期、选择、预算与参数检查
```

## 贡献与许可

欢迎通过 [Issues](https://github.com/yang202009/ai-security-radar/issues) 提交失效入口、日期错误、证据问题或使用反馈。信源贡献请附可核对的原文和用途；详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

```powershell
python -B -X utf8 -m unittest discover -s tests -v
```

代码、Skill 说明和本仓库整理的信源元数据采用 [MIT](LICENSE) 许可证。链接指向的第三方文章、论文和网站内容仍由各自权利人持有。本项目的研究复用与社区协作方法参考 last30days，并针对安全证据、企业影响和中文交付做了专门整理。
