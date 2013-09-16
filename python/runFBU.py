import commands
import json
import os

from pymc import MCMC
from numpy import array,mean,std
import matplotlib.pyplot as plt
from pylab import savefig
from pymc.Matplot import plot

############################################
# MCMC configuration
############################################
#number of MCMC trials
nMCMC = 100000

#burn value -> MCMC will skip them
nBurn = 1000

#thin parameter, remove 
nThin = 10
############################################


############################################
# Things to be changed in the template file
############################################
#histReco
data        = '[11064.75,11804.203125,11780.1181640625,11135.34375]'

#A2neg
data        = '[14942.0869140625, 15100.28515625, 15082.591796875, 15215.556640625]'
#A2pos
#data        = '[14532.328125, 14994.6572265625, 15140.3916015625, 15421.4921875]'
#A4neg
#data        = '[15169.8466796875, 15141.4794921875, 15043.4560546875, 15230.2890625]'
#A4pos
#data        = '[14347.4580078125, 14923.845703125, 15162.189453125, 15632.060546875]'
#A6neg
#data        = '[15425.5068359375, 15158.4755859375, 14985.82421875, 15249.681640625]'
#A6pos
#data        = '[14162.388671875, 14833.6416015625, 15159.6982421875, 15870.1806640625]'

#Truth versus Reco Migration matrix from protos MC, 2011 7TeV charge asymmetry analysis (closure test)
migrations  = 'array([[0.063770,0.022177,0.011848,0.007905],[0.022544,0.051560,0.026740,0.011981],[0.011556,0.026787,0.051118,0.022614],[0.007696,0.011584,0.021881,0.062564]])'
truth_do    = '1000'
truth_up    = '1500'
############################################

def formatTemplate(infile, outfile, values={}) :
    f=open(outfile, 'w')
    f.write(open(infile).read()%values)
    f.flush()
    f.close()


def getBackground(jsonfname='', variation='Nominal') :
    """Read bkg from json file. Note that because we are using this to
    fill in a template, we are returning a string, and not the actual
    numerical values.
    """
    nameBkg1 = 'BG'
    valuesBkg1 = str(json.load(open(jsonfname))[nameBkg1][variation])
    return "{ 'background1' : %s }" % valuesBkg1

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option ("-i","--inputFile", help="input template file")
    parser.add_option ("-o","--outputFile", help="where the model is defined")
    parser.add_option ("-v","--verbose", help="Toggle verbose", action="store_true", default=False)
    (opts, args) = parser.parse_args()
    if not opts.inputFile : parser.error('Template not given')
    inputFile  = opts.inputFile
    outputFile = opts.outputFile if opts.outputFile else os.path.dirname(inputFile)+'/'+'mymodel.py'
    verbose    = opts.verbose

    if outputFile[0]=='/': outputFile = outputFile[1:]

    #prepare the model
    if os.path.exists(outputFile) :
        if verbose : print "removing existing ouput '%s'"%outputFile
        os.remove(outputFile)

    projectDir = os.path.dirname(os.path.abspath(__file__)).replace('/python','')
    values = {'data':data,
              'mmatrix':migrations,
              'lower':truth_do,
              'upper':truth_up,
              'bg':getBackground(jsonfname=projectDir+'/data/background.json')
              }

    formatTemplate(inputFile, outputFile, values)

    if verbose : print "importing model '%s'"%outputFile
    mytemplate = __import__(os.path.basename(outputFile).replace('.py',''))
    mcmc = MCMC(mytemplate)
    mcmc.sample(nMCMC,burn=nBurn,thin=nThin)

    plot(mcmc)
    mcmc.stats()
    unf_trace = mcmc.trace("truth")[:]
    print unf_trace
    #plt.hist(zip(*unf_trace)[0],bins=100,range=[100000,120000])
    plt.hist(zip(*unf_trace)[0],bins=100)
    print'\n'
    print mean(zip(*unf_trace)[0])
    print std(zip(*unf_trace)[0])
    savefig("outplot.eps")
