from src.config import args
from tests.trace_fixing_test import TestTraceFixing
from tests.prompt_change_test import TestPromptChange
from tests import test_utility

"""Single variation tests"""

# basic
test_utility.run_test(args, "basic")

# area_kill
args.area_kill = True
test_utility.run_test(args, "area_kill")

# respawn_traces
args.area_kill = False
args.respawn_traces = True
test_utility.run_test(args, "respawn_traces")

# lr_boost
args.respawn_traces = False
args.lr_boost = True
test_utility.run_test(args, "lr_boost")

# evo_search
args.lr_boost = False
args.evo_search = True
test_utility.run_test(args, "evo_search")

# Existing test refactor
test_suite = test_utility.Test_Suite()

test_trace_fixing = TestTraceFixing()
test_prompt_change = TestPromptChange()

test_suite.add_tests(test_trace_fixing)
test_suite.add_tests(test_prompt_change)

test_suite.run_tests()
