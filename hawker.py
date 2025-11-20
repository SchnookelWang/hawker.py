import feedparser
from datetime import datetime
from time import mktime
import threading
from pathlib import Path
from splashscreen import *
from splashscreen import display_splash
from colorama import Fore, Back, Style, init
from bs4 import BeautifulSoup


############
### MEAL ###
############

meal = {}
def feed(url, search_mode, search_words): #feeds the selected feeds into a dictonary meal
    feed = feedparser.parse(url)
    feed_title = getattr(feed.feed, "title", url)
    meal[feed_title] = []
    
    for entry in feed.entries:
        text_to_search = entry.title.lower()  #include title
        if hasattr(entry, "summary"):
            summary_text = clean_summary(entry.summary)  #cleaned summary
            text_to_search += " " + summary_text.lower()
        
        if search_mode == 'i':
        #Filter: only keep if any keyword is found
            if not any(word.lower() in text_to_search for word in search_words):
                continue  # skip this article if no keywords matched
        elif search_mode == 'e':
         #Filter: only include articles that are DO NOT include search words
            if any(word.lower() in text_to_search for word in search_words):
                continue  # skip this article
        
        feed_entry = {"Title": entry.title,"Outlet":feed_title}
        if hasattr(entry, "link"):
            feed_entry["Link"] = entry.link
        
        if hasattr(entry, "summary"):
            feed_entry["Summary"] = entry.summary

        if hasattr(entry, "published"):
            try:
                feed_entry["Published"] = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z") #If timestamp is not formatted
            except Exception:
                feed_entry["Published"] = entry.published
        elif hasattr(entry, "published_parsed"):
            # Convert struct_time to ISO 8601
            feed_entry["Published"] = datetime.fromtimestamp(mktime(entry.published_parsed))

        meal[feed.feed.title].append(feed_entry)
    meal[feed_title].sort(key=lambda x: x.get("Published", datetime.min), reverse=True) #Sorts after date, newest bottom

############
### HAWK ###
############

def hawk(num_of_articles): #Prints the dictonary meal, containing all feeds
    init(autoreset=True) #resets colors after print

    # Flatten all articles into one list
    all_articles = [article for articles in meal.values() for article in articles]

    # Sort by published date (not reversed)
    sorted_articles = sorted(
            all_articles,
            key=lambda x: x.get("Published", datetime.min),
            reverse=False
            )

    for article in sorted_articles[-num_of_articles:]:
        print(Style.NORMAL + Back.WHITE + Fore.BLACK + article.get("Title", "No Title"))
        print()
        print(clean_summary(article.get("Summary", "No Summary")))
        print(Fore.GREEN + str(article.get("Published", "No Date")))
        print()
        print(Fore.RED + article.get("Outlet", "No Outlet Available"))
        print(Fore.CYAN + article.get("Link", "No Link Available"))
        print()


#############################
### BEAUTIFULSOUP CLEANER ###
#############################

#Incase the summary contains html elements
def clean_summary(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove noisy tags
    for tag in soup.find_all([
        "script", "style", "iframe", "form", "ul", "ol", "li", "a", "img",
        "footer", "nav", "aside", "noscript", "header"
    ]):
        tag.decompose()

    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

    if paragraphs: #checks if non-empty
        return "\n".join(paragraphs)
    else:
        return soup.get_text(strip=True) #Incase there is no HTML elements, the text is just returned


####################################
### GETTING RSS_SORUCES.TXT file ###
####################################

script_dir = Path(__file__).parent
def get_sources_file():
    while True:
        rss_feeds_data = []
        file_source = input(Style.BRIGHT + "Enter name of RSS .txt file (leave empty for default = rss_sources.txt)\nSeperate each file with a SPACE to add multiple files\n$") 
        if file_source == '':
            rss_feeds_file_path = script_dir / "rss_sources.txt" 
            rss_feeds_data = Path(rss_feeds_file_path).read_text(encoding='utf-8')
            return rss_feeds_data
        else:
            sources = file_source.split(" ") #THe ability to add multiple files seperated by a space
            all_found = True
            for source in sources:
                try:
                    rss_feeds_file_path = script_dir / source
                    lines = Path(rss_feeds_file_path).read_text(encoding='utf-8').splitlines()
                    rss_feeds_data.extend(lines)
                except FileNotFoundError:
                    print(Style.NORMAL + Fore.RED + f'Can\'t find "{source}". Make sure the file is in the same directory as hawker.py')
                    all_found = False
            if all_found and rss_feeds_data:
                return "\n".join(rss_feeds_data)
            else:
                print(Fore.YELLOW + "Please re-enter valid file name(s).\n")

def rss_feed_to_list():
    rss_feeds_data = get_sources_file().splitlines()
    search_words = []
    search_mode = input("Type 'e' to exclude or 'i' to include searchwords? Leave empty to disable\n$").lower()
    if search_mode == 'e' or search_mode == 'i':
        search_words = input("Type words, seperated by '/'\n$")
        search_words = search_words.split('/')

    rss_feeds_list = []
    for line in rss_feeds_data:
        if line == '' or line[0] == '#':
            continue
        rss_feeds_list.append(line)
    for source in rss_feeds_list:
        feed(source, search_mode, search_words)
        print(Style.NORMAL + Fore.GREEN + f'𓅪  {source}')

#################################
### INIT SETTINGS AND RUN APP ###
#################################


#Gets desired number of articles to be displayed
def get_num_articles():
    while True:
        num = input(Style.BRIGHT + "Number of articles(enter number, default = 5)?\n$")
        if num.isnumeric():
            return int(num) 
        elif num == '':
            return 5
        else:
            print(Fore.RED + "Wrong format! (only integers like 1,5,10 etc.)")

#C_MODE:

def get_c_mode():
    while True:
        c_mode = input(Style.BRIGHT + "Continious mode? Press 'y' or 'n'\n$")
        if c_mode == 'y' or c_mode == 'Y':
            return True 
        elif c_mode == '' or c_mode == 'n' or c_mode == 'N':        
            return False
        else:
            print("Press 'y' for yes, 'n' for no or leave empty for default (n)")

#############
### START ###
#############

def start_hawker():
    init(autoreset=True) #resets colors after print
    display_splash()
    print(Style.DIM + "Made by @Schnookel, 2025")
    print("HAWK, HAWK! Get RSS news from the wingtips of hawker.py\n")

    rss_feed_to_list()
    num_of_articles = get_num_articles() 

    if get_c_mode():

        def c_mode_function():
            threading.Timer(int(update_time), c_mode_function).start()
            hawk(num_of_articles)

        while True:
            update_time = input("Enter update time in seconds (default 300)")
            if update_time.isnumeric() and int(update_time) > 0:
                c_mode_function()
            elif update_time == '':
                update_time = 300
                c_mode_function()
            else:
                print(Fore.RED + "Wrong input, enter number in seconds or leave empty for default (300)")
    hawk(num_of_articles)

if __name__ == '__main__':
    start_hawker()
