'''
Created on Nov 23, 2010

@author: Yoni Lev
'''

from BeautifulSoup import BeautifulStoneSoup
from nltk import FreqDist
from ErrorCorpusReader import ErrorCorpusReader


def getTagset(path):
    file = open(path, 'r')
    fileStr = file.read()
    soup = BeautifulStoneSoup(fileStr)
    tagsAsNode = soup.findAll('tag')
    tags = [tag["symbol"].lower() for tag in tagsAsNode]
    file.close()
    return list(set(tags))

#tagset = getTagset('../tagset/TB_Poject.tagset')
#mainCategoryTags = ["err","inf","msw","not","orw","oth","pun","rdw","spl","sww","typ"]

def fdOfTags(corpus):
    return FreqDist([tag for _,tag,_ in corpus.tagged_words() if '$cont' not in tag])

def fdOfTagsWithoutOk(corpus):
    return FreqDist([tag for _,tag,_ in corpus.tagged_words() if (('$cont' not in tag) and ('ok' not in tag))])

def calPrA(corpus1,corpus2):
    taggedWords1 = corpus1.tagged_words()
    taggedWords2 = corpus2.tagged_words()
    i1=0
    i2=0
    correct = 0
    while i1<len(taggedWords1) and i2<len(taggedWords2):
        if (taggedWords1[i1][1]==taggedWords2[i2][1]):
            correct+=1
        #if there is a missing word/punc tag, needs to count extra index
        if taggedWords1[i1][0]=='' and taggedWords2[i2][0]!='':
            i1+=1
        else :
            if taggedWords1[i1][0]!='' and taggedWords2[i2][0]=='':
                i2+=1
            else:
                i1+=1
                i2+=1   
    return float(correct)/len(taggedWords1)

def calPrAWithoutOk(corpus1,corpus2):
    taggedWords1 = corpus1.tagged_words()
    taggedWords2 = corpus2.tagged_words()
    correct = 0
    total1 = 0
    total2 = 0
    i1=0
    i2=0
    while i1<len(taggedWords1) and i2<len(taggedWords2):
        if taggedWords1[i1][1]!='ok':
            total1+=1
        if taggedWords2[i2][1]!='ok':
            total2+=1 
        if (taggedWords1[i1][1]==taggedWords2[i2][1] and taggedWords1[i1][1]!='ok'):
            correct+=1
        if taggedWords1[i1][0]=='' and taggedWords2[i2][0]!='':
            i1+=1
        else :
            if taggedWords1[i1][0]!='' and taggedWords2[i2][0]=='':
                i2+=1
            else:
                i1+=1
                i2+=1
    return float(correct)/min(total1,total2)

def calPrAClassifyErrors(corpus1, corpus2):
    taggedWords1 = corpus1.tagged_words()
    taggedWords2 = corpus2.tagged_words()
    i1=0
    i2=0
    correct = 0
    while i1<len(taggedWords1) and i2<len(taggedWords2):
        #count everything that was tagged (no matter how) in both corpuses
        if (taggedWords1[i1][1]==taggedWords2[i2][1] or (taggedWords1[i1][1]!='ok' and taggedWords2[i2][1]!='ok')):
            correct+=1
        #if there is a missing word/punc tag, needs to count extra index
        if taggedWords1[i1][0]=='' and taggedWords2[i2][0]!='':
            i1+=1
        else :
            if taggedWords1[i1][0]!='' and taggedWords2[i2][0]=='':
                i2+=1
            else:
                i1+=1
                i2+=1   
    return float(correct)/len(taggedWords1)

def calPrE(corpus1,corpus2): 
    sumProb = 0
    fdOfTags1 = fdOfTags(corpus1)
    fdOfTags2 = fdOfTags(corpus2)
    tags = list(set(fdOfTags1.keys()+fdOfTags2.keys()))
    for tag in tags:
        sumProb+= fdOfTags1.freq(tag)*fdOfTags2.freq(tag)
    return sumProb

def calPrEWithoutOk(corpus1,corpus2):
    sumProb = 0
    fdOfTags1 = fdOfTagsWithoutOk(corpus1)
    fdOfTags2 = fdOfTagsWithoutOk(corpus2)
    tags = list(set(fdOfTags1.keys()+fdOfTags2.keys()))
    for tag in tags:
        sumProb+= fdOfTags1.freq(tag)*fdOfTags2.freq(tag)
    return sumProb

def calPrEClassifyErrors(corpus1, corpus2):
    sumProb = 0
    fdOfTags1 = fdOfTags(corpus1)
    fdOfTags2 = fdOfTags(corpus2)
    sumProb += fdOfTags1.freq('ok')*fdOfTags2.freq('ok')
    sumProb += (1-fdOfTags1.freq('ok'))*(1-fdOfTags2.freq('ok'))
    return sumProb

def calKappa(corpus1,corpus2,type="regular"):
    if type=="regular":
        prE = calPrE(corpus1, corpus2)
        prA = calPrA(corpus1, corpus2)
    if type=="withOutOk":
        prE = calPrEWithoutOk(corpus1, corpus2)
        prA = calPrAWithoutOk(corpus1, corpus2)
    if type=="classifyError":
        prE = calPrEClassifyErrors(corpus1, corpus2)
        prA = calPrAClassifyErrors(corpus1, corpus2)
    return (prA-prE)/(1-prE)
    
        



corpus1 = ErrorCorpusReader("tagged1")
corpus2 = ErrorCorpusReader("tagged2")

print 'Pr(A) = '+str(calPrA(corpus1, corpus2))
print 'Pr(E) = '+str(calPrE(corpus1, corpus2))
print 'Kappa = '+str(calKappa(corpus1, corpus2))
print 
print "Pr(A) without 'ok' = "+str(calPrAWithoutOk(corpus1, corpus2))
print "Pr(E) without 'ok' = "+str(calPrEWithoutOk(corpus1, corpus2))
print "Kappa without 'ok' = "+str(calKappa(corpus1, corpus2,"withOutOk"))
print 
print "Pr(A) classify errors = "+str(calPrAClassifyErrors(corpus1, corpus2))
print "Pr(E) classify errors = "+str(calPrEClassifyErrors(corpus1, corpus2))
print "Kappa classify errors = "+str(calKappa(corpus1, corpus2,"classifyError"))
