__author__ = 'kazjon'



class Model:
	s = None
	i = None
	p = None

	def __init__(self, s, i, p):
		self.s = s
		self.i = i
		self.p = p

	def printModel(self):
		self.s.printStats()
		self.i.printStats()
		self.p.printStats()

	def train(self):
		self.p.train(self.i.interpret(self.s.select()))