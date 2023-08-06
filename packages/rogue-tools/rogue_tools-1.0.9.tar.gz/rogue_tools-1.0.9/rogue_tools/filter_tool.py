

def select_filter_list(src_list,include_list=[],exclude_list=[]):
    '''
    检查src_list中的元素,是否满足过滤器的过滤条件
    '''
    if src_list==[]:
        return src_list
    if include_list==[] and exclude_list==[]:
        return src_list

    rs_list = []
    for src_str in src_list:
        if is_in_list(src_str,exclude_list):
            continue
        if len(include_list) == 0 or is_in_list(src_str,include_list):
            rs_list.append(src_str)
            continue
    return rs_list
    
def is_in_list(src_str,find_list):
    '''
    遍历检查字符串是否包含find_list中的元素(str类型)
    '''
    for find_str in find_list:
        if src_str.find(find_str)>-1:
            return True
    return False

def get_diff(list1,list2)->list:
    '''
    两个列表之间的差异
    '''
    rs_list =[]
    rs_list.extend(list(set(list1).difference(set(list2))))
    rs_list.extend(list(set(list2).difference(set(list1))))
    return rs_list

def get_same(list1,list2)->list:
    '''
    同时存在于list1和list2
    '''
    rs_list = list(set(list1).intersection(set(list2)))
    return rs_list