__author__ = 'kazjon'


class DescriptionSpace:
	predictors = []
	interpreters = []
	selectors = []

	def __init__(self, selectors, interpreters, predictors):
		self.selectors = list(selectors)
		self.interpreters = list(interpreters)
		self.predictors = list(predictors)
