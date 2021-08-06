# takes a dict of paths e.g. {a/b/c: 1, a/b/d: 2, a/c: 3, b: 4}
# and forms the tree {a: {b: {c: 1, d: 2}, c: 3}, b: 4}
def make_tree(path_dict):
    paths = [path.split("/") for path in path_dict.keys()]

    def make_tree_impl(depth, subpath):
        subpaths = [path for path in paths if path[:depth] == subpath]

        # we've reached the bottom of the tree, so return the value
        if len(subpaths[0]) == depth:
            # if there is more than one path then path_dict contains something like
            # {"x/y": 1, "x/y/z": 2}
            # which is invalid
            if len(subpaths) != 1:
                raise ValueError("failed to convert dict to tree")
            return path_dict["/".join(subpaths[0])]

        # keep recursing
        folders = set([path[depth] for path in subpaths])
        tree = {}
        for folder in folders:
            tree[folder] = make_tree_impl(depth+1, subpath+[folder])
        return tree

    return make_tree_impl(0, [])
