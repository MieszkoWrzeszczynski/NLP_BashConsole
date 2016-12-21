#-*- coding: utf-8 -*-
import ply.lex as lex
import ply.yacc as yacc
from subprocess import Popen, PIPE, STDOUT, DEVNULL,call
import os

programs_PID = []
resources_name = ["openDict","closeDict","searchDict","audioVideoExtensions","textExtensions","imageExtensions","programs"]
resources = []
programs_names = []

for resource_name in resources_name:
    with open('resources/' + resource_name + '.in', 'r') as myfile:
        resources.append(myfile.read().replace('\n', '|'))

with open('resources/programsDict.in', 'r') as file:
    programs_names = [line.split() for line in file]

programsDict = { item[0]: item[1] for item in programs_names }

tokens = (
    'RUN',
    'WEB',
    'SEARCH',
    'TEXTFILE',
    'MEDIAFILE',
    'IMAGEFILE',
    'PROGRAMS',
    'CLOSE',
    'CONCAT',
    'ALL_CLOSE'
)

t_RUN =r'\b'  +resources[0]  + '\b'
t_CLOSE = r'\b' + resources[1] + '\b'
t_WEB = r'(https?:\/\/(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})|(\.?\w+\.(pl|com|de|en|org))'
t_SEARCH = resources[2] 
t_MEDIAFILE = "[/\w/]+\.(" + resources[3] + ")"
t_TEXTFILE  = "[/\w]+\.(" + resources[4] + ")"
t_IMAGEFILE  = "[/\w]+\.(" + resources[5] + ")"
t_CONCAT = r'\b(następnie|kolejno|dalej|i)\b'
t_ignore = " \t"
t_PROGRAMS = resources[6] 
t_ALL_CLOSE = r'wszystkie|wszystko'

def t_error(t):
    t.lexer.skip(1)

lexer = lex.lex()

def p_expression(p):
    '''expression : openprogram 
                  | search
                  | openbrowser
                  | closeprogram
                  | openmusicfile
                  | opentextfile
                  | openimagefile
                  | expression CONCAT expression
                  | closeall
                  | openmultiple
                  '''

def p_search(p):
    ''' search : SEARCH '''

    query = ' '.join(natural_input.split(p[1]))
    proces = Popen("firefox -search " + r'''"''' +  query  +'''"''', shell=True, stdin=PIPE, stdout=DEVNULL, stderr=STDOUT) 
    programs_PID.append({'name' : 'firefox', 'pid' : proces})


def p_openprogram(p):
    ''' openprogram : RUN PROGRAMS 
                    | RUN PROGRAMS PROGRAMS'''

    program_name = p[2]

    if program_name in programsDict:
        program = programsDict[program_name]

    proces = Popen(program, shell=False,  stdout=DEVNULL,stderr=STDOUT) 
    programs_PID.append({'name' : program_name, 'process' : proces})

def p_openmultiple(p):
    ''' openmultiple : RUN PROGRAMS CONCAT PROGRAMS'''

    program_name_first = p[2]
    program_name_second = p[4]

    if program_name_first in programsDict:
        program_first = programsDict[program_name_first]

    if program_name_second in programsDict:
        program_second = programsDict[program_name_second]

    proces_first = Popen(program_first, shell=False,  stdout=DEVNULL,stderr=STDOUT) 
    programs_PID.append({'name' : program_name_first, 'process' : proces_first})

    proces_second = Popen(program_second, shell=False,  stdout=DEVNULL,stderr=STDOUT) 
    programs_PID.append({'name' : program_name_second, 'process' : proces_second})


def p_closeprogram(p):
    ''' closeprogram : CLOSE ALL_CLOSE '''

    for proces in programs_PID:
        proces['process'].kill()
        programs_PID.remove(proces)


def p_closeall(p):
    ''' closeall : CLOSE PROGRAMS
                     | CLOSE TEXTFILE
                     | CLOSE MEDIAFILE
                     | CLOSE IMAGEFILE
                     '''

    for proces in programs_PID:
        if(proces['name'] == p[2]):
            proces['process'].kill()
            programs_PID.remove(proces)

def p_openbrowser(p):
    ''' openbrowser : RUN WEB '''

    proces = Popen("firefox " + p[2], shell=True, stdout=DEVNULL,sterr=DEVNULL) 
    programs_PID.append({'name' : 'firefox', 'process' : proces})

def p_opentextfile(p):
    ''' opentextfile : RUN TEXTFILE'''

    proces = Popen(['gedit', p[2]], shell=False, stdout=DEVNULL,stderr=STDOUT) 
    programs_PID.append({'name' : p[2], 'process' : proces})

def p_openmusicfile(p):
    ''' openmusicfile : RUN MEDIAFILE'''

    proces = Popen(['vlc', p[2]], shell=False, stdout=DEVNULL,stderr=STDOUT) 
    programs_PID.append({'name' : p[2], 'process' : proces})

def p_openimagefile(p):
    ''' openimagefile : RUN IMAGEFILE'''

    proces = Popen(['display', p[2]], shell=False, stdout=DEVNULL,stderr=STDOUT) 
    programs_PID.append({'name' : p[2], 'process' : proces})

def p_error(p):
    print(p)
    print("Spróbuj inaczej wpisać polecenie.")

yacc.yacc()

natural_input = ""

while True: 
    natural_input  = input().lower()
    yacc.parse(natural_input)