import difflib
# 相似度比较

def diff(str1,str2):
    seq   = difflib.SequenceMatcher(None,str1,str2)
    ratio = seq.ratio()
    return ratio