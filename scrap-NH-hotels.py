import time
from selenium.webdriver import Chrome
driver_path = '/Users/fabienneauffret/OneDrive/Inalco-IM/techniques web/chromedriver'
navigateur = Chrome(executable_path=driver_path)
#ouvre l'url
navigateur.get("https://www.nh-hotels.fr/hotels")

from selenium.webdriver.common.by import By
# clique sur accepter si pop-up cookies
try:
    consentement_cookies = navigateur.find_element_by_class_name("privacy-prompt-footer")
    bouton_ok = consentement_cookies.find_element_by_tag_name("button")
    bouton_ok.click()
except: pass
import json
# PRINCIPE : sur chaque page on récolte les informations (zone, pays, villes) et les liens à ouvrir à l'étape suivante
# on crée donc  dictionnaire arborescent qui va stocker les zones géographique, les pays, les hôtels et les liens qui y mènent
#on parcourt chaque page de chaque hôtel et on regarde s'il est éco (on pourrait ajouter d'autres services à évaluer)
# on créer ensuit un autre e dictionnaire  arborescent avec les infos des hôtels {zone:{pays :{ville :[[ nom hotel1,  écologique ou non ],[nom hotel2, eco ou non]}}}
# et enfin on a CHOISI de créer ENSUITE lun autre dico ou nous organisons les données pour avoir un json facile à transformer en dataframe
# le dico de départ en arborescence est inntuitif et peut permettre de stocker facilement plus d'infos à l'avenir

#dictionnaires des liens de la page de départ
liens_dict ={}
# la page comporte des blocs avec des listes d'hôtels qui nous intéressent. Ils ont "m-block" comme style css
# ceci est valable à la fois sur la liste par zone (première page) et la liste par pays
hotels_blocs = navigateur.find_elements(By.CSS_SELECTOR, ".m-block")

# nous avons nos 4 blocs (Afrique, Amérique, Europe, Medio Oriente (sic) , au jour de mon scraping
for bloc in hotels_blocs :
    liens_hotels = bloc.find_elements_by_tag_name("a")
    titre = bloc.find_element_by_class_name("h4")
    #on garde le texte du titre pour notre clé "zone"

    zone_list = titre.text.split()
    zone_list.remove("Hôtels")
    zone_list.remove("en")
    zone = ' '.join(zone_list)


    #dictionnaires des liens de la page des zones
    liens_dict[zone] = {}
    #dans chaque bloc il y a une liste d'au moins un lien vers un hôtel
    for l in liens_hotels:
        pays = l.find_element_by_tag_name("strong").text

        liens_dict[zone][pays] = l.get_attribute('href')

#on crée un dictionnaire ville -liste des liens vers les hotels pour parcourir ensuite toutes les pages des hôtles(dernière étape)
liens_dict_hotels_ville = {}
for zone, dic_pays in liens_dict.items()  :
    liens_dict_hotels_ville[zone]={}
    for pays, lien in dic_pays.items():
        liens_dict_hotels_ville[zone][pays]={}

        navigateur.get(lien)
        # on va à la page des hotels par pays
        hotels_blocs2 = navigateur.find_elements(By.CSS_SELECTOR, ".m-block")

        for bloc2 in hotels_blocs2 :
            # bloc 2 contient le titre avec la ville (lieu2 est la ville le plus souvent)
            titre2 = bloc2.find_element_by_class_name("h4")

            lieu2_list = titre2.text.split()
            lieu2_list.remove("Hôtels")
            lieu2_list.remove("en")
            lieu2 = ' '.join(lieu2_list)

            #on initialise notre dico de villes - liens hotels
            liens_dict_hotels_ville[zone][pays][lieu2] =[]

            # construcion de la liste de liens des hotels par ville
            liens_hotels2 = bloc2.find_element_by_class_name("block-body")
            liens_hotels2_href = liens_hotels2.find_elements_by_tag_name("a")
            for l in liens_hotels2_href :
                #print(l.get_attribute("href"))
                #print(l.text)
                liens_dict_hotels_ville[zone][pays][lieu2].append(l.get_attribute('href'))

# dernière étape on parcourt les hotels ville par ville et
#  on remplit notre dictionnaire hotelgeo_dic
hotelgeo_dict = {}
for zone, pays_dict in liens_dict_hotels_ville.items()  :
    #on initialise le dico des hôtels {zone:{pays :{ville :[[ nom hotel1,   éco-friendly ou non ],[nom hotel2, eco ou non]]}}}
    hotelgeo_dict[zone]={}
    for pays, ville_dict in pays_dict.items() :
        #on initalise le dico d'hotels par pays
        hotelgeo_dict[zone][pays]={}
        for ville, liste_liens in ville_dict.items() :
            hotelgeo_dict[zone][pays][ville]=[]
            for lien in liste_liens :
                navigateur.get(lien)
                nom_hotel = navigateur.find_element_by_tag_name("h1").text
                services = navigateur.find_elements_by_class_name("color-primary")
                hotelgeo_dict[zone][pays][ville].append([nom_hotel, 0])
                # si le services eco-friendly est présent on note que l'hôtel est éco-friendly
                for s in services :
                    if s.text == 'Eco-friendly':
                        hotelgeo_dict[zone][pays][ville].pop()
                        hotelgeo_dict[zone][pays][ville].append([nom_hotel, 1])
driver.quit()

# création du dictionnaire pour écrire un json simple à transformer en dataframe pour les calculs qui nous intéressent
dict_ready_to_df ={}

for zone, pays_dict in hotelgeo_dict.items()  :
    for pays, ville_dict in pays_dict.items() :
        for ville, liste_hotels in ville_dict.items() :
            for l in liste_hotels :
                dict_ready_to_df[l[0]] = {'zone':zone, 'pays':pays, 'ville':ville, 'eco':l[1]}



print(hotelgeo_dict)
print(dict_ready_to_df)


with open('./data/hotels.json', 'w') as fp:
    json.dump(hotelgeo_dict, fp, ensure_ascii=False, indent=4)

#print(liens_dict_hotels_ville)
with open('./data/hotels2.json', 'w') as fp:
    json.dump(dict_ready_to_df, fp, ensure_ascii=False, indent=4)


