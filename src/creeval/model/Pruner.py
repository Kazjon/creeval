__author__ = 'kazjon'

class Pruner:
	creeval = None

	def __init__(self, creeval):
		self.creeval = creeval

	def run(self):
		pass

class NeverPruner(Pruner):

	def __init__(self, creeval):
		Pruner.__init__(self, creeval)
