
from subprocess import check_output, Popen, PIPE           
    
    
def call_tregex(pattern, file_path, options=["-x"], exec_path="tregex.sh",
                out_encoding="utf-8"):

    cmd = [exec_path] + options + [pattern, file_path]
    return check_output(cmd).decode(out_encoding)
    

def get_matches(pattern, file_path, exec_path="tregex.sh"):
    output = call_tregex(pattern, file_path, options=['-x'],
                         exec_path=exec_path)
    # FIXME: Only when calling tregex.sh -x through subprocess, output
    # contain duplicates. Why?
    seen = set()
    matches = []
    for pair in output.split():
        if pair not in seen:
            seen.add(pair)
            tree_n, node_n = map(int, pair.split(":"))
            matches.append((tree_n, node_n))
    return matches
    
    # This may be faster, but doesn't preserve order.
    # return list(set([tuple(map(int, pair.split(":"))) 
    # for pair in output.split()]))


