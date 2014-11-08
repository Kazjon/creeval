__author__ = 'kazjon'

import random
import model.Model

class Generator:
	dspace = None
	domain = None

	def __init__(self, dspace, domain):
		self.dspace = dspace
		self.domain = domain

	def generate(self):
		return None

class RandomGenerator(Generator):

	def __init__(self, dspace, domain):
		Generator.__init__(self, dspace, domain)

	def generate(self):
		s = random.choice(self.dspace.selectors)
		i = random.choice(self.dspace.interpreters)
		p = random.choice(self.dspace.predictors)
		comps = []
		for compclass in [s,i,p]:
			compParams = {}
			for pk,pv in compclass.exploreParamSpace.iteritems():
				if type(pv) is list:
						compParams[pk] = random.choice(pv)
				elif type(pv) is tuple:
						compParams[pk] = random.uniform(pv[0],pv[1])
			comps.append(compclass(self.domain, compParams))
		return model.Model.Model(*comps)