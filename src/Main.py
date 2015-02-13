#encoding=cp1255

from itertools import izip
from BguCorpusReader import BguCorpusReader
from nltk.probability import FreqDist
from codecs import open
from Lexicon import Lexicon
import sys
from random import shuffle
import re
from ConfusionSetClassifier import importConfusionSets
from StaticsMethods import sentToString
from Tagger import do_post
import random
from ConfusionSetSVMClassifier import *
from ConfusionSetPerceptronClassifier import *
from ConfusionSetProbsClassifier import *
from NonWordsPositionalNgramClassifier import *
from NonWordsProbabilityNgramClassifier import *
from NonWordsSVMClassifier import NonWordsSVMClassifier
from NonWordsClassifier import getTaggedWords,NonWordsClassifier
from LanguageModel import NCharsModel
from DetectErrors import ligitWord

# 126072/669275 edits1HeuristicWithReplacement  
# 482702/2707581 edits1WithReplacement
def countRealWordsFromTypos(numOfWords):
    corpus = BguCorpusReader('c:/thesis/text/corpus/tagged','1.tagged')
    lex = Lexicon()
    total=0
    realWords=0
    j=0
    dic = {}
    for word in corpus.words():
        if not lex.checkWord(word):
            continue   
        j+=1
        if j%100==0:
            print j
            print str(realWords)+'/'+str(total)
        if j==numOfWords:
            break
        if not dic.has_key(word):
            l = edits1HeuristicWithReplacement(word)
            dic[word] = []
            dic[word].append(len(l))
            tmp = 0
            for w in l:
                if lex.checkWord(w):
                    tmp+=1
            dic[word].append(tmp)
        total += dic[word][0]
        realWords += dic[word][1]
    print str(realWords)+'/'+str(total)

#corpus
#312586/333428 if not (len(word)<2 or hasDigit(word) or hasEngChars(word) or hasEngChars(word)) random words with replacement
#312586/407186  random words with replacement
#
#tb
#1576063/1694154 if not (len(word)<2 or hasDigit(word) or hasEngChars(word) or hasEngChars(word)) random words with replacement
#1576063/1971987  random words with replacement
def countRandomWordsInLexicon():
    corpus = BguCorpusReader('d:/yoni/thesis/text/corpus/tagged','1.tagged')
    total=0
    realWords=0
    lex = Lexicon()
    for word in corpus.words():
        if len(word)<2 or hasDigit(word) or hasEngChars(word) or hasEngChars(word):
            continue
        total+=1
        if lex.checkWord(word):
            realWords+=1
    print str(realWords)+'/'+str(total)
#corpus
#304333/453279 all words without replacement if not (len(word)<2 or hasDigit(word) or hasEngChars(word) or hasEngChars(word))
#
#tb
#  98843/141176 all words without replacement if not (len(word)<2 or hasDigit(word) or hasEngChars(word) or hasEngChars(word))
def countWordsInLexicon():
    lex = Lexicon()
    corpus = BguCorpusReader('d:/yoni/thesis/text/corpus')
    words = FreqDist([w for w in corpus.words()])
    print 'here'
    total=0
    realWords=0
    for word in words.keys():
        if len(word)<2 or hasDigit(word) or hasEngChars(word) or hasEngChars(word):
            continue
        total+=1
        if lex.checkWord(word):
            realWords+=1
    print str(realWords)+'/'+str(total)

def mostCommonWords():
    corpus = BguCorpusReader('c:/thesis/text/corpus')
    fd = FreqDist([w for w,t in corpus.tagged_words() if 'NOUN' in t.getPosTag()])
    file = open('KMostCommonNounsInWalla','w')
    i=0
    for k in fd.keys():
        i+=1
        file.write(k+'\n')
        if i==1000:
            break
    file.close()
    fd = FreqDist([w for w,t in corpus.tagged_words() if 'ADJECTIVE' in t.getPosTag()])
    file = open('KMostCommonAdjInWalla','w')
    i=0
    for k in fd.keys():
        i+=1
        file.write(k+'\n')
        if i==1000:
            break
    file.close()




def exportUnknownWords():
    out = open('unknownOnlyHebCharsWords.txt','w')
    corpus = BguCorpusReader('c:/thesis/text/tb/test_tagged')
    count = 0
    x = set()
    lex = Lexicon()
    for s in corpus.tagged_sents():
        ind = -1
        for w,t in s:
            ind+=1
            if w in x or hasDigit(w) or hasExtraChar(w) or hasEngChars(w) or len(w)<=1 or lex.checkWord(w):
                continue
            count+=1
            out.write(sentToStr(s,ind)+'\t'+w+'\t'+t.getPosTag()+'\n')
            x.add(w)
            if count==2000:
                break
        if count==2000:
                break

def transfromOldTagging():
    lex = Lexicon()      
    allWords = set()
    file = open('../stats/annotated/withALexicon/unknownOnlyHebCharsWords.txt','r')
    for l in file.read().split('\n'):
        split = l.split('\t')
        w = split[1]
        allWords.add(w)
    
    input = open('../stats/annotated/withALexicon/onlyHebCharsErrors.txt','r','utf-8')
    corpus = BguCorpusReader('c:/thesis/text/tb/tagged')
    raw = input.read()
    lines = raw.split('\n')
    tagged_words = []
    ind = 0
    sents = corpus.tagged_sents()
    list = []
    for sent in sents:
        tmp = ''
        for w,_ in sent:
            tmp+=w+' '
        list.append((sent,tmp))
    
    out = open('onlyHebCharsWordsNew.txt','w')
    count = 0
    print 'here'
    for l in lines:
        split = l.split('\t')
        if len(split)<3 or (split[2]!='T' and split[2]!='F'):
            continue
        s = split[0]
        w = split[1]
        w = w.encode('cp1255')
        t = split[2]
        if w in allWords or hasDigit(w) or hasExtraChar(w) or hasEngChars(w) or len(w)<=1 or lex.checkWord(w):
            continue
        allWords.add(w) 
        tmp =''
        for x in s:
            if x!=']' and x!='[':
                tmp+=x            
    
        for tup in list:
            tmp1 = tup[1]
            if w not in tmp1:
                continue
            
            if tmp in tmp1:
                tagged_sent = tup[0]
                pos = None
                for x,tag in tagged_sent:
                    if x==w:
                        pos=tag.getPosTag()
                        out.write(s+'\t'+w+'\t'+pos+'\t'+t+'\n')
                        count+=1
                        print count
                        break
                break
   
def findUnknownWords():     
    corpus = BguCorpusReader(directory="d:/yoni/thesis/text/corpus/")
    lex11 = Lexicon("11")
    lex10 = Lexicon("10")
    known10Unknown11 = open('../stats/annotated/withHspell/known10unknown11Walla.txt','w')
    known11Unknown10 = open('../stats/annotated/withHspell/known11unknown10Walla.txt','w')
    set10 = set()
    set11 = set()
    count = 0
    for w,t in corpus.tagged_words():
        count+=1
        if count%1000==0:
            print count
        if hasEngChars(w) or hasExtraChar(w) or hasDigit(w) or len(w)<2:
            continue
        if lex11.checkWord(w) and not lex10.checkWord(w):
            if w not in set11:
                set11.add(w)
                known11Unknown10.write('None\t'+w+'\t'+t.getPosTag()+'\tT\n')
        if lex10.checkWord(w) and not lex11.checkWord(w):
            if w not in set10:
                set10.add(w)
                known10Unknown11.write('None\t'+w+'\t'+t.getPosTag()+'\tF\n') 
    


def findFalseWords():     
    lex11 = Lexicon("11")
    lex9 = Lexicon("9")
    known9Unknown11 = open('falseWords.txt','w')
    set11 = set()
    count = 0
    for w in lex9.typeDic:
        count+=1
        print count
        if not lex11.checkWord(w):
            if w not in set11:
                set11.add(w)
                known9Unknown11.write(w+'\n')
        listOfRules = lex9.ruleDic[lex9.typeDic[w]]
        for add,rule in listOfRules:
            if re.match(rule,w):
                tmp = add+w
                if tmp not in set11 and not lex11.checkWord(tmp):
                    set11.add(tmp)
                    known9Unknown11.write(tmp+'\n')


def onlyOneConfWord(sent,indOfConfWord,confWords):
    i=-1
    for w in sent:
        i+=1
        if i==indOfConfWord:
            continue
        if w in confWords:
            return False
    return True
    
def getDifferentConfWord(confusionSet,confWord):
    confusionSet.remove(confWord)
    ind = random.randint(0,len(confusionSet)-1)
    ans = confusionSet[ind]
    confusionSet.append(confWord)
    return ans

def createArtificialSents():
    corpus = BguCorpusReader('c:/thesis/text/corpus/test_tagged')
    confusionSets = importConfusionSets()
    j=-1
    for confusionSet in confusionSets[-1:]:
        j+=1
        count = 0
        file = open('artificial'+str(j)+'.tagged','w')
        for s in corpus.sents():
            ind = -1
            for w in s:
                ind+=1
                if w in confusionSet:
                    if onlyOneConfWord(s,ind,confusionSet):
                        s[ind] = getDifferentConfWord(confusionSet,w)
                        tagged = do_post(sentToString(s).encode('utf8'))
                        tagged = tagged.decode('utf8')
                        tagged = tagged.replace(s[ind],w)
                        file.write(tagged)
                        count+=1
                    break
            if count==500:
                break
        file.close()
        

def createFlaggedSents():  
    confusionSets = importConfusionSets()
    i = -1
    corpus = BguCorpusReader('C:/thesis/text/tb')       
    for confusionSet in confusionSets:
        i+=1       
#        cls = ConfusionSetBayesProbsClassifier(confusionSet)    
#        folder = '../confusionSet/Probs/Bayes/flaggedSents/'
#        fileName = 'sents'+str(i)+'.txt'
#        cls.findErrors(corpus.tagged_sents(),folder+fileName,30)
#        
#        cls = ConfusionSetPerceptronClassifier('cls'+str(i))
#        folder = '../confusionSet/Perceptron/flaggedSents/'
#        fileName = 'sents'+str(i)+'.txt'
#        cls.findErrors(corpus.tagged_sents(),folder+fileName,30)

        cls = ConfusionSetSVMClassifier('cls'+str(i))
        folder = '../confusionSet/SVM/flaggedSents/'
        fileName = 'sents'+str(i)+'.txt'
        cls.findErrors(corpus.tagged_sents(),folder+fileName,100)
        if i == 3:
            break 


def doAnnotation():
    for i in range(12):
        out = open('../confusionSet/Perceptron/flaggedSents/new/sents'+str(i)+'.txt','w' )
        lines = open('../confusionSet/Perceptron/flaggedSents/sentsNew'+str(i)+'.txt','r' ).read().split('\n')[:-1]
        lines4 = open('../confusionSet/Probs/Bayes/flaggedSents/sents'+str(i)+'.txt','r' ).read().split('\n')[:-1]
        lines3 = open('../confusionSet/SVM/flaggedSents/sents'+str(i)+'.txt','r' ).read().split('\n')[:-1]
        lines2 = open('../confusionSet/Perceptron/flaggedSents/sents'+str(i)+'.txt','r' ).read().split('\n')[:-1]
        j=1
        for l in lines:
            s,g,c = l.split('\t')
            toWrite = s+'\t'+g+'\t'+c
            found = False
            if not found:
                for l2 in lines2:
                    s2,g2,c2,t21,t22 = l2.split('\t')
                    if s==s2:
                        toWrite+='\t'+t21+'\t'+t22
                        found = True
                        break
            if not found:
                for l2 in lines3:
                    s2,g2,c2,t21,t22 = l2.split('\t')
                    if s==s2:
                        toWrite+='\t'+t21+'\t'+t22
                        found = True
                        break
            if not found:
                for l2 in lines4:
                    s2,g2,c2,t21,t22 = l2.split('\t')
                    if s==s2:
                        toWrite+='\t'+t21+'\t'+t22
                        found = True
                        break
            
            toWrite+='\n'
            out.write(toWrite)
            
            

       

def checkClassifiers():
    confusionSets = importConfusionSets()
    i = -1         
    corpus = BguCorpusReader('c:/thesis/text/walla/test_tagged') 
    matrix = []
    countAcc5=0.0
    countCorr5=0.0
    
    countAcc1=0.0
    countAcc2=0.0
    countAcc3=0.0
    countAcc4=0.0
    countCorr1=0.0
    countCorr2=0.0
    countCorr3=0.0
    countCorr4=0.0
    total = 0
    for confusionSet in confusionSets:
        i+=1
        s='\\heb{'
        for w in confusionSet:
            s+=w+', '
        s=s[:-2]
        s+='}'
        row = [s]  
          
#        cls = ConfusionSetDefaultClassifier(confusionSet)
#        a,c,t = cls.testClassifier(corpus.tagged_sents())
#        row.append(a)
#        countAcc1+=a
#        countCorr1+=c
#        total+=t
#       
#        cls = ConfusionSetBayesProbsClassifier(confusionSet)    
#        a,c,_ = cls.testClassifier(corpus.tagged_sents())
#        row.append(a)
#        countAcc2+=a
#        countCorr2+=c

        
#        cls = ConfusionSetPerceptronClassifier('cls'+str(i))
#        a,c,_ = cls.testClassifier(corpus.tagged_sents())
#        row.append(a)
#        countAcc3+=a
#        countCorr3+=c     
        
#        cls = ConfusionSetSVMClassifier('cls'+str(i))
#        a,c,_ = cls.testClassifier(corpus.tagged_sents())
#        row.append(a)
#        countAcc4+=a
#        countCorr4+=c
        
        cls = ConfusionSetPerceptronWordPosClassifier('cls'+str(i))
        a,c,t = cls.testClassifier(corpus.tagged_sents())
        row.append(a)
        countAcc5+=a
        countCorr5+=c
        total+=t
        
    
        matrix.append(row)
        
    row = ['Average Accuracy']
    row+=[round(countAcc1/len(confusionSets),1),round(countAcc2/len(confusionSets),1),round(countAcc3/len(confusionSets),1),round(countAcc4/len(confusionSets),1),round(countAcc5/len(confusionSets),1)]
    matrix.append(row)
    row = ['Weighted Average Accuracy']
    row+=[round(countCorr1*100/total,1),round(countCorr2*100/total,1),round(countCorr3*100/total,1),round(countCorr4*100/total,1),round(countCorr5*100/total,1)]
    matrix.append(row)
    matrixToLatex(matrix, 'out.txt')


def checkClassifiers2():
    confusionSets = importConfusionSets()    
    matrix = []
    countAcc5=0.0
    countCorr5=0.0
    countAcc1=0.0
    countAcc2=0.0
    countAcc3=0.0
    countAcc4=0.0
    countCorr1=0.0
    countCorr2=0.0
    countCorr3=0.0
    countCorr4=0.0
    total = 0
    i = -1   
    corpus2 = BguCorpusReader('c:/thesis/text/walla/test_tagged')
    for confusionSet in confusionSets:
        cls = ConfusionSetDefaultClassifier(confusionSet)
        _,_,t = cls.testClassifier(corpus2.tagged_sents())
        total+=t
        
        i+=1 
        s='\\heb{'
        for w in confusionSet:
            s+=w+', '
        s=s[:-2]
        s+='}'
        row = [s]    
        corpus = BguCorpusReader('../text/walla/artificial_tagged/','artificial'+str(i)+'.tagged') 
        
#        cls = ConfusionSetDefaultClassifier(confusionSet)
#        a,_,_ = cls.testClassifier(corpus.tagged_sents())
#        row.append(a)
#        countAcc1+=a
#        countCorr1+=(a/100)*t
#       
#        cls = ConfusionSetBayesProbsClassifier(confusionSet)    
#        a,_,_ = cls.testClassifier(corpus.tagged_sents())
#        row.append(a)
#        countAcc2+=a
#        countCorr2+=(a/100)*t
#
#        
#        cls = ConfusionSetPerceptronClassifier('cls'+str(i))
#        a,_,_ = cls.testClassifier(corpus.tagged_sents())
#        row.append(a)
#        countAcc3+=a
#        countCorr3+=(a/100)*t     
#        
#        cls = ConfusionSetSVMClassifier('cls'+str(i))
#        a,_,_ = cls.testClassifier(corpus.tagged_sents())
#        row.append(a)
#        countAcc4+=a
#        countCorr4+=(a/100)*t
        
        cls = ConfusionSetPerceptronWordPosClassifier('cls'+str(i))
        a,_,_ = cls.testClassifier(corpus.tagged_sents())
        row.append(a)
        countAcc5+=a
        countCorr5+=(a/100)*t
    
        matrix.append(row)
        
    row = ['Average Accuracy']
    row+=[round(countAcc1/len(confusionSets),1),round(countAcc2/len(confusionSets),1),round(countAcc3/len(confusionSets),1),round(countAcc4/len(confusionSets),1),round(countAcc5/len(confusionSets),1)]
    matrix.append(row)
    row = ['Weighted Average Accuracy']
    row+=[round(countCorr1*100/total,1),round(countCorr2*100/total,1),round(countCorr3*100/total,1),round(countCorr4*100/total,1),round(countCorr5*100/total,1)]
    matrix.append(row)
    matrixToLatex(matrix, 'out2.txt')
        

def addVectors(a,b):
    ans = []
    for x1,x2 in izip(a,b):
        ans.append(x1+x2)
    return ans

    
    

def checkClassifiers3():
    confusionSets = importConfusionSets()
    i = -1         
    corpus = BguCorpusReader('c:/thesis/text/walla/test_tagged') 
    matrix = []
    avg11 = 0.0
    avg12 = 0.0
    avg13 = 0.0
    avg21 = 0.0
    avg22 = 0.0
    avg23 = 0.0
    avg31 = 0.0
    avg32 = 0.0
    avg33 = 0.0
    
    corr11 = 0.0
    corr12 = 0.0
    corr13 = 0.0
    corr21 = 0.0
    corr22 = 0.0
    corr23 = 0.0
    corr31 = 0.0
    corr32 = 0.0
    corr33 = 0.0
    
    total1 = 0.0
    total2 = 0.0
    total3 = 0.0
    
    for confusionSet in confusionSets:
        s='\\heb{'
        for w in confusionSet:
            s+=w+', '
        s=s[:-2]
        s+='}'
        row = [s]
        i+=1
        print i
        cls = ConfusionSetBayesProbsClassifier(confusionSet)    
        x11,x12,x13,t1,t2,t3 = cls.testClassifier2(corpus.tagged_sents())
        avg11+=x11
        avg12+=x12
        avg13+=x13
        total1+=t1
        total2+=t2
        total3+=t3
        corr11+=(x11/100)*t1
        print corr11
        print total1
        corr12+=(x12/100)*t2
        corr13+=(x13/100)*t3
        
        
        print i
        cls = ConfusionSetPerceptronClassifier('cls'+str(i))
        x21,x22,x23,_,_,_ = cls.testClassifier2(corpus.tagged_sents())
        avg21+=x21
        avg22+=x22
        avg23+=x23
        corr21+=(x21/100)*t1
        corr22+=(x22/100)*t2
        corr23+=(x23/100)*t3
        
        print i
        cls = ConfusionSetSVMClassifier('cls'+str(i))
        x31,x32,x33,_,_,_ = cls.testClassifier2(corpus.tagged_sents())
        avg31+=x31
        avg32+=x32
        avg33+=x33
        corr31+=(x31/100)*t1
        corr32+=(x32/100)*t2
        corr33+=(x33/100)*t3
        
        row+=[x11,x21,x31,x12,x22,x32,x13,x23,x33]
        matrix.append(row)
        
    row = ['Average Accuracy']
    row+=[round(avg11/9,1),round(avg21/9,1),round(avg31/9,1),round(avg12/9,1),round(avg22/9,1),round(avg32/9,1),round(avg13/9,1),round(avg23/9,1),round(avg33/9,1)]
    matrix.append(row)
    row = ['Weighted Average Accuracy']
    row+=[round(corr11*100/total1,1),round(corr21*100/total1,1),round(corr31*100/total1,1),round(corr12*100/total2,1),round(corr22*100/total2,1),round(corr32*100/total2,1),round(corr13*100/total3,1),round(corr23*100/total3,1),round(corr33*100/total3,1)]
    matrix.append(row)
    matrixToLatex(matrix)
           
def checkClassifiers4():
    corpus = BguCorpusReader('c:/thesis/text/walla/test_tagged') 
    confusionSets = importConfusionSets()
    i = -1 
    proportion = 25
    out = open('out3.txt','w')
    for j in range(1):
        acc1 = 0
        acc2 = 0
        acc3 = 0
        proportion = proportion*5
        calcData(proportion)
        createSVMClassifiers(proportion)
        createPerceptronClassifiers(proportion)
        i = -1
        for confusionSet in confusionSets:
            i+=1 
            cls = ConfusionSetBayesProbsClassifier(confusionSet)
            a,_,_ = cls.testClassifier(corpus.tagged_sents())
            acc1+=a
            cls = ConfusionSetPerceptronClassifier('cls'+str(i))
            a,_,_ = cls.testClassifier(corpus.tagged_sents())
            acc2+=a
            cls = ConfusionSetSVMClassifier('cls'+str(i))
            a,_,_ = cls.testClassifier(corpus.tagged_sents())
            acc3+=a 
            
        out.write(str(round(acc1/len(confusionSets),1))+'\t'+str(round(acc2/len(confusionSets),1))+'\t'+str(round(acc3/len(confusionSets),1))+'\n')
        
    
def createConfWordsTable():
    confusionSets = importConfusionSets()
    words = []
    for confusionSet in confusionSets:
        for w in confusionSet:
            if w not in words:
                words.append(w)
    cnt = {}
    corpus = BguCorpusReader('c:/thesis/text/corpus/test_tagged') 
    matrix = []
    for w in corpus.words():
        cnt[w] = cnt.get(w,0)+1
    for w in words:
        row = ['\\heb{'+w+'}',cnt[w]]
        matrix.append(row)
    matrixToLatex(matrix,'wordsTable.txt')
  
  
def matrixToLatex(matrix,fileName='output.txt'):
    output = open(fileName,'w') 
    for row in matrix:
        s=''
        for c in row:
            s+=str(c)+' & '
        s=s[:-2]
        s+='\\\\\n'
        output.write(s)
        

def checkPrecision():
    confusionSets = importConfusionSets()
    i = -1
               
    matrix = []
    for confusionSet in confusionSets:
        i+=1
        s='\\heb{'
        for w in confusionSet:
            s+=w+', '
        s=s[:-2]
        s+='}'
        row = [s]
        
        
        acc11 = 0
        acc12 = 0
        acc13 = 0
        acc21 = 0
        acc22 = 0
        acc23 = 0 
        acc31 = 0
        acc32 = 0
        acc33 = 0 
         
        count =0.0
        total =0 
        lines = open('../confusionSet/Probs/Bayes/flaggedSents/sentsAnnotated'+str(i)+'.txt','r' ).read().split('\n')[:-1]
        for l in lines:
            count+=1
            if (l!='T' and l!='F') or (l!='T' and l!='F'):
                print 'error1'
            if l=='T':
                total+=1
            
            if count==10:
                acc11 = total
            if count==20:
                acc12 = total
        acc13 = total
            
        count =0.0
        total =0  
        lines = open('../confusionSet/Perceptron/flaggedSents/sentsAnnotated'+str(i)+'.txt','r' ).read().split('\n')[:-1]
        for l in lines:
            count+=1
            if (l!='T' and l!='F') or (l!='T' and l!='F'):
                print 'error2'
            if l=='T':
                total+=1
            
            if count==10:
                acc21 = total
            if count==20:
                acc22 = total
        acc23 = total
        
        count =0.0
        total =0 
        lines = open('../confusionSet/SVM/flaggedSents/sentsAnnotated'+str(i)+'.txt','r' ).read().split('\n')[:-1]
        for l in lines:
            count+=1
            if (l!='T' and l!='F') or (l!='T' and l!='F'):
                print 'error3'
            if l=='T':
                total+=1
            
            if count==10:
                acc31 = total
            if count==20:
                acc32 = total
        acc33 = total
        
        row+=[acc11,acc21,acc31,acc12,acc22,acc32,acc13,acc23,acc33]
        matrix.append(row)
    matrixToLatex(matrix,'precision.txt')
 
 
           
            
            


def checkNonWords():
    
    tagged_words = getTaggedWords()
    matrix = []
    
    """
    model2 = NCharsModel('../nonWords/NCharsTBAllWords.model',2)  
    model3 = NCharsModel('../nonWords/NCharsTBAllWords.model',3) 
    
    
    cls = NonWordsClassifier()
    p0,r0,f0,a0 = cls.testClassifier(tagged_words)
    print 'done 0'
    
    tp = 0
    tr = 0
    ta = 0
    tf = 0
    for i in range(10):
        start = i*len(tagged_words)/10
        end = (i+1)*len(tagged_words)/10
        cls = NonWordsLanguageModelClassifier(model2,tagged_words[:start]+tagged_words[end:])
        p,r,f,a = cls.testClassifier(tagged_words[start:end])
        tp+=p
        tr+=r
        ta+=a
        tf+=f 
    p1 = tp/10.0
    r1 = tr/10.0
    a1 = ta/10.0
    f1 = tf/10.0 
    print 'done 1'
    
    tp = 0
    tr = 0
    ta = 0
    tf = 0
    for i in range(10):
        start = i*len(tagged_words)/10
        end = (i+1)*len(tagged_words)/10
        cls = NonWordsLanguageModelClassifier(model3,tagged_words[:start]+tagged_words[end:])
        p,r,f,a = cls.testClassifier(tagged_words[start:end])
        tp+=p
        tr+=r
        ta+=a
        tf+=f 
    p2 = tp/10.0
    r2 = tr/10.0
    a2 = ta/10.0
    f2 = tf/10.0    
    print 'done 2'   
    
    cls = NonWordsPositionalBigramDictionaryClassifier()
    p3,r3,f3,a3 = cls.testClassifier(tagged_words)
    print 'done 3'

    cls = NonWordsPositionalTrigramDictionaryClassifier()
    p4,r4,f4,a4 = cls.testClassifier(tagged_words)
    print 'done 4'
    
    tp = 0
    tr = 0
    ta = 0
    tf = 0
    for i in range(10):
        start = i*len(tagged_words)/10
        end = (i+1)*len(tagged_words)/10
        cls = NonWordsPeculiarityClassifier(tagged_words[:start]+tagged_words[end:])
        p,r,f,a = cls.testClassifier(tagged_words[start:end])
        tp+=p
        tr+=r
        ta+=a
        tf+=f 
    p5 = tp/10.0
    r5 = tr/10.0
    a5 = ta/10.0
    f5 = tf/10.0
    print 'done 5'
    
    tp = 0
    tr = 0
    ta = 0
    tf = 0
    for i in range(10):
        start = i*len(tagged_words)/10
        end = (i+1)*len(tagged_words)/10
        cls = NonWordsErrorProbabilityClassifier(tagged_words[:start]+tagged_words[end:])
        p,r,f,a = cls.testClassifier(tagged_words[start:end])
        tp+=p
        tr+=r
        ta+=a
        tf+=f 
    p6 = tp/10.0
    r6 = tr/10.0
    a6 = ta/10.0
    f6 = tf/10.0
    print 'done 6'
    """
    tp = 0
    tr = 0
    ta = 0
    tf = 0
    for i in range(10):
        start = i*len(tagged_words)/10
        end = (i+1)*len(tagged_words)/10
        cls = NonWordsSVMClassifier(tagged_words[:start]+tagged_words[end:])
        p,r,f,a = cls.testClassifier(tagged_words[start:end])
        tp+=p
        tr+=r
        ta+=a
        tf+=f 
    p7 = tp/10.0
    r7 = tr/10.0
    a7 = ta/10.0
    f7 = tf/10.0
    print 'done 7'
    

#    row = ['Baseline',p0,r0,f0,a0]
#    matrix.append(row)
#    row = ['Bigram TB Probability',p1,r1,f1,a1]
#    matrix.append(row)
#    row = ['Trigram TB Probability',p2,r2,f2,a2]
#    matrix.append(row)
#    row = ['Positional Bigrams',p3,r3,f3,a3]
#    matrix.append(row)
#    row = ['Positional Trigrams',p4,r4,f4,a4]
#    matrix.append(row)
#    row = ['peculariaty',p5,r5,f5,a5]
#    matrix.append(row)
#    row = ['error probability',p6,r6,f6,a6]
#    matrix.append(row)
    row = ['SVM',p7,r7,f7,a7]
    matrix.append(row)
    matrixToLatex(matrix)
    

tagged_words = getTaggedWords()
start = i*len(tagged_words)/10
end = (i+1)*len(tagged_words)/10
cls = NonWordsSVMClassifier(tagged_words[:start]+tagged_words[end:])
cls.testClassifier(tagged_words[start:end])




#checkClassifiers4()   
#checkClassifiers2()   
   
#createFlaggedSents()
#checkClassifiers()
#checkPrecision()


#checkNonWords()
#confusionSets = importConfusionSets()
#i=-1
#for confSet in confusionSets:
#    i+=1
#    cls = {}
#    for w in confSet:
#       cls[w]=0
#    corpus = BguCorpusReader('../text/walla/artificial_tagged','artificial'+str(i)+'.tagged')
#    for w in corpus.words():
#        if w in confSet:
#            cls[w]+=1
#    for w in cls:
#        print w+' : '+str(cls[w])
#    print 
#    print

