from BguCorpusReader import BguCorpusReader
from StaticsMethods import taggedSentToOutputString

def importConfusionSets():
    lst = []
    file = open('../confusionSet/confusionSets.txt','r')
    sets = file.read()[:-2].split('\n\n')
    for set in sets:
        words = set.split('\n')
        lst.append(words)
    file.close()
    return lst

      

def checkConfSent(confSent,confusionSet):
    s,ind = confSent
    if s[ind][0] not in confusionSet:
        raise Exception('wrong classifier')

def getFeatures(confSent):
    s,ind = confSent
    nextComplex = '_'
    nextWord = '_'
    prevComplex = '_'
    prevWord = '_'
    nextComplex2 = '_'
    nextWord2 = '_'
    prevComplex2 = '_'
    prevWord2 = '_'
    if ind+1<len(s):
        nextWord = s[ind+1][1].getLemma()
        nextComplex = s[ind+1][1].getComplexPosTag()
    if ind-1>=0:
        prevWord = s[ind-1][1].getLemma()
        prevComplex = s[ind-1][1].getComplexPosTag()
    if ind+2<len(s):
        nextWord2 = s[ind+2][1].getLemma()
        nextComplex2 = s[ind+2][1].getComplexPosTag()
    if ind-2>=0:
        prevWord2 = s[ind-2][1].getLemma()
        prevComplex2 = s[ind-2][1].getComplexPosTag()
    
    pwnw = prevWord+'#'+nextWord
    pcnw = prevComplex+'#'+nextWord
    pwnc = prevWord+'#'+nextComplex
    pcnc = prevComplex+'#'+nextComplex
    ppwpw = prevWord2+'#'+prevWord
    ppwpc = prevWord2+'#'+prevComplex
    ppcpw = prevComplex2+'#'+prevWord
    ppcpc = prevComplex2+'#'+prevComplex
    nwnnw = nextWord+'#'+nextWord2
    nwnnc = nextWord+'#'+nextComplex2
    ncnnw = nextComplex+'#'+nextWord2
    ncnnc = nextComplex+'#'+nextComplex2
    pc = prevComplex 
    nc = nextComplex
    pw = prevWord
    nw = nextWord
   
    return pwnw,pcnw,pwnc,pcnc,ppwpw,ppwpc,ppcpw,ppcpc,nwnnw,nwnnc,ncnnw,ncnnc,pw,nw,pc,nc
   
def getLemma(taggedWord):
    tmp = taggedWord[1].getLemma()
    if tmp=='':
        tmp = taggedWord[0]
    return tmp

def createCls(confusionSet):
    wordsToCls = {}
    clsToWords = {}
    j=0
    for x in confusionSet:
        wordsToCls[x]=j
        clsToWords[j]=x
        j+=1
    return wordsToCls,clsToWords
    




def createFeatures(tagged_sents,confusionSet):
    i=0
    features={}
    cls = {}
    occur = 0
    for s in tagged_sents:
        ind=-1
        for confWord,_ in s:
            ind+=1
            if confWord not in confusionSet:
                continue
            pwnw,pcnw,pwnc,pcnc,ppwpw,ppwpc,ppcpw,ppcpc,nwnnw,nwnnc,ncnnw,ncnnc,pw,nw,pc,nc = getFeatures((s,ind))
            occur+=1
            key = 'pwnw:'+pwnw
            cls[key]=cls.get(key,0)+1
            key = 'pcnw:'+pcnw
            cls[key]=cls.get(key,0)+1
            key = 'pwnc:'+pwnc
            cls[key]=cls.get(key,0)+1
            key = 'pcnc:'+pcnc
            cls[key]=cls.get(key,0)+1
            
            key = 'ppwpw:'+ppwpw
            cls[key]=cls.get(key,0)+1
            key = 'ppcpw:'+ppcpw
            cls[key]=cls.get(key,0)+1
            key = 'ppwpc:'+ppwpc
            cls[key]=cls.get(key,0)+1
            key = 'ppcpc:'+ppcpc
            cls[key]=cls.get(key,0)+1
            
            key = 'nwnnw:'+nwnnw
            cls[key]=cls.get(key,0)+1
            key = 'ncnnw:'+ncnnw
            cls[key]=cls.get(key,0)+1
            key = 'nwnnc:'+nwnnc
            cls[key]=cls.get(key,0)+1
            key = 'ncnnc:'+ncnnc
            cls[key]=cls.get(key,0)+1
            
            
            
            cls[key]=cls.get(key,0)+1
            key = 'pw:'+pw
            cls[key]=cls.get(key,0)+1
            key = 'nw:'+nw
            cls[key]=cls.get(key,0)+1
            key = 'nc:'+nc
            cls[key]=cls.get(key,0)+1
            key = 'pc:'+pc
            cls[key]=cls.get(key,0)+1
    
    i = 0
    total = 0
    for key in cls.keys():
        total+=1
        if cls[key]>4:
            features[key]=i
            i+=1
    
    print total
    print len(features.keys())
    return features



def createVector(confSent,features):
    vector={}
    pwnw,pcnw,pwnc,pcnc,ppwpw,ppwpc,ppcpw,ppcpc,nwnnw,nwnnc,ncnnw,ncnnc,pw,nw,pc,nc = getFeatures(confSent)
    key = 'pwnw:'+pwnw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'pcnw:'+pcnw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'pwnc:'+pwnc
    if features.has_key(key):
        vector[features[key]]=1  
    key = 'pcnc:'+pcnc
    if features.has_key(key):
        vector[features[key]]=1
    
    key = 'ppwpw:'+ppwpw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'ppcpw:'+ppcpw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'ppwpc:'+ppwpc
    if features.has_key(key):
        vector[features[key]]=1  
    key = 'ppcpc:'+ppcpc
    if features.has_key(key):
        vector[features[key]]=1  
        
    key = 'nwnnw:'+nwnnw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'ncnnw:'+ncnnw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'nwnnc:'+nwnnc
    if features.has_key(key):
        vector[features[key]]=1  
    key = 'ncnnc:'+ncnnc
    if features.has_key(key):
        vector[features[key]]=1   
    
    
    key = 'pw:'+pw
    if features.has_key(key):
        vector[features[key]]=1 
    key = 'nw:'+nw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'nc:'+nc
    if features.has_key(key):
        vector[features[key]]=1
    key = 'pc:'+pc
    if features.has_key(key):
        vector[features[key]]=1 
    return vector
  
def getFeaturesWordPos(confSent):
    s,ind = confSent
    nextComplex = '_'
    nextWord = '_'
    prevComplex = '_'
    prevWord = '_'
    nextComplex2 = '_'
    nextWord2 = '_'
    prevComplex2 = '_'
    prevWord2 = '_'
    if ind+1<len(s):
        nextWord = s[ind+1][0]
        nextComplex = s[ind+1][1].getPosTag()
    if ind-1>=0:
        prevWord = s[ind-1][0]
        prevComplex = s[ind-1][1].getPosTag()
    if ind+2<len(s):
        nextWord2 = s[ind+2][0]
        nextComplex2 = s[ind+2][1].getPosTag()
    if ind-2>=0:
        prevWord2 = s[ind-2][0]
        prevComplex2 = s[ind-2][1].getPosTag()
    
    pwnw = prevWord+'#'+nextWord
    pcnw = prevComplex+'#'+nextWord
    pwnc = prevWord+'#'+nextComplex
    pcnc = prevComplex+'#'+nextComplex
    ppwpw = prevWord2+'#'+prevWord
    ppwpc = prevWord2+'#'+prevComplex
    ppcpw = prevComplex2+'#'+prevWord
    ppcpc = prevComplex2+'#'+prevComplex
    nwnnw = nextWord+'#'+nextWord2
    nwnnc = nextWord+'#'+nextComplex2
    ncnnw = nextComplex+'#'+nextWord2
    ncnnc = nextComplex+'#'+nextComplex2
    pc = prevComplex 
    nc = nextComplex
    pw = prevWord
    nw = nextWord  
    return pwnw,pcnw,pwnc,pcnc,ppwpw,ppwpc,ppcpw,ppcpc,nwnnw,nwnnc,ncnnw,ncnnc,pw,nw,pc,nc

        
def createVectorWordPos(confSent,features):
    vector={}
    pwnw,pcnw,pwnc,pcnc,ppwpw,ppwpc,ppcpw,ppcpc,nwnnw,nwnnc,ncnnw,ncnnc,pw,nw,pc,nc = getFeaturesWordPos(confSent)
    key = 'pwnw:'+pwnw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'pcnw:'+pcnw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'pwnc:'+pwnc
    if features.has_key(key):
        vector[features[key]]=1  
    key = 'pcnc:'+pcnc
    if features.has_key(key):
        vector[features[key]]=1
    
    key = 'ppwpw:'+ppwpw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'ppcpw:'+ppcpw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'ppwpc:'+ppwpc
    if features.has_key(key):
        vector[features[key]]=1  
    key = 'ppcpc:'+ppcpc
    if features.has_key(key):
        vector[features[key]]=1  
        
    key = 'nwnnw:'+nwnnw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'ncnnw:'+ncnnw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'nwnnc:'+nwnnc
    if features.has_key(key):
        vector[features[key]]=1  
    key = 'ncnnc:'+ncnnc
    if features.has_key(key):
        vector[features[key]]=1   
    
    
    key = 'pw:'+pw
    if features.has_key(key):
        vector[features[key]]=1 
    key = 'nw:'+nw
    if features.has_key(key):
        vector[features[key]]=1
    key = 'nc:'+nc
    if features.has_key(key):
        vector[features[key]]=1
    key = 'pc:'+pc
    if features.has_key(key):
        vector[features[key]]=1 
    return vector 



       
class ConfusionSetClassifier():
    def __init__(self,confusionSet):
        self._confusionSet = confusionSet
    
    def checkConfSent(self,confSent):
        checkConfSent(confSent,self._confusionSet)
    
    def classify(self,confSent):
        return 
    
    def testClassifier(self,tagged_sents):
        total=0
        correct=0
        cnt = {}
        for s in tagged_sents:
            ind=-1
            for confWord,_ in s:
                ind+=1
                if confWord not in self._confusionSet:
                    continue
                guess,_ = self.classify((s,ind))
                if guess==s[ind][0]:
                    correct+=1
                total+=1
        baseline = 0
        accuracy = float(correct)*100/total
        print 'Accuracy = %.1f%% (%d/%d)' %(accuracy,correct,total)
        print
        return round(accuracy,1),correct,total
    
    
    
    def testClassifier2(self,tagged_sents):
        guesses = []
        result = []
        for s in tagged_sents:
            ind=-1
            for confWord,_ in s:
                ind+=1
                if confWord not in self._confusionSet:
                    continue
                guess,conf = self.classify((s,ind))
                if guess==s[ind][0]:
                    guessVal = 1
                else:
                    guessVal = 0
                guesses.append((guessVal,conf))
        guesses.sort(key=lambda x:x[1],reverse=True)
       

#        count = 0.0
#        total1 = 0.0
#        size = (len(guesses)*95)/100
#        for val,_ in guesses[:size]:
#            count+=val
#            total1+=1
#        result1 = round(count*100/total1,1)
#        
#        count = 0.0
#        total2 = 0.0
#        size = (len(guesses)*90)/100
#        for val,_ in guesses[:size]:
#            count+=val
#            total2+=1
#        result2 = round(count*100/total2,1)
        
        count = 0.0
        total3 = 0.0
        size = (len(guesses)*85)/100
        v,c = guesses[size]
        print c
#        for val,_ in guesses[:size]:
#            count+=val
#            total3+=1
#        result3 = round(count*100/total3,1)
#        return result1,result2,result3,total1,total2,total3
            
            
                
               
                
        
    def findErrors(self,tagged_sents,outputFileName,numberOfSents):
        tuples = []
        file = open(outputFileName,'w')
        for s in tagged_sents:
            ind=-1
            for confWord,_ in s:
                ind+=1
                if confWord not in self._confusionSet:
                    continue
                guess,confidence = self.classify((s,ind))
                if guess!=s[ind][0]:
                    tuples.append((taggedSentToOutputString(s,ind),guess,confidence))
        tuples.sort(key=lambda x:x[2],reverse=True)
        for s,g,c in tuples[:numberOfSents]:
            file.write(s+'\t'+g+'\t'+str(c)+'\n')
            
#    
#    def testClassifierArtificialErrors(self,artificialSents):
#        '''test the classifier on sentences with artificial error
#    
#            artificialSents: a list of (tagged_sent,ind,correctWord)
#        '''               
    
