__author__ = 'kazjon'

from Domain import Domain
import model.Predictor, model.DescriptionSpace, model.Interpreter, model.Selector, model.Generator
from CreEval import CreEval
import csv, pprint, os.path, sys
import numpy as np

ignore = ["Protoss Probe", "Protoss Pylon", "Protoss Nexus"]

def readGame(f):
	print f
	with open(f, 'rU') as infile:
		reader = csv.reader(infile)
		row = reader.next()
		while not row[0].startswith("The following players are in this replay:"):
			row = reader.next()
		row = reader.next()
		players = {}
		while not row[0].startswith("Begin replay data:"):
			players[row[0]] = {"name": row[1].strip()}
			row = reader.next()
		if len(players) != 2:
			print "Too many players in",f
			return None
		for row in reader:
			if len(row) > 3 and row[2] == "Created":
				if row[1] in players:
					#print row
					if not row[4] in ignore:
						if row[4] in players[row[1]]:
							players[row[1]][row[4]] += 1
						else:
							players[row[1]][row[4]] = 1
		#pprint.pprint(players)
	return players

def replayReadTest():
	path = "/Users/kazjon/Dropbox/Documents/Research/UNCC/ComputationalCreativity/Datasets/BWReplays/TLGGICCUP_gosu_data/"
	strats = {}
	units = set([])
	d = os.path.join(path,"PvP")
	#for d in os.listdir(path):
	#	d = os.path.join(path,d)
	if os.path.isdir(d):
		for f in os.listdir(d):
			if f.endswith(".rgd"):
				game = readGame(os.path.join(d, f))
				if game is not None:
					for k,strat in game.iteritems():
						name = f+"_"+k+"_"+strat.pop("name")
						units.update(strat.keys())
						strats[name] = strat
	#units = zip(list(units),["real"] * len(units))
	pprint.pprint(strats)
	fields = list(units)
	fields.insert(0,"name")
	with open("model/test/strats.csv", "wb") as csvf:
		writer = csv.DictWriter(csvf,fieldnames=fields, restval=0)
		writer.writerow(dict(zip(fields,fields)))
		for k,v in strats.iteritems():
			v["name"] = k
			writer.writerow(v)
	return strats,fields, units

if __name__ == "__main__":
	strats, fields, units = replayReadTest()
	domain = Domain(units, "test/")
	domain.initialise(strats)
	s = [model.Selector.EverythingSelector]
	i = [model.Interpreter.LiteralInterpreter]
	p = [model.Predictor.GMMPredictor]
	dspace = model.DescriptionSpace.DescriptionSpace(s, i, p)
	g = model.Generator.RandomGenerator(dspace, domain)
	m = g.generate()
	m.printModel()
	m.p.train(np.genfromtxt("model/test/strats.csv", delimiter=',', skip_header=1)[:,1:])

