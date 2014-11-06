__author__ = 'kazjon'

import pprint

class Interpreter:
	domain = None
	exploreParamSpace = {}
	exploitParamSpace = {}
	exploreParams = {}
	exploitParams = {}

	def __init__(self, domain, exploreParams = {}):
		self.domain = domain
		self.exploreParams = exploreParams

	def printStats(self):
		print "----",self.__class__.__name__,"----"
		print "ExploreParamSpace:"
		pprint.pprint(self.exploreParamSpace)
		print "ExploreParams:"
		pprint.pprint(self.exploreParams)
		print "ExploitParamSpace:"
		pprint.pprint(self.exploitParamSpace)
		print "ExploitParams:"
		pprint.pprint(self.exploitParams)

class LiteralInterpreter(Interpreter):

	def __init__(self,domain, exploreParams):
		Interpreter.__init__(self,domain)

	def interpret(self,data):
		return data