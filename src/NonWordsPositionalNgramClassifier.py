#encoding=cp1255
'''
Created on 17/07/2011

@author: levyeh
'''
from Lexicon import Lexicon
import pickle
import re
from NonWordsClassifier import NonWordsClassifier, getTaggedWords
from BguCorpusReader import BguCorpusReader


def createBigramDictionary():
    dics = []
    for i in range(26):
        dics.append({})
        for j in range(i-1):
            k=j+1
            while k<i:
                dics[i][(j,k)]={}
                k+=1
    
    lex10 = Lexicon("10")
    count=0
    for w in lex10.typeDic:
        count+=1
        print count
        listOfRules = lex10.ruleDic[lex10.typeDic[w]]
        for add,rule in listOfRules:
            if re.match(rule,w):
                word = add+w
                j=0
                length = len(word)
                while j<length-1:
                    k=j+1
                    while k<length:
                        dics[length][(j,k)][word[j],word[k]]=True
                        k+=1
                    j+=1
        word = w
        j=0
        length = len(word)
        while j<length-1:
            k=j+1
            while k<length:
                dics[length][(j,k)][word[j],word[k]]=True
                k+=1
            j+=1
        
    file = open('../nonWords/bigramDic.pickle', 'wb')
    print 'serializing...'
    pickle.dump(dics,file)
    file.close()

def createTrigramDictionary():
    dics = []
    for i in range(26):
        dics.append({})
        for j in range(i-2):
            k=j+1
            while k<i-1:
                h=k+1
                while h<i:
                    dics[i][(j,k,h)]={}
                    h+=1
                k+=1
    
    lex10 = Lexicon("10")
    count=0
    for w in lex10.typeDic:
        count+=1
        print count
        listOfRules = lex10.ruleDic[lex10.typeDic[w]]
        for add,rule in listOfRules:
            if re.match(rule,w):
                word = add+w
                j=0
                length = len(word)
                while j<length-2:
                    k=j+1
                    while k<length-1:
                        h=k+1
                        while h<length:
                            dics[length][(j,k,h)][word[j],word[k],word[h]]=True
                            h+=1
                        k+=1
                    j+=1
        word = w
        j=0
        length = len(word)
        while j<length-2:
            k=j+1
            while k<length-1:
                h=k+1
                while h<length:
                    dics[length][(j,k,h)][word[j],word[k],word[h]]=True
                    h+=1
                k+=1
            j+=1
        
    file = open('../nonWords/trigramDic.pickle', 'wb')
    print 'serializing...'
    pickle.dump(dics,file)
    file.close()
    

class NonWordsPositionalBigramClassifier(NonWordsClassifier):
    def __init__(self,path):
        self._dics = self.loadData(path)
        
    def classify(self,tagged_word):
        i=0
        word,_ = tagged_word
        length = len(word)
        if length>=len(self._dics):
            return "F"
        while i<length-1:
            j=i+1
            while j<length:
                if not self._dics[len(word)][(i,j)].has_key((word[i],word[j])):
                    return "F"
                j+=1
            i+=1
        return "T"
    


class NonWordsPositionalTrigramClassifier(NonWordsClassifier):
    def __init__(self,path):
        self._dics = self.loadData(path)
        
    def classify(self,tagged_word):
        i=0
        word,_ = tagged_word
        length = len(word)
        if length>=len(self._dics):
            return "F"
        while i<length-2:
            j=i+1
            while j<length-1:
                k=j+1
                while k<length:    
                    if not self._dics[len(word)][(i,j,k)].has_key((word[i],word[j],word[k])):
                        return "F"
                    k+=1
                j+=1
            i+=1
        return "T"

class NonWordsPositionalBigramDictionaryClassifier(NonWordsPositionalBigramClassifier):
    def __init__(self):
        NonWordsPositionalBigramClassifier.__init__(self, '../nonWords/bigramDic.pickle')
    
class NonWordsPositionalBigramTBClassifier(NonWordsPositionalBigramClassifier):
    def __init__(self):
        NonWordsPositionalBigramClassifier.__init__(self, '../nonWords/bigramTB.pickle')
        
class NonWordsPositionalTrigramDictionaryClassifier(NonWordsPositionalTrigramClassifier):
    def __init__(self):
        NonWordsPositionalTrigramClassifier.__init__(self, '../nonWords/trigramDic.pickle')
    
class NonWordsPositionalTrigramTBClassifier(NonWordsPositionalTrigramClassifier):
    def __init__(self):
        NonWordsPositionalTrigramClassifier.__init__(self, '../nonWords/trigramTB.pickle')        


                                    

