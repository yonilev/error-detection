'''
Created on Jul 18, 2011

@author: Yoni Lev
'''
import pickle


def getTaggedWords(path='../stats/annotated/withHspell/unknownOnlyHebCharsWords.txt'):
    file = open(path,'r')
    raw = file.read()
    lines = raw.split('\n')
    tagged_words = []
    for l in lines:
        split = l.split('\t')
        if len(split)<4 or (split[3]!='T' and split[3]!='F'):
            continue
        w = split[1]
        pos = split[2]
        err = split[3]
        tagged_words.append((w,pos,err))
    return tagged_words

class NonWordsClassifier():
    def classify(self,word):
        return "F"
    
    def loadData(self,path):
        file = open(path,'rb')
        ans = pickle.load(file)
        file.close()
        return ans
    
    def testClassifier(self,tagged_words):
        tp=0.0
        tn=0.0
        fp=0.0
        fn=0.0
        for w,p,t in tagged_words:
            pred = self.classify((w,p))
            if pred==t:
                if pred=='F':
                    tp+=1
                if pred=='T':
                    tn+=1
                    print w
            else:
                if pred=='F':
                    fp+=1
                if pred=='T':
                    fn+=1
        if tp==0:
            precision=0
            recall=0
        else:
            precision = tp/(tp+fp)
            recall = tp/(tp+fn)
        if precision==0 and recall==0:
            f_measure = 0
        else:
            f_measure = round((2*precision*recall)/(precision+recall),2)
            
#        print 'test size: '+str(len(tagged_words))
#        print 'precision '+str(round(precision,2))
#        print 'recall: '+str(round(recall,2))
#        print 'f_measure: '+str(f_measure)
#        print 'accuracy: '+str(round((tp+tn)/(tp+tn+fp+fn),2))
#        print
        return round(precision,2),round(recall,2),f_measure,round((tp+tn)/(tp+tn+fp+fn),2)
        