# import torch
# from torch import nn

import re
import os
import cv2
import json
import copy
import shutil
import pickle
import random
import imutils
import operator
import numpy as np
import pandas as pd
from tqdm import tqdm
from wasabi import msg
from pathlib import Path
from pprint import pprint
from matplotlib import colors
from yaml import load, Loader
import matplotlib.pyplot as plt
from collections import OrderedDict
from itertools import chain, groupby
from functools import reduce, partial
from configparser import ConfigParser
from imutils import resize as resize_img
from PIL import Image, ImageDraw, ImageFont
from tqdm.notebook import tqdm as tqdm_notebook
from typing import Iterable, Generator, Sequence, Iterator, List, Set, Dict, Union, Optional, Tuple

from fastcore.foundation import is_bool
from fastcore.basics import merge as merge_dicts
from fastcore.basics import chunked, store_attr, camel2snake, snake2camel, flatten