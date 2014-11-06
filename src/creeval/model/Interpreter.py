__author__ = 'kazjon'



class Interpreter:
	domain = None
	exploreParameterSpace = {}
	exploitParameterSpace = {}

	def __init__(self, domain, exploreParameterSpace):
		self.domain = domain
		self.exploreParameterSpace = exploreParameterSpace

class LiteralInterpreter(Interpreter):

	def __init__(self,domain, exploreParameterSpace):
		Interpreter.__init__(self,domain, exploreParameterSpace)

	def interpret(self,data):
		return data