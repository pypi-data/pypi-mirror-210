""" THIS LIBRARY HEPLS TO TRANSLATE LANGAUGES, THE SPECIAL THING IN THIS LIBRARY IS IT CAN UPDATE IT LANGAUGES.

    IT WORKS WITH THE BASE OF googletrans LIBRARY.BUT googletrans IS NOT UPDATABLE..

    vtrans UPDATE THE 'LANGAUGES' IN constants.py.
    
    WHEN THE GOOGLE UPDATE their LANGUAGES IN GOOGLE TRANSLATOR vtrans WILL AUTOMATICALLY UPDATE IT SELF.
    
    IT CHECK UPDATING IN EVERY IMPORT OF THIS LIBRARY IT MAKE IT LITTLE BIT SLOWER,
    
    BUT YOU CAN DISABLE AUTOUPDATE CHECKING BY THIS CODE '''vtrans.config(auto_updating = False)'''."""

__Author__ = "S.Vigneswaran"

__Version__ = 1.5



""" This function is helps to set optional settings of this translator 
       
    it helps to disable the autoupdating"""
def config(auto_updating='True'):
    #Convert auto_updating value to string
    auto_updating = str(auto_updating)

    #Get the current working interpreter site-packages to find the config file path
    site_path = get_sitePackages_path()
    config_path = site_path + "vtrans\\config.txt"

    #Open the config file
    with open(config_path,"r") as configfile:
        #Read the config file and evaluate that
        config_data = eval(configfile.read())
    
    #get the values of autoupdate and langauge_num
    autoup_config = config_data['autoupdate']
    orginal_lang = config_data['original_lang']
    prin = config_data['print']
    if autoup_config == auto_updating:
        pass
    else:
        #Save the new values in config file
        pattern = {'print':prin,'autoupdate':auto_updating,'original_lang':orginal_lang}
        with open(config_path,"w") as write_config:
            write_config.write(pattern)
        if auto_updating == 'True':
            print("Auto updating is turn enabled")
        elif auto_updating == 'False':
            print("Auto updating is disabled")

def remove_unwanted_printing():
    data =check_con()
    sitep = get_sitePackages_path()
    sitep = sitep + "vtrans\\config.txt"
    num_lang = data['original_lang']
    print_stat = data['print']
    auto_up = data['autoupdate']
    pattern = {'print':'False','autoupdate':auto_up,'original_lang':num_lang}
    with open(sitep,"w") as file:
        file.write(str(pattern))

def enable_printing():
    data =check_con()
    sitep = get_sitePackages_path()
    sitep = sitep + "vtrans\\config.txt"
    num_lang = data['original_lang']
    print_stat = data['print']
    auto_up = data['autoupdate']
    pattern = {'print':'True','autoupdate':auto_up,'original_lang':num_lang}
    with open(sitep,"w") as file:
        file.write(str(pattern))

"""  This function hels to find config data """
def check_con():
    site_path = get_sitePackages_path()
    config_path = site_path + "vtrans\\config.txt"
    with open(config_path,"r") as read_con:
        con_data = eval(read_con.read())
        return con_data
    
""" This function gets the current working interpreter path  """
def get_sitePackages_path():
    #importing site library
    import site

    #Site uses to  get current working interpreter path
    site_packages_path = site.getsitepackages()[0] + "\Lib\\site-packages\\"

    #Return the path
    return site_packages_path

""" This function used for checking updates on Google Translator updates by  Wikipedia article """
def update_chacker():
    print("Checking for updates(auto updating).auto-updating make it slower.If you want to stop auto-updating, use this code: '''vtrans.config(auto_updating=False)'''")
    
    #importing module to find valus using web scraping
    import requests
    from bs4 import BeautifulSoup

    #Set the headers
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
    
    #Send requests to https://en.wikipedia.org/wiki/Google_Translate
    page = requests.get("https://en.wikipedia.org/wiki/Google_Translate", headers=headers)

    #Get the html structure 
    soup = BeautifulSoup(page.content, 'html.parser')

    #Find all info box data the soup and extract the data
    num_lang = soup.find_all(class_='infobox-data')[1].text.strip().split()[0]

    #Using check_con function to find config data
    data = check_con()

    #And check the update is available or not
    if int(data['original_lang']) < int(num_lang):
        
        #If the original_lang is less than number of current avilable languages
        print("update is available.") #print "update is available."
        update() #use update function to update
    else:
        #Else the original_lang = number of current avilable languages 
        print("this is te latest version you don't need to update") # print "this is te latest version you don't need to update"


def update():
    print("Please wait for a few seconds, updating is in progress...")

    #importing modules

    import ast             #ast module used to edit py files
    import astor           #astor module is the give support to ast
    import pandas as pd    #pandas used to scrap the table in web page

    tables = pd.read_html('https://cloud.google.com/translate/docs/languages')  #Collect tables in https://cloud.google.com/translate/docs/languages

    langlist = tables[0].to_dict(orient='records') #Get first table of this page, make dictionary like orientation using to_dict(orient='records')

    lang_with_langcode = {} #Create new empty main dictionary
    orginal_lang = {}       #Create new empty sub dictionary

    #Create sub dictionary
    for dictio in langlist:  #Use for loop to get each colum and rows
        language = str(dictio['Language']).lower() # extract Language from that
        langcode = str(dictio['ISO-639 code'])     #Extract langaugecode from that

        language = language.lower() # Make langauge in lower case
        orginal_lang[langcode] = language #Add new key and value
    
    site_path = get_sitePackages_path() #Get site packages path
    config_path = site_path + "Vtrans\\config.txt" #and add confg file path

    with open(config_path,"r") as configfile:  #OPEN CONFIG FILE
        config_data = eval(configfile.read()) #read config file and eval it

    autoup_config = config_data['autoupdate'] #get autoupdate value
    prin = config_data['print']

    pattern = {'print':prin,'autoupdate':autoup_config,'original_lang':str(len(orginal_lang))} #insert values in dict pattern

    with open(config_path,"w") as write_config: # open and rewrite config data
        write_config.write(pattern)
    
    #Create main dictionary
    for dictio in langlist:
        language = str(dictio['Language'])
        langcode = str(dictio['ISO-639 code'])
        language = language.lower()
        langcode = langcode.split() #Split langcode to remove unwanted text
        if "(BCP-47)" in langcode:
            langcode.remove("(BCP-47)") #remove un wanted "(BCP-47)"

        if "or" in langcode: #some languages have two language code

            langcode.remove("or") #Remove "or" and get only langcode in list lancode

            for indlangcode in langcode: #use for loop to get langcode one by one
                lang_with_langcode[indlangcode] = language #add new key and values
            
        else:
            lang_with_langcode[str(langcode[0])] = language #if the langcode have only language codes add langcode list first value as new key and set new value  

    constant_path = get_sitePackages_path() #get site-packages path
    constant_path = constant_path + "googletrans\\constants.py" #add constant.py file path

    print(f"Total languages: {len(lang_with_langcode)}") #print how many langauges have updated version
    
    with open(constant_path, "r") as lang_config: #open constants.py 
        tree = ast.parse(lang_config.read()) #read file
    
    #Change LANGAUGES dictionary values with the new dictionary
    for node in tree.body:
        if node.targets[0].id == "LANGUAGES":
            dict_node = node.value
            keys = [ast.Constant(value=key) for key in lang_with_langcode.keys()]
            values = [ast.Constant(value=value) for value in lang_with_langcode.values()]
            dict_node.keys = keys
            dict_node.values = [ast.Name(id='_' + str(i)) for i in range(len(values))]
            dict_node.values = values
        modified_source = astor.to_source(tree)

    with open(constant_path, 'w') as file:
        file.write(modified_source) #Save the updated file

    print("Update finished. Now you can use extra languages.")

def ready(data):
    if data['print'] == 'True':
        print("ready to translate")

data =check_con() #get confile data

if data['autoupdate'] == 'True': #if the autoupdate value id 'true'
    update_chacker() #check the update

from googletrans import Translator #import Translator 
from googletrans import LANGCODES, LANGUAGES #import LANGCODE and LANGAUGES

ready(data=data) #if all intial work and importing or comppleted it will print ready to translate