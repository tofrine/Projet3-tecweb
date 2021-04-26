# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go
import numpy as np
import glob
import streamlit_theme as stt


# pour la partie informations sur les hôtels

@st.cache
def load_data(filename_and_path):
   df = pd.read_json(filename_and_path, orient='index')
   return df

# prépare les données avec nb d'hôtels  éco/non éco en fonction du lieu
@st.cache
def prepare_comparaison_eco_non_eco (lieu) :
    df_lieux = df[lieu].unique()
    liste_lieux = list(df_lieux)
    nb_hotels_eco = []
    nb_hotels_non_eco = []
    for p in liste_lieux :
        query1 = 'eco == "0" and ' + lieu + '  == "' + p + '"'
        query2 = 'eco == "1" and ' + lieu + '  == "' + p + '"'
        non_eco = df.query(query1)
        oui_eco = df.query(query2)
        nb_hotels_eco.append(len(oui_eco))
        nb_hotels_non_eco.append(len(non_eco))
    return nb_hotels_eco, nb_hotels_non_eco, liste_lieux




if __name__ == "__main__":



 # Page d'accuiel du projet
    st.title("De l'information pour un investissement intelligent")
    st.sidebar.header("Techniques web - Projet individuel")
    st.sidebar.info('Auteur : Fabienne AUFFRET')
    st.info("Des graphiques pour investir éthique ! Et des données pour investir informé !")

    # bouton radio pour choisr les parties du site à visiter
    st.sidebar.header("Choix :")
    radio = st.sidebar.radio(label="", options=[ "Présentation", "Les hôtels éco-friendly", "Dictionnaire Ntealan"])

    # Si bouton 'Présentation' choisi
    if radio == "Présentation":
        st.markdown("## Présentation du projet ")
        st.markdown("Cette interface est là pour vous informer sur deux domaines d'investissement possibles.")
        st.markdown("Les rubriques de ce site vous permettront de vous rendre compte concrètment du potentiel de ces deux domaines.")

        st.markdown("**NH hôtels**")
        st.markdown("*** Hôtels éco-friendly ***")
        st.markdown("Ce groupe espagnol propose des hébergements écologiques qui répondent aux objectifs actuels en matière de préservation de la planète. il compte déjà plus de 357 hôtels dans 29 pays et a reçu des prix pour ses initiatitves.")

        st.markdown("ici vous verrez les résultats de la recherche faites sur le site nh : nous avons choisi de récupérer  des informations sur tous les hôtels qui y sont répertoriés. Notre attention s'est portée sur les hôtels éco-friendly.")
        st.markdown("Vous pourrez consulter des graphiques pour visualiser facilement les données collectées et prendre une décision informée.")



        st.markdown("**Dicitonnaire des langues africaines Ntealan **")
        st.markdown("*** Des informations sur les langues et cultures des pays d'Afrique ***")
        st.markdown("Ce site propose de nombreux dictionnaire avec des langues africaines. Grâce à un réseau en construction, il peut devenir une plateforme incontournable aussi bien pour les linguistes que pour les médiateurs culturels.")


    # Si on a choisi le bouton 'NH hôtels
    elif radio == "Les hôtels éco-friendly":
        st.markdown("## Hôtels éco friendly ")
        st.markdown("Données sur les hôtels éco-friendly du site NH")


        df = load_data('./data/hotels2.json')
    # nombre total d'hôtels
        nb_hotels = df['eco'].count()
    # nombre d'hôtels éco-friendly
        nh_hotels_eco = int(df['eco'].sum(axis=0))
    # pourcentage d'hôtels éco
        mean_df = float(df.mean()*100)

        st.write(f'Nous avons collectés les données sur le site https://www.nh-hotels.fr/hotels. Nous y avons trouvé {nb_hotels} hotels ')
        st.markdown("(si la valeur de la  colonne éco est 1, il est eco-friendly)")
        st.write(df)



        group_zone = df.groupby('zone')
        group_ville = df.groupby('ville')
        group_pays = df.groupby('pays')

        st.write('Il y a {:.2f} % hôtels eco-friendly, soit {} en tout.'.format(mean_df,nh_hotels_eco))
        st.markdown("On voit que plus de la moitié des hôtels de NH Hotels ont la mention eco-friendly : ils utilisent de l'eléctricité provenant d'énergies renouvelables, optimisent leur utilisation d'eau, favorisent les déplacment en vélo ou en vég-hicules éléctriques.")
    # Visualisation de la répartion des hôtels par zone géographique
    # on renomme une colonne pour la légende

        st.markdown("(Vous pouvez interagir avec les graphiques à l'aide des boutons situés à leur coin haut droit)")
        st.markdown("#### Répartition des hôtels par lieux : ")
        gzc = group_zone.count().rename(columns = {'eco':'hôtels'}, inplace = False)
        #tracé du camembert
        fig0 = px.pie(gzc, values='hôtels', names=gzc.index, title='Répartition des hôtels par zone géographique',width=800, height=400)
        st.write(fig0)
        fig0.update_yaxes(automargin=True)


    # Visualisation de la répartion des hôtels par pays
        gpc = group_pays.count().rename(columns = {'eco':'hôtels'}, inplace = False)
        fig1 = px.pie(gpc, values='hôtels', names=gpc.index, title='Répartition des hôtels par pays',width=800, height=400)
        st.write(fig1)
        fig1.update_yaxes(automargin=True)




        st.markdown("#### Comparaison des proportions d'hôtels éco-friendly/ non éco-friendly suivant leur emplacement : ")
    # Comparasion du nombre  d'hôtels éco/ non éco par pays : de la répartion des hôtels par pays
        nb_hotels_eco, nb_hotels_non_eco, liste_pays =  prepare_comparaison_eco_non_eco('pays')

        dft = pd.DataFrame({'Hôtels éco-friendly': nb_hotels_eco,'Hôtels non éco-friendly': nb_hotels_non_eco}, index=liste_pays)



        fig2 = go.Figure(data=[go.Bar(name='Hôtels éco-friendly', x=liste_pays, y=nb_hotels_eco), go.Bar(name='non éco-friendly', x=liste_pays, y=nb_hotels_non_eco)])
    # Change the bar mode
        fig2.update_layout(barmode='group')
        st.write(fig2)


        nb_hotels_eco, nb_hotels_non_eco, liste_zone =  prepare_comparaison_eco_non_eco('zone')
        st.markdown("On constate que les hôtels écologiques sont majoritaires pour les hôtels en Europe, ce qui est certainement dû à la politique de L'Union Européenne  sur la sur la transition écologique. Les hôtels du groupe sont encore rares en Afrique et au Moyen Orient : là encore il y a de du potentiel d’évolution.")
        st.markdown("Pour le continent américain les hôtels écologiques sont plus rares, et là aussi ceci correspond aux politiques des gouvernements. Pour les États-Unis, on  peut espérer une progression avec le changement de dirigeant.")

        fig3 = go.Figure(data=[go.Bar(name='Hôtels éco-friendly', x=liste_zone, y=nb_hotels_eco), go.Bar(name='non éco-friendly', x=liste_zone, y=nb_hotels_non_eco)])
    # Change the bar mode
        fig3.update_layout(barmode='group')
        st.write(fig3)

    # cette valeur (la moyenne de la colonne 'eco') donne les pourventages dhôtel éco par pays
        group_pays.mean().T
    # visualisation avec un diagramme en barres

        st.markdown("#### Poucentage, nombre absolu d'hôtels éco-friendly par emplacement ")
        fig4 = px.bar(group_pays.mean(), x=liste_pays, y='eco',title="Pourcentages d'hôtels éco-friendly par pays")
        st.write(fig4)

        fig4bis = px.bar(group_pays.count(), x=liste_pays, y='eco',title="Nombre d'hôtels éco-friendly par pays")
        st.write(fig4bis)
        st.markdown("On voit que les hôtels écologiques dominent aux Pays-Bas, en  Belgique, en Autriche, en Allemagne,  ainsi qu'en Italie. is sont aussi nombreux en France. Il y a donc un potentiel de croissance important dans les autres pays européens ainsi que dans les autres zones.")



        fig5 = px.bar(group_ville.mean(), x=list(group_ville.mean().index), y='eco',title="Pourcentages d'hôtels éco-friendly par ville")
        st.write(fig5)

        fig5bis = px.bar(group_ville.count(), x=list(group_ville.count().index), y='eco',title="Nombre d'hôtels éco-friendly par ville")
        st.write(fig5bis)

        nb_hotels_eco, nb_hotels_non_eco, liste_ville =  prepare_comparaison_eco_non_eco('ville')

        st.markdown("#### Pour une prise de décision au plus fin : les comparaison éco/éco ville par ville ")
        fig6 = go.Figure(data=[go.Bar(name='Hôtels éco-friendly', x=liste_ville, y=nb_hotels_eco), go.Bar(name='non éco-friendly', x=liste_ville, y=nb_hotels_non_eco)])
    # Change the bar mode
        fig6.update_layout(barmode='group')
        st.write(fig6)


    # Si on a choisi le  bouton 'Ntealan'

    elif radio == "Dictionnaire Ntealan":
            st.markdown("## Ntealan ")
            st.write("Une plateforme collaborative sur les langues africaines : https://ntealan.net/dictionaries/content/fr-af/yb_fr_3031")

            st.markdown("#### Ici vous trouverez un aperçu rapide des dictionnaires proposés ")
            st.markdown("Nous avons collecté une toute petite partie des entrées des dictionnaires proposés. Le site propose un menu avec de nombreux dictionnaires (24) mais certains sont désactivés pour l'instant. Il en reste néanmoins 17. Sachant que le nombre de langues africaines se compte en centaines et le développment de ce continent, il est clair que cette plateforme a une énomrme marge de progrès. Et cette démarche peut s'inscrire dans l’initiative sur la protection du patrimoine culturel pouvant être  mis en danger par le réchauffement climatique.")
            st.markdown("Nous avons noté la part of speech du mot collecté, sa traduction dans le dictionnaire choisi, et s'il avait un audio disponible.")


            dic_df = {}
            for name in glob.glob('./data/*'):
                # nom est le nom du dico
                nom = name.split('.')[1].split('/')[-1]
                st.write(f'Extrait du dictionnaire {nom} : ')
                dft = load_data(name)
                st.write(dft)















