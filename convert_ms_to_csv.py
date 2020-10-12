"""
convert_ms_to_csv.py

This script is intended to convert basic information from a ms file to a csv file.
u,v,w coordinates, visibility and weight for a single channel are converted to csv. 
"""

import numpy as np
import csv
import optparse

try:
    import casacore.tables as tb
except ImportError:
    print("Error: Casacore package is not found")
    print("Casacore and its python module is mandatory to run this script")
    exit()

def main(options):
    
    if options.inputms == '':
        print('Error: You must specify a path to the input MS file to be converted.')
        return
    else:
        msPath = options.inputms
    
    if options.outputcsv == '':
        csvPath = msPath+'.ms'
    else:
        csvPath= options.outputcsv
    
    print("Convert information from", msPath, "to", csvPath)
    t = tb.table(msPath, readonly=True, ack=False)
    
    tFreq = tb.table(t.getkeyword("SPECTRAL_WINDOW"), readonly=True, ack=False)
    refFreq = tFreq.getcol("REF_FREQUENCY", nrow=1)[0]
    print("Reference frequency = ", (refFreq/1e6), "MHz")
    
    nrow = t.nrows()
    print("There is ", nrow, "visibilities per channel")
    
    firstTime = t.getcell("TIME", 0)
    lastTime  = t.getcell("TIME", nrow-1)
    intTime = t.getcell("INTERVAL", 0)
    nTimeSlots = (lastTime - firstTime)/intTime
    
    timeslots = list()
    for i in range(3):
        timeslots.append(0)
    
    timeslots[2] = nTimeSlots
    
    tant = tb.table(t.getkeyword('ANTENNA'), readonly=True, ack=False)
    antList = tant.getcol('NAME')
    antToPlot = list(range(len(antList)))
    
    timeskip = 1
    
    tsel = t.query('TIME >= %f AND TIME <= %f AND ANTENNA1 IN %s AND ANTENNA2 IN %s' 
                   %(firstTime+timeslots[0]*intTime, 
                     firstTime+timeslots[2]*intTime,
                     str(antToPlot), str(antToPlot)), columns='ANTENNA1, ANTENNA2, UVW, DATA, WEIGHT')    
    
    u_vals = np.array([])
    v_vals = np.array([])
    w_vals = np.array([])
    visi_r = np.array([])
    visi_i = np.array([])
    weight = np.array([])
    
    for baseline in tsel.iter(["ANTENNA1", "ANTENNA2"]):
        ant1 = baseline.getcell("ANTENNA1", 0)
        ant2 = baseline.getcell("ANTENNA2", 0)
    
        uvw = baseline.getcol('UVW', rowincr=timeskip)
        visi = baseline.getcol('DATA')[:,0,0]
        u_vals = np.append(u_vals, uvw[:,0])
        v_vals = np.append(v_vals, uvw[:,1])
        w_vals = np.append(w_vals, uvw[:,2])    
        visi_r = np.append(visi_r, visi.real)
        visi_i = np.append(visi_i, visi.imag)
        weight = np.append(weight, baseline.getcol('WEIGHT')[:,0])
    
    with open(csvPath, 'w') as csvFile:
        writter = csv.writer(csvFile, delimiter=',')
        for i in range(len(weight)):
            writter.writerow([u_vals[i],v_vals[i],w_vals[i],visi_r[i],visi_i[i],weight[i]])
        
opt = optparse.OptionParser()
opt.add_option('-i', '--inputms', help='Path to the input MS file to convert', default='')
opt.add_option('-o', '--outputcsv', help='Path to the output CSV file', default='')

options, arguments = opt.parse_args()
        
main(options)