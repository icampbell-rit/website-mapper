#link_finder.py
# By Ian Campbell
# This program maps out a website by finding and visiting
# all of the links that can be found in the html
# It then categorizes them as working or broken
# This is heavily inspired by my previous works email_parser.py
# version 1.4.0 02/28/19

#imports
import getopt
import sys
from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque

#global variables
foreign_urls = set()
processed_urls = set()
broken_urls = set()
good_urls = set()

### Main Method
### This method processes all commandline arguements
### and sets up all things necessary for performance.
def main():
    try:
        opts,args=getopt.getopt(sys.argv[2:],"o:l:mh",["help","ouput=","limit="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    outfile = ""
    out = False
    working = False
    limited = False
    limits = ""
    for one, two in opts:
        if one == "-m":
            working = True
        elif one in ("-h", "--help"):
            usage()
            sys.exit()
        elif one in ("-o","--ofile"):
            outfile = two
            out = True
        elif one in ("-l","--limit"):
            limits = two
            limited = True
        else:
            assert False, "Option not permitted"

    beg_url = sys.argv[1]
    spider(beg_url,limited,limits)

    #setup output buffers
    orig_stdout = sys.stdout
    #print(out)
    if out:
        f = open(outfile, 'w')
        sys.stdout = f

    #print active URLS
    print("\nGOOD URLS FOUND\n")
    count = 0
    for a in good_urls:
        print(str(count) + ") " + a)
        count = count + 1

    #print bad and foreign URLS
    if not working:
        print("\nFOREIGN URLS FOUND\n")
        count = 0
        for a in foreign_urls:
            print(str(count) + ") " + a)
            count = count + 1

        print("\nBROKEN URLS FOUND\n")
        count = 0
        for a in broken_urls:
            print(str(count) + ") " + a)
            count = count + 1
    #resetup the stdout
    if out:
        sys.stdout = orig_stdout
        f.close()

### This method gets the base name for the domain
### makes use of urlparse
def get_base_domain(url):
    parsed = urlparse(url)
    domain = '{uri.netloc}/'.format(uri=parsed)
    result = domain.replace('www','')
    d = result
    return d

### This method contains all main functionality
### This will spider throught the site and map out links as
### active or broken!!
def spider(starter,l,limit):
    start = starter
    domain = str
    if l:
        domain = str(limit)
    else:
        domain = get_base_domain(start)

    # data structures
    new_urls = deque([start])

    #main while loop
    while len(new_urls):
        #pop that boiyo
        url = new_urls.popleft()
        processed_urls.add(url)

        parts = urlsplit(url)
        #setup url
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        if parts.scheme != 'mailto' and parts.scheme != '#':
            path = url[:url.rfind('/') + 1] if '/' in parts.path else url
        else:
            continue
        
        #determine if it works or is broken
        try:
            response = requests.get(url)
            good_urls.add(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
            broken_urls.add(url)
            continue
        #create a BSOBJ to scan the html for links
        soup = BeautifulSoup(response.text,'lxml')

        #determine which lnks are valid from the html
        for anchor in soup.find_all("a"):
            link = anchor.attrs["href"] if "href" in anchor.attrs and anchor.attrs["href"].find("mailto") == -1 and anchor.attrs["href"].find("tel") == -1 and anchor.attrs["href"].find("#") == -1 else ''

            #append good links back to the url queue. 
            if link.startswith('/'):
                link = base_url + link
            elif not link.startswith('http'):
                link = path + link
            if not link in new_urls and not link in processed_urls and not link.find(domain) == -1:
                new_urls.append(link)
            if link.find(domain) == -1:
                foreign_urls.add(link[:75])

def usage():
    print("USAGE: python3 link_finder.py -o <outfile> -m -l <domain to be limi"
            +"ted too>\n")
    sys.exit(2)

if __name__ == "__main__":
    main()
