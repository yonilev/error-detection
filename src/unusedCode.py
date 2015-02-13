from nltk import FreqDist
from nltk import ConditionalFreqDist
from DetectErrors import serialize,loadSerializedFile
from random import shuffle
from itertools import permutations,izip,product
from BguCorpusReader import BguCorpusReader
from ConfusionSetMemoryClassifier import calcMinProbs,updateProb,importConfusionSets

PREV_WORD = 1
PREV_COMPLEX = 2
NEXT_WORD = 3
NEXT_COMPLEX = 4

def importSerialzed(folder,listOfNames):
    ans = []
    for name in listOfNames:
        ans.append(loadSerializedFile(folder+name+'.pickle'))
    return ans

def importConfusionSents(fileNum,folder='../confusionSet/confusionSents/'):
    file = open(folder+fileNum+'.conf','r')
    ans = []
    sents = file.read()[:-2].split('\n\n')
    for sent in sents:
        tagged_words = sent.split('\n')
        wordInd = int(tagged_words[1])
        sentInd = int(tagged_words[0])
        s = tagged_words[2:]
        ans.append((sentInd,wordInd,s))
    return ans

    



def calcProbFromConfSents(confSents,folder=None):
    c_confusionWords = []
    c_prev1ComplexNext1Complex = []
    c_prev1WordNext1Word = []
    c_prev1Complex = []
    c_next1Complex = []
    c_prev1Word = []
    c_next1Word = []
    c_prev1ComplexNext1Word = []
    c_prev1WordNext1Complex = []
    for _,i,s in confSents:
        confWord = s[i].split('\t')[0]
        length = len(s)
        hasNext = False
        hasPrev = False
        if i+1<length:
            hasNext=True
            splS = s[i+1].split('\t')
            nextWord = splS[0]
            nextComplex = splS[1]
        if i-1>=0:
            hasPrev = True
            splS = s[i-1].split('\t')
            prevWord = splS[0]
            prevComplex = splS[1]
       
            
        c_confusionWords.append(confWord)
        if hasPrev and hasNext:
            c_prev1Complex.append((confWord,prevComplex))
            c_prev1Word.append((confWord,prevWord))
            c_prev1ComplexNext1Complex.append((confWord,prevComplex+'#'+nextComplex))    
            c_prev1WordNext1Word.append((confWord,prevWord+'#'+nextWord))
            c_next1Complex.append((confWord,nextComplex))
            c_next1Word.append((confWord,nextWord))
            c_prev1ComplexNext1Word.append((confWord,prevComplex+'#'+nextWord))
            c_prev1WordNext1Complex.append((confWord,prevWord+'#'+nextComplex))
                
        if hasPrev and not hasNext:
            c_prev1Complex.append((confWord,prevComplex))
            c_prev1Word.append((confWord,prevWord))
                
        if not hasPrev and hasNext:
                c_next1Complex.append((confWord,nextComplex))
                c_next1Word.append((confWord,nextWord))
            
                
    fd_confusionWords = FreqDist(c_confusionWords)
    cfd_prev1ComplexNext1Complex = ConditionalFreqDist(c_prev1ComplexNext1Complex)
    cfd_prev1WordNext1Word = ConditionalFreqDist(c_prev1WordNext1Word)
    cfd_prev1Complex = ConditionalFreqDist(c_prev1Complex)
    cfd_next1Complex = ConditionalFreqDist(c_next1Complex)
    cfd_prev1Word = ConditionalFreqDist(c_prev1Word)
    cfd_next1Word = ConditionalFreqDist(c_next1Word)
    cfd_prev1ComplexNext1Word = ConditionalFreqDist(c_prev1ComplexNext1Word)
    cfd_prev1WordNext1Complex = ConditionalFreqDist(c_prev1WordNext1Complex)
    list = [(fd_confusionWords,'fd_confusionWords'),(cfd_prev1ComplexNext1Complex,'cfd_prev1ComplexNext1Complex'),(cfd_prev1WordNext1Word,'cfd_prev1WordNext1Word'),(cfd_prev1Complex,'cfd_prev1Complex'),(cfd_next1Complex,'cfd_next1Complex'),(cfd_prev1Word,'cfd_prev1Word'),(cfd_next1Word,'cfd_next1Word'),(cfd_prev1ComplexNext1Word,'cfd_prev1ComplexNext1Word'),(cfd_prev1WordNext1Complex,'cfd_prev1WordNext1Complex')]
    if folder!=None:
        serialize(list,folder)
    return  fd_confusionWords,cfd_prev1ComplexNext1Complex,cfd_prev1WordNext1Word,cfd_prev1Complex,cfd_next1Complex,cfd_prev1Word,cfd_next1Word,cfd_prev1ComplexNext1Word,cfd_prev1WordNext1Complex


def defaultGuess(fd):
    maxP = 0
    ans = None
    for k in fd.keys():
        if fd[k]>maxP:
            maxP = fd[k]
            ans = k
    return ans


def check1(cfd,word):
    max = (None,0)
    second = (None,0)
    for c in cfd.conditions():
            if cfd[c].freq(word)>max[1]:
                second = max
                max = (c,cfd[c].freq(word))
    return max,second

def testByOrder(testConfSents,checkList):
    correct = 0
    total = 0
#    errorsByGuessNumber = {} 
#    correctsByGuessNumber = {} 
#    errorsRationByGuessNumber = {}
    for _,ind,s in testConfSents:
        total+=1
        correctWord = s[ind].split('\t')[0]
        length = len(s)
        nextComplex = 'None'
        nextWord = 'None'
        prevComplex = 'None'
        prevWord = 'None'
        if ind+1<length:
            nextWord,nextComplex,_ = s[ind+1].split('\t')
        if ind-1>=0:
            prevWord,prevComplex,_= s[ind-1].split('\t')
        guessedWord = None
        for tup in checkList:
            testWord=""
            if tup[1]==None:
                guessedWord=defaultGuess(tup[0])
                break
            for w in tup[1]:
                if w==PREV_COMPLEX:
                    testWord+=prevComplex+'#'
                elif w==PREV_WORD:
                    testWord+=prevWord+'#'
                elif w==NEXT_COMPLEX:
                    testWord+=nextComplex+'#'
                elif w==NEXT_WORD:
                    testWord+=nextWord+'#'
            testWord=testWord[:-1]
            guessedWord = check1(tup[0],testWord)[0][0]
            if guessedWord!=None:
                break                                                                                   
        if guessedWord==correctWord:
            correct+=1
    return correct

#            correctsByGuessNumber[guessNumber] = correctsByGuessNumber.get(guessNumber,0)+1
#        else:
#            errorsByGuessNumber[guessNumber] = errorsByGuessNumber.get(guessNumber,0)+1
#    
#    for k in errorsByGuessNumber.keys():
#        errorsRationByGuessNumber[k] = float(correctsByGuessNumber[k])/(errorsByGuessNumber[k]+correctsByGuessNumber[k])
#    
#    print "accuracy: "+ str(correct)+"/"+str(total)
#    print errorsByGuessNumber
#    print correctsByGuessNumber
#    print errorsRationByGuessNumber


#['0', '1', '2', '3', '5', '4', '7', '6','8']

def findBestOrder(testConfSents,checkList):
    max = 0
    maxOrder = None
    iterNum = 0
    for perm in permutations(checkList):
        iterNum+=1
        if iterNum%100==0:
            print iterNum
        order = [s for _,_,s in perm]
        tmp = testByOrder(testConfSents, perm)
        if tmp>max:
            max = tmp
            maxOrder = order
            print max
            print maxOrder
            
    return max,maxOrder








        
def exportConfSents(confusionSets,corpus=BguCorpusReader('../text/walla/tagged'),folder='../confusionSet/confusionSents/'):
    fileDic = {}
    fileInd = 0
    confWordsSet = set()
    for w in confusionSets.keys():
        confWordsSet.add(w)
        for wi in confusionSets[w]:
            confWordsSet.add(wi)
    for w in confWordsSet:
        fileDic[w]= str(fileInd)
        fileInd+=1
    out = open('../confusionSet/confusionWords.txt','w')
    for w in fileDic.keys():
        out.write(w+'\n'+fileDic[w]+'\n\n') 
    out.close()
    tagged_sents = corpus.tagged_sents()
    sentInd = 0
    for s in tagged_sents:
        i = 0
        if sentInd%100==0:
            print sentInd
        for w,_ in s:
            w = w.encode('cp1255')
            if fileDic.has_key(w):
                appendConfSentToFile(folder+fileDic[w]+'.conf',i,s,sentInd)
            i+=1
        sentInd+=1
            
def appendConfSentToFile(path,i,s,sentInd,window=2):
    out = open(path,'a')
    out.write(str(sentInd)+'\n')
    confWordInd = min(2,i)
    out.write(str(confWordInd)+'\n')
    for j in range((2*window)+1):
        if i-window+j>=0 and i-window+j<len(s):
            out.write(s[i-window+j][0]+'\t'+s[i-window+j][1].getPosTag()+'\n')
    out.write('\n')
    out.close()


def importConfusionWordsDic(path):
    dic = {}
    file = open(path,'r')
    words = file.read()[:-2].split('\n\n')
    for tup in words:
        word,fileId = tup.split('\n')
        dic[word] = fileId
    return dic

def levenshtein_distance(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
        distance_matrix[i][0] = i
    for j in range(second_length):
        distance_matrix[0][j]=j
    for i in xrange(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]

