#!/usr/bin/env python3

import sys, re, os, json
from trans import translate, restore

def usage():
    print('usage:', sys.argv[0], '[--plain] [--apply-on <comment tag>] < input.amr > output.amr', file=sys.stderr)

args = sys.argv[1:]

unbracket = re.compile(r'\(\s*([^():\s"]*)\s*\)')
dangling_edges = re.compile(r':[\w\-]+\s*(?=[:)])')
missing_edges = re.compile(r'(\/\s*[\w\-]+)\s+\(')
missing_variable = re.compile(r'(?<=\()\s*([\w\-]+)\s+(?=:)')
missing_quotes = re.compile(r'("\w+)(?=\s\))')
misplaced_colon = re.compile(r':(?=\))')
missing_concept_and_variable = re.compile(r'(?<=\()\s*(?=:\w+)')
dangling_quotes = re.compile(r'(?<=\s)(\w+)"(?=\s|\)|:)')

# c = 0
def replace_var(m):
    global c
    global cc
    global ggg
#    counter += 1
    # line = re.sub(r'\(\s*([\w\-\d]+)(\W)', replace_var, line)
    if ['name','date'].count(m.group(1)) == 1:
        c += 1
        return '(v' + str(ggg) + str(c) + ' / ' + m.group(1) + m.group(2)
    if cc.count(m.group(1)) == 0:
        cc.append(m.group(1))
        return '(vv' + str(ggg) + m.group(1) + ' / ' + m.group(1) + m.group(2)
    if m.group(2) == ' )':
       return ' vv' + str(ggg) + m.group(1)
    c += 1
    return '(vvvv' + str(ggg) + str(c) + ' / ' + m.group(1) + m.group(2)
    

def replace_var2(m):
#    global counter
    if m.group(2) == "-":
        return "%s %s" % (m.group(1), m.group(2))
    if m.group(2) == "interrogative":
        return "%s %s" % (m.group(1), m.group(2))
    if m.group(2) == "expressive":
        return "%s %s" % (m.group(1), m.group(2))
    if m.group(2) == "imperative":
        return "%s %s" % (m.group(1), m.group(2))
#    counter += 1
    return "%s \"%s\"" % (m.group(1),  m.group(2))


def add_quotes(m):
    value = m.group(2).strip()
    if value == '-':
        return '%s %s ' % (m.group(1), value)
    return '%s "%s" ' % (m.group(1), value)

def convert(line):
    global cc
    global c
    global ggg
    c = 0
    cc=[]
    old_line = line
    while True:
        line = re.sub(r'(\( ?name [^()]*:op\d+|:wiki) ([^\-_():"][^():"]*)(?=[:\)])', add_quotes, line, re.I)
        # line = re.sub(r'((:op\d+|:wiki) ([^():"]+)(?=[:\)])', add_quotes, line, re.I)
        if old_line == line:
            break
        old_line = line

    line = re.sub(r'\(\s*([\w\-\d]+)(\W.|\))', replace_var, line)

    # print('>>', line)
    # line = re.sub(r'(?<=\s)(_\w+)(?=[\s)]|$)', lambda m: restore(m.group(1)), line)
    # re.sub(r'(?<=\s)(_\w+)(?=[\s)]|$)', lambda m: print(m.group(1)), line)
    line = re.sub(r'"(_[^"]+)"', lambda m: restore(m.group(1)), line)
    # line = re.sub(r'(?<=\s)(_\w+)(?=[\s)]|$)', lambda m: restore(m.group(1)), line)

    open_count = 0
    close_count = 0
    for i,c in enumerate(line):
        if c == '(':
            open_count += 1
        elif c == ')':
            close_count += 1
        if open_count == close_count and open_count > 0:
            line = line[:i].strip()
            break

    old_line = line
    while True:
        open_count = len(re.findall(r'\(', line))
        close_count = len(re.findall(r'\)', line))
        if open_count > close_count:
            line += ')' * (open_count-close_count)
        elif close_count > open_count:
            before = line
            for i in range(close_count-open_count):
                line = line.rstrip(')')
                line = line.rstrip(' ')
        #     if before == line:
        #         line = '(' * (close_count-open_count) + line
        if old_line == line:
            break
        old_line = line


    old_line = line
    while True:
        line = re.sub(r'(:\w+) ([^\W\d\-][\w\-]*)(?=\W)', replace_var2, line, re.I)
        if old_line == line:
            break
        old_line = line

    line = unbracket.sub(r'\1', line, re.U)
    line = dangling_edges.sub('', line, re.U)
    line = missing_edges.sub(r'\1 :ARG2 (', line, re.U)
    line = missing_variable.sub(r'vvvx / \1 ', line, re.U)
    line = missing_quotes.sub(r'\1"', line, re.U)
    line = misplaced_colon.sub(r'', line, re.U)
    line = missing_concept_and_variable.sub(r'd / dummy ', line, re.U)
    line = dangling_quotes.sub(r'\1', line, re.U)

    return line

global ggg
ggg = 0
for line in sys.stdin:
    ggg += 1
    line = line.rstrip().lstrip(' \xef\xbb\xbf\ufeff')
    old_line = line
    line = line.rstrip().lstrip('> ')
    if len(old_line) > len(line):
      print()
    #    else:
    if not (line == '(gm/gm' or line == ' :gs ' or line == ')') :
    #         continue
    # if len(line) > 7:
        line = convert(line)
#    line = convert(line)
    print(line)
#    print()

