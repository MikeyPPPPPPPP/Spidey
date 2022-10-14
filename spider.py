#!/usr/local/bin python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse





class SPIDER:
    """attempts to spider a site for a tags
    
    :base_url: str
    :depth: int
    """
    def __init__(self, base_url: str, depth: int) -> None:

        self.base_url = self.build_base_url(base_url) # https://stackoverflow.com

        self.depth = depth
        self.all_urls_found = []

    def build_base_url(self, url: str) -> str:
        """make the base url"""
        sch = urlparse(url)[0]
        domain = urlparse(url)[1]
        return sch + "://" + domain

    def soup_parser(self, url: str) -> str:
        """returns a bs4 object for parsing"""
        get = requests.get(url).text
        return BeautifulSoup(get, "lxml")

    def return_list_of_hrefs(self, page: str) -> list[str]:
        """returns a list of unprocessed hrefs"""
        return [x['href'] for x in page.findAll('a', href=True) if x["href"] and x["href"] != 'javascript:void(0);' or x["href"].startswith('mailto') == False]

    def valid_url(self, url: str) -> bool:
        """returns True for a 200 statuse code"""
        if requests.get(url).status_code == 200:
            return True
        return False

    def validate_url(self, url):
        """this will check if there is a http, /, mailto: after the first http://dgfd/ 
        
        there was a problem with it messing up like this 
        https://erowid.org/https://erowid.org/donations/donations_single.php?src=splashsd1

        """
        counter = 0

        count = 0
        for x in url:
            if count == 3:
                continue

            if x == '/':
                count += 1

            counter += 1

        if url[counter:].startswith('/'):
            return False
        if url[counter:].startswith('http'):
            return False
        if url[counter:].startswith('mailto:'):
            return False
            
        return True

    def proccess_links(self, link: str) -> str:
        """Makes urls valid"""

        #dose the url start with  the base path
        final_url = ""

        #if the url starts with the base url
        if link.startswith(self.base_url):# and self.valid_url(link):
            final_url = link
            return final_url

        #if the url starts with a /
        if link.startswith('/') and link.startswith('http') == False and self.validate_url(self.base_url +link):#and self.valid_url(self.base_url + link):
            final_url = self.base_url +link
            return final_url

        #if the url dose not starts with a / or http
        if link.startswith('/') == False and link.startswith('http') == False and self.validate_url(self.base_url + '/' +link):
            final_url = self.base_url + '/' +link
            return final_url

            #else:
            #print('not processed '+link)
        

    def recursive_spider(self, urls: list[str] = None) -> list[str]:
        """recursivly spider pages untill specified depth is reached"""
        if self.depth == 0:
            return

        self.depth -= 1

        #first inital check
        if urls == None:
            soup = self.soup_parser(self.base_url)
            hrefs = self.return_list_of_hrefs(soup)

            #this list contains strings and None values 
            temp_links = [self.proccess_links(links) for links in hrefs]

            #this list if like temp_links with the Nones removed
            good_links = [links for links in temp_links if links != None]

            #this will remove doubles
            self.all_urls_found = [*set(good_links)]

            self.recursive_spider(self.all_urls_found)

        if urls == None:
            return

        for link in urls:

            #we can possibly add page analyses functions here, like finding inputs and forums
            soup = self.soup_parser(link)
            hrefs = self.return_list_of_hrefs(soup)
            
            #this list contains strings and None values that are not already in self.all_urls_found
            temp_links = [self.proccess_links(links) for links in hrefs if links not in self.all_urls_found]

            #this list if like temp_links with the Nones removed
            good_links = [links for links in temp_links if links != None]

            #this will be a list of links we want to do more reursion on
            more_links = []

            for link in good_links:
                if link not in self.all_urls_found:
                    more_links.append(link)

            t = good_links + self.all_urls_found

            self.all_urls_found = [*set(t)]


            self.recursive_spider(more_links)




t = SPIDER("https://www.thegeekstuff.com/sed-awk-101-hacks-ebook/",5)#https://erowid.org/archive/", 1)
t.recursive_spider()

s = open('thegeekstuff.txt', 'w')

for x in [*set(t.all_urls_found)]:
    s.write(x+'\n')


from libs.find_inputs import find_injection_points

a = find_injection_points([0,0])

#print('find_uri_injection_points'.replace('_', ' '))
for x in [*set(t.all_urls_found)]:
    a.parse_uris_that_are_injectable(x)



'''

s.write('\n\n\nfind_uri_injection_points\n----------------------------------\n\n'.replace('_', ' '))
for x in a.uri_points:
    s.write(x+'\n')
'''
s.close()
