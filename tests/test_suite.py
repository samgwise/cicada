import inspect

class Test_Suite:
    """Setup the test, log the outputs, status, completion and all tests"""

    def __init__(self):
        self.test_suite = []

    def add_tests(self, new_tests):
        self.test_suite.append(new_tests)

    def run_tests(self):
        for test_object in self.test_suite:
            t = test_object
            attrs = (getattr(t, name) for name in dir(t))
            methods = filter(inspect.ismethod, attrs)
            for method in methods:
                try:
                    method()
                    print(f"Completed Test from: {type(test_object)}")
                except TypeError:
                    # Can't handle methods with required arguments.
                    pass
        print("Done")