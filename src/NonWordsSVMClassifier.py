#encoding=cp1255

from svmutil import *
from NonWordsProbabilityNgramClassifier import NonWordsErrorProbabilityClassifier
from NonWordsClassifier import NonWordsClassifier, getTaggedWords
from translitsIdentifier import transClassifier


wordPunc = """".'"""
alphabet = "פםןוטארקשדגכעיחלךףץתצמנהבסז"
puncAndAlph = wordPunc+alphabet
cls = {'F':1,'T':-1}
clsToWords = {1:'F',-1:'T'}
rafiClassifier = transClassifier(prior_prob_of_heb = 0.1)
pos = open('../linguistic/pos.txt','r').read().split('\n')






class NonWordsSVMClassifier(NonWordsClassifier):   
    def _countChar(self,w):
        cnt = {}
        for c in w:
            cnt[c] = cnt.get(c,0) + 1
        return cnt


    def _createFeatures(self):
        i=0
        features ={}
        
        features['length']=i
        i+=1
        
        for c in puncAndAlph:
            features['count_'+c]=i
            i+=1
        
        
        for c in puncAndAlph:
            features['startsWith_'+c]=i
            i+=1
        
        for c in puncAndAlph:
            features['middleChar_'+c]=i
            i+=1
       
                
        for c1 in puncAndAlph:
            for c2 in puncAndAlph:
                features['startsWith_'+c1+c2]=i
                i+=1
      
        for c in puncAndAlph:
            features['endsWith_'+c]=i
            i+=1
       
                
        for c1 in puncAndAlph:
            for c2 in puncAndAlph:
                features['endsWith_'+c1+c2]=i
                i+=1
        
        for c1 in puncAndAlph:
            for c2 in puncAndAlph:
                features['contains_'+c1+c2]=i
                i+=1
           
                
        for c1 in puncAndAlph:
            for c2 in puncAndAlph:
                for c3 in puncAndAlph:
                    features['contains_'+c1+c2+c3]=i
                    i+=1
        
       
        features['FOR']=i
        i+=1
           
        for p in pos:
            features['pos_'+p]=i
            i+=1
        
       
    
        return features

    
        

    def _createVector(self,tagged_word,features):
        vector = {}
        w= tagged_word[0]
        pos= tagged_word[1]
        #1
        vector[features['length']]=len(w)/20.0
        
        #2
        cnt = self._countChar(w)
        for c in cnt.keys():
            vector[features['count_'+c]]=cnt[c]/7.0
       
        
        for i in range(len(w)-2):
            #3
            key = 'middleChar_'+w[i+1]
            if features.has_key(key):
                vector[features[key]]=1
            
        if len(w)>=1:
            #4
            key = 'startsWith_'+w[0]
            if features.has_key(key):
                vector[features[key]]=1
    
    
            #6
            key = 'endsWith_'+w[-1]
            if features.has_key(key):
                vector[features[key]]=1
    
        if len(w)>=2:
            #7
            key = 'startsWith_'+w[:2]
            if features.has_key(key):
                vector[features[key]]=1
            #8
            key = 'endsWith_'+w[-2:]
            if features.has_key(key):
                vector[features[key]]=1
            for i in range(len(w)-1):
                c1=w[i]
                c2=w[i+1]
                if features.has_key('contains_'+c1+c2):   
                    #9             
                    vector[features['contains_'+c1+c2]]=1
        
        if len(w)>=3:
            for i in range(len(w)-2):
                c1=w[i]
                c2=w[i+1]
                c3=w[i+2]
                if features.has_key('contains_'+c1+c2+c3):    
                    #10            
                    vector[features['contains_'+c1+c2+c3]]=1
                        
    
        rafiCls = rafiClassifier.classify(w,":PROPERNAME:")
        if rafiCls=="FOR":
            #14
            vector[features["FOR"]]=1
        
        key = 'pos_'+pos
        if features.has_key(key):
                vector[features[key]]=1
        
          
        return vector
             
    def __init__(self,tagged_words):
        param = '-t 0 -c 0.1'
        self._features = self._createFeatures()
        trainX = []
        trainY = []
        for tagged_word in tagged_words:
            x = self._createVector(tagged_word,self._features)
            y = cls[tagged_word[2]]
            trainX.append(x)
            trainY.append(y)
        prob  = svm_problem(trainY, trainX)
        self._m = svm_train(prob, param) 
        self._threshold = 0
        

    def classify(self,tagged_word):
        x = self._createVector(tagged_word,self._features)
        p_labels, _, p_vals = svm_predict([-1],[x],self._m)
#        label = p_labels[0]
#        guess = clsToWords[label]
        pred = self._m.get_labels()[0]*p_vals[0][0]
        if pred>=self._threshold:
            return 'F'
        else:
            return 'T'
        return guess
        
    def setThreshold(self,th):
        self._threshold = th
    
