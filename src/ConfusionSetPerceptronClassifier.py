'''
Created on Jul 21, 2011

@author: Yoni Lev
'''

from Perceptron import VotedPerceptron
from ConfusionSetClassifier import createCls,createFeatures,createVector,\
    importConfusionSets,ConfusionSetClassifier,createVectorWordPos
from StaticsMethods import serialize,loadSerialize,NUM_OF_SENTS
from BguCorpusReader import BguCorpusReader

import os


def findFeaturesDim(features):
    return max(features.values())+1


def createClassifier(confusionSet,tagged_sents,folderName):
    features = createFeatures(tagged_sents,confusionSet)
    event_size = findFeaturesDim(features)
    wordsToCls,clsToWords = createCls(confusionSet)
    outcome_size = len(clsToWords.keys())
    m = VotedPerceptron(event_size)
    for s in tagged_sents:
        ind=-1
        for confWord,_ in s:
            ind+=1
            if confWord not in confusionSet:
                continue
            x = createVector((s,ind), features)
            y = wordsToCls[s[ind][0]]
            m.train(x,y)
    print 'done learning...'
    serialize(features,folderName+'/features.pickle')
    serialize(clsToWords,folderName+'/clsToWords.pickle')
    serialize(m,folderName+'/m.pickle')
    
def createPerceptronClassifiers(proportion=1):
    trainCorpus = BguCorpusReader('c:/thesis/text/walla/tagged')
    confusionSets = importConfusionSets()
    i=0
    size = NUM_OF_SENTS/proportion
    for confusionSet in confusionSets:
        print 'perceptron'
        print i
        folder = '../confusionSet/Perceptron/cls'+str(i)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        createClassifier(confusionSet,trainCorpus.tagged_sents()[:size],folder)
        i+=1
        

class ConfusionSetPerceptronClassifier(ConfusionSetClassifier):
    def __init__(self,folder):
        self._features = loadSerialize('../confusionSet/Perceptron/'+folder+'/features.pickle')
        self._clsToWords = loadSerialize('../confusionSet/Perceptron/'+folder+'/clsToWords.pickle')
        self._m = loadSerialize('../confusionSet/Perceptron/'+folder+'/m.pickle')
        self._dim = findFeaturesDim(self._features)
        ConfusionSetClassifier.__init__(self,self._clsToWords.values())
        
        
        
    def classify(self,confSent):
        x = createVector(confSent,self._features)
        label,confidence = self._m.score(x)
        guessedWord = self._clsToWords[label]
        return guessedWord,confidence
    
    
class ConfusionSetPerceptronWordPosClassifier(ConfusionSetPerceptronClassifier):
    def __init__(self,folder):
        self._features = loadSerialize('../confusionSet/wordSimple/Perceptron/'+folder+'/features.pickle')
        self._clsToWords = loadSerialize('../confusionSet/wordSimple/Perceptron/'+folder+'/clsToWords.pickle')
        self._m = loadSerialize('../confusionSet/wordSimple/Perceptron/'+folder+'/m.pickle')
        self._dim = findFeaturesDim(self._features)
        ConfusionSetClassifier.__init__(self,self._clsToWords.values())
    
    def classify(self,confSent):
        x = createVectorWordPos(confSent,self._features)
        label,confidence = self._m.score(x)
        guessedWord = self._clsToWords[label]
        return guessedWord,confidence

#createClassifiers()
