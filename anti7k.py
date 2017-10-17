import configparser
import sys
import os
import re
import random
import datetime
from colorama import Fore, Style

WORDS_COMPLETED=set()
WORDS_LEARNING={}
WORDS = {}
WORDS_REVIEWED = set()
INTERVALS = [0, 1, 2, 4, 7, 13, 25, 49]
WORDS_PRACTISE_TODAY = set()
FILTER_MODE = False
#
# Profile format
#[Completed]
#1,3,4,5
#[InProgress]
#2=count,2017-10-01
#
#
PROFILE_PATHNAME = 'profile.ini'

def save_status():
    config = configparser.ConfigParser(allow_no_value=True)
    lst = (str(x) for x in sorted(list(WORDS_COMPLETED)))
    completed = ','.join(lst)
    config['Completed'] = {
        'ids' : completed,
    }
    progress = {x: '%s,%s' % y for x,y in WORDS_LEARNING.items()}
    
    config['Progress'] = progress
    
    '''
    config['Progress'] = {
    }
    status = {}
    for x in WORDS_LEARNING:
        status[x] = 
    '''
    
    
    with open(PROFILE_PATHNAME, 'w') as fout:
        config.write(fout)
        
def load_profile():
    global WORDS_COMPLETED
    global WORDS_LEARNING
    config = configparser.ConfigParser()

    config.read(PROFILE_PATHNAME)

    if 'Completed' not in config.sections():
        WORDS_COMPLETED = set()
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")
        WORDS_LEARNING = {x: (date, 0) for x in WORDS}
        save_status()
        
    else:
        ids = config['Completed']['ids'].strip()
        if ids:
            lst = ids.split(',')
            lst = [int(x) for x in lst]
            WORDS_COMPLETED = set(lst)
        else:
            WORDS_COMPLETED = set()
            
        for x in config['Progress']:
            value = config['Progress'][x]
            lst = value.split(',')
            WORDS_LEARNING[int(x)] = (lst[0], int(lst[1]))

        
def load_7k(pathname):
    pattern = re.compile(r'^(\d+)\s+(\w+)\s+\w')
    idx = None
    desc = ''

    with open(pathname) as fin:
        for line in fin:
            m = pattern.match(line)
            if m:
                if idx is not None:
                    #save last word first
                    WORDS[idx] = desc
                    
                idx = int(m.group(1))
                desc = ''                
                WORDS[idx] = desc

            
            if idx:
                desc += line
                

def randomly_pickup_word():
    global WORDS_PRACTISE_TODAY
    
    if not WORDS_PRACTISE_TODAY:
        WORDS_PRACTISE_TODAY = [x for x in WORDS_LEARNING]

    length = len(WORDS_PRACTISE_TODAY)
    if length == 0:
        return None, None
    

    i = random.random() * len(WORDS_PRACTISE_TODAY)
    n = round(i)
    idx = WORDS_PRACTISE_TODAY[n]
        
    return idx, WORDS[idx]


def increase_learning_times(idx):
    date, count = WORDS_LEARNING[idx]
    WORDS_PRACTISE_TODAY.remove(idx)
    if count >= 8:
        WORDS_COMPLETED.add(idx)
        WORDS_LEARNING.pop(idx)
    else:
        WORDS_LEARNING[idx] = (date, count+1)

WORDS_IDENTIFIED = set()
def get_word():
    for x in WORDS_LEARNING:
        if x not in WORDS_IDENTIFIED:
            return x, WORDS[x]

    print("All words identified, quit")
    
def filter_word(idx, remove=False):
    if remove:
        WORDS_LEARNING.pop(idx)
        WORDS_COMPLETED.add(idx)
        
    WORDS_IDENTIFIED.add(idx)

            
def display_word(desc):
    #clear screen
    print(chr(27) + "[2J")
    lst = desc.splitlines()
    title = lst[0]
    content = lst[1:]
    content = '\n'.join(content)

    print(Fore.BLUE + title + Style.RESET_ALL)
    print('_____________________________________________________')

    print(content)
    
def main(pathname):
    load_7k(pathname)
    load_profile()


    while True:
        if FILTER_MODE:
            idx, desc = get_word()
        else:
            idx, desc = randomly_pickup_word()
            
        if idx == None:
            print("You already completed all learning sessions")
            save_status()
            exit(0)

        display_word(desc)
        
        try:
            key = input("Know the word? (Y/N)").strip().lower()
        except EOFError:
            save_status()
            continue
        except Exception:
            save_status()
            break



        if FILTER_MODE:
            if key == 'y' or key == '':
                filter_word(idx, True)
            else:
                filter_word(idx, False)
        else:
            if key == 'y' or key == '':
                increase_learning_times(idx)
            
            

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'filter':
        print("You are in filtering mode, this is first time you choose new words from the list")
        FILTER_MODE = True
        
    config = configparser.ConfigParser()
    pathname = '7kwords.txt'
    main(pathname)
    
