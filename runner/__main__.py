'''
agent
	__init__.py
		def create_agent()
	...
test_suite
	__init__.py
		test_suite = TestSuite()
'''

import argparse

class TestSuiteNotFound(Exception): pass
class AgentNotFound(Exception): pass

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--output-path', default=None)
	args = parser.parse_args()

	try:
		from test_suite import test_suite
	except ModuleNotFoundError as e:
		raise TestSuiteNotFound(str(e))
	try:
		from agent import create_agent
	except ModuleNotFoundError as e:
		raise AgentNotFound(str(e))

	output = test_suite.run(create_agent)

	if args.output_path is not None:
		output.to_json(args.output_path)

	print(output.to_json())


if __name__ == "__main__":
    main()
