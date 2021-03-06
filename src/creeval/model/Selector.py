__author__ = 'kazjon'

import pprint

class Selector:
	domain = None
	exploreParamSpace = {}
	exploitParamSpace = {}
	exploreParams = {}
	exploitParams = {}

	def __init__(self, domain, exploreParams = {}):
		self.domain = domain
		self.exploreParams = exploreParams

	def select(self):
		pass

	def printStats(self):
		print "----",self.__class__.__name__, "----"
		print "ExploreParamSpace:\n  ",
		pprint.pprint(self.exploreParamSpace)
		print "ExploreParams:\n  ",
		pprint.pprint(self.exploreParams)
		print "ExploitParamSpace:\n  ",
		pprint.pprint(self.exploitParamSpace)
		print "ExploitParams:\n  ",
		pprint.pprint(self.exploitParams)


class EverythingSelector(Selector):

	def __init__(self, domain, exploreParams = {}):
		Selector.__init__(self,domain, exploreParams)

	def select(self):
		return self.domain.artefacts