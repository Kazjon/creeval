__author__ = 'kazjon'

from sklearn.mixture import GMM
try: import simplejson as json
except ImportError: import json

from collections import OrderedDict

from spearmint.utils.database.mongodb import MongoDB
from spearmint.tasks.task_group	   import TaskGroup

from spearmint.resources.resource import parse_resources_from_config
from spearmint.resources.resource import print_resources_status

from spearmint.utils.parsing import parse_db_address

from spearmint import main

import os.path, textwrap, optparse, importlib, sys, os, time, csv, pprint

class Predictor:
	domain = None
	exploreParams = {}
	exploitParams = {}
	exploitParamSpace = {}
	exploreParamSpace = {}
	scratchPath = None
	spearmintRun = ""
	spearmintImports = ""

	def __init__(self, domain, exploreParams = {}, exploitParams = {}):
		self.domain = domain
		self.exploreParams = exploreParams
		self.exploitParams = exploitParams
		self.scratchPath = domain.scratchPath

	def train(self,artefacts):
		pass

	def predict(self,artefact):
		pass

	def evaluateUnexpectedness(self,artefact):
		pass

	# Tuples indicate min and max values for real-valued params, lists indicate possible values -- lists of strings for categorical, lists of ints for ordinal
	def genSpearmintTemplate(self,params, fname):
		data = {"language": "PYTHON", "main-file":fname+".py", "experiment-name": fname, "likelihood": "NOISELESS", "resources": {"my-machine": {"scheduler":"local","max-concurrent":4,"max-finished-jobs":100}}}
		paramdict = {}
		for k,v in params.iteritems():
			var = {}
			if type(v) is list:
				if type(v[0]) is str:
					var["type"] = "ENUM"
					var["size"] = 1
					var["options"] = v
				elif type(v[0]) is int:
					var["type"] = "INT"
					var["size"] = 1
					var["min"] = v[0]
					var["max"] = v[1]
			elif type(v) is tuple:
				var["type"] = "FLOAT"
				var["size"] = 1
				var["min"] = v[0]
				var["max"] = v[1]
			paramdict[k] = var
		data["variables"] = paramdict
		expdir = os.path.abspath(os.path.join(self.scratchPath,fname))+"/"
		with open(os.path.join(expdir,'config.json'), "w") as f:
			f.writelines(json.dumps(data, indent=4))

	def genModelScript(self, spearmintImports, spearmintRun, fname):
		experiment_dir = os.path.abspath(os.path.join(self.scratchPath,fname))
		with open(experiment_dir+"/"+fname+".py", "w") as f:
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
					data = np.genfromtxt('{1}',delimiter=',')
					return run(data, asciiparams, exploreParams)
			""".format(str(self.exploreParameters), experiment_dir+"/data.csv")))

	def runSpearmint(self, name):
		#subprocess.call("spearmint {0} --driver=local --method=GPEIOptChooser".format(os.path.abspath(os.path.join(self.scratchPath,name+".pb"))), shell=True)
		options, expt_dir = self.get_options([os.path.abspath(os.path.join(self.scratchPath,name))])
		#options, expt_dir = self.get_options(["/Applications/Spearmint/examples/noisy"])

		resources = main.parse_resources_from_config(options)

		# Load up the chooser.
		chooser_module = importlib.import_module('spearmint.choosers.' + options['chooser'])
		chooser = chooser_module.init(options)
		experiment_name = options.get("experiment-name", 'unnamed-experiment')

		# Connect to the database
		db_address = options['database']['address']
		sys.stderr.write('Using database at %s.\n' % db_address)
		db = MongoDB(database_address=db_address)

		while True:
			for resource_name, resource in resources.iteritems():
				jobs = main.load_jobs(db, experiment_name)
				# resource.printStatus(jobs)
				# If the resource is currently accepting more jobs
				# TODO: here cost will eventually also be considered: even if the
				#	   resource is not full, we might wait because of cost incurred
				# Note: I chose to fill up one resource and them move on to the next
				# You could also do it the other way, by changing "while" to "if" here

				while resource.acceptingJobs(jobs):
					# Load jobs from DB
					# (move out of one or both loops?) would need to pass into load_tasks
					jobs = main.load_jobs(db, experiment_name)

					# Remove any broken jobs from pending.
					main.remove_broken_jobs(db, jobs, experiment_name, resources)

					# Get a suggestion for the next job
					suggested_job = main.get_suggestion(chooser, resource.tasks, db, expt_dir, options, resource_name)

					# Submit the job to the appropriate resource
					process_id = resource.attemptDispatch(experiment_name, suggested_job, db_address, expt_dir)

					# Set the status of the job appropriately (successfully submitted or not)
					if process_id is None:
						suggested_job['status'] = 'broken'
						main.save_job(suggested_job, db, experiment_name)
					else:
						suggested_job['status'] = 'pending'
						suggested_job['proc_id'] = process_id
						main.save_job(suggested_job, db, experiment_name)

					jobs = main.load_jobs(db, experiment_name)

					# Print out the status of the resources
					# resource.printStatus(jobs)
					print_resources_status(resources.values(), jobs)

			# If no resources are accepting jobs, sleep
			# (they might be accepting if suggest takes a while and so some jobs already finished by the time this point is reached)
			if main.tired(db, experiment_name, resources):
				time.sleep(options.get('polling-time', 5))

	def get_options(self, override_args = None):
		parser = optparse.OptionParser(usage="usage: %prog [options] directory")

		parser.add_option("--config", dest="config_file",
						  help="Configuration file name.",
						  type="string", default="config.json")

		if override_args is not None:
			(commandline_kwargs, args) = parser.parse_args(override_args)
		else:
			(commandline_kwargs, args) = parser.parse_args()

		# Read in the config file
		expt_dir  = os.path.realpath(args[0])
		if not os.path.isdir(expt_dir):
			raise Exception("Cannot find directory %s" % expt_dir)
		expt_file = os.path.join(expt_dir, commandline_kwargs.config_file)

		try:
			with open(expt_file, 'r') as f:
				options = json.load(f, object_pairs_hook=OrderedDict)
		except:
			raise Exception("config.json did not load properly. Perhaps a spurious comma?")
		options["config"]  = commandline_kwargs.config_file


		# Set sensible defaults for options
		options['chooser']  = options.get('chooser', 'default_chooser')
		if 'tasks' not in options:
			options['tasks'] = {'main' : {'type' : 'OBJECTIVE', 'likelihood' : options.get('likelihood', 'GAUSSIAN')}}

		# Set DB address
		db_address = parse_db_address(options)
		if 'database' not in options:
			options['database'] = {'name': 'spearmint', 'address': db_address}
		else:
			options['database']['address'] = db_address

		if not os.path.exists(expt_dir):
			sys.stderr.write("Cannot find experiment directory '%s'. "
							 "Aborting.\n" % (expt_dir))
			sys.exit(-1)

		return options, expt_dir

	def train(self, data):
		name = self.__class__.__name__+str(id(self))
		expdir = os.path.abspath(os.path.join(self.scratchPath,name))+"/"
		if not os.path.exists(expdir):
			os.makedirs(expdir)
		self.writeData(data, expdir)
		self.genSpearmintTemplate(self.exploitParamSpace, name)
		self.genModelScript(textwrap.dedent(self.spearmintImports), textwrap.dedent(self.spearmintRun), name)
		self.runSpearmint(name)

	def writeData(self,data, name):
		with open(name+"/data.csv", "wb") as csvf:
			writer = csv.writer(csvf)
			writer.writerows(data)

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




class GMMPredictor(Predictor):
	exploreParamSpace = {"n_components" : range(1, 10)}
	exploitParamSpace = {"min_covar": (1e-8, 1e-2), "covariance_type": ["spherical", "tied", "diag", "full"]}
	spearmintImports =  """\
							from sklearn.mixture import GMM
						"""

	spearmintRun =  """\
						def run(data, exploitParams, exploreParams):
							gmm = GMM(exploreParams["n_components"],covariance_type = exploitParams["covariance_type"], min_covar=exploitParams["min_covar"])
							gmm.fit(data)
							return gmm.bic(data)
					"""

	def __init__(self, domain, exploreParams):
		Predictor.__init__(self, domain, exploreParams)


	def predict(self, artefact):
		pass


	def evaluateUnexpectedness(self, artefact):
		return self.predict(artefact)
