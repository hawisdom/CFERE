from treelib import Tree
ROOT = 0

#Structure of SSDP tree nodes
class SSDP_Tree_Node(object):
    def __init__(self,postag,dp_relation,sdp_relation):
        self.postag = postag
        self.dp = dp_relation
        self.sdp = sdp_relation

#Structure of associated nodes between events
class Event_Rela_Node(object):
    def __init__(self,parent,dp):
        self.parent = parent
        self.dp = dp

class SSDP_graph:
    #The DP tree is established by recursion
    def build_dp_tree(self,tree,words,postags,arcs,root_node):
        for i in range(len(arcs)):
            #search the parent of current node, build parent-child relation，then Recursive search
            if arcs[i].head == root_node:
                tree.create_node(words[i], i + 1, parent=root_node,
                                 data=SSDP_Tree_Node(postags[i],arcs[i].relation,None))
                self.build_dp_tree(tree,words,postags,arcs,i + 1)
        return tree

    def continuous_verb(self,dp_tree,cur_node,child_node):
        id = cur_node.identifier
        while cur_node.identifier < child_node.identifier:
            id += 1
            if id == child_node.identifier:
                return 1
            node = dp_tree.get_node(id)
            if node and not (node.data.dp == 'ADV'):
                return 0

        while cur_node.identifier > child_node.identifier:
            id -= 1
            if id == child_node.identifier:
                return 1
            node = dp_tree.get_node(id)
            if node and not (node.data.dp == 'ADV'):
                return 0
    def has_VOB(self,dp_tree,cur_node):
        child_nodes = dp_tree.children(cur_node.identifier)

        for child_node in child_nodes:
            if child_node.data.dp == 'VOB':
                return 1

        return 0

    #Adjust the level of verbs that depend directly on the verb chain
    def adjust_eroot(self,dp_tree,cur_node,root,bro_tree):
        self.combin_node = []
        #from HED
        child_nodes = dp_tree.children(cur_node.identifier)

        #scan all children of HED node for VOB or COO nodes
        for child_node in child_nodes:
            #the child is verb
            dp = child_node.data.dp
            #If it is a COO continuous verb, incorporate it into the predicate
            if child_node.data.postag == 'v' and dp == 'COO' and ((child_node.identifier) == cur_node.identifier + 1):
                #Add the merged node to the list to prevent the node from being deleted
                self.combin_node.append(child_node)
                self.adjust_eroot(dp_tree,child_node,root,bro_tree)
            elif child_node.data.postag == 'v' and dp == 'COO' and ((child_node.identifier) != cur_node.identifier + 1):
                #Verbs with adverbs in the middle are considered continuous verbs and incorporated into predicates
                if self.continuous_verb(dp_tree,cur_node,child_node):
                    self.combin_node.append(child_node)
                    self.adjust_eroot(dp_tree, child_node, root, bro_tree)
                else:
                    #build tree for brother nodes
                    cur_parent = dp_tree.parent(cur_node.identifier)
                    if cur_parent in self.combin_node:
                        pparent = dp_tree.parent(cur_parent.identifier)
                        parent_id = pparent.identifier
                    else:
                        parent_id = cur_node.identifier
                    bro_tree.create_node(child_node.tag, child_node.identifier, parent=ROOT,
                                    data=Event_Rela_Node(parent_id,child_node.data.dp))

                    #Adjust the verb hierarchy in CVC
                    dp_tree.move_node(child_node.identifier, ROOT)
                    child_node.data.dp = 'HED'
                    self.adjust_eroot(dp_tree, child_node, root, bro_tree)
            #COO child node is a verb and relates to VOB, and VOB node also has VOB node, then the VOB node is included in the predicate
            elif child_node.data.postag == 'v' and dp == 'VOB' and (cur_node.data.dp == 'COO' or cur_node.data.dp == 'HED') and ((child_node.identifier) == cur_node.identifier + 1) and self.has_VOB(dp_tree,child_node):
                self.adjust_eroot(dp_tree, child_node, root, bro_tree)
        return

    #build ssdp tree
    def build_ssdp_tree(self,words,postags,arcs):
        dp_tree = Tree()
        #create Root node of DP
        dp_tree.create_node('DROOT',ROOT, data=SSDP_Tree_Node(None ,None,None))

        #create tree for brother nodes
        bro_tree = Tree()
        bro_tree.create_node('BROOT', ROOT, data=Event_Rela_Node(ROOT, 'Root'))

        #build DP tree
        self.build_dp_tree(dp_tree, words, postags,arcs,ROOT)

        HED_node_list = dp_tree.children(ROOT)

        #adjust eroot nodes
        self.adjust_eroot(dp_tree,HED_node_list[0],ROOT,bro_tree)

        return dp_tree,bro_tree


#obtain event list in a sentence
def get_event_pair_list(dp_tree,bro_tree):
    event_pair_list = []

    eroots = bro_tree.children(ROOT)
    if not eroots:
        return event_pair_list

    for eroot in eroots:

        depen_event = dp_tree.get_node(eroot.identifier)
        rele_event_id = eroot.data.parent

        rele_event_node = dp_tree.get_node(rele_event_id)

        if not rele_event_node:
            event_pair_list.append((rele_event_node, depen_event))
            continue

        if rele_event_node.data.postag == 'v':
            event_pair_list.append((rele_event_node,depen_event))

    return event_pair_list

#obtain event pairs
def get_event_pair(dp_tree,bro_tree):
    eroots = bro_tree.children(ROOT)
    if not eroots:
        return 0,(None,None)

    eroot = eroots[0]

    eroot_bro = bro_tree.get_node(eroot.identifier)
    par_id = eroot_bro.data.parent
    par_node = dp_tree.get_node(par_id)

    if not par_node:
        return 0,(None, eroot)

    if par_node.data.postag == 'v':
        return 1,(par_node,eroot)

    return 0,(None,eroot)

def node_sort(node):
    return node.identifier

def get_event_info(dp_tree,eroot):
    sub = ''
    obj = ''

    children_nodes = dp_tree.children(eroot.identifier)
    for child_node in children_nodes:
        if child_node.data.dp == 'SBV':
            sub = complete_ee(dp_tree,child_node)
        if child_node.data.dp == 'VOB':
            obj = complete_ee(dp_tree,child_node)
    return sub,obj



#add all children information of the node
def complete_ee(tree,par_node):
    child_nodes = tree.children(par_node.identifier)
    left_info = ''
    right_info = ''
    if not child_nodes:
        return par_node.tag

    child_nodes.sort(key= node_sort)

    for child_node in child_nodes:
        if child_node.tag == '，':
            continue
        if child_node.identifier < par_node.identifier:
            left_info += complete_ee(tree,child_node)
        elif child_node.identifier > par_node.identifier:
            right_info += complete_ee(tree,child_node)

    return left_info + par_node.tag + right_info

#obtain all the children of the specified node
def get_all_node(dp_tree, cur_node,dp_node_list):
    if not cur_node:
        return dp_node_list
    child_nodes = dp_tree.children(cur_node.identifier)
    for child_node in child_nodes:
        get_all_node(dp_tree,child_node,dp_node_list)
        if child_node.tag in Symbol_list:
            continue
        dp_node_list.append(child_node)