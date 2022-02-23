"""
    import des modules necessaire
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
from pathlib import Path
import csv
import os
from os import getcwd

"""
############################################### section fonctions ######################################################
"""

"""
######## Fonction gerant les données de livre ########
"""


# Fonction de recuperation du titre du livre
def get_book_title(page_content):
    book_title = page_content.h1.string
    return book_title


# Fonction de recuperation de la category du livre
def get_book_category(page_content):
    book_category_line = page_content.find_all(href=re.compile("/category/books/"))
    return book_category_line[0].string


# Fonction de recuperation de la description du livre
def get_book_description(page_content):
    book_desription = page_content.find_all("meta", attrs={"name": "description"})
    description_to_clean = book_desription[0].get("content")
    return description_to_clean.strip()


# Fonction de recuperation de l'url de l'image d'un livre
def get_image_url(page_content):
    image_tag = page_content.find("img")
    image_short_url = image_tag["src"]
    image_url = image_short_url.replace("../..", "https://books.toscrape.com")
    return image_url


# Fonction de recuperation du rating d'un livre
def get_book_review_rating(page_content):
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


# Fonction de recupération de l'upc d'un livre
def get_book_page_table(page_content):
    book_table_datas = {}
    table = page_content.find_all("table", class_="table table-striped")
    for rows in table[0].find_all(lambda tag: tag.name == 'tr'):
        book_table_datas[rows.th.string] = rows.td.string
    return book_table_datas


# Fonction de recuperation et transformation en integer du nombre de livre disponible
def get_book_availability(page_content):
    availability_number = ""
    book_table_temp = get_book_page_table(page_content)
    extracted_availability_number = [int(s) for s in re.findall(r'\d', book_table_temp["Availability"])]
    for number in extracted_availability_number:
        availability_number += str(number)
    return availability_number


# Fonction de recuperation des information sur un livre
def get_data_book(url_link):
    page = requests.get(url_link)
    book_soup_content = BeautifulSoup(page.content, 'html.parser')

    # Recuperation des donnée tableau de la page du livre
    book_table = get_book_page_table(book_soup_content)

    # Traitement des prix afin de supprimé la devise
    price_without_tax = re.findall("\\d+\\.\\d+", book_table["Price (excl. tax)"])
    price_with_tax = re.findall("\\d+\\.\\d+", book_table["Price (incl. tax)"])

    # Entrée des donnée du livre dans la liste a retourné
    book_data_list = [url_link,
                      book_table["UPC"],
                      get_book_title(book_soup_content),
                      price_with_tax[0],
                      price_without_tax[0],
                      get_book_availability(book_soup_content),
                      get_book_description(book_soup_content),
                      get_book_category(book_soup_content),
                      get_book_review_rating(book_soup_content),
                      get_image_url(book_soup_content)]
    return book_data_list


"""
######## Fonction gérant les données de categorie ##########
"""


# Fonction de recuperation de la liste des liens de chaque categorie
def get_category_link(category_name):
    page = requests.get("https://books.toscrape.com/catalogue/category/books_1/index.html")
    category_soup_content = BeautifulSoup(page.content, 'html.parser')
    category_link = ""
    ul_nav_list = category_soup_content.find_all("ul", class_="nav nav-list")
    lis_categories = ul_nav_list[0].find_all("li")
    for li in lis_categories:
        a_label = li.find("a")
        category_to_test = re.sub("\\n|\\s", "", str(a_label.string))
        if category_to_test == category_name:
            c_link = li.a["href"]
            category_link = c_link.replace("../", "https://books.toscrape.com/catalogue/category/")
    return category_link


# Fonction de recuperation de la liste des noms de chaque categorie
def get_categories_list():
    page = requests.get("https://books.toscrape.com/catalogue/category/books_1/index.html")
    categories_soup_content = BeautifulSoup(page.content, 'html.parser')

    categories_list = []

    ul_nav_list = categories_soup_content.find_all("ul", class_="nav nav-list")
    lis_categories = ul_nav_list[0].find_all("li")
    for li in lis_categories:
        a_label = li.find("a")
        string_category = re.sub("\\n|\\s", "", str(a_label.string))
        if string_category != 'Books' and string_category != 'None':
            categories_list.append(string_category)
    return categories_list


# Fonction de recuperation de la category d'une url donnée
def get_category_from_url(url_link):
    page = requests.get(url_link)
    soup_category_page = BeautifulSoup(page.content, 'html.parser')
    ul_breadcrumb = soup_category_page.find_all('ul', class_="breadcrumb")
    li_active = ul_breadcrumb[0].find_all("li", class_="active")
    category_to_return = li_active[0].string
    return category_to_return


"""
####### Fonction de navigation #########
"""


# Fonction pour renvoyer le nombre de page d'index en integer
def get_number_of_page(url_link):
    page = requests.get(url_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    pager_ul = soup.find_all("ul", class_="pager")
    if len(pager_ul) != 0:
        pager_lis = pager_ul[0].find_all("li", class_="current")
        string_pager = pager_lis[0].string
        entire_number_of_page = re.sub("\\n|\\s", "", string_pager)
        entire_number_of_page = re.sub("Page1of", "", entire_number_of_page)
    else:
        entire_number_of_page = 1

    return int(entire_number_of_page)


# Fonction renvoyant la prochaine page du pager
def get_next_page_link(url_link):
    page = requests.get(url_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    pager_ul = soup.find_all("ul", class_="pager")
    pager_lis = pager_ul[0].find_all("li", class_="next")
    href_next_page = pager_lis[0].a["href"]
    current_page_name = url_link.split("/")[-1]
    current_url_root_directory = re.sub(current_page_name, "", url_link)
    link_next_page = current_url_root_directory + href_next_page
    return link_next_page


# Fonction renvoyant la liste des url de livre d'un page categorie
def get_book_link_in_page(url_link):

    # declaration de la liste a retourner
    page_book_link_list = []

    page = requests.get(url_link)
    page_soup_content = BeautifulSoup(page.content, 'html.parser')
    articles_container = page_soup_content.find_all("article")
    for article in articles_container:
        h3_balise = article.find("h3")
        a_link = h3_balise.find("a")
        b_link = a_link["href"]
        page_book_link_list.append(b_link.replace("../../..", "https://books.toscrape.com/catalogue"))
    return page_book_link_list


"""
######## Fonction de gestion du fichier de sortie ##########
"""


# Fonction retournant le fichier de resultat incluant le dossier par type d'extraction
def get_result_filename(filename, directory_type):
    if filename == "":
        choice_result_filename = input(
            "Entrer le nom du fichier de resultat sans extension (si laissé a vide le nom sera forcé a 'resultat') :")

        # Si nom de fichier vide force le nom 'resultat'
        if choice_result_filename == "":
            choice_result_filename = "resultat"
    else:
        choice_result_filename = filename

    # Recuperation du repertoire courant
    current_directory = getcwd()

    # Definition du repertoire de destination du fichier
    my_directory = Path(current_directory + "\\" + directory_type)

    # Si le repertoire de destination n'existe pas
    if not my_directory.exists():
        my_new_directory = Path(my_directory.name + "\\" + "Archive")
        os.makedirs(my_new_directory)

    # Si le fichier existe deja l'archiver dans le repertoire archive avec un timestamp inclu dans le nom
    # a developper

    # Defintion du path du fichier de resultat a retourner
    result_filename_defined = my_directory.name + "\\" + choice_result_filename + ".csv"
    return result_filename_defined


# Fonction pour creer le fichier de sortie si il n'existe pas et rajouter un ligne
def fill_result_file(file_path, line_to_fill):

    # Declaration variable
    my_file = Path(file_path)

    # Declaration des l'en-tete des colonnes du fichier
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
    if not my_file.exists():
        with open(result_filename, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(en_tete)

    # si le fichier resultat.csv existe j'ajoute la ligne d'information pour un livre
    if my_file.exists():
        with open(result_filename, 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(line_to_fill)


"""
############################# Fonction gestion UI #######################
"""


# Fonction du menu d'execution
def get_choice_menu_ui():
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
    return str(execution_mode_code)


# Fonction de nettoyage de la console
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


# Fonction qui test la valeur de l'url et sa reponse
def test_url(url):
    if "https://" in url or "http://" in url:
        reponse_get_request = requests.get(url)
        if reponse_get_request.status_code == 200:
            url_to_test = url
        else:
            print("erreur sur l'url : " + str(reponse_get_request))
            url_to_test = ""
    else:
        url_to_test = ""

    return url_to_test


# Fonction pour testé si une string correspond a une categorie existante et renvoi une string vide si non reconnu
def test_category(category_to_test):
    category_to_return = ""
    categories_list = get_categories_list()
    for category_name in categories_list:
        if str(category_name) == category_to_test:
            category_to_return = category_name

    return str(category_to_return)


"""
######################################## Fin de la section Fonctions ###################################################
"""

"""
########################################## Section main du programme ###################################################
"""

# intialisation variable

execution_mode = ""
url_OK = ""
url_entry = ""
category_OK = ""
result_filename = ""

"""
##### Recuperation des argument passé au lancement du programme ######
"""

"""
##### Determine le type d'execution demandé ##########################
"""


# Mode d'execution livre
if len(sys.argv) > 1 and str(sys.argv[1]) == "livre":

    # initialisation de la variable url a consulter : laisse a blanc si non valide
    if len(sys.argv) == 3:
        url_OK = test_url(sys.argv[2])
    else:
        url_OK = ""

    execution_mode = "1"

# Mode d'execution categorie
elif len(sys.argv) > 1 and str(sys.argv[1]) == "categorie":

    # Intialise la variable url ou categorie le cas echeant : laisse a blanc si non reconnu
    if len(sys.argv) == 3:
        url_OK = test_url(sys.argv[2])
        if url_OK == "":
            category_OK = test_category(sys.argv[2])
    else:
        url_OK = ""
        category_OK = ""

    execution_mode = "2"

# Mode d'execution complet
elif len(sys.argv) > 1 and str(sys.argv[1]) == "complet":

    # Partie site complet

    execution_mode = "3"

else:
    # Sans argument passage en mode ui menu
    execution_mode = get_choice_menu_ui()

"""
################################ Gestion du mode d'execution du programme ##############################################
"""


# execution pour un seul livre #########################################
if execution_mode == "1":

    # Demande d'url si url null
    if url_OK == "":
        url_entry = input("Entre l'url du livre a recuperer :")
        url_OK = test_url(url_entry)

    # Recuperation des donnée du livre
    line_to_write = get_data_book(url_OK)

    # declaration du fichier de resultat
    result_filename = get_result_filename(line_to_write[2], "livre")

    # Envoi des données dans le fichier de resultat
    fill_result_file(result_filename, line_to_write)

# Execution pour une categorie #######################################
elif execution_mode == "2":

    # Declaration de la liste des url des livre de la categorie et du nombre de page de la categorie
    list_link_in_category = []
    page_number = 1

    # definition de categorie si url defini et categorie nul
    if url_OK != "" and category_OK == "":
        category_OK = get_category_from_url(url_OK)

    # Definition d'url si url null et categorie definie
    elif url_OK == "" and category_OK != "":
        url_OK = test_url(get_category_link(category_OK))

    # Recuperation d'url si url null et categorie null
    else:
        # Nettoyage de la sonsole et affichage de la liste des category
        cls()
        while url_OK == "":
            print("Aucune url ou categorie correcte n'ont encore été saisies :")
            print(get_categories_list())
            category_entry = input("Entre le nom de la categorie choisie dans la liste ci-dessus (case sensitive) :")
            if test_category(category_entry) != "":
                url_OK = test_url(get_category_link(category_entry))
                category_OK = category_entry
            else:
                cls()
                print(category_entry + " n'est pas une categorie du site !")

    # declaration du fichier de resultat
    result_filename = get_result_filename(category_OK, "categorie")

    # Recuperation du nombre de page de la catégorie
    number_of_page = get_number_of_page(url_OK)

    # Nettoyage de la console
    cls()

    # Affichage de debut d'execution sur la console
    print("===================================================")
    print("extraction de la catégorie  : " + category_OK)
    print("url de la catégorie : " + url_OK)
    print("nbr. de page de la categorie : " + str(number_of_page))
    print("En cours d'extraction...")

    # Navigation dans les differentes pages de la categorie
    while page_number <= number_of_page:
        # Recuperation des url de livre de la page
        list_link_in_category = get_book_link_in_page(url_OK)
        for link in list_link_in_category:
            line_to_write = get_data_book(link)
            fill_result_file(result_filename, line_to_write)
        if page_number < number_of_page:
            url_OK = get_next_page_link(url_OK)
        page_number += 1

    # Affichage de la fin d'execution sur la console
    print("Extraction terminée !")
    print("Emplacement du fichier de resultat : " + result_filename)
    print("===================================================")


# Execution pour le site entier ###############################################
elif execution_mode == "3":
    # nettoyage de la console
    cls()

    # Initialisation variable
    categories_name_list = get_categories_list()

    for category in categories_name_list:
        # Test de l'url de la categorie
        url_OK = test_url(get_category_link(category))

        # Affichage de debut d'execution sur la console
        print("===================================================")
        print("extraction de la catégorie  : " + category)
        print("url de la catégorie : " + url_OK)
        print("En cours d'extraction...")

        # initialisation de la variable numero de page
        page_number = 1

        # declaration du fichier de resultat
        result_filename = get_result_filename(category, "complet")

        # Recuperation du nombre de page de la catégorie
        number_of_page = get_number_of_page(url_OK)
        print("nbr. de page de la categorie : " + str(number_of_page))

        # Navigation dans les differentes pages de la categorie
        while page_number <= number_of_page:
            # Recuperation des url de livre de la page
            list_link_in_category = get_book_link_in_page(url_OK)
            for link in list_link_in_category:
                line_to_write = get_data_book(link)
                fill_result_file(result_filename, line_to_write)
            if page_number < number_of_page:
                url_OK = get_next_page_link(url_OK)
            page_number += 1

        # Affichage de la fin d'execution sur la console
        print("Extraction terminée !")
        print("Emplacement du fichier de resultat : " + result_filename)
        print("===================================================")

# Sortie du programme ##########################################################
elif execution_mode == "4":
    sys.exit()
else:
    print("entree incorrecte. Sortie du programme !" + str(execution_mode) + "n'etait pas attendu !")
