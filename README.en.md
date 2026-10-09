# AI Security Radar

[简体中文](README.md) · [Skill instructions](SKILL.md) · [MIT License](LICENSE)

An AI cybersecurity research skill for assistants with web search and page-reading tools. It follows primary evidence, checks attack prerequisites and remediation, and produces event briefs with enterprise implications and coverage gaps. The skill instructions and default reports are in Simplified Chinese.

## Scope

- Securing AI systems: prompt injection, agent permissions, MCP tool poisoning, RAG and memory poisoning, supply chains, credentials and sandboxes.
- AI-assisted attacks: phishing, social engineering, malware and automated intrusion, separating observed activity from speculation.
- AI for defense: vulnerability discovery, code review and SOC automation, including evaluation conditions and limitations.

The registry contains 97 source entries, three depth presets and eight topic packs. Source scores guide discovery; individual claims still require verification. Reposts of one report do not count as independent evidence.

## Requirements and installation

The host assistant supplies search and full-text reading. This repository does not include a web crawler, platform credentials or a scheduler. Python 3.10+ is optional for the offline planner; it uses only the standard library and requires no package installation.

Clone into a skill directory supported by your host. For a project using `.agents/skills/`, run from its root:

```powershell
git clone https://github.com/yang202009/ai-security-radar.git .agents/skills/ai-security-radar
```

Load `ai-security-radar` through your host, or ask your assistant to read `SKILL.md` and follow its workflow. Hosts supporting `$skill-name` can use:

```text
Use $ai-security-radar to review the past 30 days of AI cybersecurity events. Focus on agents, MCP and prompt injection. Check prerequisites and fixes, explain enterprise implications, and report actual coverage gaps.
```

Defaults: 30 calendar days including today, Asia/Shanghai timezone, balanced depth, usually 5–8 qualified events, delivery in chat. Specify a product, role, window or output purpose to change the scope. Reports are saved only on request; cloning does not start scheduled research.

## Offline planner

From this repository root:

```powershell
python -B -X utf8 scripts/plan_search.py --days 30 --depth balanced
python -B -X utf8 scripts/plan_search.py --days 7 --entity 'Claude Code' --topic 'prompt injection' --depth deep
python -B -X utf8 scripts/plan_search.py --days 30 --lane china
python -B -X utf8 scripts/plan_search.py --help
```

The planner emits JSON only: source queries, direction queries, public community queries and an initial coverage template. It performs no network requests or file writes. Search date operators are discovery hints, not publication-date verification. `--sources` takes precedence over `--lane` and depth presets. Aliases require identity checks; exclusions are review hints rather than automatic filters.

Topic packs: `secure-ai`, `ai-assisted-attack`, `ai-defense`, `china`, `frameworks`, `papers`, `industry`, `news`. Community modes: `auto`, `off`, `public`. Omitting `--as-of` uses the current UTC+08:00 date.

## Evidence and follow-ups

Reports provide conclusions, linked events, optional writing angles or customer questions, recommended reading, and coverage gaps. Claims are graded as strong, medium or pending verification. Research demonstrations, observed exploitation and proposed controls are kept distinct. Failed searches, zero results and unqueried sources are reported separately.

Follow-ups reuse prior evidence for rewrites, check targeted claims for current status, or compare newly disclosed events, substantive updates and corrections against a baseline. Private notes and customer materials stay out of remote queries.

Native community data can use a separately installed [last30days](https://github.com/mvanhorn/last30days-skill), following its current requirements. It is optional and not bundled. This planner's JSON is not the engine's `--plan` format. See [integration guidance](references/last30days-bridge.md).

## Development and license

```powershell
python -B -X utf8 -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for source corrections and contributions. Code, skill instructions and curated metadata use the [MIT License](LICENSE). Linked third-party content remains subject to its owners' rights. Research reuse and community integration methods were informed by last30days and adapted for cybersecurity evidence and Chinese reporting.
