from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import os
from dotenv import load_dotenv


#on initialise
driver_path = './resources/chromedriver'
driver = Chrome(executable_path=driver_path)
# définit la taille de fenêtre
driver.set_window_size(1600,30000)
#Attente pour les lenteurs de chargement
driver.implicitly_wait(3)
actions = ActionChains(driver)



# liste des dictionnaires actifs

dictionnaires_actifs = ["bambara-français", "bassa-français", "duala-français", "Eton-français",
 "ejagham-francais", "feefee-français", "fulfulde-français", "ghomala-français","medʉmba-francais",
  "ŋk̀ùnàbémbé-français", "mafa-francais", "ndemli-français" , "ŋgəmba-français", "oku-english",
   "soninké-français-anglais", "yemba-français", "yangben-français"]


def close_covid () :# clique sur accepter si pop-up covid-19
    time.sleep(2)
    try:
        alerte_covid = driver.find_element_by_class_name("modal-bottom")
        bouton_ok = alerte_covid.find_element_by_tag_name("button")
        bouton_ok.click()
    except: pass


# Login pour ne pas avoir de limite de consultation du dictionnaire
def login() :
    time.sleep(2)
    login = driver.find_element_by_class_name("float-right")
    time.sleep(2)
    login.click()
    username = driver.find_element_by_id("pseudo")
    password = driver.find_element_by_id("password")

    username.send_keys("tofrine")
    password.send_keys("mboning")
    # il y a deux boutons de ce type un pour créer un compte l'autre pour le login
    buttons = driver.find_elements(By.CSS_SELECTOR, ".btn.bg-primary.btn-sm.text-white")
    for b in buttons :
        if b.text ==  "Connexion" :
            b.click()

# selection du  dictionnaire :
def selection(nom_dico) :
    liste_dico = driver.find_element_by_xpath('//*[@id="page"]/div[1]/div/app-entete/div[5]/div/div[2]/div[1]/div[1]/ng-select')
    driver.execute_script("arguments[0].scrollIntoView(true);", liste_dico)
    time.sleep(0.5)
    liste_dico.click()
    # on clique sur le dictonnaire choisi
    driver.find_element_by_xpath(f"//div[@role='option' and span/text()='{nom_dico}']").click()
    time.sleep(1)



def extraire_entrees(nom_dico) :
    selection(nom_dico)
    close_covid()
    #on initialise le dictionnaire qui va contenir les mots yemba et leur traduction
    dico = {}
    # on récupère la zone de la liste non ordonnées ou les mots sont listés
    zoneUL = driver.find_element_by_class_name("listeUL")
    time.sleep(2)
    # on récupère la liste des mots
    li  = zoneUL.find_elements_by_tag_name("li")
    # on parcourt cette liste et on initialise un compteur pour n'extraire que les 25 premieres entrées par dico
    cnt = 0
    for element in li :
        cnt += 1


        #on  se déplace vers la div on clique dessus pour faire apparaître l'entrée du dictionnaire
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        element.click()
        time.sleep(0.5)
        # on récupère le bloc t"translation" dans l'article à droite de la liste
        # avec le mot (prefixe + radical) et son pos
        bloc_article = driver.find_element_by_class_name("article")
        radical = bloc_article.find_element_by_class_name("radical")
        prefix = bloc_article.find_elements_by_class_name("aprefix")
        suffix = bloc_article.find_elements_by_class_name("suffix")
        # on a renvoyé une liste (pour avoir une liste vide si pas de préfix ou pas de suffix -->t pas d'erreur) (on aurait pu faire un try)
        pref =''
        suff =''
        for p in prefix :
            pref = p.text
        for s in suffix :
            suff = s.text
        mot = pref + radical.text + suff
        print(mot)
        cat = bloc_article.find_element_by_class_name("cat_part")
        pos = cat.text
        print(pos)
        # on note s'il y a un fichier audio ou non
        audio_ok = 0
        try :
            audio = bloc_article.find_element(By.CSS_SELECTOR, "audio>source")
            if audio.get_attribute("src") != "https://ntealan.net/dictionaries/null" :
                audio_ok = 1
        except :
            audio_ok = 0


        bloc_traduction = driver.find_element_by_class_name("translation")

        # dans ce bloc c'est cette partie qui nous intéresse
        group_equiv =bloc_traduction.find_elements_by_class_name("group_equiv")

        trad = []
        # dans cette liste on récupère le texte de la traduction en français
        for g in group_equiv :
            traduction = g.find_element_by_class_name("equivalent").text
            #time.sleep(2)
            trad.append(traduction)
        # on ajoute la traduction au dictionnaire
        dico[mot] = {'pos' : pos, 'prefix' : pref, 'suffix' : suff, 'audio' : audio_ok, 'traduction-fr':trad}
        if cnt == 25:
            break
    print(dico)
    return dico


def main():



    # ouvre le site sur la page de recherche
    driver.get("https://ntealan.net/dictionaries/content/fr-af/yb_fr_3031")

    #fermer popup covid
    close_covid()
    time.sleep(1)

    # se connexion
    login()
    time.sleep(1)

    extrait_dicos_ntealan = []
    # on parcourt la liste des dictionaires et collecte 10 entrées rées pour chaque dictionnaire actif
    for dictionnaire in dictionnaires_actifs:
        try :
            dico_courant = extraire_entrees(dictionnaire)
            extrait_dicos_ntealan.append(dico_courant)
            filePathNameWExt =  './data/' + dictionnaire + '.json'
            with open(filePathNameWExt, 'w') as fp:
                json.dump(dico_courant, fp, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erreur lors du traitment du dictionnaire  : {e})")



    driver.quit()

    # try:
    #     os.mkdir('data')
    # except OSError as error:
    #     print(error)




if __name__ == "__main__":
    main()




