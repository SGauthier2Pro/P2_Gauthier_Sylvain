"""
    import des modules necessaire
"""
import time
import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import sys
from pathlib import Path
import csv
import os

"""
############################################### section fonctions ######################################################
"""

"""
######## Fonction de gestion des fichiers de sortie et des repertoires ##########
"""


def create_directory_structure():
    current_directory = os.getcwd()

    directories_list = [current_directory + "\\livre\\old",
                        current_directory + "\\categorie\\old",
                        current_directory + "\\images\\old"]
    for directory in directories_list:
        directory_to_create = Path(directory)
        if not directory_to_create.exists():
            print("Creation du repertoire : " + str(directory_to_create.resolve()))
            os.makedirs(directory_to_create)


def archive_if_exists(my_directory, my_filename, my_file_type):
    filepath_to_test = Path(my_directory + "\\" + my_filename + my_file_type)

    if filepath_to_test.exists():

        file_last_modification = time.strptime(time.ctime(os.stat(filepath_to_test.resolve()).st_mtime),
                                               "%a %b %d %H:%M:%S %Y")
        last_modification_string = time.strftime("_%Y%m%d_%H%M%S", file_last_modification)

        my_source = str(filepath_to_test.resolve())
        my_destination = str(my_directory + "\\old\\" + my_filename + last_modification_string + my_file_type)

        Path(my_source).rename(my_destination)


def get_result_filename(filename, *args):
    file_type = ".csv"
    directory_type = "categorie"

    for argument in args:
        if argument == "livre":
            directory_type = "livre"
        elif argument == "image":
            directory_type = "images"
            file_type = ".jpg"

    filename = re.sub("[,\"*?]", "", re.sub("[ \\/:]", "_", filename))
    choice_result_filename = filename + file_type

    current_directory = os.getcwd()
    my_directory = Path(current_directory + "\\" + directory_type)

    result_filename_defined = str(my_directory.resolve()) + "\\" + choice_result_filename

    archive_if_exists(str(my_directory), str(filename), str(file_type))

    return result_filename_defined


def fill_result_file(file_path, line_to_fill):
    my_file = Path(file_path)

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

    if not my_file.exists():
        with open(result_filename, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(en_tete)
            writer.writerow(line_to_fill)
    else:
        with open(result_filename, 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(line_to_fill)


"""
######## Fonction gerant les données de livre ########
"""


def get_book_title(page_content):
    book_title = page_content.h1.string
    return book_title


def get_book_category(page_content):
    book_category_line = page_content.find_all(href=re.compile("/category/books/"))
    return book_category_line[0].string


def get_book_description(page_content):
    book_description = page_content.find_all("meta", attrs={"name": "description"})
    description_to_clean = book_description[0].get("content")
    description_to_clean = description_to_clean.strip()
    description_to_return = description_to_clean[375:len(description_to_clean)]
    description_to_return_in_byte = str(description_to_return).encode('ascii', 'ignore')
    description_to_return = description_to_return_in_byte.decode('utf8', 'ignore')
    if len(description_to_return) == 0:
        description_to_return = description_to_clean
    return str(description_to_return)


def get_image_url(page_content):
    image_tag = page_content.find("img")
    image_short_url = image_tag["src"]
    image_url = image_short_url.replace("../..", "https://books.toscrape.com")
    return image_url


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


def get_book_page_table(page_content):
    book_table_datas = {}
    table = page_content.find_all("table", class_="table table-striped")
    for rows in table[0].find_all(lambda tag: tag.name == 'tr'):
        book_table_datas[rows.th.string] = rows.td.string
    return book_table_datas


def get_book_availability(availability_string):
    availability_number = ""
    extracted_availability_number = [int(s) for s in re.findall(r'\d', availability_string)]
    for number in extracted_availability_number:
        availability_number += str(number)
    return availability_number


def get_price_without_tax(price_without_tax_string):
    price_without_tax = re.findall("\\d+\\.\\d+", price_without_tax_string)
    return price_without_tax[0]


def get_price_with_tax(price_with_tax_string):
    price_with_tax = re.findall("\\d+\\.\\d+", price_with_tax_string)
    return price_with_tax[0]


def get_data_book(url_link):
    page = requests.get(url_link)
    book_soup_content = BeautifulSoup(page.content, 'html.parser')

    print("Extraction des données du livre : " + get_book_title(book_soup_content))
    print("url du livre : " + url_link)

    book_table = get_book_page_table(book_soup_content)

    book_data_list = [url_link,
                      book_table["UPC"],
                      get_book_title(book_soup_content),
                      get_price_with_tax(book_table["Price (incl. tax)"]),
                      get_price_without_tax(book_table["Price (excl. tax)"]),
                      get_book_availability(book_table["Availability"]),
                      get_book_description(book_soup_content),
                      get_book_category(book_soup_content),
                      get_book_review_rating(book_soup_content),
                      get_image_url(book_soup_content)]

    download_book_picture(book_data_list[9], book_data_list[2])

    return book_data_list


def download_book_picture(url_link, local_picture_name):
    remote_picture_url = url_link
    picture_filepath = Path(get_result_filename(local_picture_name, "image"))

    if not picture_filepath.exists():
        print("telechargement de l'image du livre " + local_picture_name + " a l'adresse :" + remote_picture_url)
        if requests.get(url_link).status_code == 200:
            urllib.request.urlretrieve(remote_picture_url, picture_filepath)
            print("Telechargement terminé avec succès !")
        else:
            print("Image du livre " + local_picture_name + " indisponible !")
    else:
        print("Image du livre déjà existante !")


"""
######## Fonction gérant les données de categorie ##########
"""


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


def get_category_from_url(url_link):
    page = requests.get(url_link)
    soup_category_page = BeautifulSoup(page.content, 'html.parser')
    ul_breadcrumb = soup_category_page.find_all('ul', class_="breadcrumb")
    li_active = ul_breadcrumb[0].find_all("li", class_="active")
    category_to_return = li_active[0].string
    return category_to_return


def test_category(category_to_test):
    category_to_return = ""
    categories_list = get_categories_list()
    for category_name in categories_list:
        if str(category_name) == category_to_test:
            category_to_return = category_name

    return str(category_to_return)


def get_all_books_in_category(url_link, category_name, result_filepath):

    page_number = 1

    number_of_page = get_number_of_page(url_link)

    print("===================================================")
    print("extraction de la catégorie  : " + category_name)
    print("url de la catégorie : " + url_link)
    print("nbr. de page de la categorie : " + str(number_of_page))
    print("En cours d'extraction...")

    while page_number <= number_of_page:

        list_link_in_category = get_book_link_in_page(url_link)
        for link in list_link_in_category:
            book_line_to_write = get_data_book(link)
            fill_result_file(result_filepath, book_line_to_write)

        if page_number < number_of_page:
            url_link = get_next_page_link(url_link)

        page_number += 1

    print("Extraction terminée !")
    print("Emplacement du fichier de resultat : " + result_filepath)
    print("===================================================")


"""
####### Fonction de navigation #########
"""


def get_number_of_page(url_link):

    page = requests.get(url_link)
    soup = BeautifulSoup(page.content, 'html.parser')

    pager_ul = soup.find_all("ul", class_="pager")

    if len(pager_ul) != 0:
        pager_lis = pager_ul[0].find_all("li", class_="current")
        string_pager = pager_lis[0].string
        entire_number_of_page = re.sub("Page1of", "", re.sub("\\n|\\s", "", string_pager))
    else:
        entire_number_of_page = 1

    return int(entire_number_of_page)


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


def get_book_link_in_page(url_link):

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
############################# Fonction generale et gestion UI #######################
"""


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

    execution_mode_code = input("Entrez le chiffre du mode d'execution souhaité :")
    return str(execution_mode_code)


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def test_url(url):
    if ("https://" in url or "http://" in url) and ".html" in url:
        response_get_request = requests.get(url)
        if response_get_request.status_code == 200:
            url_to_test = url
        else:
            print("erreur sur l'url : " + str(response_get_request))
            url_to_test = ""
    else:
        url_to_test = ""

    return url_to_test


"""
######################################## Fin de la section Fonctions ###################################################
"""

"""
########################################## Section main du programme ###################################################
"""


execution_mode = ""
url_OK = ""
url_entry = ""
category_OK = ""
result_filename = ""

create_directory_structure()


"""
##### Recuperation des argument passé au lancement du programme ######
##### Determine le type d'execution demandé ##########################
"""


if len(sys.argv) > 1 and str(sys.argv[1]) == "livre":

    cls()

    if len(sys.argv) == 3:
        url_OK = test_url(sys.argv[2])
        if url_OK == "":
            print("L'url entré est invalide !")
    else:
        url_OK = ""

    execution_mode = "1"

elif len(sys.argv) > 1 and str(sys.argv[1]) == "categorie":

    if len(sys.argv) == 3:
        if "https://books.toscrape.com/catalogue/category" in sys.argv[2]:
            url_OK = test_url(sys.argv[2])
            category_OK = ""
        else:
            category_OK = test_category(sys.argv[2])
            url_OK = ""

    else:
        url_OK = ""
        category_OK = ""

    execution_mode = "2"

elif len(sys.argv) > 1 and str(sys.argv[1]) == "complet":

    execution_mode = "3"

else:

    execution_mode = get_choice_menu_ui()

"""
################################ Gestion du mode d'execution du programme ##############################################
"""


if execution_mode == "1":

    if url_OK == "":
        url_entry = input("Entre l'url du livre a recuperer :")
        url_OK = test_url(url_entry)

    print("===================================================")

    line_to_write = get_data_book(url_OK)

    result_filename = get_result_filename(line_to_write[2], "livre")

    fill_result_file(result_filename, line_to_write)

    print("Extraction terminée !")
    print("Emplacement du fichier de resultat : " + result_filename)
    print("===================================================")

elif execution_mode == "2":

    if url_OK != "" and category_OK == "":
        category_OK = get_category_from_url(url_OK)

    elif url_OK == "" and category_OK != "":
        url_OK = test_url(get_category_link(category_OK))

    else:

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

    cls()

    result_filename = get_result_filename(category_OK)

    get_all_books_in_category(url_OK, category_OK, result_filename)

elif execution_mode == "3":

    cls()

    categories_name_list = get_categories_list()

    for category in categories_name_list:

        result_filename = get_result_filename(category)

        url_OK = test_url(get_category_link(category))

        get_all_books_in_category(url_OK, category, result_filename)

elif execution_mode == "4":
    sys.exit()
else:
    print("entree incorrecte. Sortie du programme !" + str(execution_mode) + "n'etait pas attendu !")
