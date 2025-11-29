from django.test import TestCase
from .scoring import analyze_tasks, detect_cycles

class ScoringTests(TestCase):
    def test_basic_scoring(self):
        tasks = [
            {'title': 'A', 'due_date': '2025-12-01', 'estimated_hours': 2, 'importance': 8, 'dependencies': []},
            {'title': 'B', 'due_date': '2025-11-01', 'estimated_hours': 5, 'importance': 6, 'dependencies': ['A']},
        ]
        res = analyze_tasks(tasks)
        self.assertEqual(len(res), 2)
        self.assertTrue(res[0]['score'] >= res[1]['score'])

    def test_detect_cycle(self):
        tasks = [
            {'id':'1','title':'T1','dependencies':['2']},
            {'id':'2','title':'T2','dependencies':['1']},
        ]
        cycles = detect_cycles(tasks)
        self.assertTrue('1' in cycles and '2' in cycles)
