# 贡献说明

欢迎修正失效链接、来源身份、日期规则和使用说明，也欢迎提交能复现的计划助手问题。

## 报告问题

请提供涉及的文件或来源 ID、实际行为、预期行为，以及支持判断的公开原文。计划助手问题请附 Python 版本、参数和错误信息。移除凭证、客户信息与私有笔记。

## 修改信源

`references/sources.json` 是唯一机器可读清单。新入口应有唯一 ID，并说明公开 URL、角色、专题用途、共同机构、评分依据和实际核验状态。预设、专题包及 `context_ids` 只能引用存在的 ID。质量分遵循[评分方法](references/source-review.md)；来源身份不能替代文章证据。

提交 PR 时说明解决的问题、原文依据和验证结果。流程或脚本修改应保持计划生成与联网研究的边界，不把网页结果当原生平台数据。

## 本地验证

在仓库根目录运行，无需安装依赖：

```powershell
python -B -X utf8 -m unittest discover -s tests -v
python -B -X utf8 scripts/plan_search.py --days 7 --entity 'Claude Code' --topic 'prompt injection'
```

文档修改检查相对链接、参数与中文标点。说明实际跑过的检查，不把离线测试写成联网覆盖验证。

本仓库采用 MIT 许可证；贡献内容须有相应使用权。第三方文章和论文仅链接，避免复制受版权保护的正文。
