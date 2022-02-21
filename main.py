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


def get_category_link(url_link, category_name):
    # Fonction de recuperation de la liste des liens de chaque categorie
    page = requests.get(url_link)
    category_soup_content = BeautifulSoup(page.content, 'html.parser')
    category_link = ""
    ul_nav_list = category_soup_content.find_all("ul", class_="nav nav-list")
    lis_categories = ul_nav_list[0].find_all("li")
    for li in lis_categories:
        a_label = li.find("a")
        if re.sub("\n|\s","",a_label.string) == category_name:
            link = a_label["href"]
            category_link = link.replace("../", "https://books.toscrape.com/")
    return category_link


def get_categories_list(url_link):
    # Fonction de recuperation de la liste des liens de chaque categorie
    page = requests.get(url_link)
    categories_soup_content = BeautifulSoup(page.content, 'html.parser')

    categories_list = []

    ul_nav_list = categories_soup_content.find_all("ul", class_="nav nav-list")
    lis_categories = ul_nav_list[0].find_all("li")
    for li in lis_categories:
        a_label = li.find("a")
        string_category = re.sub("\n|\s", "", str(a_label.string))
        if string_category != 'Books' and string_category != 'None':
            categories_list.append(string_category)
    return categories_list

"""
def get_categories_link_list(url_link):
    # Fonction de recuperation de la liste des liens de chaque categorie
    categories_link_list = []
    ul_nav_list = page_content.find_all("ul", class_="nav nav-list")
    lis_categories = ul_nav_list[0].find_all("li")
    for li in lis_categories:
        a_balise = li.find("a")
        link = a_balise["href"]
        categories_link_list.append("https://books.toscrape.com/" + link)
    return categories_link_list
"""

def get_book_link_in_page(url_link):
    # Fonction renvoyant la liste des url de livre d'un page

    # declaration de la liste a retourner
    page_book_link_list = []

    page = requests.get(url_link)
    page_soup_content = BeautifulSoup(page.content, 'html.parser')
    articles_container = page_soup_content.find_all("article")
    for article in articles_container:
        h3_balise = article.find("h3")
        a_link = h3_balise.find("a")
        link = a_link["href"]
        page_book_link_list.append(link.replace("../../..", "https://books.toscrape.com/catalogue"))
    return page_book_link_list

def get_data_book(url_link):
    # Fonction de recuperation des information sur un livre
    page = requests.get(url_link)
    book_soup_content = BeautifulSoup(page.content, 'html.parser')
    book_table = get_book_page_table(book_soup_content)
    book_data_list = [url_link, book_table["UPC"],
                     get_book_title(book_soup_content),
                     book_table["Price (incl. tax)"],
                     book_table["Price (excl. tax)"],
                     get_book_availability(book_soup_content),
                     get_book_description(book_soup_content),
                     get_book_category(book_soup_content),
                     get_book_review_rating(book_soup_content),
                     get_image_url(book_soup_content)]
    return book_data_list


def get_result_filename():
    # Fonction retournant le fichier de resultat
    choice_result_filename = input(
        "Entrer le nom du fichier de resultat sans extension (si laissé a vide le nom sera forcé a 'resultat') :")

    # Si nom de fichier vide force le nom 'resultat'
    if choice_result_filename == "":
        choice_result_filename = "resultat"

    current_directory = getcwd()
    result_filename_defined = current_directory + "\\" + choice_result_filename + ".csv"
    return result_filename_defined

def fill_result_file(file_path, line_to_fill):
    # Fonction pour rajouter un ligne dans le fichier resultat
    # Declaration variable
    fileObj = Path(file_path)

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

    # si le fichier resultat.csv existe j'ajoute la ligne d'information pour un livre
    if fileObj.exists():
        with open(result_filename, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(line_to_fill)


def get_choice_menu_UI():
    execution_mode_code = ""
    # Menu d'execution
    print("###########################################################")
    print("#                                                         #")
    print("#               Scraping Book To Scrap                    #")
    print("#                                                         #")
    print("###########################################################")
    print("\n")
    print("1 : recuperation d'un livre.")
    print("2 : recuperation d'une categorie.")
    print("3 : recuperation du site complet.")
    print("4 : Sortie sans execution.")

    # Demande d'entrée du mode voulu : livre, category, complet
    execution_mode_code = input("Entrez le chiffre du mode d'execution souhaité :")
    return execution_mode_code


def test_url(url):
    # Test de la reponse de l'url
    reponse_get_request = requests.get(url)
    if reponse_get_request.status_code == 200:
        url_to_test = url
    else:
        print("erreur sur l'url : " + str(reponse_get_request))
        sys.exit()
    return url_to_test

# partie main du programme


# intialisation variable


execution_mode = ""
url_OK = ""
url_entry = ""


# Recuperation des argument passé au programme

if len(sys.argv) > 1 and str(sys.argv[1]) == "livre":

    # Partie livre
    url_OK = test_url(sys.argv[2])
    execution_mode = "1"

elif len(sys.argv) > 1 and str(sys.argv[1]) == "categorie":

    # Partie categorie
    url_OK = test_url(sys.argv[2])
    execution_mode = "2"

elif len(sys.argv) > 1 and str(sys.argv[1]) == "complet":

    # Partie site complet
    url_OK = test_url(sys.argv[2])
    execution_mode = "3"

else:
    # Sans argument passage en mode ui menu
    execution_mode = get_choice_menu_UI()


# Gestion du mode d'execution du programme

# Gestion du choix
if execution_mode == "1":

    # pour un seul livre
    result_filename = get_result_filename()
    # Demande d'url si url null car provenant du menu
    if url_OK == "":
        url_entry = input("Entre l'url du livre a recuperer :")
        url_OK = test_url(url_entry)

    line_to_write = get_data_book(url_OK)
    fill_result_file(result_filename, line_to_write)

elif execution_mode == "2":

    # pour une catégorie
    result_filename = get_result_filename()
    list_link_in_category = []
    # Demande d'url si url null car provenant du menu
    if url_OK == "":
        url_entry = input("Entre l'url du livre a recuperer :")
        url_OK = test_url(url_entry)

    list_link_in_category = get_book_link_in_page(url_OK)
    for link in list_link_in_category:
        line_to_write = get_data_book(link)
        fill_result_file(result_filename, line_to_write)

elif execution_mode == "3":
    # Pour le site entier
    print(" site complet en construction")

elif execution_mode == "4":
    # sortie du programme
    sys.exit()
else:
    print("entree incorrecte. Sortie du programme !" + str(execution_mode))
