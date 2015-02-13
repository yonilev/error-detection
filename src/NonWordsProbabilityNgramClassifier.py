#encoding=cp1255

from NonWordsClassifier import NonWordsClassifier, getTaggedWords
from LanguageModel import NCharsModel
from math import log10,sqrt


#def findInd(self,val,ReversedSortedList):
#        ans = 0
#        for v in ReversedSortedList:
#            if v > val:
#                ans+=1
#            else:
#                return ans
#        return ans
    
def myLog(num):
        if num==0:
            return -10
        return log10(num)

class NonWordsLanguageModelClassifier(NonWordsClassifier):
    
    def _countProbs(self,prob,length,tuples):
        more=0
        less=0
        for p,l in tuples:
            if length==l:
                if p>=prob:
                    more+=1
                else:
                    less+=1
        return more,less

    def __init__(self,model,trainWords):
        # finds best threshold according to training
        corrects = [(model.getProb(w),len(w)) for w,_,t in trainWords if t=='T']
        errors = [(model.getProb(w),len(w)) for w,_,t in trainWords if t=='F']
        self._thresholds = {}
        maxValues={}
        for i in range(30):
            self._thresholds[i]=0
            maxValues[i]=(0,0)
        corrects.sort(reverse=True)
        errors.sort(reverse=True)
        for p,l in corrects+errors:
            errorsMore,errorsLess = self._countProbs(p,l,errors)
            correctsMore,correctsLess = self._countProbs(p,l,corrects)
            tp = errorsLess
            tn = correctsMore
            fp = correctsLess
            fn = errorsMore
            if tp+fp==0:
                precision=0
            else:
                precision = float(tp)/(tp+fp)
            if tp+fn==0:
                recall=0
            else:
                recall = float(tp)/(tp+fn)
            accuracy = float(tp+tn)/(tp+tn+fp+fn)
            if precision+recall==0:
                f_measure=0
            else:
                f_measure =(2*precision*recall)/(precision+recall)
            if maxValues[l][0] < f_measure or (maxValues[l][0]==f_measure and maxValues[l][1]<accuracy):
                maxValues[l] = (f_measure,accuracy)
                self._thresholds[l] = p
        
        self._model = model

    def classify(self,tagged_word):
        word,_ = tagged_word
        prob = self._model.getProb(word)
        if self._thresholds.has_key(len(word)):
            if prob>self._thresholds[len(word)]:
                return "T"
        return "F"
          

class NonWordsPeculiarityClassifier(NonWordsClassifier):
    def _peculiarity(self,w):
        w = 'B'+w+'E'
        sum = 0
        count = 0.0
        for i in range(len(w)-2):
            count+=1
            c=w[i:i+3]
            prevC = c[:-1]
            nextC = c[1:]
            fC = 0
            fPrevC = 0
            fNextC = 0
            if self._freq.has_key(c):
                fC = self._freq[c]
            if self._freq.has_key(prevC):
                fPrevC = self._freq[prevC]
            if self._freq.has_key(nextC):
                fNextC = self._freq[nextC]
            sum+=pow((0.5*myLog(fPrevC-1)+0.5*myLog(fNextC-1))-myLog(fC-1),2)
        return sqrt(sum/count)
         
    def _countProbs(self,pec,listOfPec):
        more=0
        less=0
        for p in listOfPec:
            if p>=pec:
                more+=1
            else:
                less+=1
        return more,less       
    
    
    def _readFreq(self):
        freq = {}
        file = open('../nonWords/NCharsTBAllWords.freq','r')
        lines = file.read().split('\n')
        for l in lines:
            c,f = l.split('\t')
            f = float(f)
            freq[c]=f
        return freq     
    
    def __init__(self,trainWords):
        # finds best threshold according to training
        self._freq = self._readFreq()
#        corrects = [self._peculiarity(w) for w,_,t in trainWords if t=='T']
#        errors = [self._peculiarity(w) for w,_,t in trainWords if t=='F']
        self._threshold = 0
#        maxF = 0
#        maxA = 0
#        for p in corrects+errors:
#            errorsMore,errorsLess = self._countProbs(p,errors)
#            correctsMore,correctsLess = self._countProbs(p,corrects)
#            tp = errorsMore
#            tn = correctsLess
#            fp = correctsMore
#            fn = errorsLess
#            if tp+fp==0:
#                precision=0
#            else:
#                precision = float(tp)/(tp+fp)
#            recall = float(tp)/(tp+fn)
#            accuracy = float(tp+tn)/(tp+tn+fp+fn)
#            if precision+recall==0:
#                f_measure=0
#            else:
#                f_measure =(2*precision*recall)/(precision+recall)
#            if maxF < f_measure or (maxF==f_measure and maxA<accuracy):
#                maxF = f_measure
#                maxA = accuracy
#                self._threshold = p

    def setThreshold(self,th):
        self._threshold = th
        
    def classify(self,tagged_word):
        word,_ = tagged_word
        pec = self._peculiarity(word)
        if pec>self._threshold:
            return "F"
        return "T"
        
        
class NonWordsErrorProbabilityClassifier(NonWordsClassifier): 
    # finds best threshold according to training
    def _calcErrorProbs(self,trainWords):
       
        countE = {}
        countV = {}
        probs = {}
        for w,_,t in trainWords:
            w = 'B'+w+'E'
            for i in range(len(w)-2):
                c=w[i:i+3]
                if t=='T':
                    countV[c]=countV.get(c,0)+1.0
                else:
                    if t=='F':
                        countE[c]=countE.get(c,0)+1.0
                    else:
                        print 'Error in train words'
        for c in countE.keys()+countV.keys():
            E = 0
            V = 0
            if countE.has_key(c):
                E = countE[c]
            if countV.has_key(c):
                V = countV[c]    
            probs[c]= E/(E+V)
        return probs 
        
            
    def __init__(self,trainWords):
        print 'training...'
        self._probs  = self._calcErrorProbs(trainWords)
        self._threshold = 0
        maxA = 0
        maxF = 0
        maxTH = 0
        for x in range(1001):
            th = x/1000.0
            self.setThreshold(th)
            p1,r1,f1,a1 = self.testClassifier(trainWords)
            if f1>maxF or (f1==maxF and a1>maxA):
                maxA = a1
                maxF = f1
                maxTH = th
        self.setThreshold(maxTH)
        print 'done training...'
    
        
    def setThreshold(self,th):
        self._threshold = th
        
    def classify(self,tagged_word):
        word,_ = tagged_word
        word = 'B'+word+'E'
        for i in range(len(word)-3):
            c1=word[i:i+3]
            c2=word[i+1:i+4]
            p1 = 1
            p2 = 1
            
            if self._probs.has_key(c1):
                p1 = self._probs[c1]
            if self._probs.has_key(c2):
                p2 = self._probs[c2]
                
            if p1>=self._threshold and p2>=self._threshold:
                return 'F'
        return 'T'  
    