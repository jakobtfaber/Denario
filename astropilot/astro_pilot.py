from .idea import develop_idea
from .method import design_method
from .experiment import run_experiment
from .paper import write_paper

class AstroPilot:
    def __init__(self, params={}):
        self.params = params

    def idea(self, **kwargs):
        return develop_idea(self.params, **kwargs)

    def method(self, **kwargs):
        return design_method(self.params, **kwargs)

    def experiment(self, **kwargs):
        return run_experiment(self.params, **kwargs)

    def paper(self):
        return write_paper(self.params)