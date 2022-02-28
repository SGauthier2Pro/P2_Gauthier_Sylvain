# Scraping_Book_To_Scrap 
***
This program aims to get all books data sold on the "Book to Scrap" web site and inject result in csv files
***
***
## Table of Contents
1. [General Info](#general-info)
2. [Technologies](#technologies)
3. [Installation](#installation)
4. [Collaboration](#collaboration)
5. [FAQs](#faqs)
***
***
## General Info
***
This script is finished.
all books datas could be get from the web site and all picture could be backed up.
But some implementation could be added : management of long path file for windows OS, picture archive management could be removed to reduce
result data size ; to see with the asker.
***
## Technologies
***
List of technologies used within this project :
* [Windows 10](https://www.microsoft.com/fr-fr/software-download/windows10): version 21H2
* [Python](https://www.python.org/downloads/release/python-3100/):  version 3.10.0
* [PyCharm](https://www.jetbrains.com/fr-fr/pycharm/): version 2021.2.3
* [git](https://git-scm.com/download/win): version 2.35.1.windows.2
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/): version 4.10.0
* [bs4](https://pypi.org/project/bs4/): version 0.0.1
* [certifi](https://pypi.org/project/certifi/): version 2021.10.8
* [charset-normalizer](https://pypi.org/project/charset-normalizer/): version 2.0.12
* [idna](https://pypi.org/project/idna/): version 3.3
* [requests](https://pypi.org/project/requests/): version 2.27.1
* [soupsieve](https://pypi.org/project/soupsieve/): version 2.3.1
* [urllib3](https://pypi.org/project/urllib3/): version 1.26.8
***
## Installation
***
This process suggests that you have admin priviledges on you computer
### Python 3.10.0 installation
***
1. Get the exe file to install python 3.10.0 at this adress : https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe
2. Execute the exe file downloaded ![win_installer](https://user-images.githubusercontent.com/99419487/155973764-7d247762-f552-481f-8f31-6b557e32a638.png)
3. Check the checkboxes "Install launcher for all users(recommanded)" and "Add Python 3.10 to PATH" then clic on "Install Now". 
5. If during the pregression, administrator elevation will be asked, clic on "Yes".
6. At the end of the installation, clic on "Disable path length limit"![win_installer_end](https://user-images.githubusercontent.com/99419487/155973946-61421b0a-f96b-49e5-9a52-b72615d1d49e.png)
7. In order to check if your installation is OK, launch a cmd console and type the following command : "python --version"
8. Verify that you have the same result :
   ![python_version_verif](https://user-images.githubusercontent.com/99419487/155974788-1a055c62-06b3-402e-ba80-969864c282ce.png)

***
### Git 2.35.1 installation
***
1. Get the exe file to install python 3.10.0 at this adress : https://github.com/git-for-windows/git/releases/download/v2.35.1.windows.2/Git-2.35.1.2-64-bit.exe
2. Execute the exe file downloaded and clic "Next" on each following windows without changing any option and then clic "Install"![git_install_bigging](https://user-images.githubusercontent.com/99419487/155984934-1c3a5db3-1644-404f-baf5-829a3449576d.png)
![git_install_button](https://user-images.githubusercontent.com/99419487/155984959-aacfdbd0-ad09-4b69-bbe0-0c9a368a35e2.png)
3. At the end of the installation, uncheck the "View Relesae Note" Checkbox and check the "Launch Git Bash" Checkbox then clic on "Finish" button.![git_install_end](https://user-images.githubusercontent.com/99419487/155985188-498d88c1-955e-4d41-9a55-bc79c1c0f694.png)
4. In order to check if your installation is OK, on the Git Bash prompt type the following command : "git --version"
5. Verify that you have the same result :
   
   ![git_version_result](https://user-images.githubusercontent.com/99419487/155986385-18609f61-511d-40a8-a569-9885e4c1dec6.png)
   
***
#### Git configuration 
***
(Even if you did not have done before, create an account on Github at the adress : https://github.com)

1. In order to configure your git IDs , see the following process in GitBash console :
   Type the following command
   ``` 
       $ git config --global user.name "your_github_username"
       $ git config --global user.email your_email@your_provider.com
   ```
2. Type the following command to configure the GitBash console interface (optional) :
  ```
       $ git config --global color.diff auto
       $ git config --global color.status auto 
       $ git config --global color.branch auto
  ```
***
### Clone the distant repository with Gitbash
***
You have now to clone the distant repository on your computer.
1. type the following command in Gitbash console :
    ```
        $ git clone https://github.com/SGauthier2Pro/P2_Gauthier_Sylvain.git
    ```
2. Verify that you got the source directory opening an explorator and verifying that the main.py, requirements.txt and README.md files are in:
    
![directory_clone](https://user-images.githubusercontent.com/99419487/156000270-e7d992d6-23ec-4df5-99fa-f1f09f601f5b.png)

***
### configure the python environment for application
***
 1. open a command prompt typing "cmd" in the Windows search bar
 2. go to program directory where you clone the distant repository in the precedent step :
    ```
      cd c:/path_where_you_put_the clone_repo/P2_Gauthier_Sylvain
    ```
 3. create the virtual environment with the following command :
    ```
    python -m venv env
    env/Scripts/activate.bat
    ```
 4. Verify that the virtual environment is activate checking the presence of (env) before the prompt :
 ![venv](https://user-images.githubusercontent.com/99419487/156004026-823cdefb-93f5-4075-86a5-3f91db263f34.png)
 
 5. Type the following command to implement all necessary modules in your environment :
 
    ```
      pip install -r requirements.txt
    ```
 6. verify that all packages are installed typing "pip freeze" command. You should get this result :
 
 ![pip_freeze_result](https://user-images.githubusercontent.com/99419487/156006764-77865de3-4e47-4563-9361-c50ce7452954.png)
 
 7. now your environement is ready to execute the program.




