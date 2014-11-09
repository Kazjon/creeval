__author__ = 'kazjon'

import Domain, model.Pruner, model.Generator

# Workflow for using creeval:
#
# 1. Transform your data into a set of features, each of type BINARY, REAL, BINARY_SEQUENCE or REAL_SEQUENCE
# 2. Create a Domain, pass it a dict of featurename:type pairs.
# 3. Create a CreEval, pass it your Domain
# 4. Add your initial training data (and right now we only support initial data)
# 5.   -- A PerformanceSpace object is created automatically.
# 6.

# Domains have a dict of name:type pairs to define their feature space.
class CreEval:
	domain = None
	pSpace = None
	known_models = []
	active_models = []
	pruner = None
	generator = None
	dirpath = None

	def __init__(self, dirpath, domain, generator=None, pruner=None):
		self.domain = domain
		self.domain.scratchPath = dirpath
		self.dirpath = dirpath
		self.generator = generator
		if pruner is not None:
			self.pruner = pruner
		else:
			self.pruner = model.Pruner.NeverPruner(self)

	def addInitialData(self, data):
		self.pSpace = self.domain.initialise(data) #adds the data, then creates a pSpace

		#Main update function -- increments the evaluator by one step
	def update(self):
		if self.hasNewData():
			pass  # Currently not implemented
		else:
			#At the moment the system always adds a new model when this is called -- eventually we will want this to be a decision.
			self.generateAndTrainModel()
			#At the moment the pruner never deletes anything.
			self.pruner.run()

	def generateAndTrainModel(self):
		if self.generator is not None:
			model = self.generator.generate()
			self.known_models.append(model)
			self.active_models.append(model)
			model.train()
			return model
		return None

	def hasNewData(self):
		return False

if __name__ == "__main__":
	pass