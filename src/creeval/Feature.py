__author__ = 'kazjon'

class Feature:

	def __init__(self):
		pass


class CategoricalFeature(Feature):

	def __init__(self):
		Feature.__init__(self)


class RealFeature(Feature):

	def __init__(self):
		Feature.__init__(self)


#These aren't supported yet.
#class BinarySequenceFeature(Feature):
#
#	def __init__(self):
#		Feature.__init__(self)
#
#class RealSequenceFeature(Feature):
#
#	def __init__(self):
#		Feature.__init__(self)
