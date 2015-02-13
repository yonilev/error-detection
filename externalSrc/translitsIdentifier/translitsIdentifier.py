# encoding: cp1255


"""
This is a class for classifying transliterations in the medical domain

"""

from codecs import open

from langmod import *
import os
import re

def levenshtein(s, t):
    m, n = len(s), len(t)
    d = [range(n+1)]
    d += [[i] for i in range(1,m+1)]
    for i in range(0,m):
        for j in range(0,n):
            cost = 1
            if s[i] == t[j]: cost = 0
            d[i+1].append( min(d[i][j+1]+1, # deletion
                              d[i+1][j]+1, #insertion
                              d[i][j]+cost) #substitution
                         )
    return d[m][n]



def getStem(word,morphList,tags2letters):
    stem = "NA"
    if len(morphList[0]) > 0:
        try:
            for prefix in tags2letters[morphList[0]].split("|".encode("cp1255")):
                if word[0:len(prefix)] == prefix:
                    stem = word[len(prefix):]
        except:
            
            #print "ERROR",word,morphList[0]
            return "NA"
            print morphList[0] + "\t" + word + tags2letters[morphList[0]]
    if not stem == "NA":
        word = stem
    if len(morphList[2]) > 0:
        try:
            for postfix in tags2letters[morphList[2]].split("|".encode("cp1255")):

                    if word[-len(postfix):] == postfix:
                        stem = word[0:-len(postfix)]
                        #fix removing last letter when result is illegal
                        suffixes = ['נ', 'פ', 'מ', 'צ']
                        for s in suffixes:
                            if stem.endswith(s):
                                stem = word
        except:
            print word
            #print morphList[2] + "\t" + word + "\t" + tags2letters[morphList[2]]
    return stem

def readTagsToLetters(file = r'../externalSrc/translitsIdentifier/tags'):
    fid = open(file,"rb","cp1255")
    table = {}
    for line in fid:
        line = line.rstrip()
        tmp = line.split("\t")
        table[tmp[0]] = tmp[1]
    return table


def cleanUTFHeb(data):
    data = data.encode("cp1255")
    data = data.replace(",".encode("cp1255"), " ")
    data = data.replace("-".encode("cp1255"), " ")
    data = data.replace((r".").encode("cp1255"), " ")
    data = data.replace("?".encode("cp1255"), " ")
    data = data.replace(")".encode("cp1255"), " ")
    data = data.replace("(".encode("cp1255"), " ")
    data = data.replace("\n".encode("cp1255"), " ")
    data = data.replace('"'.encode("cp1255"), " ")
    data = data.replace("'".encode("cp1255"), " ")
    data = data.replace(":".encode("cp1255"), " ")
    data = data.replace("\%".encode("cp1255"), " ")
    data = data.replace("\!".encode("cp1255"), " ")
    data = data.replace("/".encode("cp1255"), " ")
    return data


def checkDict(word,dict):
    if word == "NA":
        return False
    if word in dict:
        return True
    wordList = removeKtivMale(word)
    for w in wordList:
        if w in dict:
            return True
    return False

def checkDict2(word,dict):
    if word == "NA":
        return False,""
    if word in dict:
        return True,word
    wordList = removeKtivMale(word)
    for w in wordList:
        if w in dict:
            return True,w
    return False,""

def removeKtivMale(word):
    myStrs = removeKfolot(word,"יי")
    if len(myStrs) > 0:
        hasWord = myStrs[0]
        myStrs += removeKfolot(hasWord,"וו")
    myStrs += removeKfolot(word,"וו")

    myStrs = set(myStrs)
    return myStrs

def removeKfolot(word,kfola):
    i = word.find(kfola,0);
    if i >= 0 and i < len(word)-1:
        nword = []
        nword.append(word[0:i]+word[i+1:])
        return nword
    return []


class transClassifier:
    def __init__(self,prior_prob_of_heb = 0.1,foreignModel = '../externalSrc/translitsIdentifier/drug.model',namesModel = '../externalSrc/translitsIdentifier/names.model',toStem = True,lengthRule = 100):
        
        self.HSPELL_WORDS = set([w.strip() for w in open(r'../externalSrc/translitsIdentifier/hspell_words.txt',"r","cp1255")])
        hebmodel = Probber(LetterLangModel(5).fromFile('../externalSrc/translitsIdentifier/by2-cp1255.model'))
        medmodel = Probber(LetterLangModel(5).fromFile(foreignModel))
        namesmodel = Probber(LetterLangModel(5).fromFile(namesModel))
        heb  = CombinedProbber(hebmodel, Probber(BackwardModel(hebmodel.model)))
        med  = CombinedProbber(medmodel, Probber(BackwardModel(medmodel.model)))
        name = CombinedProbber(namesmodel, Probber(BackwardModel(namesmodel.model)))

        self.tags2letters = readTagsToLetters();
        pdict1 = {
              'HEB':heb,
              'FOR':med,
              'NAM':name,
              }
        pprobs1 = { 'HEB':prior_prob_of_heb, 'FOR':1,'NAM':1}
        self.decider = Decider(pdict1,pprobs1)#Decider(pdict2,pprobs2)

    def classify(self,word,wordTag, baseForm = "AAAAA",memoizationTable = {}):
        #print word
        if checkDict(baseForm,self.HSPELL_WORDS):
            print 'here'
            return "HEB"
        if word+wordTag in memoizationTable:
            return memoizationTable[word+wordTag]
        morphList = wordTag.split(":")
        #print morphList
        stem = getStem(word, morphList,self.tags2letters)
        stemDecision = "NA"
        wordDecision = "HEB"
        if len(word) > 2:
            wordDecision = self.decider.decide(word)
            if wordDecision == "HEB" and len(word) > 9:
                wordDecision = "FOR"#decider1.decide(word)

            if checkDict(word,self.HSPELL_WORDS) or checkDict(stem,self.HSPELL_WORDS):
                wordDecision = "HEB"
                stemDecision = "HEB"

        if len(stem) > 2 and (not stem == word) and (not stemDecision == "HEB"):
            stemDecision = self.decider.decide(stem)
            if stemDecision == "HEB" and len(stem) > 8:
                stemDecision = "FOR"#decider1.decide(stem)
            #prefering the stem decision
            wordDecision = stemDecision
            if stem in self.HSPELL_WORDS:
                stemDecision = "HEB"
                wordDecision = "HEB"
        if not wordDecision == "HEB":
            wordDecision = "FOR"
        memoizationTable[word+wordTag] = wordDecision
        #if morphList[1][0:4]=="VERB":
        #    wordDecision = "HEB"
        return wordDecision


    def getStem(self,word,wordTag):
        morphList = wordTag.split(":")
        #print morphList
        stem = getStem(word, morphList,self.tags2letters)
        return stem
    

    

if __name__ == '__main__':
    myClassifier = transClassifier(prior_prob_of_heb = 0.1)
    print myClassifier.classify("בדפלפט",":PROPERNAME:")
    print myClassifier.classify("הסעיפים","DEF:NOUN-M,P,ABS:")
    print myClassifier.classify("למשפט","PREPOSITION+DEF:NOUN-M,S,ABS:")
    print myClassifier.classify("כיפיוניים",":NOUN-F,P,ABS:")
    print myClassifier.classify("הטגרטול","DEF:PROPERNAME:")
    print myClassifier.classify("בעתתיד","PREPOSITION:ADJECTIVE-M,S,CONST:")
    print myClassifier.classify("דיימון","DEF:PROPERNAME:")
    print myClassifier.classify("רונאלדו",":PROPERNAME:")
    print myClassifier.classify("נדאל",":PROPERNAME:")
