"""Deterministic agent adapters; no LLM provider or external account is configured."""
import json
from .client import AnalyzerClient

class RecordsAgent:
    def __init__(self, client): self.client = client
    def run(self): return self.client.get('/api/students/', page_size=100)

class SummaryAgent:
    def run(self, records):
        averages = [s['average'] for s in records['results'] if s['average'] is not None]
        return {'total_visible_records': records['count'], 'sample_size': len(records['results']),
                'sample_average': round(sum(averages) / len(averages), 2) if averages else None,
                'scope': 'First page only; not a full-dataset statistic.'}

def run_pipeline():
    return SummaryAgent().run(RecordsAgent(AnalyzerClient()).run())

if __name__ == '__main__': print(json.dumps(run_pipeline(), indent=2))
