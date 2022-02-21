"""
    import des modules necessaire
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
from pathlib import Path
import csv
from os import getcwd


"""
    declaration des fonctions de recuperation de données
"""


def get_book_title(page_content):
    # fonction de recuperation du titre du livre
    book_title = page_content.h1.string
    return book_title


def get_book_category(page_content):
    # fonction de recuperation de la category du livre
    book_category_line = page_content.find_all(href=re.compile("/category/books/"))
    return book_category_line[0].string


def get_book_description(page_content):
    # fonction de recuperation de la description du livre
    book_desription = page_content.find_all("meta", attrs={"name": "description"})
    description_to_clean = book_desription[0].get("content")
    return description_to_clean.strip()


def get_image_url(page_content):
    # Fonction de recuperation de l'url de l'image d'un livre
    image_tag = page_content.find("img")
    image_short_url = image_tag["src"]
    image_url = image_short_url.replace("../..", "https://books.toscrape.com")
    return image_url


def get_book_review_rating(page_content):
    # fonction de recuperation du rating d'un livre
    rating_level_to_return = ""
    book_review_rating = page_content.find_all("p", class_=re.compile("star-rating"))
    rating_level = book_review_rating[0].get("class")
    if rating_level[1] == "Zero":
        rating_level_to_return = "0\\5"
    elif rating_level[1] == "One":
        rating_level_to_return = "1\\5"
    elif rating_level[1] == "Two":
        rating_level_to_return = "2\\5"
    elif rating_level[1] == "Three":
        rating_level_to_return = "3\\5"
    elif rating_level[1] == "Four":
        rating_level_to_return = "4\\5"
    elif rating_level[1] == "Five":
        rating_level_to_return = "5\\5"
    return rating_level_to_return


def get_book_page_table(page_content):
    # fonction de recupération de l'upc d'un livre
    book_table_datas = {}
    table = page_content.find_all("table", class_="table table-striped")
    for rows in table[0].find_all(lambda tag: tag.name == 'tr'):
        book_table_datas[rows.th.string] = rows.td.string
    return book_table_datas


def get_book_availability(page_content):
    # fonction de recuperation et transformation en integer du nombre de livre disponible
    availability_number = ""
    book_table_temp = get_book_page_table(page_content)
    extracted_availability_number = [int(s) for s in re.findall(r'\d', book_table_temp["Availability"])]
    for number in extracted_availability_number:
        availability_number += str(number)
    return availability_number


def get_categories_link_list(page_content):
    # Fonction de recuperation de la liste des liens de chaque categorie
    categories_link_list = []
    ul_nav_list = page_content.find_all("ul", class_="nav nav-list")
    lis_categories = ul_nav_list.find_all("li")
    for li in lis_categories:
        a_balise = li.find("a")
        link = a_balise["href"]
        categories_link_list.append("https://books.toscrape.com" + link)
    return categories_link_list


def get_data_book(url_link, page_content):
    # Fonction de recuperation des information sur un livre
    book_table = get_book_page_table(page_content)
    book_data_list = [url_link, book_table["UPC"],
                     get_book_title(page_content),
                     book_table["Price (incl. tax)"],
                     book_table["Price (excl. tax)"],
                     get_book_availability(page_content),
                     get_book_description(page_content),
                     get_book_category(page_content),
                     get_book_review_rating(page_content),
                     get_image_url(page_content)]
    return book_data_list


# partie main du programme


url = sys.argv[1]  # recuperation de l'url passé en argument dans le terminal
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

current_directory = getcwd()
result_filename = current_directory + "\\resultat.csv"
fileObj = Path(result_filename)

en_tete = ["product_page_url",
           "universal_ product_code",
           "title",
           "price_including_tax",
           "price_excluding_tax",
           "number_available",
           "product_description",
           "category",
           "review_rating",
           "image_url"]

# verifiation de l'existance du fichier si false je le crée et ajoute les en-tetes de colone

if not fileObj.exists():
    with open(result_filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(en_tete)

# si le fichier resultat.csv existe j'ajjoute la ligne d'information pour un livre
if fileObj.exists():
    line_to_write = get_data_book(url, soup)
    
    with open(result_filename, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(line_to_write)
    
