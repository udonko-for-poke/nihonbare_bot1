import math
def get_B(HP, GET):
    return math.floor(((HP * 3 - 2) * GET)/(HP*3))
    
def get_G(B):
    return math.floor(65535/ ((255/B)**0.1875))