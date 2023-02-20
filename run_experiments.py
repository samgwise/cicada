from tests.test_suite import Test_Suite
from tests.trace_fixing_test import TestTraceFixing
from tests.prompt_change_test import TestPromptChange
from tests.evo_search_test import TestEvoSearch

test_suite = Test_Suite()

test_trace_fixing = TestTraceFixing()
test_prompt_change = TestPromptChange()
test_evo_search = TestEvoSearch()

test_suite.add_tests(test_evo_search)
# test_suite.add_tests(test_trace_fixing)
# test_suite.add_tests(test_prompt_change)

test_suite.run_tests()
