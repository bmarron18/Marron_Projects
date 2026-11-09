"""
Code to parse sklearn classification_report
"""
#%% STEP 1
##
import sys
import collections
##
def parse_classification_report(clfreport):
    """
    Parse a sklearn classification report into a dict keyed by class name
    and containing a tuple (precision, recall, fscore, support) for each class
    """
    lines = clfreport.split('\n')
    # Remove empty lines
    lines = filter(lambda l: not len(l.strip()) == 0, lines)

    # Starts with a header, then score for each class and finally an average
    header = lines[0]
    cls_lines = lines[1:-1]
    avg_line = lines[-1]

    assert header.split() == ['precision', 'recall', 'f1-score', 'support']
    assert avg_line.split()[0] == 'avg'

    # We cannot simply use split because class names can have spaces. So instead
    # figure the width of the class field by looking at the indentation of the
    # precision header
    cls_field_width = len(header) - len(header.lstrip())
    # Now, collect all the class names and score in a dict
    def parse_line(l):
        """Parse a line of classification_report"""
        cls_name = l[:cls_field_width].strip()
        precision, recall, fscore, support = l[cls_field_width:].split()
        precision = float(precision)
        recall = float(recall)
        fscore = float(fscore)
        support = int(support)
        return (cls_name, precision, recall, fscore, support)

    data = collections.OrderedDict()
    for l in cls_lines:
        ret = parse_line(l)
        cls_name = ret[0]
        scores = ret[1:]
        data[cls_name] = scores

    # average
    data['avg'] = parse_line(avg_line)[1:]

    return data
#parse_classification_report(clfreport)
#%% STEP 2
##
def report_to_latex_table(data):
    out = ""
    out += "\\begin{tabular}{c | c c c c}\n"
    out += "Class & Precision & Recall & F-score & Support\\\\\n"
    out += "\hline\n"
    out += "\hline\\\\\n"
    for cls, scores in data.iteritems():
        out += cls + " & " + " & ".join([str(s) for s in scores])
        out += "\\\\\n"
    out += "\\end{tabular}"
    return out

#%% STEP 3 Not sure how this works! ==> skip STEP 3
#http://stackoverflow.com/questions/419163/what-does-if-name-main-do
#print report_to_latex_table(data)
if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        data = parse_classification_report(f.read())
    print report_to_latex_table(data)
    
#%% Work around STEP 3
    
# define output from the classifiaction report
clfreport = classification_report(te_d_y, classifier_model_pred)

#then after running STEP 1 and STEP 2      
test = parse_classification_report(clfreport)   
report_to_latex_table(test)


#%%
"""
Output will need cleanup! For example,

Out[18]: '\\begin{tabular}{c | c c c c}\nClass & Precision & 
Recall & F-score & Support\\\\\n\\hline\n\\hline\\\\\n0.0 & 0.61 
& 0.65 & 0.63 & 922\\\\\n1.0 & 0.5 & 0.46 & 0.48 & 714\\\\\navg & 
0.56 & 0.57 & 0.56 & 1636\\\\\n\\end{tabular}'


in LaTex,

\begin{tabular}{c | c c c c}
Class & Precision & Recall & F-score & Support\\
0.0 & 0.61 & 0.65 & 0.63 & 922\\
1.0 & 0.5 & 0.46 & 0.48 & 714\\
avg & 0.56 & 0.57 & 0.56 & 1636\\
\end{tabular}

"""
    
    
    