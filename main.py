import time

import cloudscraper
from PyQt5 import QtSql
from PyQt5.QtSql import QSqlQuery
from bs4 import BeautifulSoup

links = []
url_forge = 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A7498&filter-sort=2'
url_fabric = 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A7499&filter-sort=2'

table_forge = '''
CREATE TABLE IF NOT EXISTS Forge (
    path        TEXT NOT NULL,
    name	    TEXT NOT NULL,
    icon	    TEXT NOT NULL,
    create_date INT NOT NULL,
    update_date INT NOT NULL,
    categories  TEXT NOT NULL DEFAULT 'Sin categoria',
    PRIMARY KEY(path));
'''

table_fabric = '''
CREATE TABLE IF NOT EXISTS Fabric (
    path        TEXT NOT NULL,
    name	    TEXT NOT NULL,
    icon	    TEXT NOT NULL,
    create_date INT NOT NULL,
    update_date INT NOT NULL,
    categories  TEXT NOT NULL DEFAULT 'Sin categoria',
    PRIMARY KEY(path));
'''


class Mod:
    def __init__(self, path, icon, name, create_date, update_Date, categories):
        self.path = path
        self.icon = icon
        self.name = name
        self.create_date = create_date
        self.update_Date = update_Date
        self.categories = categories

    def print(self):
        print(self.path)
        print(self.icon)
        print(self.name)
        print(self.create_date)
        print(self.update_Date)
        print('categories:')
        for x in self.categories:
            print('     ' + x)
        print('-----------------------------------------------------\n')


def exec(db, sql):
    if not db.exec(sql):
        print(db.lastError().text())


def execq(q):
    b = q.exec()
    if not b:
        print(q.lastError().text())
    return b


def crear_db():
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('test.db')

    if not db.open():
        print("DataBase Error:", db.lastError().databaseText())
    else:
        db.exec("PRAGMA foreign_keys = ON;")
        db = QSqlQuery()
        exec(db, table_forge)
        exec(db, table_fabric)


def get_scraper_and_max_pages(url, scraper=None):
    maxpages = ''

    while not maxpages:
        try:
            time.sleep(1)
            if scraper is None:
                scraper = cloudscraper.create_scraper(delay=1)
            soup = BeautifulSoup(scraper.get(url).text, 'html.parser')
            maxpages = soup.find_all('a', class_="pagination-item").pop().find('span').text
        except Exception as e:
            scraper = None

    return scraper, int(maxpages)


def get_path(div):
    try:
        return div.find('a', class_="my-auto").get_attribute_list('href').pop()
    except Exception:
        return 'PATH'


def get_icon(div):
    try:
        return div.find('img', class_="mx-auto").get_attribute_list('src').pop()
    except Exception:
        return 'NAME'


def get_name(div):
    try:
        return div.find('h3', class_="font-bold text-lg").text
    except Exception:
        return 'NAME'


def get_dates(div):
    try:
        fechas = div.find_all('abbr', class_="tip standard-date standard-datetime")
        update_date = fechas.pop().get_attribute_list('data-epoch').pop()
        create_date = fechas.pop().get_attribute_list('data-epoch').pop()
        return create_date, update_date
    except Exception:
        return 0, 0


def get_categories(div):
    try:
        categories = ''
        for div in div.find_all('div', class_='px-1')[1:]:
            categories += div.find('a').get_attribute_list('href').pop()+','
        return categories
    except Exception:
        return 'Sin categoria'


def save_mod(q, mod, table):
    q.prepare('INSERT INTO ' + table + ' (path, icon, name, create_date, update_date, categories)' 'VALUES (:path, :icon, :name, :create_date, :update_date, :categories)')
    q.bindValue(':path', mod.path)
    q.bindValue(':icon', mod.icon)
    q.bindValue(':name', mod.name)
    q.bindValue(':create_date', mod.create_date)
    q.bindValue(':update_date', mod.update_Date)
    q.bindValue(':categories', mod.categories)
    execq(q)


def get_mods(q, url, scraper, maxpages, loader):
    mods = []
    for i in range(1, maxpages+1):
        soup = BeautifulSoup(scraper.get(url + '&page=' + str(i)).text, 'html.parser')
        for div in soup.find_all('div', class_='my-2'):
            create_date, update_date = get_dates(div)
            save_mod(
                q,
                Mod(path=get_name(div), icon=get_icon(div), name=get_name(div), create_date=create_date, update_Date=update_date, categories=get_categories(div)),
                loader
            )
        print(loader+':', i, '/', maxpages)
    return mods


if __name__ == '__main__':

    crear_db()
    q = QtSql.QSqlQuery()

    #scraper, maxpages = get_scraper_and_max_pages(url_forge)
    #get_mods(q, url_forge, scraper, maxpages, 'Forge')
    scraper, maxpages = get_scraper_and_max_pages(url_fabric)
    get_mods(q, url_fabric, scraper, maxpages, 'Fabric')


