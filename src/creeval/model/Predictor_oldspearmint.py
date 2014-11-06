__author__ = 'kazjon'

from sklearn.mixture import GMM
import subprocess, os.path, textwrap

class Predictor:
	exploreParameters = {}
	exploitParameters = {}
	scratchPath = None

	def __init__(self, exploreParams, scratchPath):
		self.exploreParameters = exploreParams
		self.scratchPath = scratchPath

	def train(self,artefacts):
		pass

	def predict(self,artefact):
		pass

	def evaluateUnexpectedness(self,artefact):
		pass

	def runSpearmint(self, filename):
		subprocess.check_call("spearmint",filename,".py --driver=local --method=GPEIOptChooser", shell=True)
		#read in the result file, return the best params

	# Tuples indicate min and max values for real-valued params, lists indicate possible values -- lists of strings for categorical, lists of ints for ordinal
	def genSpearmintTemplate(self,params, fname):
		with open(os.path.abspath(os.path.join(self.scratchPath,fname+'.pb')), "w") as f:
			lines = ["language: PYTHON", 'name: "'+fname+'"', ""]
			for k,v in params.iteritems():
				lines.append("variable {")
				lines.append(" name: \""+k+'"')
				if type(v) is list:
					if type(v[0]) is str:
						lines.append(" type: ENUM")
						lines.append(" size: 1")
						for option in v:
							lines.append(" options: \""+str(option)+"\"")
					elif type(v[0]) is int:
						lines.append(" type: INT")
						lines.append(" size: 1")
						lines.append(" min: "+str(v[0]))
						lines.append(" max: "+str(v[1]))
				elif type(v) is tuple:
					lines.append(" type: FLOAT")
					lines.append(" size: 1")
					lines.append(" min: "+str(v[0]))
					lines.append(" max: "+str(v[1]))
				lines.append("}")
				lines.append("")
			f.writelines(line + "\n" for line in lines)

	def genModelScript(self, dataPath, spearmintImports, spearmintRun, fname):
		with open(os.path.abspath(os.path.join(self.scratchPath,fname+".py")), "w") as f:
			f.write(spearmintImports+"import numpy as np\n\n")
			f.write(spearmintRun+"\n")
			f.write(textwrap.dedent("""\
				def main(job_id, params):
					asciiparams = dict()
					for k,v in params.iteritems():
						k_a = k
						v_a = v
						if type(k_a) is list:
							k_a = k_a[0]
						if type(v_a) is list:
							v_a = v_a[0]
						if type(k_a) is unicode:
							k_a = k_a.encode('ascii','ignore')
						if type(v_a) is unicode:
							v_a = v_a.encode('ascii','ignore')
						asciiparams[k_a] = v_a
					import pprint
					pprint.pprint(asciiparams)
					exploreParams = {0}
					return run(np.genfromtxt('{1}',delimiter=','), asciiparams, exploreParams)
			""".format(str(self.exploreParameters), dataPath)))

	def runSpearmint(self, name):
		subprocess.call("spearmint {0} --driver=local --method=GPEIOptChooser".format(os.path.abspath(os.path.join(self.scratchPath,name+".pb"))), shell=True)


class GMMPredictor(Predictor):
	exploreParameterSpace = {"n_components" : range(1, 10)}
	exploitParameterSpace = {"min_covar": (1e-6, 1e-1), "covariance_type": ["spherical", "tied", "diag", "full"]}
	spearmintImports =  """\
							from sklearn.mixture import GMM
						"""

	spearmintRun =  """\
						def run(data, exploitParams, exploreParams):
							gmm = GMM(exploreParams["n_components"],covariance_type = exploitParams["covariance_type"], min_covar=exploitParams["min_covar"])
							gmm.fit(data)
							return gmm.bic(data)
					"""

	def __init__(self, exploreParams, scratchPath):
		Predictor.__init__(self,exploreParams, scratchPath)


	def train(self,dataPath):
		name = self.__class__.__name__+str(id(self))
		self.genSpearmintTemplate(self.exploitParameterSpace, name)
		self.genModelScript(os.path.abspath(dataPath), textwrap.dedent(self.spearmintImports), textwrap.dedent(self.spearmintRun), name)
		self.runSpearmint(name)


	def predict(self,artefact):
		pass


	def evaluateUnexpectedness(self,artefact):
		return self.predict(artefact)
