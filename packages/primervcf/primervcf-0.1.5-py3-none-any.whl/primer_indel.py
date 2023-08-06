# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 28/10/2022 12:47 PM
# @Author  : Runsheng
# @File    : primer_indel.py

"""
use the long indel information to design hyplotype specific primers
"""

from LR_toolkit.ssw.ssw_wrap import Aligner
from primerdiffer.utils import reverse_complement


def cigar_getlen(cigar):
    """
    input cigar is a cigar number tuple
    return: match
    """
    M = 0
    for c in cigar:
        if c[0] == 0:
            M += c[1]
    return M


def cigar_getfree3(cigar):
    free3 = 0
    if cigar[-1][0] == 4:
        free3 = cigar[-1][1]

    return free3


def is_no_local_hit(primer, seq, cutoff_alignlength, cutoff_free3, debugmod=False):
    aligner = Aligner(seq, report_cigar=True)
    aln = aligner.align(primer)
    cigar = parse_cigar(aln.cigar_string)

    M = cigar_getlen(cigar)
    free3 = cigar_getfree3(cigar)

    if debugmod == True:
        print(aln.score, aln.ref_begin, aln.ref_end, aln.query_begin, aln.query_end, aln.cigar_string)

    if M <= cutoff_alignlength or free3 >= cutoff_free3:
        return False
    else:
        return True


def is_primer_local_nohit(primer_left, primer_right, seq, cutoff_alignlength=16,
                          cutoff_free3=2, profuct_cutoff=2000, debugmod=False):
    """
    para: the left and right primers
    return: a bed-like tuple-list

    need: parser_cigar, cigar_getlen, cigar_getfree3
    """
    if is_no_local_hit(primer_left, seq, cutoff_alignlength, cutoff_free3, debugmod) == False or \
            is_no_local_hit(reverse_complement(primer_right), seq, cutoff_alignlength, cutoff_free3, debugmod) == False:
        return True
    else:
        return False


def del_primer_check(del_single, db, ref_dict, primer_number=5, debugmod=False):
    '''
    del_single, use this to design a primer
    db is blastdb

    call:
    insilicon_pcr: have only one match in current genome
    check_deletion_local： no local match for the deleted sequence
    return primer tuple

    '''
    chro, start, end = del_single
    del_len = end - start
    name, seq = chr_select(ref_dict, chro, start - 1000, end + 1000)  # the origin sequence
    seq_new = seq[:1000] + seq[(1000 + del_len):]  # the seq with deletion inside
    myprimer = my_design_primer(name=name, seq=seq)

    product_l = []

    for i in range(0, primer_number):
        try:
            left = myprimer['PRIMER_LEFT_' + str(i) + '_SEQUENCE']
            right = myprimer['PRIMER_RIGHT_' + str(i) + '_SEQUENCE']
            product_size = myprimer['PRIMER_PAIR_' + str(i) + '_PRODUCT_SIZE']
            product_l = insilicon_pcr(left, right, db)
        except KeyError:
            pass

        if debugmod:
            print
            "The %d primer :" % i
            print
            left, right, reverse_complement(left), reverse_complement(right)
            print
            is_primer_local_nohit(left, right, seq_new, debugmod=debugmod)
            print
            is_primer_local_nohit(left, right, seq, debugmod=debugmod)

        if len(product_l) == 1 and (is_primer_local_nohit(left, right, seq_new, debugmod=debugmod)):
            # print "pass"
            # with open((name+".txt"), "w") as fw:
            # fw.write("%s\t%s\t%s\t%d" % (name,left,right,product_size))
            return (name, left, right, product_size)
        else:
            pass
            # print "unpass"
    return 0


def my_design_primer(name, seq):
    primer3_general_settings = {
        'PRIMER_OPT_SIZE': 20,
        'PRIMER_PICK_LEFT_PRIMER': 1,
        'PRIMER_PICK_RIGHT_PRIMER': 1,
        'PRIMER_PICK_INTERNAL_OLIGO': 0,
        'PRIMER_MIN_SIZE': 18,
        'PRIMER_MAX_SIZE': 24,
        'PRIMER_OPT_TM': 57.0,
        'PRIMER_MIN_TM': 44.0,
        'PRIMER_MAX_TM': 63.0,
        'PRIMER_MIN_GC': 20.0,
        'PRIMER_MAX_GC': 80.0,
        'PRIMER_PRODUCT_SIZE_RANGE': [[200, 850]],
        'PRIMER_NUM_RETURN': 5,
        'PRIMER_LIB_AMBIGUITY_CODES_CONSENSUS': 0,
        'PRIMER_MIN_THREE_PRIME_DISTANCE': 10
    }

    seq_args = {'SEQUENCE_ID': name,
                'SEQUENCE_TEMPLATE': seq,
                'SEQUENCE_OVERLAP_JUNCTION_LIST': 1000,
                'PRIMER_MIN_3_PRIME_OVERLAP_OF_JUNCTION': 6
                }

    # IMPORTANT: do not misuse the seq_args and the general_args!
    myprimer = primer3.bindings.designPrimers(seq_args, primer3_general_settings)
    return myprimer


if __name__ == "__main__":
    name, seq = chr_select(cb4, 'I', 231537 - 1000, 231551 + 1000)
    myprimer = my_design_primer(name=name, seq=seq)
    # for k,v in myprimer.iteritems():
    # print k,v
    for i in range(0, 5):
        left = myprimer['PRIMER_LEFT_' + str(i) + '_SEQUENCE']
        right = myprimer['PRIMER_RIGHT_' + str(i) + '_SEQUENCE']
        print()
        left, right, reverse_complement(left), reverse_complement(right)

    print()
    chr_select(cb4, "I", 231537, 231551)


if __name__ == "__main__":
    print()
    del_primer_check(del_QR25[1], db="/home/zhaolab1/data/dnaseq/refindex/cb4", ref_dict=cb4, debugmod=True)
    print( chr_select(cb4, *del_QR25[1]) )