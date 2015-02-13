#encoding=cp1255
import os
from svmutil import *
from BguCorpusReader import BguCorpusReader
from ConfusionSetClassifier import ConfusionSetClassifier,importConfusionSets,getFeatures,\
    createFeatures, createCls, createVector
from StaticsMethods import serialize,loadSerialize,NUM_OF_SENTS


def createClassifier(confusionSet,tagged_sents,folderToSave,param='-t 0 -h 0'):
    features = createFeatures(tagged_sents,confusionSet)
    wordsToCls,clsToWords = createCls(confusionSet)
    trainX = []
    trainY = []
    for s in tagged_sents:
        ind=-1
        for confWord,_ in s:
            ind+=1
            if confWord not in confusionSet:
                continue
            x = createVector((s,ind), features)
            y = wordsToCls[s[ind][0]]
            trainX.append(x)
            trainY.append(y)
            
    prob  = svm_problem(trainY, trainX)
    m = svm_train(prob, param)
    svm_save_model(folderToSave+'/m.svm',m)
    serialize(features,folderToSave+'/features.pickle')
    serialize(clsToWords,folderToSave+'/clsToWords.pickle')
    
def createSVMClassifiers(proportion=1):
    trainCorpus = BguCorpusReader('c:/thesis/text/walla/tagged')
    size = NUM_OF_SENTS/proportion
    confusionSets = importConfusionSets()
    i=0
    for confusionSet in confusionSets:
        print 'svm'
        print i
        folder = '../confusionSet/SVM/cls'+str(i)
        if not os.path.isdir(folder):
            os.mkdir(folder)
        createClassifier(confusionSet,trainCorpus.tagged_sents()[:size],folder)
        i+=1




class ConfusionSetSVMClassifier(ConfusionSetClassifier):
    def __init__(self,folder):
        self._features = loadSerialize('../confusionSet/SVM/'+folder+'/features.pickle')
        self._clsToWords = loadSerialize('../confusionSet/SVM/'+folder+'/clsToWords.pickle')
        self._m = svm_load_model('../confusionSet/SVM/'+folder+'/m.svm')
        ConfusionSetClassifier.__init__(self,self._clsToWords.values())
        
        
        
    def classify(self,confSent):
        x = createVector(confSent,self._features)
        p_labels,_, p_vals = svm_predict([-1],[x],self._m)
        label = p_labels[0]
        guessedWord = self._clsToWords[label]
        probabilities = p_vals[0]
#        probabilities.sort(reverse=True)
#        max = probabilities[0]
#        second = probabilities[1]
        return guessedWord,abs(probabilities[0])
        
        

#createClassifiers()
