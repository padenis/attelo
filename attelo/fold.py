'''
Group-aware n-fold evaluation.

Attelo uses a variant of n-fold evaluation, where we (still)
andomly partition the dataset into a set of folds of roughly even
size, but respecting the additional constraint that any two data
entries belonging in the same "group" (determined a single
distiguished feature, eg. the document id, the dialogue id, etc)
are always in the same fold. Note that this makes it a bit harder
to have perfectly evenly sized folds


Created on Jun 20, 2012

@author: stergos

contribs: phil
'''

import random

import Orange


def make_n_fold(data, folds=5, meta_index="FILE"):
    """Given an Orange table, provides a n-folds based on the meta index,
    in order not to mix instances from the same origin in train and test
    (eg, not to mix instances from the same file in train and test data
    in discourse experiment)

    Returns a dict from meta index to fold index
    """

    file_index = data.domain.index(meta_index)
    fold_dict = dict()
    for i in range(len(data)):
        file_key = data[i][file_index].value
        if not file_key in fold_dict:
            fold_dict[file_key] = -1
    keys = fold_dict.keys()

    for current in xrange(((len(keys)) / folds) + 1):
        random_values = random.sample(xrange(folds), folds)
        for i in xrange(folds):
            position = (current * folds) + i
            if position < len(keys):
                fold_dict[keys[position]] = random_values[i]

    return fold_dict


def folds_to_orange(data, fold_dict, meta_index="FILE"):
    """Given an Orange table and a fold dictionary (eg.
    one generated by `make_n_fold`), return a list of the
    same length, each item being the fold assignation
    for the corresponding entry in the table.

    These fold indices allow for the the use of any normal
    Orange method as if it were classical cross-validation
    (see `Orange.data.select`)
    """
    index = []
    file_index = data.domain.index(meta_index)
    for one in data:
        file_key = one[file_index].value
        index.append(fold_dict[file_key])
    return index


# pylint: disable=too-many-arguments
def process_by_file_folds(data, selection,
                          f_train, f_test, f_eval,
                          folds=5):
    """
    just for demo/example purposes
    could be a template of processing a corpus based on folds-on-files

    ;param data: a data table
    :param selection: an index of folds for each instance, eg
           can be computed with
           `orange.MakeRandomIndicesCV(data, folds=5)`
    :param f_train: what to do on training/testing (same with `f_test`)
    :param f_eval: evaluate one fold
    :param folds: number of folds. must be the same as the nb in
           selection (should/could be recomputed from selection)
    """
    evals = []
    for test_fold in range(folds):
        train_data = data.select_ref(selection, test_fold, negate=1)
        test_data = data.select_ref(selection, test_fold)
        model = f_train(train_data)
        results = f_test(test_data, model)
        evals.append(f_eval(results))
    # or evals+results
    return evals
# pylint: enable=too-many-arguments


def _example():
    "testing with a simple 5-fold cross-validation"
    import sys

    #random.seed()#"just an illusion")

    bayes = Orange.classification.bayes.NaiveLearner(adjust_threshold=True)
    data = Orange.data.Table(sys.argv[1])
    fold_struct = make_n_fold(data, folds=5)
    #print fold_struct
    #sys.exit(0)

    selection = folds_to_orange(data, fold_struct)

    print ">>>> 5-fold with file awareness"
    results = Orange.evaluation.testing.test_with_indices([bayes],
                                                          data,
                                                          selection)
    print "accuracy =", Orange.evaluation.scoring.CA(results)[0]
    cmatrix = Orange.evaluation.scoring.confusion_matrices(results)[0]
    print "F1 for class True", Orange.evaluation.scoring.F1(cmatrix)

    # comparaison avec nfold sans tri par fichier
    print ">>>> 5-fold without file awareness"
    results = Orange.evaluation.testing.cross_validation([bayes],
                                                         data,
                                                         folds=5)
    print "accuracy =", Orange.evaluation.scoring.CA(results)[0]
    cmatrix = Orange.evaluation.scoring.confusion_matrices(results)[0]
    print "F1 for class True", Orange.evaluation.scoring.F1(cmatrix)

    # test distrib
    bayes(data)(data[0],
                result_type=Orange.classification.Classifier.GetBoth)


if __name__ == "__main__":
    _example()
