
from bs4 import BeautifulSoup
from urllib2 import urlopen,HTTPError

def make_soup(url):
    try:
        html = urlopen(url).read()
        return BeautifulSoup(html, "lxml")
    except HTTPError:    #If webpage can not be accessed.
        #contents = error.read()       
        print("Cannot read web-page {0}\n".format(url))
        return None
    
def find_parent(soup,tag,text):
    try:
        return soup.find(tag,text=text).parent
    except Exception as err:
        print(err)
        return None

def find_children(soup,tag):
    try:
        return soup.find_all(tag,recursive=False)
    except Exception as err:
        print(err)
        return None

def scrub_line(a_string):
    '''Strips left and right whitespace, newlines, and tabs.
    Returns the first non-empty line.'''
    tmp = a_string.strip().split('\n')
    try:    #Get the first non-empty line
        tmp = [line for line in tmp if (line) or (line is False)][0]
        return tmp
    except IndexError:  #If there were no non-empty lines, return empty
        return ""
    

