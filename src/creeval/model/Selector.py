__author__ = 'kazjon'


from creeval.src.creeval.Domain import Domain

class Selector:
	domain = None
	exploreParameterSpace = {}
	exploitParameterSpace = {}

	def __init__(self,domain, exploreParameterSpace):
		self.domain = domain
		self.exploreParameterSpace = exploreParameterSpace

	def select(self):
		pass

class EverythingSelector(Selector):

	def __init__(self, domain,exploreParameterSpace):
		Selector.__init__(self,domain,exploreParameterSpace)

	def select(self):
		return self.domain.artefacts