"""
Usage:
    python evaluation_erd.py <qrel_file> <result_file>
e.g.
    python evaluation_erd.py qrels_sets_ERD-dev.txt ERD-dev_MLMcg-GIF.txt


Notes:
1. Qrel and result files are in the same format:

2. Qrel file contains all queries, even the ones without any annotation.
    Qrel files can be found under: qrels/IF/


@author: Faegheh Hasibi (faegheh.hasibi@nunu.no)
"""

from __future__ import division
import sys
from collections import defaultdict


class Evaluator(object):

    def __init__(self, qrels, results):
        self.qrels_dict = qrels
        self.results_dict = results
        qid_overlap = set(self.qrels_dict.keys()) & set(self.results_dict.keys())
        if len(qid_overlap) == 0:
            print("ERR: Query mismatch between qrel and result file!")
            exit(0)

    def eval(self, eval_query_func):
        """
        Evaluates all queries and calculates total precision, recall and F1 (macro averaging).

        :param eval_query_func: A function that takes qrel and results for a query and returns evaluation metrics
        :return  Total precision, recall, and F1 for all queries
        """
        queries_eval = {}
        total_prec, total_rec, total_f = 0, 0, 0
        for qid in sorted(self.qrels_dict):
            queries_eval[qid] = eval_query_func(self.qrels_dict[qid], self.results_dict.get(qid, []))

            total_prec += queries_eval[qid]['prec']
            total_rec += queries_eval[qid]['rec']

        n = len(self.qrels_dict)  # number of queries
        total_prec /= n
        total_rec /= n
        total_f = (2 * total_prec * total_rec) / (total_prec + total_rec) if total_prec + total_rec != 0 else 0

        log = "\n----------------" + "\nEvaluation results:\n" + \
              "Prec: " + str(round(total_prec, 4)) + "\n" +\
              "Rec:  " + str(round(total_rec, 4)) + "\n" + \
              "F1:   " + str(round(total_f, 4)) + "\n" + \
              "all:  " + str(round(total_prec, 4)) + ", " + str(round(total_rec, 4)) + ", " + str(round(total_f, 4))
        print(log)
        metrics = {'prec': total_prec, 'rec': total_rec, 'f': total_f}
        return metrics


def eval_query(query_qrels, query_results):
    """
    Evaluates a single query.

    :param query_qrels: Query annotations from Qrel [en1, en2, ..]
    :param query_results: Query annotations from result file [en1, en2, ..]
    :return: precision, recall, and F1 for a query
    """
    tp = 0  # correct
    fn = 0  # missed
    fp = 0  # incorrectly returned

    # ----- Query has no annotation. ------
    if len(query_qrels) == 0:
        if len(query_results) == 0:
            return {'prec': 1, 'rec': 1, 'f': 1}
        return {'prec': 0, 'rec': 0, 'f': 0}

    # ----- Query has at least one annotation. -----
    # Iterate over qrels to calculate TP and FN
    for qrel_item in query_qrels:
        if find_item(qrel_item, query_results):
            tp += 1
        else:
            fn += 1
    # Iterate over results to calculate FP
    for res_item in query_results:
        if not find_item(res_item, query_qrels):  # Finds the result in the qrels
            fp += 1

    prec = tp / (tp+fp) if tp+fp != 0 else 0
    rec = tp / (tp+fn) if tp+fn != 0 else 0
    f = (2 * prec * rec) / (prec + rec) if prec + rec != 0 else 0
    metrics = {'prec': prec, 'rec': rec, 'f': f}
    return metrics


def find_item(item_to_find, items_list):
    """
    Returns True if an item is found in the item list.

    :param item_to_find: item to be found
    :param items_list: list of items to search in
    :return boolean
    """
    is_found = False
    item_to_find = set(item_to_find)

    for item in items_list:
        if set(item) == item_to_find:
            is_found = True
    return is_found


def parse_file(file_name):
    """
    Parses file and returns the positive instances for each query.

    :param file_name: Name of file to be parsed
    :return list of lines {qid: [e1, e2, ...], ..}
    """
    res = defaultdict(list)
    efile = open(file_name, "r")
    for line in efile.readlines():
        if line.strip() == "":
            continue
        cols = line.strip().split("\t")
        if len(cols) > 1:
            res[cols[0]].append(cols[1])
        else:
            res[cols[0]] = []
    return res


def main(args):
    if len(args) < 2:
        print("\tUsage: [qrel_file] [result_file]")
        exit(0)
    qrels = parse_file(args[0])
    # print(qrels)
    results = parse_file(args[1])
    evaluator = Evaluator(qrels, results)
    evaluator.eval(eval_query)

if __name__ == '__main__':
    main(sys.argv[1:])
