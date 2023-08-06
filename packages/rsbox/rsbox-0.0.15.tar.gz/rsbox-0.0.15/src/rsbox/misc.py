"""
File: misc.py 
-------------- 
Miscellaneous utils. 
""" 

import pickle
from datetime import datetime
from pytz import timezone
import requests
import cloudpickle as cp
from urllib.request import urlopen


def timestamp():
    """
    Simple function that retrieves the current date and time
    and returns a properly formatted string (i.e., a timestamp).  
    """
    now = datetime.now()
    date_time = now.strftime("%-I-%M-%p-%b-%d-%Y")
    return str(date_time)


def pickle(filepath, object_to_pickle):
	"""
	Pickles object_to_pickle saved at 
	filepath. filepath is a 'str' and
	should end in '.pkl'.  
	"""
	out_file = open(filepath, "wb")
	pickle.dump(object_to_pickle, out_file)
	out_file.close()


def unpickle(filepath):
	"""
	Takes in a path to a pickled 
	.pkl file (type: 'str') and
	returns the unpickled object. 
	"""
	in_file = open(filepath, 'rb')
	loaded_object = pickle.load(in_file) 
	return loaded_object


def load_dataset(urlpath=None):
	"""
	Given a url to a .pkl dataset file,
	loads and returns the dataset object. 
	"""
	if urlpath is None:
		urlpath = r"https://stanford.edu/~rsikand/assets/datasets/mini_cifar.pkl"
	
	dataset = cp.load(urlopen(urlpath)) 
	return dataset

