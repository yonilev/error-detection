#encoding=cp1255
'''
Created on 14/02/2011

@author: levyeh
'''
from BguCorpusReader import BguCorpusReader
from Lexicon import Lexicon
from nltk.probability import FreqDist
from DetectErrors import hasEngChars, hasExtraChar, hasDigit,ligitWord

def countNChars(words,N):
    if N<1:
        return None
    count = {}
    for w in words:
        for i in range(len(w)-N+1):
            c = ''
            for j in range(N):
                c+=w[i+j]
            count[c] = count.get(c,0) + 1
    return count

def probNChars(words,N):
    count = countNChars(words,N)
    prob = {}
    total = 0.0
    for t in count.values():
        total+=t
    for c in count.keys():
        prob[c] = count[c]/total
    return prob



def exportNCharsModel(words,N):
    file = open(str(N)+'CharsTBAllWords.model','w')    
    end = ''
    if N>1:
        end = 'E'
    begin = ''
    for _ in range(N-1):
        begin+='B'    
    wordsWithMarks =[begin+w+end for w in words]
    prob = probNChars(wordsWithMarks,N)
    for c in prob.keys():
        file.write(c+'\t'+str(prob[c])+'\n')
    if N>1:
        wordsWithMarks =[w[:-1] for w in wordsWithMarks]
        prob = probNChars(wordsWithMarks,N-1)
        for c in prob.keys():
            file.write(c+'\t'+str(prob[c])+'\n')
    
def exportFreq(words):
    N=3
    file = open('../nonWords/NCharsTBAllWords.freq','w')    
    end = 'E'
    begin = 'B'
    wordsWithMarks =[begin+w+end for w in words]
    count = countNChars(wordsWithMarks,N)
    for c in count.keys():
        file.write(c+'\t'+str(count[c])+'\n')
    count = countNChars(wordsWithMarks,N-1)
    for c in count.keys():
        file.write(c+'\t'+str(count[c])+'\n')        
    

class NCharsModel():
    def __init__(self,path,N,prior=0.1,smooth=None):
        file = open(path,'r')
        lines = file.read().split('\n')
        self.prob = {}
        m = 1
        for l in lines:
            c,p = l.split('\t')
            p = float(p)
            m = min(m,p)
            self.prob[c]=p         
        if smooth==None:
            self.smooth = m/2
        else:
            self.smooth = smooth
        self.N = N
        self.end = ''
        if self.N>1:
            self.end = 'E'
        self.begin = ''
        for _ in range(self.N-1):
            self.begin+='B'
        file.close()
       
    def getProb(self,w):
        p = 1
        w = self.begin+w+self.end
        for i in range(len(w)-self.N+1):
            c=w[i:i+self.N]
            prevC = c[:-1]
            if self.prob.has_key(c) and self.N>1:
                p = p * (self.prob[c]/self.prob[prevC])
            elif self.prob.has_key(c):
                p = p * (self.prob[c])
            else:
                p = p * self.smooth  
        return p
    
    def getMinNgramProb(self,w):
        w = self.begin+w+self.end
        minVal = 1
        for i in range(len(w)-self.N+1):
            c=w[i:i+self.N]
            if not self.prob.has_key(c):
                return 0
            minVal = min(minVal,self.prob[c])
        return minVal

           
#corpus = BguCorpusReader('c:/thesis/text/tb')
#words = [w for w in corpus.words() if len(w)>=2 and ligitWord(w)]
#exportFreq(words)



#fdWords = FreqDist(words)
#exportNCharsModel(fdWords.keys(),3)
#exportNCharsModel(fdWords.keys(),2)


#exportNCharsModel(fdWords.keys(),3)
#exportNCharsModel(fdWords.keys(),2)
#exportNCharsModel(fdWords.keys(),1)

#model1 = NCharsModel('NChars.model',1)
#model2 = NCharsModel('NChars.model',2)
#model3 = NCharsModel('NChars.model',3)
#print model3.getProb('a')

#
#
#print model1.getProb('ו')
#print model2.getProb('ו')
#print model3.getProb('ו')
#print
#print model1.getProb('ור')
#print model2.getProb('ור')
#print model3.getProb('ור')
#print
#print model1.getProb('ורד')
#print model2.getProb('ורד')
#print model3.getProb('ורד')