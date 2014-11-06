__author__ = 'kazjon'

from Feature import *
from model.PerformanceSpace import PerformanceSpace

# feature type definitions
BINARY = CategoricalFeature
REAL = RealFeature
#BINARY_SEQUENCE = BinarySequenceFeature  ---- These aren't supported yet
#REAL_SEQUENCE = RealSequenceFeature


# Domains have a dict of name:type pairs to define their feature space.
class Domain:
	featureNames = {}
	features = {}
	artefacts = []
	pSpace = []
	performanceSpace = None

	def __init__(self, attributes):
		self.featureNames = attributes
		for name, ftype in enumerate(self.featureNames):
			if ftype == "real":
				self.features[name] = RealFeature() # In future we'll probably want to store more stuff in here...
			if ftype == "categorical":
				self.features[name] = CategoricalFeature() # In future we'll probably want to store/calculate more stuff in here...

	def addData(self, artefacts, evaluate=True):
		for artefact in artefacts:
			self.artefacts.append(artefact)
		if evaluate:
			pass # Do evaluaty things to our new artefacts!

	def initialise(self,artefacts):
		self.addData(artefacts, evaluate=False)
		self.pSpace = PerformanceSpace(self)
		return self.pSpace

	def evaluate(self, artefacts):
		results = []
		for artefact in artefacts:
			results.append(self.addArtefact(artefact))
