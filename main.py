from bs4 import BeautifulSoup
import requests
import re
from dateutil.parser import parse

"""
what it does?
- parses all movies and their data in a list-page
- paginates to last page automatically while keeping track of their cookie and keys
- sanitizes/cleans up the movie name, year and rating to usable string
- writes them in a letterboxd-supported .csv file (uses Rating10)
"""

#input list's link here
next_page = f"https://www.imdb.com/user/ur54854806/ratings"
total = 0
page = 1
i = 1
with open('fixed.csv', 'w') as f:
    f.write(f"Title,Year,Rating10\n")
    while i > 0:
        r = requests.get(next_page)
        soup = BeautifulSoup(r.content, 'html5lib')
        data = soup.findAll('div',attrs={'class':'lister-item-content'})
        total = total + len(data)
        print(f"parsing page {page}, found {len(data)} movies... writing them to csv, {total} so far...")
        for movie in data:
            singleMovie = movie.find('h3', attrs={'class':'lister-item-header'})
            mov = singleMovie.find('a')
            year = movie.find('span', attrs={'class':'lister-item-year text-muted unbold'})
            rating_before = movie.find('div', attrs={'class':'ipl-rating-star ipl-rating-star--other-user small'})
            rating_now = rating_before.find('span', attrs={'class':'ipl-rating-star__rating'})
            year_parsed = re.sub(r"\((.*?)\)", r"\1", year.string)
            #https://stackoverflow.com/questions/40121822/extracting-year-from-string-in-python
            f.write(f"{str(mov.string).replace(',','')},{str(parse(year_parsed, fuzzy=True).year)},{str(rating_now.string)}\n")

        # this is to avoid imdb's clever key-ed pagination
        try:
            next_page_element = soup.find('a', attrs={'class':'flat-button lister-page-next next-page'})
            next_page = f"https://www.imdb.com{next_page_element['href']}"
            page = page+1
        except:
            no_next_page = soup.find('a',attrs={'class':'flat-button next-page disabled'})
            if no_next_page['href'] == "#":
                print(f"Reached the last page, we break now.")
                break

print(f"Success, parsed and wrote {total} movies from {page} pages in total")
f.close()
