# encoding: cp1255
"""
letter level language model
"""
import sys
from operator import itemgetter
import re

class Model:
   pass

class LetterLangModel:
   def __init__(self, min_cnt = 5):
      self.counts = {}
      self.probs  = {}
      self.tot_for_len = {}
      self.min_cnt = min_cnt
      self.total_of_len_1 = 0

   def fromFile(self,filename):
      """
      reads counts and probs from a model file created by getCounts.pl
      """
      min_cnt = self.min_cnt
      for line in file(filename).readlines()[1:]:
         if line.startswith('Err?'): continue
         (ngram,ln,cnt,tot,prob) = line.strip().split(",")
         if ngram.startswith('HA'): continue
         if ln == '1': self.total_of_len_1 += int(cnt)
         if ln == '3':
            try:
               self.counts[ngram[0]+"_"+ngram[2]] += int(cnt)
            except KeyError: self.counts[ngram[0]+"_"+ngram[2]] = int(cnt)
         #if int(cnt) < min_cnt: continue
         self.tot_for_len[int(ln)] = int(tot)
         self.counts[ngram] = int(cnt)
         self.probs[ngram] = float(prob)
      return self

   def get_count(self,ngram):
      #ngram = re.sub("#+","#",ngram)
      try:
         cnt = self.counts[ngram]
         if cnt < self.min_cnt: return 0
         else: return cnt
         return self.counts[ngram]
      except KeyError:
         #print "ERR:",ngram
         return 0
   def get_prob(self,ngram):
      try:
         #if self.probs[ngram] != self.counts[ngram] / self.counts[ngram[:-1]]:
         #   print "E: ",ngram, self.probs[ngram], self.counts[ngram] / self.counts[ngram[:-1]]
         #if len(ngram) == 1:
         #   return self.probs[ngram]
         if len(ngram) == 1:
            return (float(self.get_count(ngram)) / self.total_of_len_1)
         return float(self.get_count(ngram)) / self.get_count(ngram[:-1])
      except KeyError:
         return 0
      except ZeroDivisionError:
         return 0

   def get_tot_for_len(self, len):
      return self.tot_for_len(len)

class PrefixatedLangModel:
   def __init__(self, model):
      self.model = model

   prefixes = ['ו', 'ב', 'ש', 'ה', 'ל', 'מ', 'כ', 'כש', 'וש']

   def get_count(self,ngram):
      ln = len(ngram)
      if ngram == '#': return self.model.get_count('#')
      for p in self.prefixes:

         if ngram.startswith("#%s" % p): #   #Pxy => #xy
            if ln == 2: return self.model.get_count("#")
            else:
               #print "%s --< %s" % (ngram, "#" + ngram[len(p)+1:])
               return self.model.get_count("#" + ngram[len(p)+1:])

         elif ngram.startswith(p): # Pxy => Pxy + #x
            #print "%s --> %s + %s" % (ngram, ngram, '#' + ngram[len(p):-len(p)])
            cnt = self.model.get_count(ngram) + self.model.get_count("#" + ngram[len(p):-len(p)])
            return cnt
      # ngram does not start with prefix
      if ngram.startswith("#"): return 0
      else:
         return self.model.get_count(ngram)

   def get_prob(self, ngram):
      if len(ngram) == 1:
         return self.model.get_prob(ngram) ## TODO make better count here..
      else:
         if self.get_count(ngram) == 0: return 0
         if self.get_count(ngram[:-1]) == 0:
            print "Err:" + ngram[:-1]
            sys.stderr.write("??")
            return 0
         return float(self.get_count(ngram)) / float(self.get_count(ngram[:-1]))

class SuffixatedLangModel:
   def __init__(self, model):
      self.model = model

   suffixes = ['יו', 'ין', 'ים', 'ית', 'יות']

   def get_count(self,ngram):
      ln = len(ngram)
      if ngram == '#': return self.model.get_count('#')
      for p in self.suffixes:

         if ngram.endswith("%s#" % p): #   xyP# => xy#
            if ln == 2: return self.model.get_count("#")  # TODO  what about > 2 ?
            else: return self.model.get_count(ngram[:-len(p)] + "#") # TODO check indexes

         elif ngram.endswith(p): # xyP => xyP + x#
            cnt = self.model.get_count(ngram) + self.model.get_count(ngram[:len(p)] + "#")
            return cnt
      # ngram does not end with prefix
      if ngram.endswith("#"): return 0
      else:
         return self.model.get_count(ngram)

   def get_prob(self, ngram):
      if len(ngram) == 1:
         return self.model.get_prob(ngram) ## TODO make better count here..
      else:
         if self.get_count(ngram) == 0: return 0
         if self.get_count(ngram[:-1]) == 0:
            #print "Err:" + ngram[:-1]
            sys.stderr.write("??")
            return 0
         return float(self.get_count(ngram)) / float(self.get_count(ngram[:-1]))

from math import log
class DunningModel:
   def __init__(self, model):
      self.model = model

   def __getattr__(self, a):
      return getattr(self.model,a)

   def get_prob(self, ngram):
      prob = ((float(self.model.get_count(ngram)) + 1) / (float(self.model.get_count(ngram[:-1])) + 22))
      return prob

class BackDunningModel:
   def __init__(self, model):
      self.model = model

   def __getattr__(self, a):
      return getattr(self.model,a)

   def get_prob(self, ngram):
      prob = ((float(self.model.get_count(ngram)) + 1) / (float(self.model.get_count(ngram[1:])) + 22))
      return prob

class BackwardModel:
   def __init__(self, model):
      self.model = model

   def __getattr__(self, a):
      return getattr(self.model,a)

   def get_prob(self, ngram):
      
      if len(ngram) == 1:
         return self.model.get_prob(ngram)

      try:
         prob = float(self.model.get_count(ngram)) / float(self.model.get_count(ngram[1:]))
      except ZeroDivisionError:
         #print ngram 
         prob = 0
      return prob


def get_ngrams(word,ln):
   #word = "%s%s%s" % ('#' * (ln-1), word, '#' * (ln-1))
   for i in range(0,len(word)-ln+1):
      yield word[i:i+ln]

class Probber:
   """ assigns probablistics to words according to model """
   def __init__(self, model):
      self.model = model
      self.ngram_lens = [1,2,3,4]
      self.word_sep = '#'
      #self.weights = [0.05,0.2,0.3,0.9]
      self.weights = [0.25,0.25,0.25,0.25]
      #self.weights = [0,0.33,0.33,0.34]
   def get_prob(self,word):
      prob = 0
      word = word.replace(self.word_sep,'')
      word = "%s%s%s" % (self.word_sep,word,self.word_sep)
      for ln in self.ngram_lens:
         inner_prob = 1
         for ng in get_ngrams(word,ln):
            inner_prob *= self.model.get_prob(ng)
            #if inner_prob == 0: print "%s -> 0" % ng
         #print "ln %s prob %s\n" % (ln, inner_prob)
         prob += inner_prob * self.weights[ln-1]
      #print "prob of",word,"is:",prob
      return prob

class CombinedProbber:
   """
   a prober that takes two probers and returns the probability based on both
   """
   def __init__(self, p1, p2):
      """ prober_and_weights: ((p1,w1),(p2,w2),...) """
      self.probers_and_weights = [(p1,0.5),(p2,0.5)]

   def get_prob(self,word):
      return sum([prober.get_prob(word) * wgt for (prober,wgt) in self.probers_and_weights])

class DunningProber:
   def __init__(self, model, ngram_len = 5):
      self.model = DunningModel(model)
      self.word_sep = '#'
      self.ngram_len = ngram_len
   def get_prob(self, word):
      prob = 1
      word = word.replace(self.word_sep,'')
      word = "%s%s%s" % (self.word_sep,word,self.word_sep)
      for ng in get_ngrams(word,self.ngram_len):
         prob *= self.model.get_prob(ng)
      return prob

class BackDunningProber:
   def __init__(self, model, ngram_len = 4):
      self.model = BackDunningModel(model)
      self.word_sep = '#'
      self.ngram_len = ngram_len
   def get_prob(self, word):
      prob = 1
      word = word.replace(self.word_sep,'')
      word = "%s%s%s" % (self.word_sep,word,self.word_sep)
      for ng in get_ngrams(word,self.ngram_len):
         prob *= self.model.get_prob(ng)
      return prob

class InnerProbber:
   def __init__(self, model):
      self.model = model
      self.word_sep = '#'
   def get_prob(self, word):
      prob = 1
      word = word.replace(self.word_sep,'')
      word = "%s%s%s" % (self.word_sep,word,self.word_sep)
      for ng in get_ngrams(word,3):
         prob *= (float(self.model.get_count(ng) + 1) / float(self.model.get_count(ng[0]+"_"+ng[2])+22))
      return prob

class IbmEntropyProbber:
   def __init__(self, model):
      self.model = model
      self.word_sep = '#'
   def get_prob(self, word):
      prob = 0
      word = word.replace(self.word_sep,'')
      word = "%s%s%s" % (self.word_sep,word,self.word_sep)
      for ng in get_ngrams(word,3):
         p = self.model.get_prob(ng)
         #print p, prob
         if p != 0:
            prob += p*(-log(p,2))
      return prob

def preproc(word):
   word = word.strip()
   word = word.replace("#",'')
   word = word.replace("ן","נ").replace("ם","מ").replace("ך","כ").replace("ף","פ").replace("ץ","צ")
   word = word.replace("ג'","J").replace("ז'","Z").replace("צ'","C")
   word = word.replace("-","#").replace(" ","#") # todo -- regex replace /[- ]+//
   return word

def postproc(word):
   word = word.replace("J,","ג'").replace("Z","ז'").replace("C","צ'")
   word = word.replace("#"," ")
   return word


class Decider:
   """
   Decide between several models
   """
   def __init__(self, prober_dict, pprobs = {}):
      """
      prober_dict: a dictionary of {'prober_name': prober}
      """
      self.prober_dict = prober_dict
      self.prior_probs = pprobs

   def decide__(self, word):
      w = preproc(word)
      maxn = 0
      best_name = 'UN'
      for (name, prober) in self.prober_dict.iteritems():
         p = prober.get_prob(w)
         if p > maxn:
            best_name = name
            maxn = p
      return best_name

   def decide(self, word):
      s = self.sorted_with_probs(word)
      return s[0][0]

   def sort_classes(self, word):
      w = preproc(word)
      lst = []
      for (name, prober) in self.prober_dict.iteritems():
         lst.append((name, prober.get_prob(w)))
      return [x[0] for x in sorted(lst, key=itemgetter(1), reverse=True)]

   def top_n(self, word, n):
      n = min(len(self.prober_dict.keys()), n)
      return self.sort_classes(word)[:n]

   def sorted_with_probs(self, word):
      w = preproc(word)
      names = []
      probs = []
      for (name, prober) in self.prober_dict.iteritems():
         names.append(name)
         try:
            prior_prob = self.prior_probs[name]
         except KeyError:
            prior_prob = 1
         probs.append(prober.get_prob(w)  * prior_prob)

      # normalize probs
      s = float(sum(probs))
      if s == 0: s = 1
      probs = [p/s for p in probs]
      return sorted(zip(names, probs), key=itemgetter(1), reverse = True)

class EnHebPrefDecider:
   """
   Decide between English, Hebrew, And Prefixated hebrew
   """
   def __init__(self, en_prober, heb_prober, pref_stats_file):
      """
      pref_stats_file generated by "make_prefix_stats.py"
      includes: prefix,mean diff,stddev diff,mean+stddev
      """
      self.eng = en_prober
      self.heb = heb_prober
      self.pref_deltas = self.read_deltas(pref_stats_file)
      self.prefixes = self.pref_deltas.keys()

   def read_deltas(self, filename):
      deltas = {}
      for l in file(filename):
         t = l.strip().split(",")
         deltas[t[0]] = float(t[-1])
      return deltas

   def decide(self, word):
      w = preproc(word)
      enprob = self.eng.get_prob(w)
      heprob = self.heb.get_prob(w)
      if heprob == enprob == 0: return 'UNK'
      ep = enprob / (heprob + enprob)
      hp = heprob / (heprob + enprob)

      d1 = hp - ep

      if d1 < 0: return 'EN'
      #if d1 < -0.77: return 'EN'

      for p in self.prefixes:
         if word.startswith(p):
            d2 = self.heb.get_prob(preproc(word[len(p):])) - self.eng.get_prob(preproc(word[len(p):]))
            if d2 < 0 and d1 - d2 > self.pref_deltas[p]:
               return 'EN'  # TODO NOTE: בנקינג turned out to be P_EN, check how we can fight that

      return 'HE'

class EnHebSufDecider:
   """
   Decide between English, Hebrew, And Suffixated hebrew
   """
   def __init__(self, en_prober, heb_prober, suf_stats_file = None):
      """
      suf_stats_file generated by "make_suffix_stats.py"
      includes: suffix,mean diff,stddev diff,mean+stddev
      """
      self.eng = en_prober
      self.heb = heb_prober
      #self.suf_deltas = self.read_deltas(suf_stats_file)
      #self.suffixes = self.suf_deltas.keys()
      self.suffixes = ['ים', 'ות', 'יות', 'ימ','ית']

   def read_deltas(self, filename):
      deltas = {}
      for l in file(filename):
         t = l.strip().split(",")
         deltas[t[0]] = float(t[-1])
      return deltas

   def decide(self, word):
      w = preproc(word)
      enprob = self.eng.get_prob(w)
      heprob = self.heb.get_prob(w)
      if heprob == enprob == 0: return 'UNK'
      # normalize
      ep = enprob / (heprob + enprob)
      hp = heprob / (heprob + enprob)

      d1 = hp - ep

      if d1 < 0:
         # word identified as english. Is it a neologism (english with heb suffix?)
         # if it has a possible hebrew suffix:
         for s in self.suffixes:
            if word.endswith(s):
               # check if it's a neologism, or part of the english word
               return 'S_EN_1' # TODO -- actualy check..
               return 'EN_NEO?' # TODO -- actualy check..
         # if we are here, there is no hebrew suffix -- the word is english
         return 'EN'
      else:
         # word identified as hebrew.
         # Is it just because of a suffix bias?
         # if it has a possible hebrew suffix:
         for s in self.suffixes:
            if word.endswith(s):
               # try dropping the suffix and check if we are more english
               d2 = self.heb.get_prob(preproc(word[:-len(s)])) - self.eng.get_prob(preproc(word[:-len(s)]))
               if d2 > 0:
                  # we are still hebrew..
                  return 'S_HE'
                  return 'HE'
               else:
                  if False and d1 - d2 > self.suf_deltas[s]:
                     # we are much more english
                     return 'EN_NEO'
                  else:
                     # er are a little more english..
                     return 'S_EN_2'
                     return 'EN_NEO'

         # if we got here we are indeed hebrew (no suffixes, so no excuse)
         return 'HE'

class RankOrderProfile:
   def __init__(self, filename):
      self.profile = [s.strip() for s in file(filename).readlines()]
   def get_rank_order(self, w):
      sum = 0
      for ln in range(1,5):
         ngrams = get_ngrams(w,ln)
         counts = {}
         for ngram in ngrams:
            try:
               counts[ngram]+=1
            except:
               counts[ngram]=1
         ngrams = map(itemgetter(0),sorted(counts.iteritems(), reverse=True, key=itemgetter(1)))
         for (i,ngram) in enumerate(ngrams):
            try:
               sum += abs(self.profile.index(ngram) - i)
            except ValueError:
               sum += abs(400 - i)
      return sum


class RankorderDecider:
   def __init__(self,pdict):
      self.pdict = pdict
   def decide(self, word):
      w = preproc(word)
      results = [(name,prof.get_rank_order(w)) for (name, prof) in self.pdict.iteritems()]
      return sorted(results, key=itemgetter(1))[0][0]

class IbmDecider(Decider):
   """
   If above avg_entropy - min_entropy of hebrew corpus, it's english, else it's hebrew
   REALLY LOUSY RESULTS.
   Entropy is calculated by IbmEntropyProbber
      enthebmodel = IbmEntropyProbber(LetterLangModel().fromFile('by2-cp1255-model'))
      decider = IbmDecider(enthebmodel)
   """
   def __init__(self, probber):
      """
      prober_dict: a dictionary of {'prober_name': prober}
      """
      self.prober = probber

   def decide(self, word):
      w = preproc(word)
      if self.prober.get_prob(word) > 1.77: return 'ENG'
      else: return 'HEB'

   def sort_classes(self, word):
      return None

if __name__ == '__main__':

   hebmodel = Probber(LetterLangModel(5).fromFile('by2-cp1255.model'))
   #hebmodel = Probber(LetterLangModel(5).fromFile('byTop.model'))
   #byprunedmodel = Probber(LetterLangModel().fromFile('by.pruned.model'))
   #a7hebmodel = Probber(LetterLangModel().fromFile('a7-cp1255.model'))
   engmodel = Probber(LetterLangModel(5).fromFile('brownheb_tsk.model'))
   #engmodel = Probber(LetterLangModel().fromFile('brn_tsk_gj.model'))
   namesmodel = Probber(LetterLangModel(5).fromFile('hebeng_names_2.model'))
   #rusmodel = Probber(LetterLangModel(5).fromFile('hebrus_rus_names.model'))
   #rusmodel_fixback = Probber(LetterLangModel(5).fromFile('hebrus_rus.model'))
   #aramaicmodel = Probber(LetterLangModel(5).fromFile('aramic.model'))
   #namesmodel = Probber(LetterLangModel().fromFile('brn_tsk_gj_names.model'))
   #njjvbgmodel = Probber(LetterLangModel().fromFile('brn_eng_n_j_vbg.model'))

   heb  = CombinedProbber(hebmodel, Probber(BackwardModel(hebmodel.model)))
   eng  = CombinedProbber(engmodel, Probber(BackwardModel(engmodel.model)))
   name = CombinedProbber(namesmodel, Probber(BackwardModel(namesmodel.model)))
   #rus = CombinedProbber(rusmodel, Probber(BackwardModel(rusmodel.model)))
   #rus_fix = CombinedProbber(rusmodel_fixback, Probber(BackwardModel(rusmodel_fixback.model)))
   #aram = CombinedProbber(aramaicmodel, Probber(BackwardModel(aramaicmodel.model)))
   #eng2 = CombinedProbber(njjvbgmodel, Probber(BackwardModel(njjvbgmodel.model)))
   #hebpr  = CombinedProbber(byprunedmodel, Probber(BackwardModel(byprunedmodel.model)))
   #eng3 = CombinedProbber(engmodel_3, Probber(BackwardModel(engmodel_3.model)))
   #name3 = CombinedProbber(namesmodel_3, Probber(BackwardModel(namesmodel_3.model)))

   #prefNameModel = Probber(PrefixatedLangModel(namesmodel.model))
   #prefEngmodel = Probber(PrefixatedLangModel(engmodel.model))
   #prefHebmodel = Probber(PrefixatedLangModel(hebmodel.model))

   #prefEngmodel = Probber(LetterLangModel().fromFile('brn_hebeng_pref.model'))

   #i_hebmodel = InnerProbber(LetterLangModel().fromFile('by2-cp1255.model'))
   #i_a7hebmodel = InnerProbber(LetterLangModel().fromFile('a7_model'))
   #i_engmodel = InnerProbber(LetterLangModel().fromFile('brownheb_tsk.model'))
   #i_namesmodel = InnerProbber(LetterLangModel().fromFile('hebeng_names_2.model'))

   dun_hebmodel = DunningProber(hebmodel.model,3)
   dun_engmodel = DunningProber(engmodel.model,3)
   dun_hebback = CombinedProbber(dun_hebmodel, BackDunningProber(hebmodel.model,3))
   dun_engback = CombinedProbber(dun_engmodel, BackDunningProber(engmodel.model,3))
   #namesmodel = DunningProber(LetterLangModel().fromFile('hebeng_names.model'))
   #prefEngmodel = DunningProber(PrefixatedLangModel(engmodel.model))
   #prefHebmodel = DunningProber(PrefixatedLangModel(hebmodel.model))
   #prefNameModel = DunningProber(PrefixatedLangModel(namesmodel.model))

   #suffEng = Probber(SuffixatedLangModel(engmodel.model))
   #suffHeb = Probber(SuffixatedLangModel(hebmodel.model))

   #pdict = {'HEB':hebmodel , 'ENG':engmodel, '(ENG)NAME':namesmodel, 'PREF_ENG': prefEngmodel, 'PREF_HEB': prefHebmodel,
   #         'PREF_(ENG)NAME': prefNameModel, 'SUF_ENG':suffEng, 'SUF_HEB':suffHeb}
   #pdict = {'HEB':hebmodel , 'ENG':engmodel, '(ENG)NAME':namesmodel}
   #pdict = {'HEB':i_hebmodel ,  'ENG':i_engmodel, 'EN_NAME':i_namesmodel }

   pdict_noback = {
      'HEB_BY':hebmodel,
      #'HEB_A7':a7hebmodel,
      'ENG':engmodel,
      'EN_NAME':namesmodel,
      #'PR_ENG':prefEngmodel,
      #,'PR_NAME':prefNameModel
      }
   pdict_noback_noname = {
      'HEB_BY':hebmodel,
      'ENG':engmodel,
      }
   pdict_noname = {
      'HEB':heb,
      'ENG':eng,
      }

   pdict = {
      'HEB':heb,
      #'HEB_A7':a7hebmodel,
      'ENG':eng,
      #'ENG_2':eng2,
      'EN_NAME':name,
      #'EN_RUS':rus,
      #'HEB_':rus_fix,
      #'ARAMAIC':aram,
      #'PR_ENG':prefEngmodel,
      #,'PR_NAME':prefNameModel
      }
   pprobs = { 'HEB':1, 'ENG':1, 'EN_NAME':1 }
   #pdict_2 = {
   #   'HEB':heb,
      #'HEB_A7':a7hebmodel,
   #   'ENG':eng3,
      #'ENG_2':eng2,
   #   'EN_NAME':name3,
      #'PR_ENG':prefEngmodel,
      #,'PR_NAME':prefNameModel
   #   }


   #ehp = EnHebPrefDecider(engmodel,hebmodel, "pref_stats.csv")
   #ehp = EnHebPrefDecider(eng,heb, "pref_stats.csv")
   #ehs = EnHebSufDecider(eng,heb, "pref_stats.csv")
   #decider = ehs
   #decider = RankorderDecider({'HEB':RankOrderProfile('heb_profile.txt'), 'ENG':RankOrderProfile('eng_profile.txt')})
   decider = Decider({'DN_HEB':dun_hebmodel,'DN_ENG':dun_engmodel})
   #decider = Decider({'DN_HEB':dun_hebback,'DN_ENG':dun_engback})
   decider = Decider(pdict_noback_noname)
   decider = Decider(pdict_noname)
   decider = Decider(pdict,pprobs)
   #decider = Decider({'HE':i_hebmodel,'EN':i_engmodel}) #,'EN_NAME':i_namesmodel})
   #decider = ehp

