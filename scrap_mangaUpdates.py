import requests
import mysql.connector
from bs4 import BeautifulSoup

# image url extraction is not working
# https://www.mangaupdates.com/genres.html
# https://www.mangaupdates.com/series.html?perpage=100&genre=Action&orderby=rating

host = "localhost"
user = "root"
passwd = "toor"
database_name = "mangaka"


def get_soup(url):
    parser = 'lxml'

    req_obj = requests.get(url)
    data = req_obj.content
    soup = BeautifulSoup(data, parser)
    return(soup)

def extract_particular_genre_details(url = ""):
    soup = get_soup(url)
    mangas = soup.find_all('div', class_ = 'col-12 col-lg-6 p-3 text')
    
    all_manga_details = []

    for manga in mangas:
        each_manga_details = []
        
        try:
            manga_name = manga.find('div', class_ = "col text p-1 pl-3").div.b.text
            manga_year = manga.find('div', class_ = "col text p-1 pl-3").find_all('div', class_ = "text")[2].text.split(' ')[0]
            manga_genre = manga.find('div', class_ = "col text p-1 pl-3").find('div', class_ = "textsmall").a['title']
            manga_rating = manga.find('div', class_ = "col text p-1 pl-3").find_all('div', class_ = "text")[2].b.text
            manga_link = manga.find('div', class_ = "col-auto align-self-center series_thumb p-0").a['href']
            manga_pic_link = str(manga.find('div', class_ = "col-auto align-self-center series_thumb p-0").a.img).split('"')[1]
        
            each_manga_details = [manga_name, manga_year, manga_genre, manga_rating, manga_link, manga_pic_link]
            all_manga_details.append(each_manga_details)
    
        except Exception as e:
            print(f'{manga_name} - started error - {e}')
    
    return(all_manga_details)


def extract_all_genre_details(url = ""):
    soup = get_soup(url)
    genres = soup.find_all('div', class_ = 'pl-3 pt-3 pr-3 releasestitle')
    about_genres = soup.find_all('div', class_ = 'p-3 pb-4 text')

    all_genre = []

    for (genre, about_genre) in zip(genres, about_genres):
        each_genre = [] #temporary list just to hold a single genre and about_genre
        
        #converting in list for better accessebility later when dealing with database
        
        each_genre.append(genre.text)
        each_genre.append(about_genre.text.split('.')[0])
        
        all_genre.append(each_genre)

    return(all_genre)

# function below is created because mysql table names follow certain rules
def format_sqltable_name(string_):  
    words = list(string_)
    words = ['_' if i==' ' else i for i in words]
    words = ['_' if i=='-' else i for i in words]
    string_ = "".join(words)
    return(string_)
    
def create_database():
    db = mysql.connector.connect(
        host = host,
        user = user,
        passwd = passwd,
        auth_plugin='mysql_native_password'
    )
    mycursor = db.cursor()
    mycursor.execute(f"CREATE DATABASE {database_name}")


def create_mysql_tables():
    db = mysql.connector.connect(
        host = host,
        user = user,
        passwd = passwd,
        database = database_name,
        auth_plugin='mysql_native_password'
    )
    mycursor = db.cursor()
    genres = extract_all_genre_details(url = "https://www.mangaupdates.com/genres.html")

    for genre in genres:
        try:
            genre[0] = format_sqltable_name(genre[0])
            mycursor.execute(f"CREATE TABLE {genre[0]} (manga_ID smallint UNSIGNED PRIMARY KEY AUTO_INCREMENT, manga_name VARCHAR(200), manga_year smallint UNSIGNED, manga_genre VARCHAR(250), manga_rating float(4,2), manga_link VARCHAR(150), manga_pic_link VARCHAR(150))")
        except Exception as e:
            print(e)
        

def insert_data_in_tabels():
    db = mysql.connector.connect(
        host = host,
        user = user,
        passwd = passwd,
        database = database_name,
        auth_plugin='mysql_native_password'
    )
    mycursor = db.cursor()
    
    no_of_pages = int(input("\n\nhow many pages do you want to scratch for each genre: "))
    print("\nNow you will see each genre's completion message. 'done inseting' does not mean all mangas were inserted.\n")
    genres = extract_all_genre_details(url = "https://www.mangaupdates.com/genres.html")

    for genre in genres:
        genre[0] = format_sqltable_name(genre[0])
        for page in range(1, no_of_pages + 1):
            if (page == 1):
                particular_genre_mangas = extract_particular_genre_details(url = f'https://www.mangaupdates.com/series.html?perpage=100&genre={genre[0]}&orderby=rating')
            elif (page > 1):
                particular_genre_mangas = extract_particular_genre_details(url = f'https://www.mangaupdates.com/series.html?page={page}&perpage=100&genre={genre[0]}&orderby=rating')
            try:
                for manga in particular_genre_mangas:
                    mycursor.execute(f"INSERT INTO {genre[0]} (manga_name, manga_year, manga_genre, manga_rating, manga_link, manga_pic_link) VALUES {tuple(manga)}")
                db.commit()
            except Exception as e:
                print(e)
        print(f"done inserting {genre[0]}'s mangas' details")
  
def interface():
    print("""
**************************************
if any error comes, handle it yourself
**************************************
Press:
1. to create database
2. to create tables in an existing database
3. to insert values in existing database already having tables
0. if you know nothing and want it done all by itself

enter q to quit
or enter anything for that matter :()
**************************************\n
""")
    
    while(True):
        user_input  = input("")
        if (user_input == "1"):
            create_database()
            print("\n\n Done!!!")
        elif (user_input == "2"):
            create_mysql_tables()
            print("\n\n Done!!!")
        elif (user_input == "3"):
            insert_data_in_tabels()
            print("\n\n Done!!!")
        elif (user_input == "0"):
            create_database()
            print("Database Created!!!")
            create_mysql_tables()
            print("Tables Created!!!")
            insert_data_in_tabels()
            print("\n\n Completed!!!")
            exit()
        else:
            exit()

interface()