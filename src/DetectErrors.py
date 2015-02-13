#encoding=cp1255
from nltk import FreqDist
from nltk import ConditionalFreqDist
from nltk.util import clean_html
from BguCorpusReader import BguCorpusReader, bguTag
from codecs import open
import pickle
from itertools import izip
from translitsIdentifier import transClassifier
import bgutags_new
import hebtokenizer
from Lexicon import Lexicon

english = "qwertyuioplkjhgfdsazxcvbnmQWERTYUIOPLKJHGFDSAZXCVBNM"
alphabet = "פםןוטארקשדגכעיחלךףץתצמנהבסז".decode('cp1255')
digits = "1234567890"
extraChars = """`!@#$%^&*()=+\]~}[{,;:/><?_ֱֲֳִֵֶַָֹּׁׂ"""
ligitsChars = alphabet+"""."'"""

def hasExtraChar(word):
    for c in word:
        if c in extraChars:
            return True
    return False

def hasDigit(word):
    for c in word:
        if c in digits:
            return True
    return False

def hasEngChars(word):
    for c in word:
        if c in english:
            return True
    return False

def ligitWord(word):
    for c in word:
        if c not in ligitsChars:
            return False
    return True

def allHebChars(word):
    for c in word:
        if c not in alphabet:
            return False
    return True    

    
def printSent(words,start,count):
    ans = ''
    half = count/2
    for j in range(half):
        if start-(half-j)<len(words) and start-(half-j)>=0:
            ans+=words[start-(half-j)]+' '
    ans+='['+words[start]+'] '
    for j in range(half):
        if start+j+1<len(words) and start+j+1>=0:
            ans+=words[start+j+1]+' '
    print ans
  

def serialize(list,folder):
    for par,parStr in list:
        file = open(folder+parStr+'.pickle', 'wb')
        print 'serializing...'
        pickle.dump(par,file)
        file.close()
        


#    return fdWords,fdWords2,fdWords3,fdTags,fdTags2,fdTags3
#    return cfdWordsNextTags,cfdWordsNextTags2,cfdWordsPrevTags,cfdWordsPrevTags2

def saveData(data,name,folder):
    list = [(data,name)]
    serialize(list,folder)
    
def loadData(folder,name):
    return loadSerializedFile(folder+name+'.pickle')
            
def save(corpus,folder,th=0):
    saveFdPosTags(corpus,folder,th)
    print'1 done...'
    saveFdPosTags2(corpus,folder,th)
    print'2 done...'
    saveFdPosTags3(corpus,folder,th)
    print'3 done...'
    saveFdWords(corpus,folder,th)
    print'4 done...'
    saveFdWords2(corpus,folder,th)
    print'5 done...'
    saveFdWords3(corpus,folder,th)
    print'6 done...'
    saveCfdWordsNextPosTags(corpus,folder,th)
    print'7 done...'
    saveCfdWordsNextPosTags2(corpus,folder,th)
    print'8 done...'   
    saveCfdWordsPrevPosTags(corpus,folder,th)
    print'9 done...' 
    saveCfdWordsPrevPosTags2(corpus,folder,th)
    print'10 done...'
   


    
def saveFdPosTags(corpus,folder,th=0):
    fdPosTags =  corpus.fdPosTags(th)
    list = [(fdPosTags,'fdPosTags')]
    serialize(list,folder)

def saveFdPosTags2(corpus,folder,th=0):
    fdPosTags2 =  corpus.fdPosTags2(th)
    list = [(fdPosTags2,'fdPosTags2')]
    serialize(list,folder)
    
def saveFdPosTags3(corpus,folder,th=0):
    fdPosTags3 =  corpus.fdPosTags3(th)
    list = [(fdPosTags3,'fdPosTags2')]
    serialize(list,folder)

def saveFdWords(corpus,folder,th=0):
    fdFdWords =  corpus.fdFdWords(th)
    list = [(fdFdWords,'fdFdWords')]
    serialize(list,folder)

def saveFdWords2(corpus,folder,th=0):
    fdFdWords2 =  corpus.fdFdWords2(th)
    list = [(fdFdWords2,'fdFdWords2')]
    serialize(list,folder)
    
def saveFdWords3(corpus,folder,th=0):
    fdFdWords3 =  corpus.fdFdWords3(th)
    list = [(fdFdWords3,'fdFdWords3')]
    serialize(list,folder)
  
def saveCfdWordsNextPosTags(corpus,folder,th=0):
    cfdWordsNextPosTags = corpus.cfdWordsNextPosTags(th) 
    list = [(cfdWordsNextPosTags,'cfdWordsNextPosTags')]   
    serialize(list,folder)

def saveCfdWordsNextPosTags2(corpus,folder,th=0):
    cfdWordsNextPosTags2 = corpus.cfdWordsNextPosTags2(th) 
    list = [(cfdWordsNextPosTags2,'cfdWordsNextPosTags2')]   
    serialize(list,folder)
    
def saveCfdWordsPrevPosTags(corpus,folder,th=0):
    cfdWordsPrevPosTags = corpus.cfdWordsPrevPosTags(th) 
    list = [(cfdWordsPrevPosTags,'cfdWordsPrevPosTags')]   
    serialize(list,folder)
    
def saveCfdWordsPrevPosTags2(corpus,folder,th=0):
    cfdWordsPrevPosTags2 = corpus.cfdWordsPrevPosTags2(th) 
    list = [(cfdWordsPrevPosTags2,'cfdWordsPrevPosTags2')]   
    serialize(list,folder)   
       

def loadSerializedFile(path):
    file = open(path,'rb')
    ans = pickle.load(file)
    file.close()
    return ans

def loadUnknwon_words(folder):
    return loadSerializedFile(folder+'/unknown_words.pickle')

def loadFdPosTags(folder):
    return loadSerializedFile(folder+'/fdPosTags.pickle')

def loadFdPosTags2(folder):
    return loadSerializedFile(folder+'/fdPosTags2.pickle')

def loadFdPosTags3(folder):
    return loadSerializedFile(folder+'/fdPosTags3.pickle')

def loadFdWords(folder):
    return loadSerializedFile(folder+'/fdWords.pickle')

def loadFdWords2(folder):
    return loadSerializedFile(folder+'/fdWords2.pickle')

def loadFdWords3(folder):
    return loadSerializedFile(folder+'/fdWords3.pickle')

def loadCfdWordsNextPosTags(folder):
    return loadSerializedFile(folder+'/cfdWordsNextPosTags.pickle')

def loadCfdWordsNextPosTags2(folder):
    return loadSerializedFile(folder+'/cfdWordsNextPosTags2.pickle')

def loadCfdWordsPrevPosTags(folder):
    return loadSerializedFile(folder+'/cfdWordsPrevPosTags.pickle')

def loadCfdWordsPrevPosTags2(folder):
    return loadSerializedFile(folder+'/cfdWordsPrevPosTags2.pickle')
    




def edits1(word):
    try:
        wordDec = word.decode('cp1255')
    except:
        wordDec = word
    splits     = [(wordDec[:i], wordDec[i:]) for i in range(len(wordDec) + 1)]
    deletes    = [(a + b[1:]) for a, b in splits if b]
    transposes = [(a + b[1] + b[0] + b[2:]) for a, b in splits if len(b)>1]
    replaces   = [(a + c + b[1:]) for a, b in splits for c in alphabet if b]
    inserts    = [(a + c + b)     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def knownEdits1(word,fdWords,th=0):
    list = edits1(word)
    return [w for w in list if fdWords[w]>th]

def knownEdits2(word,fdWords,th=0):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if fdWords[e2]>th)

def editDistance(word,fdWords,th=0):
    if fdWords[word]>th:
        return 0
    e1 = isEdit1(word,fdWords,th)
    if e1==None:
        return 1
    for w in e1:
        e2 = isEdit1(w,fdWords,th)
        if e2==None:
            return 2
    return -1
    
#returns None if the word is edit distance 1 from a word in the lexicon, else returns edits1(word)
def isEdit1(word,lexicon):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    e1 = []
    for a, b in splits:
        if b:
            temp = (a+b[1:])
            if lexicon.checkWord(temp):
                return True
            else:
                e1.append(temp)
    for a, b in splits:
        if len(b)>1:
            temp = (a + b[1] + b[0] + b[2:])
            if lexicon.checkWord(temp):
                return True
            else:
                e1.append(temp)
    for a, b in splits:
        for c in alphabet:
            if b:
                temp = (a + c + b[1:])
                if lexicon.checkWord(temp):
                    return True
                else:
                    e1.append(temp)
    for a, b in splits:
        for c in alphabet:
            if b:
                temp = (a + c + b)
                if lexicon.checkWord(temp):
                    return True
                else:
                    e1.append(temp)
    return False



def wordInSent(word,taggedSent):
    for w,_ in taggedSent:
        if w==word:
            return True
    return False

def findAllSent(corpus,word):
    dWord = word.decode('cp1255')
    ans = []
    for sent in corpus.tagged_sents():
        if wordInSent(dWord,sent):
            ans.append(sent)
    return ans

def perOfWordsWithChar(words,c):
    count = 0
    total = 0.0
    for w in words:
        total+=1
        if c in w:
            count+=1
    return count/total
            
"""*****************************************CODE TESTS*************************************************"""


def testData(corpus,folder,th):
    fdPosTags =  corpus.fdPosTags(th)
    fdPosTags2 = corpus.fdPosTags2(th)
    fdPosTags3 = corpus.fdPosTags3(th)
    print 'fd pos done...'
    fdWords = corpus.fdWords(th)
    fdWords2 = corpus.fdWords(th)
    fdWords3 = corpus.fdWords(th)
    print 'fd words done...'
    cfdWordsNextPosTags = corpus.cfdWordsNextPosTags(th)
    cfdWordsNextPosTags2 = corpus.cfdWordsNextPosTags2(th)
    print 'cfd next done...'
    cfdWordsPrevPosTags =  corpus.cfdWordsPrevPosTags(th)
    cfdWordsPrevPosTags2 = corpus.cfdWordsPrevPosTags2(th)
    print 'loading files...'
    _fdWords = loadFdWords(folder)
    _fdWords2 = loadFdWords2(folder)
    _fdWords3 = loadFdWords3(folder)
    _fdPosTags = loadFdPosTags(folder)
    _fdPosTags2 = loadFdPosTags2(folder)
    _fdPosTags3 = loadFdPosTags3(folder) 
    _cfdWordsNextPosTags = loadCfdWordsNextPosTags(folder)
    _cfdWordsNextPosTags2 = loadCfdWordsNextPosTags2(folder)
    _cfdWordsPrevPosTags = loadCfdWordsPrevPosTags(folder)
    _cfdWordsPrevPosTags2 = loadCfdWordsPrevPosTags2(folder)
    th = 1
    print 'testing fd...'
    print testFd(fdWords,_fdWords,th)
    print testFd(fdWords2,_fdWords2,th)
    print testFd(fdWords3,_fdWords3,th)
    print testFd(fdPosTags,_fdPosTags,th)
    print testFd(fdPosTags2,_fdPosTags2,th)
    print testFd(fdPosTags3,_fdPosTags3,th)
    print 'testing cfd...'
    print testCfd(cfdWordsNextPosTags,_cfdWordsNextPosTags,th)
    print testCfd(cfdWordsNextPosTags2,_cfdWordsNextPosTags2,th)
    print testCfd(cfdWordsPrevPosTags,_cfdWordsPrevPosTags,th)
    print testCfd(cfdWordsPrevPosTags2,_cfdWordsPrevPosTags2,th)
    
def testFd(fd,_fd,th):
    for w in fd.keys():
        if fd[w]>=th and fd[w]!=_fd[w]:
            return False
    return True
        
def testCfd(cfd,_cfd,th):
    for cond in cfd.conditions():
        if not testFd(cfd[cond], _cfd[cond], th):
            return False
    return True    





"""**********************************************EXPERIMENTS**************************************************"""
"""
def test(i):
    testCorpus = BguCorpusReader("../test_tagged","1_tagged.txt")
    fdWords,fdWords2,fdWords3,fdTags,fdTags2,fdTags3 = loadFd()
    cfdWordsNextTags,cfdWordsNextTags2,cfdWordsPrevTags,cfdWordsPrevTags2 = loadCfd()
    testTaggedWordsE = testCorpus.tagged_sents()[i]
    testTaggedWords = testCorpus.tagged_sents()[i+1]
    testWordsE,testTagsE =  testCorpus.getSentWordsPosTags(i)
    testWords2E,testWords3E,testTags2E,testTags3E = computeBiTri(testWordsE,testTagsE)
    testWordsNextTagsE = getWordsNextTags(testTaggedWordsE, fdWords, 0)
    testWordsNextTags2E = getWordsNextTags2(testTaggedWordsE, fdWords, 0)
    testWordsPrevTagsE = getWordsPrevTags(testTaggedWordsE, fdWords, 0)
    testWordsPrevTags2E = getWordsPrevTags2(testTaggedWordsE, fdWords, 0)
    testWords,testTags =  testCorpus.getSentWordsPosTags(i+1)
    testWords2,testWords3,testTags2,testTags3 = computeBiTri(testWords,testTags)
    testWordsNextTags = getWordsNextTags(testTaggedWords, fdWords, 0)
    testWordsNextTags2 = getWordsNextTags2(testTaggedWords, fdWords, 0)
    testWordsPrevTags = getWordsPrevTags(testTaggedWords, fdWords, 0)
    testWordsPrevTags2 = getWordsPrevTags2(testTaggedWords, fdWords, 0)
    print''
    print 'words bigrams:'
    for wE,w in izip(testWords2E,testWords2):
        print '\t'+wE[0]+' '+wE[1]+' : '+str(fdWords2[wE])+'\t\t'+w[0]+' '+w[1]+' : '+str(fdWords2[w])
            
    print''
    print 'words trigrams:'
    for wE,w in izip(testWords3E,testWords3):
        print '\t'+wE[0]+' '+wE[1]+' '+wE[2]+' : '+str(fdWords3[wE])+'\t\t'+w[0]+' '+w[1]+' '+w[2]+' : '+str(fdWords3[w])
            
    print''
    print 'tags bigrams:'
    for wE,w in izip(testTags2E,testTags2):
        print '\t'+wE[0]+' '+wE[1]+' : '+str(fdTags2[wE])+'\t\t'+w[0]+' '+w[1]+' : '+str(fdTags2[w])
        
    print''
    print 'tags trigrams:'
    for wE,w in izip(testTags3E,testTags3):
        print '\t'+wE[0]+' '+wE[1]+' '+wE[2]+' : '+str(fdTags3[wE])+'\t\t'+w[0]+' '+w[1]+' '+w[2]+' : '+str(fdTags3[w])
            
    print''
    print 'words next tags:'
    for wE,w in izip(testWordsNextTagsE,testWordsNextTags):
        print '\t'+wE[0]+' '+wE[1]+' : '+str(cfdWordsNextTags[wE[0]][wE[1]])+'\t\t'+w[0]+' '+w[1]+' : '+str(cfdWordsNextTags[w[0]][w[1]])
            
    print''
    print 'words prev tags:'
    for wE,w in izip(testWordsPrevTagsE,testWordsPrevTags):
        print '\t'+wE[0]+' '+wE[1]+' : '+str(cfdWordsPrevTags[wE[0]][wE[1]])+'\t\t'+w[0]+' '+w[1]+' : '+str(cfdWordsPrevTags[w[0]][w[1]])
        
    print''
    print 'words next tags2:'
    for wE,w in izip(testWordsNextTags2E,testWordsNextTags2):
        print '\t'+wE[0]+' '+wE[1][0]+' '+wE[1][1]+' : '+str(cfdWordsNextTags2[wE[0]][wE[1]])+'\t\t'+w[0]+' '+w[1][0]+' '+w[1][1]+' : '+str(cfdWordsNextTags2[w[0]][w[1]])
            
    print''
    print 'words prev tags2:'
    for wE,w in izip(testWordsPrevTags2E,testWordsPrevTags2):
        print '\t'+wE[0]+' '+wE[1][0]+' '+wE[1][1]+' : '+str(cfdWordsPrevTags2[wE[0]][wE[1]])+'\t\t'+w[0]+' '+w[1][0]+' '+w[1][1]+' : '+str(cfdWordsPrevTags2[w[0]][w[1]])

def test2(testSents,fdS,knownWordTh,errorTh):
    fdWords,fdWords2,fdWords3,fdTags,fdTags2,fdTags3 = loadFd()
    cfdWordsNextTags,cfdWordsNextTags2,cfdWordsPrevTags,cfdWordsPrevTags2 = loadCfd()
    for sent in testSents:
        for i in range(len(sent)):
            if sent[i][0]!='אם':
                break
            currTag = sent[i][1]
            currWord = sent[i][0]
            if i>0:
                prevTag = sent[i-1][1]
                prevWord = sent[i-1][0]
            else:
                prevTag = '*'
                prevWord = '*'
            if i>1:
                prevPrevTag = sent[i-2][1]
                prevPrevWord = sent[i-2][0]
            else:
                prevPrevTag = '*'
                prevPrevWord = '*'
            if i<len(sent)-1:
                nextTag = sent[i+1][1]
                nextWord = sent[i+1][0]
            else:
                nextTag = '*'
                nextWord = '*'
            if i<len(sent)-2:
                nextNextTag = sent[i+2][1]
                nextNextWord = sent[i+2][0]
            else:
                nextNextTag = '*'
                nextNextWord = '*'
            pWordNextWord = max(fdWords2[(currWord,nextWord)],0.4)
            pWordPrevWord = max(fdWords2[(prevWord,currWord)],0.4)
#            pTagNextTag = fdTags2[(currTag,nextTag)] 
#            pTagPrevTag = fdTags2[((prevTag,currTag))]
            pWordNextTag = max(cfdWordsNextTags[currWord][nextTag],0.4)
            pWordPrevTag = max(cfdWordsPrevTags[currWord][prevTag],0.4)
            pWordNextNextTag = max(cfdWordsNextTags2[currWord][(nextTag,nextNextTag)],0.4)
            pWordPrevPrevTag = max(cfdWordsPrevTags2[currWord][(prevPrevTag,prevTag)],0.4)
            
            known = knownEdits1(sent[i][0],fdWords,knownWordTh)
            for _word in known:
                _pWordNextWord = fdWords2[(_word,nextWord)]
                _pWordPrevWord = fdWords2[(prevWord,_word)]
#                _pTagNextTag = fdTags2[(currTag,nextTag)] 
#                _pTagPrevTag = fdTags2[((prevTag,currTag))]
                _pWordNextTag = cfdWordsNextTags[_word][nextTag]
                _pWordPrevTag = cfdWordsPrevTags[_word][prevTag]
                _pWordNextNextTag = cfdWordsNextTags2[_word][(nextTag,nextNextTag)]
                _pWordPrevPrevTag = cfdWordsPrevTags2[_word][(prevPrevTag,prevTag)]
                if _pWordNextTag/pWordNextTag>errorTh or _pWordNextNextTag/pWordNextNextTag>errorTh or _pWordPrevTag/pWordPrevTag>errorTh or _pWordPrevPrevTag/pWordPrevPrevTag>errorTh:
                    printSent(zip(*sent)[0], i, 20)
                    break
                    
                    
                    
                    
def countUnknownInHeadline:
    tb = BguCorpusReader()
    total = 0
    count = 0
    for i in range(36):
        lib = str(i+1)
        for j in range(100):
            try:
                file = str(((i+1)*100)+j)
                print 'file: '+file
                unknownPath = '../text_tagged/'+lib+'/'+file+'_tagged.txt'
                headlinePath = '../text_tagged/'+lib+'/'+file+'_headlineWords.txt'
                unknown_words = tb.unknown_words(unknownPath)
                headline_words_file = open(headlinePath,'r')
                headline_words = headline_words_file.read().split('\n')
                headline_words_file.close()
                for w in unknown_words:
                    total+=1
                    if w in headline_words:
                        count+=1
                print count
            except:
                continue
            
    print 
    print count
    print total
         
                    
                    
"""


"""*************************************************************************************************"""




#haaretz = BguCorpusReader("../haaretz","haaretz.bitmask",'utf-8',"BITMASK")
#save(haaretz,'../serialized/haaretz/')
#
#
#print
#print'======= haaretz done =========='
#print
#
#tb = BguCorpusReader('../text_tagged')
#save(tb,'../serialized/text/')


#import sys
#sys.path.append('C:\Python26\Lib\site-packages\BeautifulSoup-3.2.0')


        
