# minimal test for the Image class.
# works so far, using python 3.4.2 on FreeBSD
import os
import sys
sys.path.insert(0, os.path.normpath('../plastex'))
from plasTeX.Imagers import Image
from plasTeX.Config import config
import pickle

image = Image(config=config, filename='image')


pickle.dump(image, open('/tmp/dump', 'wb'))
img = pickle.load(open('/tmp/dump', 'rb'))
print(img.__dict__)
