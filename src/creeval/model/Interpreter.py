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
		print "ExploreParamSpace:\n  ",
		pprint.pprint(self.exploreParamSpace)
		print "ExploreParams:\n  ",
		pprint.pprint(self.exploreParams)
		print "ExploitParamSpace:\n  ",
		pprint.pprint(self.exploitParamSpace)
		print "ExploitParams:\n  ",
		pprint.pprint(self.exploitParams)

	def interpret(self):
		return None

class LiteralInterpreter(Interpreter):

	def __init__(self,domain, exploreParams):
		Interpreter.__init__(self,domain)

	def interpret(self,data):
		return data