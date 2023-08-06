#python2 python3 compatibility
from functools import reduce

def proper_dir_path(dirname0):
    if "/" not in dirname0[-1]:
        dirname = dirname0+"/"
    else:
        dirname = dirname0
    return dirname

def dress_skeleton(repl,skel,dressed):

    """
    dress_skeleton(repl,skel,dressed) dresses file skel into file dressed
    with the replacements in repl
    
    skel and dressed are strings (the names of the skeleton and output files)
    repl is a sequence of tuples of two strings, the first being the string 
    to be replaced and the second the one to replace it with
    
    sample ussage:
    
    myrepl= ('change_A','with_A'),('change_B','with_B')
    dress_skeleton(myrepl,'file1.dat','file2.dat')
    
    this will make a copy of file1.dat into file2.dat with every occurence
    of 'change_A' being replaced with 'with_A' and every occurence of
    'change_B' being replaced with 'with_B'
    """
    dressed_file = open(dressed, 'w')
    skel_file = open(skel, 'r')
    for line in skel_file:        
        dressed_file.write(reduce(lambda a, kv:a.replace(*kv),repl,line))
    skel_file.close()
    dressed_file.close()


