#encoding=cp1255
import re
from codecs import open
from nltk import FreqDist

class Lexicon():
    def __init__(self,version='11'):
        self.ruleDic = {}
        self.typeDic = {}
        blocks = open('../lexicons/hspell'+version+'.aff','r').read().split('\n\n')
        for block in blocks:
            lines = block.split('\n')
            type = lines[0].split(' ')[1]
            self.ruleDic[type] = []
            for l in lines[1:]:
                _,type,_,_,_,add,rule = l.split(' ')
                if '"' in add:
                    continue
                self.ruleDic[type].append((add,rule))
            
        lines = open('../lexicons/hspell'+version+'.dic','r').read().split('\n')
        for line in lines:
            word,type = line.split('/')
            self.typeDic[word] = type
        lines = None


    def checkWord(self,word):
        for i in range(len(word)):
            prefix = word[:i]
            rest = word[i:]
            if self.typeDic.has_key(rest):
                if prefix=="":
                    return True
                listOfRules = self.ruleDic[self.typeDic[rest]]
                for add,rule in listOfRules:
                    if re.match(rule, rest) and (add+rest==word):
                        return True
        return False

def totalWordsWithLexiconToFiles():
    j=0
    wordsDic = {}
    fileDic = {}
    lex = Lexicon('1.0')
    alphabet = """פםןוטארק'"ףךלחיעכגדשץתצמנהבסז"""
    i=0
    for c1 in alphabet:
        for c2 in alphabet:
            i+=1
            fileDic[c1+c2]=str(i)
    for word in lex.typeDic.keys():
        j+=1
        if wordsDic.has_key(word[:2]):
            wordsDic[word[:2]].append(word)
        else:
            wordsDic[word[:2]]=[word]
        type = lex.typeDic[word]
        listOfRules = lex.ruleDic[type]
        for add,rule in listOfRules:
                if re.match(rule, word):
                    toWrite = add+word
                    if wordsDic.has_key(toWrite[:2]):
                        wordsDic[toWrite[:2]].append(toWrite)
                    else:
                        wordsDic[toWrite[:2]]=[toWrite]
        if j%10000==0:
            for k in wordsDic:
                file = open('../tmp/'+fileDic[k]+'.txt','a')
                for w in wordsDic[k]:
                    file.write(w+'\n')
                file.close()
                wordsDic[k] = []
        if j==328995:
            for k in wordsDic:
                file = open('../tmp/'+fileDic[k]+'.txt','a')
                for w in wordsDic[k]:
                    file.write(w+'\n')
                file.close()
                wordsDic[k] = []
 
def totalWordsWithLexiconFromFiles(): 
    total = 0
    count = 0
    for i in range(850):
        try:
            file = open('../tmp/'+str(i)+".txt",'r')
            words = file.read()[:-1].split('\n')
            total+=len(words)
            fd = FreqDist(words)
            count+=len(fd.keys())
            file.close()
            print count
        except:
            continue
    print 'total unique words: '+str(count)  
    print 'total words: '+str(total)  
    

   
#    
#lex11 = Lexicon("11")
#print lex11.checkWord('בדרוג')