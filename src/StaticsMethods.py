import pickle

def serialize(object,picklePath):    
    file = open(picklePath, 'wb')
    print 'serializing...'
    pickle.dump(object,file)
    file.close()
    
def loadSerialize(picklePath):
    file = open(picklePath,'rb')
    ans = pickle.load(file)
    file.close()
    return ans

def taggedSentToOutputString(taggedSent,ind):
    s = ''
    i = -1
    for w,_ in taggedSent:
        i+=1
        if i==ind:
            s+='['+w+'] '
        else:
            s+=w+' '
    return s

NUM_OF_SENTS = 1433046
def sentToString(sent):
    s = ''
    for w in sent:
        s+=w+' '
    return s




    