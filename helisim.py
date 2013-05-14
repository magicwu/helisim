#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, tempfile
from daetools.pyDAE import *
from time import localtime, strftime

# Standard variable types are defined in daeVariableTypes.py
from pyUnits import m, kg, s, K, Pa, mol, J, W

class modTutorial(daeModel):
    def __init__(self, Name, Parent = None, Description = ""):
        daeModel.__init__(self, Name, Parent, Description)

        self.DR = daeParameter("D_R", m, self, "Rotor diameter")
        self.Omega = daeParameter("&Omega;", rpm, self, "Rotor speed")

    def DeclareEquations(self):
        pass

class simTutorial(daeSimulation):
    def __init__(self):
        daeSimulation.__init__(self)
        self.m = modTutorial("helisim")
        self.m.Description = "This model simulates the dynamic behavior of a helicopter rotor."
        
    def SetUpParametersAndDomains(self):
        pass

    def SetUpVariables(self):
        pass

def export(simulation, objects_to_export):
    pydae_model = simulation.m.ExportObjects(objects_to_export, ePYDAE)
    cdae_model  = simulation.m.ExportObjects(objects_to_export, eCDAE)

    file_pydae = open(tempfile.gettempdir() + "/" + simulation.m.Name + "_export.py", "w")
    file_cdae  = open(tempfile.gettempdir() + "/" + simulation.m.Name + "_export.h",  "w")

    file_pydae.write(pydae_model)
    file_cdae.write(cdae_model)
    file_pydae.close()
    file_cdae.close()

# Use daeSimulator class
def guiRun(app):
    sim = simTutorial()
    sim.m.SetReportingOn(True)
    sim.ReportingInterval = 10
    sim.TimeHorizon       = 1000
    simulator  = daeSimulator(app, simulation=sim)
    simulator.exec_()

# Setup everything manually and run in a console
def consoleRun():
    # Create Log, Solver, DataReporter and Simulation object
    log          = daePythonStdOutLog()
    daesolver    = daeIDAS()
    datareporter = daeTCPIPDataReporter()
    simulation   = simTutorial()

    # Enable reporting of all variables
    simulation.m.SetReportingOn(True)

    # Set the time horizon and the reporting interval
    simulation.ReportingInterval = 10
    simulation.TimeHorizon = 1000

    #simulation.ReportingTimes = [10, 11, 124, 125, 356, 980, 1000]
    #print simulation.ReportingTimes
    
    # Connect data reporter
    simName = simulation.m.Name + strftime(" [%d.%m.%Y %H:%M:%S]", localtime())
    if(datareporter.Connect("", simName) == False):
        sys.exit()

    # Initialize the simulation
    simulation.Initialize(daesolver, datareporter, log)

    # Save the model report and the runtime model report
    simulation.m.SaveModelReport(simulation.m.Name + ".xml")
    simulation.m.SaveRuntimeModelReport(simulation.m.Name + "-rt.xml")

    # Models and ports now can be exported into some other modelling language
    # At the moment, models can be exported into pyDAE (python) and cDAE (c++)
    # but other languages will be supported in the future (such as OpenModelica, EMSO ...)
    # export() auxiliary function exports the model into pyDAE and cDAE and saves the
    # exported models into the temporary folder (/tmp or c:\temp)
    export(simulation, [simulation.m])
    
    # Solve at time=0 (initialization)
    simulation.SolveInitial()

    # Run
    simulation.Run()
    simulation.Finalize()

if __name__ == "__main__":
    if len(sys.argv) > 1 and (sys.argv[1] == 'console'):
        consoleRun()
    else:
        from PyQt4 import QtCore, QtGui
        app = QtGui.QApplication(sys.argv)
        guiRun(app)
