from .utils import time, prints
from collections import namedtuple
from enum import Enum
from contextlib import redirect_stdout
import json


TestCaseResult = namedtuple('TestCaseResult', ['test_case', 'evaluation', 'error', 'output'])


class TestCase(object):
	def __init__(self, identifier, test_env, time_limit=None, **kwargs):
		self.identifier = identifier
		self.test_env = test_env
		self.time_limit = time_limit
		self.runs = kwargs.get('runs', 1)

	def run(self, agent_create_fn):
		error = None
		evaluation = None
		try:
			with time.time_limit(self.time_limit), redirect_stdout(None):
				agent = agent_create_fn(self.identifier)
				evaluation = self.test_env.run(agent, runs=self.runs)
		except Exception as e: # also catch TimeoutException
			error = e
			evaluation = self.test_env.terminated(e)
		finally:
			return TestCaseResult(test_case=self, evaluation=evaluation, error=error, output=None)


class TestSuite(object):
	def __init__(self, identifier, test_cases, point_fn=None, show_outputs=False):
		self.identifier = identifier
		self.test_cases = test_cases
		self.point_fn = point_fn
		self.show_outputs = show_outputs

	def run(self, agent_create_fn):
		results = []
		point = None
		for tc in self.test_cases:
			result = tc.run(agent_create_fn)
			results.append(result)
		if self.point_fn:
			point = self.point_fn(results)
		return TestSuiteResult(test_suite=self, results=results, point=point, show_outputs=self.show_outputs)


class TestSuiteResult(object):
	def __init__(self, test_suite, results, point, show_outputs=False):
		self.test_suite = test_suite
		self.results = results
		self.point = point
		self.show_outputs = show_outputs

	@property
	def data(self):
		test_cases = {}
		for res in self.results:
			test_cases[res.test_case.identifier] = res.evaluation.json
			if self.show_outputs:
				test_cases[res.test_case.identifier]['output'] = res.output
		data = {
			'identifier': self.test_suite.identifier,
			'test_cases': test_cases,
			'point': self.point
		}
		return data

	def to_json(self, path=None):
		if path is None:
			return json.dumps(self.data)
		with open(path, 'w') as f:
			json.dump(self.data, f)
