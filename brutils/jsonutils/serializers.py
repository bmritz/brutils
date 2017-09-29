""" JSON serializers for use with the python builtin json module
"""
import json
import numpy

from datetime import date, datetime

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)

class DateEncoder(json.JSONEncoder):
	def default(self, obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
    	return super(DateEncoder, self).default(obj)


