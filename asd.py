import time

import cloudscraper
from bs4 import BeautifulSoup, Tag

links = []
url = 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A8516&filter-sort=2'


def get_link(html):
    soup = BeautifulSoup(html, 'html.parser')
    for div in soup.find_all('div', class_='flex items-end lg:hidden'):  # type: Tag
        div = div.find('a')
        links.append((div.find('h3').text, div.get_attribute_list('href').pop()))


def get_scraper_and_max_pages():
    i = 0

    maxpages = ''
    scraper = None

    while not maxpages:
        try:
            time.sleep(1)
            scraper = cloudscraper.create_scraper(delay=1)
            soup = BeautifulSoup(scraper.get(url).text, 'html.parser')
            maxpages = soup.find_all('a', class_="pagination-item").pop().find('span').text
        except Exception as e:
            i+=1
            print('ERROR: ', i)


    return scraper, int(maxpages)

if __name__ == '__main__':
    scraper, maxpages = get_scraper_and_max_pages()
    #print(maxpages)

    for i in range(1, 2):
        soup = BeautifulSoup(scraper.get(url + '&page=' + str(i)).text, 'html.parser')
        for div in soup.find_all('div', class_='my-2'):
            print(div.find('a', class_="my-auto").get_attribute_list('href').pop())
            print(div.find('img', class_="mx-auto").get_attribute_list('src').pop())
            print(div.find('h3', class_="font-bold text-lg").text)
            print(div.find('abbr', class_="tip standard-date standard-datetime").get_attribute_list('data-epoch').pop())
            for div in div.find_all('div', class_='px-1')[1:]:
                print(div.find('a').get_attribute_list('href').pop())
            break
