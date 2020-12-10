import re

def calcform(form):
    print(form)
    if (len(form) == 0):
        return 0.0
    
    m = re.fullmatch('\d+\.?\d*|\.\d+', form)
    if (m != None):
        return float(form)
    
    m = re.search(r'\(.*\)', form)
    if (m != None):
        return calcform(form[:m.start()] + str(calcform(m.group()[1:-1])) + form[m.end():])
    
    m = re.search(r'\+', form)
    if (m != None):
        span = m.start()
        return calcform(form[:span]) + calcform(form[span+1:])
    
    m = re.search(r'\-', form)
    if (m != None):
        span = m.start()
        return calcform(form[:span]) - calcform(form[span+1:])
    
    m = re.search(r'\*', form)
    if (m != None):
        span = m.start()
        return calcform(form[:span]) * calcform(form[span+1:])
    
    m = re.search(r'\/', form)
    if (m != None):
        span = m.start()
        return calcform(form[:span]) / calcform(form[span+1:])
    
    m = re.search(r'\^', form)
    if (m != None):
        span = m.start()
        return calcform(form[:span]) ** calcform(form[span+1:])
    
    return None
        

def calc(formula):
    form = formula[1:].replace(' ', '')
    if (len(formula) <= 0):
        return 1, '不適切な数式です'

    m = re.findall(r'[^0-9\+\-\*\/\^\(\)]', form)
    if (len(m) > 0):
        return 0, m
    form_tree = calcform(form)
    return 1, form_tree