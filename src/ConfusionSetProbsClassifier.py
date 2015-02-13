#encoding=cp1255

'''
Created on Mar 21, 2011

@author: Yoni Lev
'''
from nltk import FreqDist
from itertools import izip
from BguCorpusReader import BguCorpusReader
from codecs import open
from ConfusionSetClassifier import ConfusionSetClassifier,importConfusionSets, getFeatures
from nltk.probability import ELEProbDist
from StaticsMethods import NUM_OF_SENTS






def calcConfWordsFreq(tagged_sents,allWords):
    count = []
    dic = {}
    for w in allWords:
        dic[w]=None
    c=0
    for s in tagged_sents:
        for w,_ in s:
            c+=1
            if dic.has_key(w):
                count.append(w)
    print 'total words : '+ str(c)
    fd = FreqDist(count)
    writeFdToFile(fd)
    
        
    
def calcCollocations(tagged_sents,confusionSets):
    featuresInd = 0
    PWNW = featuresInd
    featuresInd+=1
    PWNC = featuresInd
    featuresInd+=1
    PCNW = featuresInd
    featuresInd+=1
    PCNC = featuresInd
    featuresInd+=1
    PPWPW = featuresInd
    featuresInd+=1
    PPWPC = featuresInd
    featuresInd+=1
    PPCPW = featuresInd
    featuresInd+=1
    PPCPC = featuresInd
    featuresInd+=1
    NWNNW = featuresInd
    featuresInd+=1
    NWNNC = featuresInd
    featuresInd+=1
    NCNNW = featuresInd
    featuresInd+=1
    NCNNC = featuresInd
    featuresInd+=1
    PW = featuresInd
    featuresInd+=1
    NW = featuresInd
    featuresInd+=1
    PC = featuresInd
    featuresInd+=1
    NC = featuresInd
    featuresInd+=1
    
    confusionWords = allConfWords(confusionSets)
    lstConfusoinWords = list(confusionWords)
    for l in range(1):
        startIndex = l*(len(lstConfusoinWords)/1)
        endIndex = (l+1)*(len(lstConfusoinWords)/1)
        if l==19:
            endIndex = len(lstConfusoinWords)
        sentInd = 0
        confusionWords = lstConfusoinWords[startIndex:endIndex]
        c_word = {}
        for w in confusionWords:
            c_word[w] = []
            for i in range(featuresInd):
                c_word[w].append([])
                
        for s in tagged_sents:
            sentInd+=1
            ind=-1
            for confWord,_ in s:
                ind+=1
                if confWord not in confusionWords:
                    continue
                length = len(s)
                hasNext = False
                hasPrev = False
                hasNext2 = False
                hasPrev2 = False
                prevWord = '_'
                nextWord = '_'
                prevWord2 = '_'
                nextWord2 = '_'
                prevComplex = '_'
                nextComplex= '_'
                prevComplex2 = '_'
                nextComplex2 = '_'
                if ind+1<length:
                    hasNext=True
                    nextWord = s[ind+1][1].getLemma()
                    nextComplex = s[ind+1][1].getComplexPosTag()
                if ind-1>=0:
                    hasPrev = True
                    prevWord = s[ind-1][1].getLemma()
                    prevComplex = s[ind-1][1].getComplexPosTag()
                if ind+2<length:
                    hasNext2 = True
                    nextWord2 = s[ind+2][1].getLemma()
                    nextComplex2 = s[ind+2][1].getComplexPosTag()
                if ind-2>=0:
                    hasPrev2 = True
                    prevWord2 = s[ind-2][1].getLemma()
                    prevComplex2 = s[ind-2][1].getComplexPosTag()
                    
                c_word[confWord][PC].append(prevComplex)
                c_word[confWord][NC].append(nextComplex)
                c_word[confWord][PW].append(prevWord)
                c_word[confWord][PWNW].append(prevWord+'#'+nextWord)
                c_word[confWord][NW].append(nextWord)
                c_word[confWord][PCNW].append(prevComplex+'#'+nextWord)
                c_word[confWord][PWNC].append(prevWord+'#'+nextComplex)
                c_word[confWord][PCNC].append(prevComplex+'#'+nextComplex)
                c_word[confWord][PPWPW].append(prevWord2+'#'+prevWord)
                c_word[confWord][PPWPC].append(prevWord2+'#'+prevComplex)
                c_word[confWord][PPCPW].append(prevComplex2+'#'+prevWord)
                c_word[confWord][PPCPC].append(prevComplex2+'#'+prevComplex)
                c_word[confWord][NWNNW].append(nextWord+'#'+nextWord2)
                c_word[confWord][NWNNC].append(nextWord+'#'+nextComplex2)
                c_word[confWord][NCNNW].append(nextComplex+'#'+nextWord2)
                c_word[confWord][NCNNC].append(nextComplex+'#'+nextComplex2)
                    
           
        for w in c_word.keys():
            lst = []
            for j in range(featuresInd):
                lst.append(FreqDist(c_word[w][j]))
                c_word[w][j] = None          
            writeFdListToFile(lst,w)
            
                

def allConfWords(confusionSets):
    confWordsSet = set()
    for confusionSet in confusionSets:
        for w in confusionSet:
            confWordsSet.add(w)
    return confWordsSet
    
def calcData(proportion=1):
    corpus = BguCorpusReader('c:/thesis/text/walla/tagged')
    size = NUM_OF_SENTS/proportion
    tagged_sents = corpus.tagged_sents()[:size]
    confusionSets = importConfusionSets()
    allWords = allConfWords(confusionSets)
    calcConfWordsFreq(tagged_sents,allWords)
    calcCollocations(tagged_sents, confusionSets)

    
def writeFdToFile(fd):
    for k in fd.keys():
        file = open('../confusionSet/Probs/ProbsFiles/'+k.decode('cp1255')+'.probs','w')
        file.write(str(fd.freq(k))+'\n\n')
        file.close()
        

def writeFdListToFile(listOfFd,word):
    for fd in listOfFd:
        file = open('../confusionSet/Probs/ProbsFiles/'+word.decode('cp1255')+'.probs','a')
        ele = ELEProbDist(fd)
        file.write(str(ele.prob(None))+'\n')
        for k in fd.keys():
            if fd[k]>4:
                file.write(k+'\t'+str(ele.prob(k))+'\n')
        file.write('\n')
        file.close()
            
            
class ConfusionSetDefaultClassifier(ConfusionSetClassifier):
    def __init__(self,confusionSet):
        ConfusionSetClassifier.__init__(self,confusionSet)
        maxProb = 0
        self._tag = None
        for w in confusionSet:    
            file = open('../confusionSet/Probs/ProbsFiles/'+w.decode('cp1255')+'.probs','r')
            blocks = file.read()[:-2].split('\n\n')
            p = float(blocks[0])
            if p>maxProb:
                maxProb = p
                self._tag = w
    
    def classify(self,confSent):
        return self._tag,None
        
class ConfusionSetProbsClassifier(ConfusionSetClassifier):
    def __init__(self,confusionSet):
        ConfusionSetClassifier.__init__(self,confusionSet)
        self._probsDic = {}
        self._defaultProbsDic = {}
        for w in confusionSet:
            self._probsDic[w],self._defaultProbsDic[w] = self._readProb(w)
             
            
    def _readProb(self,name):
        file = open('../confusionSet/Probs/ProbsFiles/'+name.decode('cp1255')+'.probs','r')
        blocks = file.read()[:-2].split('\n\n')
        probLst = []
        defaultProbsLst = []
        if blocks[0]=='':
            probLst.append(0)
        else:
            probLst.append(float(blocks[0]))
        for block in blocks[1:]:
            prob = {}
            lines = block.split('\n')
            defaultProbsLst.append(float(lines[0]))
            for l in lines[1:]:
                spl = l.split('\t')
                if len(spl)==2:
                    k,f = spl
                else:
                    f=0
                    k='None'
                prob[k]=float(f)
            probLst.append(prob)
        return probLst,defaultProbsLst
    

class ConfusionSetBayesProbsClassifier(ConfusionSetProbsClassifier):
    def __init__(self,confusionSet):
        ConfusionSetProbsClassifier.__init__(self,confusionSet)
         

    
    def _calcMinProb(self,fdLst):
        ans = []
        for fd in fdLst:
            tmp = 0
            if len(fd.keys())!=0:
                tmp = fd[fd.keys()[-1]]
            if tmp==0:
                tmp = pow(10,-8)
            else:
                tmp = tmp/10
            ans.append(tmp)
        return ans 
        
    def _calcMinProbs(self,probsDic):
        probs = {}
        for c in probsDic.keys():
            probs[c] = self._calcMinProb(probsDic[c][1:])
        return probs
    
    
    
    def classify(self,confSent):
        pwnw,pcnw,pwnc,pcnc,ppwpw,ppwpc,ppcpw,ppcpc,nwnnw,nwnnc,ncnnw,ncnnc,pw,nw,pc,nc = getFeatures(confSent)
        confWordsProb = {}
        for c in self._confusionSet:
            confWordsProb[c] = 1
        featuresLst = [pwnw,pcnw,pwnc,pcnc,ppwpw,ppwpc,ppcpw,ppcpc,nwnnw,nwnnc,ncnnw,ncnnc,pw,nw,pc,nc]
        self._updateProb(featuresLst,self._probsDic,confWordsProb,self._defaultProbsDic)
        max = 0
        second=0
        guessedWord = None
        for k in confWordsProb.keys():
            if confWordsProb[k]>max:
                max = confWordsProb[k]
                guessedWord = k
        for k in confWordsProb.keys():
                if k==guessedWord:
                    continue
                if confWordsProb[k]>second:
                    second = confWordsProb[k] 
        confidence = max/second
        return guessedWord,confidence
    
    def _updateProb(self,featuresLst,probsDic,confWordsProb,minProbs):
        for k in confWordsProb.keys():
            probsLst = probsDic[k]
            confWordsProb[k] = confWordsProb[k]*(pow(probsLst[0],16))
            for feature,probs,minProb in izip(featuresLst,probsLst[1:],minProbs[k]):
                confWordsProb[k] = confWordsProb[k]*probs.get(feature,minProb)
                

class ConfusionSetMemoryProbsClassifier(ConfusionSetProbsClassifier):
    def __init__(self,confusionSet):
        ConfusionSetProbsClassifier.__init__(self,confusionSet)        
    
    def classify(self,confSent):
        pwnw,pcnw,pwnc,pcnc,ppwpw,ppwpc,ppcpw,ppcpc,nwnnw,nwnnc,ncnnw,ncnnc,pw,nw,pc,nc = getFeatures(confSent)
        contextLst = [pwnw,pcnw,pwnc,pcnc,ppwpw,ppwpc,ppcpw,ppcpc,nwnnw,nwnnc,ncnnw,ncnnc,pw,nw,pc,nc]
        ind=0
        max = 0
        count = 0
        guessedWord = None
        for context in contextLst:
            count+=1
            ind+=1
            for w in self._confusionSet:
                p = self._probsDic[w][ind].get(context,0)
                if p>max:
                    max = p
                    guessedWord = w
            if guessedWord!=None:
                break
        # no counts were found -> select most frequent word
        if guessedWord==None:
            count+=1
            for w in self._confusionSet:
                p = self._probsDic[w][0]
                if p>max:
                    second = max
                    max = p
                    guessedWord = w      
        confidence = max/pow(5,count)
        return guessedWord,confidence
              

#corpus = BguCorpusReader('c:/thesis/text/walla/tagged') 
#calcData(corpus.tagged_sents())

#confusionSets = importConfusionSets()
#corpus = BguCorpusReader('c:/thesis/text/walla/test_tagged') 
#for confusionSet in confusionSets:  
#    cls = ConfusionSetBayesProbsClassifier(confusionSet)
#    cls.testClassifier(corpus.tagged_sents())
       