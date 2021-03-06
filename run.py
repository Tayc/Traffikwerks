#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------
# Editted for Traffikwerks by Tom Carswell and Shawn Lauzon on May 30th 
# for the NuMenta hackathon in NYC
# 
# note: still trying to impliment the hack, added a function that will translate
# the data files we've accrude, but it still needs to be tested. the parameter file
# have also been tweeked; may need finetuning. need to test everything basically
# 
"""
Groups together code used for creating a NuPIC model and dealing with IO.
(This is a component of the One Hot Gym Anomaly Tutorial.)
"""
import importlib
import sys
import csv
import datetime
import os

from nupic.data.inference_shifter import InferenceShifter
from nupic.frameworks.opf.modelfactory import ModelFactory

import nupic_anomaly_output

DESCRIPTION = (
  "Starts a NuPIC model from the model params returned by the swarm\n"
  "and pushes each line of input from the gym into the model. Results\n"
  "are written to an output file (default) or plotted dynamically if\n"
  "the --plot option is specified.\n"
)
GYM_NAME = "Traffikwerks"
DATA_DIR = "/home/god/Desktop/Data"
MODEL_PARAMS_DIR = "./model_params"
# '7/2/10 0:00'
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"


def translate(fileLocation):
	pass


def createModel(modelParams):
  """
  Given a model params dictionary, create a CLA Model. Automatically enables
  inference for kw_energy_consumption.
  :param modelParams: Model params dict
  :return: OPF Model object
  """
  model = ModelFactory.create(modelParams)
  model.enableInference({"predictedField": "travelTime"})
  return model



def getModelParamsFromName(gymName):
  """
  Given a gym name, assumes a matching model params python module exists within
  the model_params directory and attempts to import it.
  :param gymName: Gym name, used to guess the model params module name.
  :return: OPF Model params dictionary
  """
  importName = "model_params.%s_model_params" % (
    gymName.replace(" ", "_").replace("-", "_")
  )
  print "Importing model params from %s" % importName
  try:
    importedModelParams = importlib.import_module(importName).MODEL_PARAMS
  except ImportError:
    raise Exception("No model params exist for '%s'. Run swarm first!"
                    % gymName)
  return importedModelParams



def runIoThroughNupic(inputDir, model, gymName, plot):
  """
  Handles looping over the input data and passing each row into the given model
  object, as well as extracting the result object and passing it into an output
  handler.
  :param inputData: file path to input data CSV
  :param model: OPF Model object
  :param gymName: Gym name, used for output handler naming
  :param plot: Whether to use matplotlib or not. If false, uses file output.
  """
  #inputFile = open(inputData, "r")
  #csvReader = csv.reader(inputFile)
  shifter = InferenceShifter()
  if plot:
    output = nupic_anomaly_output.NuPICPlotOutput(gymName)
  else:
    output = nupic_anomaly_output.NuPICFileOutput(gymName)
  
  old_line = []
  is_first_line = False
  for txt_file in sorted(os.listdir(inputDir)):
	with open(inputDir + txt_file, 'rb') as in_file:
		#print in_file
	   	reader = csv.reader(in_file, delimiter = '\t')
		is_first_line = True
		reader.next() # skip the header row
		for line in reader:
		    linkId = str(line[5])
		    if linkId != '4616352':
			continue
		    travelTime = int(line[2])
		    timestamp = datetime.datetime.strptime(line[4], DATE_FORMAT)
		    result = model.run({
		    "timestamp": timestamp,
		    "travelTime": travelTime
		    })
	  	    prediction = result.inferences["multiStepBestPredictions"][1]
	  	    anomalyScore = result.inferences["anomalyScore"]
		    output.write(timestamp, travelTime, prediction, anomalyScore)
		    result = shifter.shift(result)
			    
  	if plot:
	    result = shifter.shift(result)
  output.close()

"""
  counter = 0
  for row in csvReader:
    counter += 1
    if (counter % 100 == 0):
      print "Read %i lines..." % counter
    timestamp = datetime.datetime.strptime(row[0], DATE_FORMAT)
    consumption = float(line[2])
"""
  





def runModel(gymName, plot=False):
  """
  Assumes the gynName corresponds to both a like-named model_params file in the
  model_params directory, and that the data exists in a like-named CSV file in
  the current directory.
  :param gymName: Important for finding model params and input CSV file
  :param plot: Plot in matplotlib? Don't use this unless matplotlib is
  installed.
  """
  print "Creating model from %s..." % gymName
  model = createModel(getModelParamsFromName(gymName))
  inputDir = "%s/" % DATA_DIR
  runIoThroughNupic(inputDir, model, gymName, plot)



if __name__ == "__main__":
  print DESCRIPTION
  plot = False
  args = sys.argv[1:]
  if "--plot" in args:
    plot = True
  runModel(GYM_NAME, plot=plot)
