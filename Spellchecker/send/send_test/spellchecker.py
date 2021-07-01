import sys
import pickle
from tqdm import tqdm
import numpy as np
import math
import re
from sklearn.preprocessing import StandardScaler as SS
from sklearn.linear_model import LogisticRegression as LogReg
from util import d

if __name__ == '__main__':
	end = 0
	for i, line in enumerate(sys.stdin):
		end = i
		print(line.strip())
		#print('<{}>'.format(line.strip()))
	
	a = d()
	print( '{}'.format(a), file=sys.stderr )
