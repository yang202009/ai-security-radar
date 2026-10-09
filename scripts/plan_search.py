#!/usr/bin/env python3
"""Build an offline AI-security search plan; performs no network or file writes."""

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


DEFAULT_QUERY = '("AI security" OR "prompt injection" OR "agent security" OR "AI-assisted attack" OR "AI vulnerability discovery" OR "cyber evaluation")'
DIRECTIONS = {
    "secure-ai": {
        "terms": ["prompt injection", "MCP tool poisoning", "agent security", "memory poisoning"],
        "query": '("prompt injection" OR "agent security" OR "MCP tool poisoning" OR "memory poisoning")',
        "question": "Which AI systems have newly disclosed trust-boundary failures, under what permissions and configurations?",
    },
    "ai-assisted-attack": {
        "terms": ["adversarial misuse", "AI-assisted attack", "autonomous intrusion"],
        "query": '("adversarial misuse" OR "AI-assisted attack" OR "autonomous intrusion")',
        "question": "What observed attacks used AI, and which steps are directly supported by telemetry rather than attribution or speculation?",
    },
    "ai-defense": {
        "terms": ["AI vulnerability discovery", "agentic code review", "cyber evaluation"],
        "query": '("AI vulnerability discovery" OR "agentic code review" OR "cyber evaluation" OR "SOC automation")',
        "question": "What AI defense capabilities were tested, with what baseline, evaluation conditions and limits?",
    },
}
COMMUNITY_PLATFORMS = [
    ("github", "github.com", '(vulnerability OR "security advisory" OR "prompt injection")'),
    ("hackernews", "news.ycombinator.com", '(security OR vulnerability OR "prompt injection")'),
    ("reddit", "reddit.com", '(security OR vulnerability OR "prompt injection")'),
    ("x", "x.com", '(vulnerability OR "prompt injection" OR "agent security")'),
    ("youtube", "youtube.com", '(security OR vulnerability OR "prompt injection")'),
]


def clean_values(values, label):
    cleaned = []
    for value in values or []:
        value = value.strip()
        if not value:
            raise ValueError(label + " must not contain blank values")
        if value not in cleaned:
            cleaned.append(value)
    return cleaned


def quote_term(value):
    # Quotes here belong to a web-search expression, never a shell command.
    return '"' + value.replace('"', ' ').strip() + '"'


def build_plan(days, as_of, topic, depth, selected_ids=None, lane=None, *, entity=None, aliases=None, exclude=None, community="auto"):
    if not 1 <= days <= 3660:
        raise ValueError("days must be between 1 and 3660")
    if depth not in {"quick", "balanced", "deep"}:
        raise ValueError("unknown depth: " + depth)
    if community not in {"auto", "off", "public"}:
        raise ValueError("unknown community mode: " + community)
    if entity is not None:
        entity = entity.strip()
        if not entity:
            raise ValueError("entity must not be blank")
    aliases = clean_values(aliases, "aliases")
    exclude = clean_values(exclude, "exclude")
    if aliases and not entity:
        raise ValueError("aliases require an entity")
    entity_names = list(dict.fromkeys([entity] + aliases)) if entity else []
    entity_query = " OR ".join(quote_term(name) for name in entity_names)
    if len(entity_names) > 1:
        entity_query = "(" + entity_query + ")"
    registry_path = Path(__file__).resolve().parents[1] / "references" / "sources.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    by_id = {source["id"]: source for source in registry["sources"]}
    if lane is not None and lane not in registry.get("lanes", {}):
        raise ValueError("unknown lane: " + lane)
    ids = selected_ids if selected_ids is not None else (
        registry["lanes"][lane] if lane is not None else registry["presets"][depth]
    )
    if not ids:
        raise ValueError("sources must not be empty")
    unknown = sorted(set(ids) - set(by_id))
    if unknown:
        raise ValueError("unknown source IDs: " + ", ".join(unknown))
    ids = list(dict.fromkeys(ids))
    start = as_of - timedelta(days=days - 1)
    # Search operators are discovery hints. Page metadata still needs verification.
    discovery_dates = (
        f"after:{(start - timedelta(days=1)).isoformat()} "
        f"before:{(as_of + timedelta(days=1)).isoformat()}"
    )
    topic = topic.strip()
    if not topic:
        raise ValueError("topic must not be blank")
    queries = []
    for source_id in ids:
        source = by_id[source_id]
        scope = source.get("query_scope", "")
        query_topic = source.get("default_query", DEFAULT_QUERY) if topic == "AI security" else f"({topic})"
        if topic != "AI security" and source.get("language") == "zh":
            query_topic = f"({topic}) {source.get('default_query', '')}".strip()
        if entity_query:
            query_topic = f"{entity_query} {query_topic}"
        queries.append({
            "query_id": "source:" + source_id,
            "source_id": source_id,
            "source_name": source["name"],
            "role": source["role"],
            "entry_url": source["url"],
            "tier": source["tier"],
            "quality_score": source["rating"]["quality"],
            "radar_fit": source["rating"]["radar_fit"],
            "source_family": source["source_family"],
            "verification": source["verification"],
            "caveat": source["caveat"],
            "alternate_urls": source.get("alternate_urls", []),
            "query": " ".join(
                part for part in [f"site:{source['domain']}", scope, query_topic, discovery_dates] if part
            ),
        })
    directions = [lane] if lane in DIRECTIONS else list(DIRECTIONS)
    discovery_queries = []
    for direction in directions:
        angle = DIRECTIONS[direction]
        topic_query = "" if topic == "AI security" else f"({topic})"
        discovery_queries.append({
            "query_id": "direction:" + direction,
            "direction": direction,
            "purpose": "Discover primary reports beyond the selected source registry.",
            "query": " ".join(part for part in [entity_query, topic_query, angle["query"], discovery_dates] if part),
            "ranking_question": " ".join(part for part in [f"For {entity}." if entity else "", f"Regarding {topic}." if topic != "AI security" else "", angle["question"]] if part),
        })
    # Public web discovery does not imply platform login, native search, or health.
    community_count = 0 if community == "off" or (community == "auto" and depth == "quick") else (5 if depth == "deep" else 2)
    community_topic = ('("AI" OR "LLM" OR "MCP")' if not entity else "") if topic == "AI security" else f"({topic})"
    community_queries = [
        {
            "query_id": "community:" + platform,
            "platform": platform,
            "access_mode": "public-web-discovery",
            "purpose": "Find disclosures, fixes, reproducible observations or disputed claims; trace the original evidence.",
            "query": " ".join(part for part in [f"site:{domain}", entity_query, community_topic, DIRECTIONS[lane]["query"] if lane in DIRECTIONS else terms, discovery_dates] if part),
        }
        for platform, domain, terms in COMMUNITY_PLATFORMS[:community_count]
    ]
    all_queries = queries + discovery_queries + community_queries
    return {
        "schema_version": 2,
        "skill": "ai-security-radar",
        "plan_only": True,
        "topic": topic,
        "entity_resolution": {
            "canonical": entity,
            "aliases": aliases,
            "exclude": exclude,
            "status": "provided-unverified" if entity else "not-provided",
            "instruction": "Verify identity and aliases against official pages; anchor every relevant query. Exclusions are review hints, not established facts.",
        },
        "depth": depth,
        "lane": lane,
        "selection": "explicit-sources" if selected_ids is not None else ("lane" if lane else "preset"),
        "timezone": "Asia/Shanghai",
        "window": {"start": start.isoformat(), "end": as_of.isoformat(), "days": days, "inclusive": True},
        "registry_reviewed_at": registry["reviewed_at"],
        "freshness_warning": "Search date filters do not prove publication dates. Verify pages and exclude items after the actual research cutoff.",
        "queries": queries,
        "discovery_queries": discovery_queries,
        "community_mode": community,
        "community_queries": community_queries,
        "coverage_template": [
            {"query_id": query["query_id"], "search_status": "not-run", "read_status": "not-attempted", "returned_items": None, "verified_events": None}
            for query in all_queries
        ],
        "budget": {
            "source_queries": len(queries),
            "direction_queries": len(discovery_queries),
            "community_queries": len(community_queries),
            "gap_queries_reference_cap": {"quick": 4, "balanced": 8, "deep": 15}[depth],
            "instruction": "Do not run every optional query automatically. Follow the user scope and stop when material claims and coverage are sufficiently checked.",
        },
        "follow_up_lanes": [
            {"direction": direction, "terms": DIRECTIONS[direction]["terms"]}
            for direction in directions
        ],
        "source_warnings": [
            {"source_id": source_id, "tier": by_id[source_id]["tier"], "caveat": by_id[source_id]["caveat"]}
            for source_id in ids if by_id[source_id]["tier"] in {"hold", "background"}
        ],
        "context_sources": [by_id[source_id] for source_id in registry["context_ids"]],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=30, help="Calendar days including the end date (default: 30)")
    parser.add_argument("--as-of", type=date.fromisoformat, help="End date YYYY-MM-DD (default: current date in UTC+08:00)")
    parser.add_argument("--topic", default="AI security", help="Search terms; use English terms for overseas sources")
    parser.add_argument("--entity", help="Canonical product or organization name; identity still requires external verification")
    parser.add_argument("--alias", action="append", help="Repeatable entity alias; requires --entity and external verification")
    parser.add_argument("--exclude", action="append", help="Repeatable name-collision review hint; does not automatically alter queries")
    parser.add_argument("--community", choices=["auto", "off", "public"], default="auto", help="Public-web community query budget; does not access native platforms")
    parser.add_argument("--depth", choices=["quick", "balanced", "deep"], default="balanced")
    parser.add_argument("--sources", help="Comma-separated source IDs, overriding the depth preset")
    parser.add_argument("--lane", choices=["secure-ai", "ai-assisted-attack", "ai-defense", "china", "frameworks", "papers", "industry", "news"], help="Topic source pack, overriding the depth preset; --sources takes precedence")
    args = parser.parse_args()
    as_of = args.as_of or datetime.now(timezone(timedelta(hours=8))).date()
    ids = [item.strip() for item in args.sources.split(",") if item.strip()] if args.sources is not None else None
    try:
        plan = build_plan(args.days, as_of, args.topic, args.depth, ids, args.lane, entity=args.entity, aliases=args.alias, exclude=args.exclude, community=args.community)
    except (ValueError, OSError, KeyError) as exc:
        parser.error(str(exc))
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
