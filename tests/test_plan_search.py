import importlib.util
import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('plan_search', ROOT / 'scripts/plan_search.py')
PLANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLANNER)


class PlanTests(unittest.TestCase):
    def plan(self, days=30, depth='balanced', **kwargs):
        return PLANNER.build_plan(days, date(2026, 10, 9), 'AI security', depth, **kwargs)

    def test_inclusive_calendar_windows(self):
        self.assertEqual(self.plan()['window']['start'], '2026-09-10')
        self.assertEqual(self.plan(1)['window']['start'], '2026-10-09')
        self.assertEqual(self.plan()['timezone'], 'Asia/Shanghai')

    def test_leap_day(self):
        plan = PLANNER.build_plan(2, date(2024, 3, 1), 'AI security', 'quick')
        self.assertEqual(plan['window']['start'], '2024-02-29')

    def test_presets_and_community_budget(self):
        for depth, sources, communities in [('quick', 5, 0), ('balanced', 8, 2), ('deep', 12, 5)]:
            with self.subTest(depth=depth):
                plan = self.plan(depth=depth)
                self.assertEqual(len(plan['queries']), sources)
                self.assertEqual(len(plan['community_queries']), communities)
                self.assertEqual(len(plan['discovery_queries']), 3)

    def test_all_topic_packs_resolve(self):
        for lane in ['secure-ai', 'ai-assisted-attack', 'ai-defense', 'china', 'frameworks', 'papers', 'industry', 'news']:
            with self.subTest(lane=lane):
                plan = self.plan(lane=lane)
                self.assertGreater(len(plan['queries']), 0)
                self.assertEqual(plan['selection'], 'lane')
                self.assertEqual(len(plan['discovery_queries']), 1 if lane in PLANNER.DIRECTIONS else 3)

    def test_explicit_sources_override_and_deduplicate(self):
        plan = self.plan(lane='china', selected_ids=['thn', 'embrace', 'thn'])
        self.assertEqual([q['source_id'] for q in plan['queries']], ['thn', 'embrace'])
        self.assertEqual(plan['selection'], 'explicit-sources')

    def test_entity_anchor_reaches_each_query(self):
        plan = self.plan(entity='Claude Code', aliases=['Claude Code', 'Claude CLI'], exclude=['unrelated'])
        for query in plan['queries'] + plan['discovery_queries'] + plan['community_queries']:
            self.assertIn('"Claude Code"', query['query'])
            self.assertIn('"Claude CLI"', query['query'])
        self.assertEqual(plan['entity_resolution']['status'], 'provided-unverified')
        self.assertEqual(plan['entity_resolution']['exclude'], ['unrelated'])

    def test_chinese_topic_retains_entity_and_topic(self):
        plan = PLANNER.build_plan(7, date(2026, 10, 9), '提示注入', 'balanced', lane='china', entity='MCP')
        for query in plan['queries']:
            self.assertIn('提示注入', query['query'])
            self.assertIn('"MCP"', query['query'])

    def test_community_modes(self):
        self.assertEqual(len(self.plan(depth='deep', community='off')['community_queries']), 0)
        self.assertEqual(len(self.plan(depth='quick', community='public')['community_queries']), 2)

    def test_initial_coverage_does_not_claim_execution(self):
        plan = self.plan()
        self.assertTrue(plan['plan_only'])
        self.assertEqual(len(plan['coverage_template']), sum(len(plan[k]) for k in ['queries', 'discovery_queries', 'community_queries']))
        for row in plan['coverage_template']:
            self.assertEqual(row['search_status'], 'not-run')
            self.assertEqual(row['read_status'], 'not-attempted')
            self.assertIsNone(row['returned_items'])
            self.assertIsNone(row['verified_events'])

    def test_invalid_arguments_are_rejected(self):
        for options in [dict(days=0), dict(days=3661), dict(depth='bad'), dict(lane='bad'), dict(selected_ids=[]), dict(selected_ids=['missing']), dict(entity=' '), dict(aliases=['alias']), dict(community='bad')]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.plan(**options)
        with self.assertRaises(ValueError):
            PLANNER.build_plan(7, date(2026, 10, 9), ' ', 'balanced')

    def test_registry_references_and_scores(self):
        registry = json.loads((ROOT / 'references/sources.json').read_text(encoding='utf-8'))
        identifiers = {s['id'] for s in registry['sources']}
        self.assertEqual(len(identifiers), len(registry['sources']))
        for group in list(registry['presets'].values()) + list(registry['lanes'].values()) + [registry['context_ids']]:
            self.assertTrue(set(group).issubset(identifiers))
        for source in registry['sources']:
            rating = source['rating']
            self.assertEqual(rating['quality'], 5 * rating['authority'] + 6 * rating['originality'] + 6 * rating['transparency'] + 3 * rating['access'])

    def test_cli_produces_json_without_file_writes(self):
        before = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(ROOT / 'scripts/plan_search.py'), '--days', '7', '--as-of', '2026-10-09', '--sources', 'thn,embrace', '--community', 'off'], capture_output=True, text=True, encoding='utf-8', check=True)
        plan = json.loads(result.stdout)
        self.assertEqual(plan['window']['start'], '2026-10-03')
        self.assertEqual(len(plan['queries']), 2)
        self.assertEqual(before, {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()})

    def test_cli_invalid_input_returns_argument_error(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/plan_search.py'), '--sources', 'missing'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 2)
        self.assertIn('unknown source IDs', result.stderr)


if __name__ == '__main__':
    unittest.main()
