# Copyright (c) 2009 Leif Johnson <leif@leifjohnson.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''A basic one-vs-all multiclass Voted Perceptron algorithm.'''

import logging
from collections import defaultdict


class VotedPerceptron(object):
    '''The Voted Perceptron is a fast wide-margin classifier.

    This implementation is completely sparse ; that is, both labels and weights
    for those labels are maintained using dictionaries. All dot products are
    calculated by summing the nonzero feature weights for a set of features.
    New labels are introduced by calling train() ; such labels will start out
    with an empty set of feature weights.
    '''

    def __init__(self, feature_beam=5000):
        '''Create a new Voted Perceptron.

        feature_beam: The maximum number of weights to retain in each class.
        '''
        self._local = {}
        self._global = {}
        self._survived = 0
        self._iterations = 0
        self._feature_beam = feature_beam

    def train(self, features, correct):
        '''Present a labeled feature set to the perceptron for learning.

        features: A set of features for classification.
        correct: The correct label for the given features.
        '''
        if correct not in self._local:
            self._local[correct] = defaultdict(int)
            self._global[correct] = defaultdict(int)

        self._iterations += 1
        predicted, _ = self._max_label_score(features, self._local)
        if predicted == correct:
            self._survived += 1
            return True

        if self._survived > 0:
            self._update_global(predicted)
            self._update_global(correct)
            self._survived = 0
        self._update_local(predicted, features, -1)
        self._update_local(correct, features, 1)
        return False

    def score(self, features):
        '''Get a score for a feature set.

        features: A set of features for a scoring decision.

        Return a (label, score) pair.
        '''
        label, score = self._max_label_score(features, self._global)
        return label, float(score) / self._iterations

    def top_features(self, num_features):
        '''Iterate over the top features for all classes.

        num_features: The number of features to return for each class.
        '''
        for label, fws in self._global.iteritems():
            ordered = sorted(fws.iteritems(), key=lambda x: -abs(x[1]))
            yield label, [(f, float(w) / self._iterations)
                          for f, w in ordered[:num_features]]

    def _max_label_score(self, features, weights):
        '''Get the maximal class and sum of the weights for a feature vector.

        features: A set of feature pairs.
        weights: A map from labels to weights.

        Returns a (label, score) pair where the score is the greatest out of all
        scores for all labels.
        '''
        max_label = None
        max_score = -1e100
        second_score = 0
        for label, fws in weights.iteritems():
            score = sum(fws.get(f, 0) for f in features)
            logging.debug('score for %s = %.2f (%d weights)',
                          label, score, len(fws))
            if score > max_score:
                max_label = label
                max_score = score
            else:
                if score>second_score:
                    second_score = score
        
        return max_label, abs(float(max_score)-second_score)

    def _update_global(self, label):
        '''Merge the local weight set with the global set for a class.'''
        g = self._global[label]
        for f, w in self._local[label].iteritems():
            g[f] += self._survived * w
        self._prune(g)

    def _update_local(self, label, features, delta):
        '''Update the local weights for an class based on a set of features.'''
        w = self._local[label]
        for f in features:
            w[f] += delta
        self._prune(w)

    def _prune(self, weights):
        '''Retain only the top feature_beam feature weights.'''
        if len(weights) < 1.5 * self._feature_beam:
            return
        fws = sorted(weights.iteritems(), key=lambda x: -abs(x[1]))
        for f, _ in fws[self._feature_beam:]:
            del weights[f]

    def merge(self, other):
        '''Merge the weights from another classifier into this one.'''
        for label, source in other._global.iteritems():
            target = self._global.setdefault(label, defaultdict(int))
            for f, w in source.iteritems():
                target[f] += w
            self._prune(target)
        self._iterations += other._iterations