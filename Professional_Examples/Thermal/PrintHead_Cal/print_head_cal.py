#Russell Stanbery, Markforged

#perform load cell and temperature calibration on the print head
#input directory where telemetry data is stored, filename of which hotend, and test type to perform
#output calibration values to be entered into machine

import json
from os import name, path
import os
import numpy as np
import matplotlib.pyplot as plt
import argparse



coords = []

#----------FNCs
# convert telemetry data chunks to npy
def ctn(chunk_path, desired_axes=None):
    axes = json.load(open(path.join(chunk_path, "axes.json")))
    if desired_axes:  # filter out undesired axes
        axes = [axis for axis in axes if axis["name"] in desired_axes]
    assert len(axes) != 0, "chunk path and axis list results in no data"
    dtype = [(axis["name"], axis["numberType"].split("_")[0]) for axis in axes]
    print(dtype)
    arr = np.empty((axes[0]["numSamples"],), dtype)
    for name, field_type in dtype:  # load data from raw files
        arr[name] = np.fromfile(path.join(chunk_path, name + ".bin"), field_type)
    return arr

# load in file and return npy temperature data
def loadfileT(directory,file,side):
	return ctn(directory+'/'+str(file)+'/data/chunks/start/',desired_axes = [str(side)+'_nozzle_temp','aux_head_rtd_temp'])

#find value that occurs most (peak of the histogram)-------------
def most(data,key):
	histo = np.histogram(data[key],bins = 100)
	index = np.where(histo[0] == np.max(histo[0])) #where is the histogram peak
	val = np.round(histo[1][index]) #round to nearest integer
	return int(val)

#calculate offset and scale-------------------
#    for adc
def calc_forT(val1k, val25k):
	offset = int(np.round((40960 * val1k - 16384 * val25k) / 24576))
	scale = int(np.round(1610612736 / (val25k - val1k)))

	return offset, scale
#    for load cell
def calc_forload(val_nomass,val_mass):
	offset = val_nomass
	scale = int(np.round(123404288 / (val_mass - val_nomass)))

	return offset, scale

#get tel and translate into mfp-------------------
def trans(directory,filename):
	os.chdir('/media/markforged/302C-33AB/mfpTranslatorDist') ####EDIT this directory line
	os.system('translate.sh '+directory+'/'+filename+'.mfp')
	return

#make T table--------------------------------
def cal_helper(target0, actual0, target1, actual1):  # args in degrees C
    default_temps = 1.0828e5 - (1.3498e10 - 1.1082e8 * np.arange(65))**.5
    target_points = [default_temps[0], 25*32, target0*32, target1*32,
                     default_temps[-1]]
    actual_points = [default_temps[0], 25*32, actual0*32, actual1*32,
                     default_temps[-1] - target1*32 + actual1*32]
    table = np.interp(default_temps, target_points, actual_points)
    rounded = np.around(table, 0).astype('int')
    print(' '.join(map(str, rounded)))
    return


#Use mouse clicks to determine where T settles out------------
def onclick(event):
	global ix, iy
	ix, iy = event.xdata, event.ydata
	print ('x = %d, y = %d'%(ix, iy))
	global coords
	coords.append((ix, iy))

	if len(coords) == 4:
		fig.canvas.mpl_disconnect(cid)

	return coords


#-----------------load cell cal test, 30s mass plate only, 30s mass on
def LC(directory,file,side):
	axis = side+'_hotend_force_raw'
	trans(directory,file)
	data = ctn(directory+'/'+file+'/data/chunks/start/',desired_axes=axis)
	val_nomass = np.mean(data[axis][0:15000])
	val_mass = np.mean(data[axis][23500:])
	vals = calc_forload(val_nomass, val_mass)
	print('The offset and scale for {} hotend are: '.format(side)+str(vals))
	return

#----------------adc cal, 1k and 2.5k resistors
def T(directory):
	file1k = input('filename (no ext) of 1k ')
	file2_5k = input('filename (no ext) of 2.5k ')
	axes = ['left_nozzle_rtd_raw','right_nozzle_rtd_raw','fiber_nozzle_rtd_raw','aux_head_rtd_raw']
	Rs = ['1k','2_5k']
	trans(directory,file1k)
	trans(directory,file2_5k)

	data1k = ctn(directory+'/'+file1k+'/data/chunks/start/',desired_axes=axes)
	data2_5k = ctn(directory+'/'+file2_5k+'/data/chunks/start/',desired_axes=axes)
	
	data_dict = {}

	for R in Rs:
		for axis in axes:
			key = axis + '_' + R
			if R == '1k':
				data_dict[key] = most(data1k,axis)
			else:
				data_dict[key] = most(data2_5k,axis)

	offs = {}

	for axis in axes:
		key = axis.split('_')[0]
		val1k = data_dict[axis+'_1k']
		val25k = data_dict[axis + '_2_5k']
		offs[key] = calc_forT(val1k,val25k)
	print(offs)
	return

#------------------RTD cal, low and high T for one nozzle at a time
def RTD(directory,file,side):
	trans(directory,file)
	data = loadfileT(directory,file,side)
	
	
	fig = plt.figure()
	plt.plot(data[side+'_nozzle_temp']/32,color = 'green',label = side+' Nozzle Temp')
	plt.plot(data['aux_head_rtd_temp']/32,color = 'red',label = 'AUX')
	plt.ylabel('Temp [C]')
	plt.title(side+' Hotend Temp Cal')
	plt.legend()
	plt.show()

	print('Click the start and stop points where T has settled (4x points)')
	cid = fig.canvas.mpl_connect('button_press_event',onclick)
	input('enter')
	fig.canvas.mpl_disconnect(cid)
	print(coords)
	print('table for {} RTD cal: '.format(side))

	x_low_start =int(np.round(coords[0][0]))
	x_low_fin = int(np.round(coords[1][0]))

	x_high_start = int(np.round(coords[2][0]))
	x_high_fin = int(np.round(coords[3][0]))

			

	low_target = np.mean(data[side+'_nozzle_temp'][x_low_start:x_low_fin])/32
	low_actual = np.mean(data['aux_head_rtd_temp'][x_low_start:x_low_fin])/32
	high_target = np.mean(data[side+'_nozzle_temp'][x_high_start:x_high_fin])/32
	high_actual = np.mean(data['aux_head_rtd_temp'][x_high_start:x_high_fin])/32


	cal_helper(low_target,low_actual,high_target,high_actual)
	return

#------------------------------------------------

def main():

	plt.ion()
	parser = argparse.ArgumentParser()
	parser.add_argument('-d',help="directory where data files are",type = str)
	parser.add_argument('-t', help = 'test type', type = str)
	parser.add_argument('-s', help = 'side', type = str)
	parser.add_argument('-f', help = 'file name, no ext',type = str) 
	args = parser.parse_args()
	directory= args.d #all the way down to UNIT #
	testtype = args.t
	side = args.s
	file = args.f

	#main funcs to take in either a T test file
	if testtype == "LC":
		LC(directory,file,side)
	elif testtype == "T":
		T(directory)
	elif testtype == "RTD":
		RTD(directory,file,side)
	else:
		raise ValueError('{} Not a valid test type. Expecting: LC (load cell cal), T (1k and 2.5k resistor adc cal), or RTD (temp cal)'.format(testtype))


	return 

#----------------------------------------------
if __name__ == '__main__':
	main()

