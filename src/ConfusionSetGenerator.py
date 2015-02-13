#encoding=cp1255
from nltk import FreqDist,ConditionalFreqDist
from DetectErrors import serialize, loadData
from BguCorpusReader import BguCorpusReader

#total sents in walla 1548848
ALPHABET = "פםןוטארקשדגכעיחלךףץתצמנהבסז"
ALEF = 'א'
BET = 'ב'
GIMEL = 'ג'
DALET = 'ד'
HEY = 'ה'
VAV = 'ו'
ZAIN = 'ז'
HET = 'ח'
TET = 'ט'
YOD = 'י'
KAF = 'כ'
LAMED = 'ל'
MEM = 'מ'
NUN = 'נ'
SAMEH = 'ס'
AYIN = 'ע'
PEY = 'פ'
TZADIK = 'צ'
KUF = 'ק'
REISH = 'ר'
SHIN = 'ש'
TAF = 'ת'
PEY_SOFIT = 'ף'
KAF_SOFIT = 'ך'
TZAIDK_SOFIT = 'ץ'
NUN_SOFIT = 'ן'
MEM_SOFIT = 'ם'
KEYBOARD = [[None,None,KUF,REISH,ALEF,TET,VAV,NUN_SOFIT,MEM_SOFIT,PEY],[SHIN,DALET,GIMEL,KAF,AYIN,YOD,HET,LAMED,KAF_SOFIT,PEY_SOFIT],[ZAIN,SAMEH,BET,HEY,NUN,MEM,TZADIK,TAF,TZAIDK_SOFIT,None]]

def printList(list):
    for l in list:
        print l

def createKeyBoardDic():
    dic = {}
    for row in range(len(KEYBOARD)):
        for col in range(len(KEYBOARD[row])):
            if KEYBOARD[row][col]==None:
                continue
            tmp = []
            if col+1<len(KEYBOARD[row]) and KEYBOARD[row][col+1]!=None:
                tmp.append(KEYBOARD[row][col+1])
                
            if col-1>=0 and KEYBOARD[row][col-1]!=None:
                tmp.append(KEYBOARD[row][col-1])
                
            if row+1<len(KEYBOARD) and KEYBOARD[row+1][col]!=None:
                tmp.append(KEYBOARD[row+1][col])
                
            if row-1>=0 and KEYBOARD[row-1][col]!=None:
                tmp.append(KEYBOARD[row-1][col])
                
            if row+1<len(KEYBOARD) and  col-1>=0 and KEYBOARD[row+1][col-1]!=None:
                tmp.append(KEYBOARD[row+1][col-1])
            
            if row-1>=0 and  col+1<len(KEYBOARD[row]) and KEYBOARD[row-1][col+1]!=None:
                tmp.append(KEYBOARD[row-1][col+1])
                
            dic[KEYBOARD[row][col]] = tmp
    return dic

phoneticDic = {ALEF:[AYIN,HEY,VAV],AYIN:[AYIN,HEY],HEY:[AYIN,ALEF],TAF:[TET],TET:[TAF],HET:[KAF,KAF_SOFIT],KAF:[HET],KAF_SOFIT:[HET],SHIN:[SAMEH],SAMEH:[SHIN],VAV:[ALEF]}
for c in ALPHABET:
    if not phoneticDic.has_key(c):
        phoneticDic[c]=[]

keyboardDic = createKeyBoardDic()


def getLexWords(path):
    return open(path,'r').read().split('\n')

def edits1(word):
    return set(edits1WithReplacement)

def edits1_heuristic(word):
    return set(edits1HeuristicWithReplacement)

def edits1WithReplacement(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [(a + b[1:]) for a, b in splits if b]
    transposes = [(a + b[1] + b[0] + b[2:]) for a, b in splits if len(b)>1]
    replaces   = [(a + c + b[1:]) for a, b in splits for c in ALPHABET if b]
    inserts    = [(a + c + b)     for a, b in splits for c in ALPHABET]
    tmp = deletes + transposes + replaces + inserts
    return [w for w in tmp if w!=word]

def edits1HeuristicWithReplacement(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [(a + b[1:]) for a, b in splits if b]
    transposes = [(a + b[1] + b[0] + b[2:]) for a, b in splits if len(b)>1]
    replaces   = []
    for a, b in splits:
        if b:
            lst = []
            if keyboardDic.has_key(b[0]):
                lst+= keyboardDic[b[0]]
            for c in lst:
                replaces.append((a + c + b[1:]))
    inserts = []
    for a, b in splits:
        lst = []
        if b:
            if keyboardDic.has_key(b[0]):
                lst+= keyboardDic[b[0]]
        if a:
            if keyboardDic.has_key(a[-1]):
                lst+= keyboardDic[a[-1]]
        for c in lst:
            inserts.append(a+c+b)
    tmp = deletes + transposes + replaces + inserts
    return [w for w in tmp if w!=word]


def knownEdits1(word,fdWords,th=0):
    list = edits1_heuristic(word)
    return [w for w in list if fdWords[w]>th]



def edits1DicForAllLexWords():
    fdKWords = FreqDist(getLexWords('../lexicons/k_walla_lexicon.txt'))
    fdAllWords = FreqDist(getLexWords('../lexicons/lexicon.txt'))
    edits1DicTmp = {}
    for w in fdKWords.keys():
        tmp = knownEdits1(w,fdAllWords)
        if len(tmp)>0:
            edits1DicTmp[w] = tmp   
    edits1Dic = {}
    for target in edits1DicTmp.keys():
        for w in edits1DicTmp[target]:
            if edits1Dic.has_key(w):
                edits1Dic[w].append(target)
            else:
                edits1Dic[w] = [target]
    return edits1Dic



def exportCfd(corpus,folder='../confusionSet/tbConfWordsProbs/'):
    fdWords = FreqDist(getLexWords('../lexicons/lexicon.txt'))
    tagged_sents = corpus.tagged_sents()
    c_prev1WordNext1Word = [] 
    c_prev2WordNext2Word = [] 
    c_prev2ComplexNext2Complex = [] 
    for s in tagged_sents:
        length = len(s)
        for i in range(len(s)):
            currWord = s[i][0].encode('cp1255')
            if fdWords[currWord]==0:
                continue           
            hasNext2 = False
            hasPrev2 = False
            hasNext1 = False
            hasPrev1 = False
            if i+1<length:
                hasNext1 = True
                nextWord = s[i+1][0]
                nextComplex = s[i+1][1].getPosTag() 
            if i-1>=0:
                hasPrev1 = True
                prevWord = s[i-1][0]
                prevComplex = s[i-1][1].getPosTag()
            if i+2<length:
                hasNext2=True
                next2Complex = s[i+2][1].getPosTag() 
                next2Word = s[i+2][0]
            if i-2>=0:
                hasPrev2 = True
                prev2Complex = s[i-2][1].getPosTag()  
                prev2Word = s[i-2][0]

            if hasPrev1 and hasNext1:
                c_prev1WordNext1Word.append((currWord,prevWord+'#'+nextWord))
            if hasPrev2 and hasNext2:
                c_prev2ComplexNext2Complex.append((currWord,prev2Complex+'#'+prevComplex+'#'+nextComplex+'#'+next2Complex))
                c_prev2WordNext2Word.append((currWord,prev2Word+'#'+prevWord+'#'+nextWord+'#'+next2Word))
             
    cfd_prev1WordNext1Word = ConditionalFreqDist(c_prev1WordNext1Word)
    list = [(cfd_prev1WordNext1Word,"cfd_prev1WordNext1Word")]
    serialize(list,folder)

def importProb(name,folder='../confusionSet/tbConfWordsProbs/'):
    return loadData(folder,name)





# all words with limited edit distance 1 and then context by 1 window words   
def createConfusionSets(confusionSetFolder):
    cfd_prev1WordNext1Word = importProb('cfd_prev1WordNext1Word')
    dic = edits1DicForAllLexWords()
    confusionSets = {}
    for testedWord in dic.keys():
        possibleWords = []
        for w in dic[testedWord]:
            for c in cfd_prev1WordNext1Word[testedWord].keys():
                if cfd_prev1WordNext1Word[w][c]>0:
                    possibleWords.append(w)
                    break  
        possibleWords = set(possibleWords)
        if testedWord in possibleWords:
            possibleWords.remove(testedWord)
        if len(possibleWords)>0:
            confusionSets[testedWord] = possibleWords

    out = open('../confusionSet/'+confusionSetFolder+'/confusionSets.txt','w')
    for k in confusionSets.keys():
        out.write(k+'\n')
        for w in confusionSets[k]:
            out.write(w+'\n')
        out.write('\n')  
    out.close()    
    return confusionSets

def createConfusionSets2(confusionSetFolder):
    kLexWords = getLexWords('../lexicons/10k_walla_lexicon.txt')
    fdKLexWords = FreqDist(kLexWords)
    lexWords = getLexWords('../lexicons/lexicon.txt')
    fdLexWords = FreqDist(lexWords)
    prefs = getLexWords('../linguistic/prefs.txt')
    corpus = BguCorpusReader('d:/yoni/thesis/text/walla/')
    wordsSet = set()
    confusionSets = {}
    for w,t in corpus.tagged_words():
        if fdKLexWords[w]==0 or w!=t.getLemma() or len(w)<3:
            continue
        pos = t.getPosTag()
        if 'NOUN' in pos:
            wordsSet.add(t.getLemma())
    for w in wordsSet:
        lst = []
        for p in prefs:
            if fdLexWords[p+w]>0:
                lst.append(p+w)
        if len(lst)>0:
            confusionSets[w] = lst
    out = open(confusionSetFolder+'confusionSets.txt','w')
    for k in confusionSets.keys():
        out.write(k+'\n')
        for w in confusionSets[k]:
            out.write(w+'\n')
        out.write('\n')  
    out.close()    
    return confusionSets
        
#exportCfd(BguCorpusReader('c:/thesis/text/tb/tagged'))
#createConfusionSets('keyboardPhoneticConfusion')

