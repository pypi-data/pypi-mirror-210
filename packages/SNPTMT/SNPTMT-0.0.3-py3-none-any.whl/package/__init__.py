import pandas as pd
import pymorphy2

import nltk
import ssl

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

import re

import spacy

from scipy.spatial.distance import cdist

import scipy.cluster.hierarchy as sch
from scipy.cluster.hierarchy import linkage, dendrogram

from scipy.spatial.distance import cdist, squareform

from scipy.cluster.hierarchy import fcluster

import math
import random