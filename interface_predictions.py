import streamlit as st
from datetime import datetime
import pandas as pd
from catboost import CatBoostRegressor, Pool
from sklearn.preprocessing import LabelEncoder
import numpy as np
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
import gdown
from PIL import Image
import streamlit.components.v1 as components
import base64
import requests
import json


# Remplacez FILE_ID par l'ID de votre fichier sur Google Drive
file_id_im = '1ZkzOtSsL6MLYbuChyua77l9vR-W5oGXT'  # Remplacez ceci par l'ID réel de votre fichier
image_url_im = f'https://drive.google.com/uc?id={file_id_im}'

# Télécharger l'image depuis Google Drive
response = requests.get(image_url_im)

# Si l'image est correctement téléchargée
if response.status_code == 200:
    # Convertir l'image en base64
    encoded_image = base64.b64encode(response.content).decode()
    print("Image encodée en base64.")
else:
    print("Erreur de téléchargement de l'image.")

# Appliquer le CSS pour ajouter l'image en arrière-plan
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* Main container styling */
    .main-container {{
        background-color: rgba(255, 255, 255, 0.85);
        width: 60%;  /* Adjust width as desired */
        margin: auto;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);  /* Subtle shadow */
    }}

    h1, h2, h3 {{
        color: #ffffff;
        text-align: center;
        font-family: 'Arial', sans-serif;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);  /* Add subtle shadow */
    }}

    /* Button styling */
    .stButton button {{
        background-color: #003366;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 1em;
        border: none;
        box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.3);  /* Button shadow */
        transition: background-color 0.3s ease;
    }}
    .stButton button:hover {{
        background-color: #005999;  /* Lighter shade on hover */
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# Vérifiez si l'utilisateur est déjà authentifié dans la session
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def authenticate():
    # CSS pour centrer le formulaire
    st.title("Bienvenue dans votre application de prédiction de tonnage !")
    st.markdown("""
        <style>
        .auth-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 30vh;
            flex-direction: column;
        }
        </style>
        """, unsafe_allow_html=True)

    # Conteneur du formulaire centré
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            # Vérification des informations d'identification
            if username == "ABDESSALAM" and password == "tonnage_predictor":
                st.session_state.authenticated = True  # Mettre à jour l'état d'authentification
                st.rerun()  # Relancer l'application pour afficher l'interface principale
            else:
                st.warning("Identifiants incorrects.")
        st.markdown('</div>', unsafe_allow_html=True)

# Afficher l'écran de connexion si l'utilisateur n'est pas authentifié
if not st.session_state.authenticated:
    authenticate()  # Appelez la fonction d'authentification
else:
    # Si l'utilisateur est authentifié, afficher l'interface principale
    st.title("Bienvenue dans votre application de prédiction de tonnage !")
    st.write("Voici l'interface principale de l'application.")
    # Ajoutez ici le reste de votre application (graphique, analyses, etc.)







    # Remplace FILE_ID par l'ID de ton fichier
    file_id = '1Jtff-WoPZDY4MiEaMqAQoYEedaup7Lfk'
    url = f"https://drive.google.com/uc?id={file_id}"
    # Chemin local où tu veux enregistrer le fichier
    output = 'dataset.xlsx'  # ou 'dataset.xlsx' si c'est un fichier Excel
    # Télécharger le fichier
    gdown.download(url, output, quiet=False)
    df=pd.read_excel(output)
    # CORRECTION DE basess
    # Suppression des 3 premières lignes de baseSS
    #df = df.iloc[3:]
    df = df.fillna(0)  # Remplir les valeurs manquantes par zéro
    #df=df.drop(df.index[644:730])
    df.reset_index(drop=True, inplace=True)  # Réinitialisation de l'index





    def duree_en_heures_depuis_minuit(heure):
        # Séparer les heures, minutes, et secondes
        h, m, s = map(int, heure.split(':'))

        # Si l'heure est 24:00:00, retourner 24.0 heures
        if h == 24 and m == 0 and s == 0:
            return 24.0

        # Calculer la durée en heures
        return h + m / 60 + s / 3600


    def duree_en_heures_depuis_minuit(heure):
        # Convertir l'heure donnée en un objet datetime
        heure_donnee = datetime.strptime(heure, '%H:%M:%S')

        # Extraire les heures, minutes et secondes
        heures = heure_donnee.hour
        minutes = heure_donnee.minute
        secondes = heure_donnee.second

        # Calculer la durée écoulée en heures depuis minuit
        duree_heures = heures + minutes / 60 + secondes / 3600

        return duree_heures

    def correct (base):


    # Créer une copie de la DataFrame pour éviter de modifier l'original
        base_copy = base.copy()

        # Ajouter des caractéristiques temporelles
        base_copy['Date'] = pd.to_datetime(base_copy['Date'], format='%d/%m/%Y', errors='coerce')
        base_copy['JourSemaine'] = base_copy['Date'].dt.weekday
        base_copy['JourMois'] = base_copy['Date'].dt.day
        base_copy['Mois'] = base_copy['Date'].dt.month
        base_copy['JourAnnee'] = base_copy['Date'].dt.dayofyear

        # Supprimer la colonne 'Date'
        base_copy = base_copy.drop(columns=['Date'])

        # Colonnes d'intérêt
        columns_of_interest1 = ['Production Port', 'Production Total ', "Transfert vers l'U262",
            'stock solide prenable Hangar1', 'stock solide prenable Hangar2', 'Total prenable déclaré',
            'JourSemaine', 'JourMois', 'Mois', 'JourAnnee', 'Jour Férié', 'Arrêts Q4(Durée)',
            'Q4_Nature_OCP', 'Q4_Nature_EXTERNE', 'Q4_Nature_FLS', 'Q4_Nature_TKIS',
            'Arrêts Q5(Durée)', 'Q5_Nature_OCP', 'Q5_Nature_EXTERNE', 'Q5_Nature_FLS', 'Q5_Nature_TKIS',
            'TRG', 'Navire_Quai 4', 'Navire_Quai 4 bis', 'Navire_Quai 5', 'Navire_Quai 16','TONNAGE Humide\nB/L_Q4','TONNAGE Humide\nB/L_Q5','TONNAGE Humide\nB/L_Q4bis','nombre de navires en décharge_Q4','nombre de navires en décharge_Q5','nombre de navires en décharge_Q4bis','T0_QUAI4bis','T0_QUAI4','T0_QUAI5','Etape_Quai4','Etape_Quai4bis','Etape_Quai5', 'décharge Quai 5','décharge Quai 4','décharge Quai 4 bis']
        base_copy = base_copy[columns_of_interest1]
        #base_copy = base_copy.iloc[:1009]

        # Encodage des navires
        label_encoder = LabelEncoder()
        base_copy['Navire_Quai_4_encoded'] = label_encoder.fit_transform(base_copy['Navire_Quai 4'])
        navire_encoding_dict4 = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))

        label_encoder4bis = LabelEncoder()
        base_copy['Navire_Quai_4bis_encoded'] = label_encoder4bis.fit_transform(base_copy['Navire_Quai 4 bis'])
        navire_encoding_dict4bis = dict(zip(label_encoder4bis.classes_, label_encoder4bis.transform(label_encoder4bis.classes_)))

        label_encoder5 = LabelEncoder()
        base_copy['Navire_Quai_5_encoded'] = label_encoder5.fit_transform(base_copy['Navire_Quai 5'])
        navire_encoding_dict5 = dict(zip(label_encoder5.classes_, label_encoder5.transform(label_encoder5.classes_)))

        label_encoder16 = LabelEncoder()
        base_copy['Navire_Quai_16_encoded'] = label_encoder16.fit_transform(base_copy['Navire_Quai 16'])
        navire_encoding_dict16 = dict(zip(label_encoder16.classes_, label_encoder16.transform(label_encoder16.classes_)))


        label_encoder_ET4 = LabelEncoder()
        base_copy['Etape_Quai4_enc'] = label_encoder_ET4.fit_transform(base_copy['Etape_Quai4'])
        navire_encoding_dictET4 = dict(zip(label_encoder_ET4.classes_, label_encoder_ET4.transform(label_encoder_ET4.classes_)))

        label_encoder_ET5 = LabelEncoder()
        base_copy['Etape_Quai5_enc'] = label_encoder_ET5.fit_transform(base_copy['Etape_Quai5'])
        navire_encoding_dictET5 = dict(zip(label_encoder_ET5.classes_, label_encoder_ET5.transform(label_encoder_ET5.classes_)))

        label_encoder_ET4bis = LabelEncoder()
        base_copy['Etape_Quai4bis_enc'] = label_encoder_ET4bis.fit_transform(base_copy['Etape_Quai4bis'])
        navire_encoding_dictET4bis = dict(zip(label_encoder_ET4bis.classes_, label_encoder_ET4bis.transform(label_encoder_ET4bis.classes_)))


        base_copy = base_copy.drop(columns=['Navire_Quai 4', 'Navire_Quai 4 bis', 'Navire_Quai 5', 'Navire_Quai 16','Etape_Quai4','Etape_Quai4bis','Etape_Quai5'])

        base4=base_copy.copy()
        base5=base_copy.copy()
        base4bis=base_copy.copy()


        return base4,base5,base4bis, navire_encoding_dict4, navire_encoding_dict4bis, navire_encoding_dict5, navire_encoding_dict16,navire_encoding_dictET4,navire_encoding_dictET4bis,navire_encoding_dictET5


    def remplacer_tonnage(df, jour, nouveau_tonnage1,nouveau_tonnage2,nouveau_tonnage3):
        # Convertir le jour donné en format datetime s'il ne l'est pas déjà
        jour = pd.to_datetime(jour)
        df2=df.copy()
        # Calculer la date du jour précédent
        jour_precedent = jour - pd.Timedelta(days=1)

        # Vérifier si le jour précédent existe dans la DataFrame
        if jour_precedent in df2['Date'].values:
            # Remplacer la valeur de 'Tonnage Humide par jour' par le nouveau tonnage
            df2.loc[df2['Date'] == jour_precedent, 'décharge Quai 4'] = nouveau_tonnage1
            df2.loc[df2['Date'] == jour_precedent, 'décharge Quai 5'] = nouveau_tonnage2
            df2.loc[df2['Date'] == jour_precedent, 'décharge Quai 4 bis'] = nouveau_tonnage3
            print(f"Le tonnage pour le {jour.date()} a été mis à jour avec les valeurs .")
        else:
            print(f"Le jour précédent ({jour_precedent.date()}) n'existe pas dans la DataFrame.")

        return df2



    def remlissage(dict_original, d, e, f, g,h,i,j, df1, output):
        # Créer une copie du dictionnaire pour éviter de modifier l'original
        dict_copie = dict_original.copy()
        cles_a_supprimer = ['Navire_Quai_4bis_encoded', 'Navire_Quai_5_encoded', 'Navire_Quai_16_encoded','Navire_Quai_4_encoded','Etape_Quai4_enc','Etape_Quai5_enc','Etape_Quai4bis_enc','JourSemaine', 'JourMois', 'Mois', 'JourAnnee']

        # Utilisation de la boucle pour supprimer les clés
        for cle in cles_a_supprimer:
            del dict_copie[cle]
        # Appliquer les modifications sur la copie
        dict_copie['Date'] = pd.to_datetime(d)
        dict_copie['Navire_Quai 4'] = e
        dict_copie['Navire_Quai 5'] = g
        dict_copie['Navire_Quai 4 bis'] = f
        dict_copie['Navire_Quai 16'] = "-"
        dict_copie['Etape_Quai4'] = h
        dict_copie['Etape_Quai5'] = i
        dict_copie['Etape_Quai4bis'] = j

        new_row = pd.DataFrame([dict_copie])
        for col in df1.columns:
            if col not in new_row.columns:
                new_row[col] = 'à remplir'

        new_row = new_row[df1.columns]
        df1 = pd.concat([df1, new_row], ignore_index=True)
        df1.to_excel(output, index=False, engine='openpyxl')
        
        

        SCOPES = ['https://www.googleapis.com/auth/drive']
        # Charger les informations d'identification depuis les secrets
        credentials_json = os.environ.get("GOOGLE_CREDENTIALS")
        credentials_dict = json.loads(base64.b64decode(credentials_json))
        
        credentials = service_account.Credentials.from_service_account_info(credentials_dict)
        service = build('drive', 'v3', credentials=credentials)
        media = MediaFileUpload(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        updated_file = service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()

        return df1



    # Interface Streamlit
    st.title("Prédicteur de Tonnage")

    # Créer deux colonnes
    col1, col2 = st.columns(2)
    with col1:


        # Entrées utilisateur
        jour_data = {}
        jour_mei={}
        jour_mau={}
        with st.form("tonnage_prediction_form"):
            day = st.date_input("Entrez le jour : ")
            date = pd.to_datetime(day, format='%Y/%m/%d')
            df['Date'] = pd.to_datetime(df['Date'])

            # Récupérer la date de la dernière ligne
            last_date = df['Date'].iloc[-1]
            jour_data['Jour Férié'] = st.checkbox("Est-ce un jour férié (0/1): ")
            jour_data['Production Port'] = st.number_input("Entrez la production Port: ")
            usine=st.number_input("Entrez la production Usine: ")
            jour_data['Production Total '] = usine + jour_data['Production Port']
            jour_data["Transfert vers l'U262"] = st.number_input("Entrez le transfert vers l'U262: ")
            jour_data['stock solide prenable Hangar1'] = st.number_input("Entrez le stock solide prenable Hangar1: ")
            jour_data['stock solide prenable Hangar2'] = st.number_input("Entrez le stock solide prenable Hangar2: ")
            h3=st.number_input("Entrez le stock solide prenable Hangar3: ")
            AL=st.number_input("Entrez le stock solide prenable Air libre: ")
            jour_data['Total prenable déclaré'] = jour_data['stock solide prenable Hangar1']+jour_data['stock solide prenable Hangar2']+h3+AL
            jour_data['TRG'] = st.number_input("Entrez le TRG(%): ")




            st.subheader("QUAI 4")

            jour_data['TONNAGE Humide\nB/L_Q4'] = st.number_input("Enter le tonnage humide du Navire en Q4 (s'il y a deux navires , entrer juste le tonnage du navire entrant): ")
            jour_data["nombre de navires en décharge_Q4"]=st.number_input("Entrez le nombre de navires en déchargement en Q4:")
            a=st.text_input("Entrez les navires en déchargement en Quai 4 (s'il n'existe pas, tapez (-), s'il y a plus qu'un entrer navire1+navire2 ): ", "-",key="a")
            st.markdown('Navire 1')
            a14 = st.radio("Est-ce que le navire 1 vient de commencer aujourd'hui ?", [0, 1], index=0, key='a14')
            HD14=st.text_input("Si OUI , ENTRER l'Heure de son début en décharge( sous la forme hh:mm:ss) ': ", "00:00:00",key="HD14")
            HF14=st.text_input("S'il termine aujourd'hui  , ENTRER l'Heure de sa fin en décharge( sous la forme hh:mm:ss) ': ", "23:59:59",key="HF14")
            st.markdown("Navire 2 (navire entrant)")
            a24 = st.radio("Est-ce que le navire 2 vient de commencer aujourd'hui ?", [0, 1], index=0, key='a24')
            HD24=st.text_input("Si OUI , ENTRER l'Heure de son début en décharge( sous la forme hh:mm:ss) ': ", "00:00:00",key="HD24")
            HF24=st.text_input("S'il termine aujourd'hui  , ENTRER l'Heure de sa fin en décharge( sous la forme hh:mm:ss) ': ", "23:59:59",key="HF24")

            ET4=st.text_input("Entrez l'étape de déchargement en Quai 4 (Finition,Déchargement,Préparation), s'il y a plus qu'une étape, veuillez taper ETAPE1 + ETAPE2 en laissant un espace en les mots , et s'il n' y a pas de navire taper 'Pas de navire': ", 'Pas de navire',key="ET4")




            st.subheader("QUAI 5")

            jour_data['TONNAGE Humide\nB/L_Q5'] = st.number_input("Enter le tonnage humide du Navire en Q5 (s'il y a deux navires , entrer juste le tonnage du deuxième navire): ")
            jour_data["nombre de navires en décharge_Q5"]=st.number_input("Entrez le nombre de navires en déchargement en Q5:")
            c=st.text_input("Entrez les navires en déchargement en Quai 5 (s'il n'existe pas, tapez (-)), s'il y a plus qu'un entrer navire1+navire2 : ", "-",key="c")
            st.markdown('Navire 1')
            a15 = st.radio("Est-ce que le navire 1 vient de commencer aujourd'hui ?", [0, 1], index=0, key='a15')
            HD15=st.text_input("Si OUI , ENTRER l'Heure de son début en décharge( sous la forme hh:mm:ss) ': ", "00:00:00",key="HD15")
            HF15=st.text_input("S'il termine aujourd'hui  , ENTRER l'Heure de sa fin en décharge( sous la forme hh:mm:ss) ': ", "23:59:59",key="HF15")
            st.markdown("Navire 2 (navire entrant)")
            a25 = st.radio("Est-ce que le navire 2 vient de commencer aujourd'hui ?", [0, 1], index=0, key='a25')
            HD25=st.text_input("Si OUI , ENTRER l'Heure de son début en décharge( sous la forme hh:mm:ss) ': ", "00:00:00",key="HD25")
            HF25=st.text_input("S'il termine aujourd'hui  , ENTRER l'Heure de sa fin en décharge( sous la forme hh:mm:ss) ': ", "23:59:59",key="HF25")
            ET5=st.text_input("Entrez l'étape de déchargement en Quai 5 (Finition,Déchargement,Préparation), s'il y a plus qu'une étape, veuillez taper ETAPE1 + ETAPE2 en laissant un espace en les mots , et s'il n' y a pas de navire taper 'Pas de navire': ", 'Pas de navire',key="ET5")





            st.subheader("QUAI 4 BIS")


            jour_data['TONNAGE Humide\nB/L_Q4bis'] = st.number_input("Enter le tonnage humide du Navire en Q4 bis (s'il y a deux navires , entrer juste le tonnage du deuxième navire): ")
            jour_data["nombre de navires en décharge_Q4bis"]=st.number_input("Entrez le nombre de navires en déchargement en Q4 bis:")
            b=st.text_input("Entrez les navires en déchargement en Quai 4 bis (s'il n'existe pas, tapez (-)): ", "-",key="b")
            st.markdown('Navire 1')
            a14bis = st.radio("Est-ce que le navire 1 vient de commencer aujourd'hui ?", [0, 1], index=0, key='a14bis')
            HD14bis=st.text_input("Si OUI , ENTRER l'Heure de son début en décharge( sous la forme hh:mm:ss) ': ", "00:00:00",key="HD14bis")
            HF14bis=st.text_input("S'il termine aujourd'hui  , ENTRER l'Heure de sa fin en décharge( sous la forme hh:mm:ss) ': ", "23:59:59",key="HF14bis")
            st.markdown("Navire 2 (navire entrant)")
            a24bis = st.radio("Est-ce que le navire 2 vient de commencer aujourd'hui ?", [0, 1], index=0, key='a24bis')
            HD24bis=st.text_input("Si OUI , ENTRER l'Heure de son début en décharge( sous la forme hh:mm:ss) ': ", "00:00:00",key="HD24bis")
            HF24bis=st.text_input("S'il termine aujourd'hui  , ENTRER l'Heure de sa fin en décharge( sous la forme hh:mm:ss) ': ", "23:59:59",key="HF24bis")
            ET4bis=st.text_input("Entrez l'étape de déchargement en Quai 4 bis (Finition,Déchargement,Préparation), s'il y a plus qu'une étape, veuillez taper ETAPE1 + ETAPE2 en laissant un espace en les mots , et s'il n' y a pas de navire taper 'Pas de navire': ", "Pas de navire",key="ET4bis")









            st.subheader("ARRÊTS")

            quai_4_option = st.radio("Y a-t-il un arrêt en Quai 4:", [0, 1], index=1, key='quai_4_option')



            jour_data["Arrêts Q4(Durée)"]=st.number_input("Entrez la durée de l'arrêt en Q4 (h):")
            jour_data["Q4_Nature_OCP"]=0
            jour_data["Q4_Nature_EXTERNE"]=0
            jour_data["Q4_Nature_FLS"]=0
            jour_data["Q4_Nature_TKIS"]=0


            quai_5_option = st.radio("Y a-t-il un arrêt en Quai 5:", [0, 1], index=1, key='quai_5_option')



            jour_data["Arrêts Q5(Durée)"]=st.number_input("Entrez la durée de l'arrêt Q5 (h):")
            jour_data["Q5_Nature_OCP"]=0
            jour_data["Q5_Nature_EXTERNE"]=0
            jour_data["Q5_Nature_FLS"]=0
            jour_data["Q5_Nature_TKIS"]=0


            data_jour_avant_Q4=st.number_input(f"Entrer le tonnage déchargé du jour précédent en Q4 [{last_date }]: ")
            data_jour_avant_Q5=st.number_input(f"Entrer le tonnage déchargé du jour précédent en Q5 [{last_date }]: ")
            data_jour_avant_Q4bis=st.number_input(f"Entrer le tonnage déchargé du jour précédent en Q4 bis [{last_date }]: ")

            submit_button = st.form_submit_button(label="Soumettre")








        if submit_button:

            with col2:
                st.header("Résultats de prédiction")


                df=remplacer_tonnage(df,day,data_jour_avant_Q4,data_jour_avant_Q5,data_jour_avant_Q4bis)

                baseSS4,baseSS5,baseSS4bis,navire_encoding_dict4,navire_encoding_dict4bis,navire_encoding_dict5,navire_encoding_dict16,navire_encoding_dictET4,navire_encoding_dictET4bis,navire_encoding_dictET5 = correct(df)
                print(baseSS4)


                jour_data['JourSemaine'] = date.weekday()
                jour_data['JourMois'] = date.day
                jour_data['Mois'] = date.month
                jour_data['JourAnnee'] = date.dayofyear




                jour_data['Navire_Quai_4_encoded'] = navire_encoding_dict4.get(a,-1)
                jour_data['Navire_Quai_4bis_encoded'] = navire_encoding_dict4bis.get(b,-1)
                jour_data['Navire_Quai_5_encoded'] = navire_encoding_dict5.get(c,-1)
                jour_data['Navire_Quai_16_encoded'] = navire_encoding_dict16.get("-")
                jour_data['Etape_Quai4_enc'] = navire_encoding_dictET4.get(ET4,"Pas de navire")
                jour_data['Etape_Quai5_enc'] = navire_encoding_dictET5.get(ET5,"Pas de navire")
                jour_data['Etape_Quai4bis_enc'] = navire_encoding_dictET4bis.get(ET4bis,"Pas de navire")


                if jour_data["nombre de navires en décharge_Q4"]==1 and a14==0 and a24==0:
                    jour_data['TONNAGE Humide\nB/L_Q4']=baseSS4['TONNAGE Humide\nB/L_Q4'].iloc[-1]-data_jour_avant_Q4
                    jour_data['T0_QUAI4']= duree_en_heures_depuis_minuit(HF14)
                elif jour_data["nombre de navires en décharge_Q4"]==1 and (a14==1 or a24==1):
                    jour_data['TONNAGE Humide\nB/L_Q4']=jour_data['TONNAGE Humide\nB/L_Q4']
                    jour_data['T0_QUAI4']=duree_en_heures_depuis_minuit(HF14)-duree_en_heures_depuis_minuit(HD14)
                elif jour_data["nombre de navires en décharge_Q4"]==2:
                    jour_data['TONNAGE Humide\nB/L_Q4']=baseSS4['TONNAGE Humide\nB/L_Q4'].iloc[-1]-data_jour_avant_Q4+jour_data['TONNAGE Humide\nB/L_Q4']
                    jour_data['T0_QUAI4']=24 - (duree_en_heures_depuis_minuit(HD24)-duree_en_heures_depuis_minuit(HF14))
                elif jour_data["nombre de navires en décharge_Q4"]==0:
                    jour_data['T0_QUAI4']=0
                    jour_data['TONNAGE Humide\nB/L_Q4']=0
                print(jour_data['T0_QUAI4'])
                print(jour_data['TONNAGE Humide\nB/L_Q4'])


                if jour_data["nombre de navires en décharge_Q5"]==1 and a15==0 and a25==0:
                    jour_data['TONNAGE Humide\nB/L_Q5']=baseSS5['TONNAGE Humide\nB/L_Q5'].iloc[-1]-data_jour_avant_Q5
                    jour_data['T0_QUAI5']= duree_en_heures_depuis_minuit(HF15)
                elif jour_data["nombre de navires en décharge_Q5"]==1 and (a15==1 or a25==1):
                    jour_data['TONNAGE Humide\nB/L_Q5']=jour_data['TONNAGE Humide\nB/L_Q5']
                    jour_data['T0_QUAI5']=duree_en_heures_depuis_minuit(HF15)-duree_en_heures_depuis_minuit(HD15)
                elif jour_data["nombre de navires en décharge_Q5"]==2:
                    jour_data['TONNAGE Humide\nB/L_Q5']=baseSS5['TONNAGE Humide\nB/L_Q5'].iloc[-1]-data_jour_avant_Q5+jour_data['TONNAGE Humide\nB/L_Q5']
                    jour_data['T0_QUAI5']=24 - (duree_en_heures_depuis_minuit(HD25)-duree_en_heures_depuis_minuit(HF15))
                elif jour_data["nombre de navires en décharge_Q5"]==0:
                    jour_data['T0_QUAI5']=0
                    jour_data['TONNAGE Humide\nB/L_Q5']=0
                print(jour_data['T0_QUAI5'])
                print(jour_data['TONNAGE Humide\nB/L_Q5'])


                if jour_data["nombre de navires en décharge_Q4bis"]==1 and a14bis==0 and a24bis==0:
                    jour_data['TONNAGE Humide\nB/L_Q4bis']=baseSS4bis['TONNAGE Humide\nB/L_Q4bis'].iloc[-1]-data_jour_avant_Q4bis
                    jour_data['T0_QUAI4bis']= duree_en_heures_depuis_minuit(HF14bis)
                elif jour_data["nombre de navires en décharge_Q4bis"]==1 and (a14bis==1 or a24bis==1):
                    jour_data['TONNAGE Humide\nB/L_Q4bis']=jour_data['TONNAGE Humide\nB/L_Q4bis']
                    jour_data['T0_QUAI4bis']=duree_en_heures_depuis_minuit(HF14bis)-duree_en_heures_depuis_minuit(HD14bis)
                elif jour_data["nombre de navires en décharge_Q4bis"]==2:
                    jour_data['TONNAGE Humide\nB/L_Q4bis']=baseSS4bis['TONNAGE Humide\nB/L_Q4bis'].iloc[-1]-data_jour_avant_Q4bis+jour_data['TONNAGE Humide\nB/L_Q4bis']
                    jour_data['T0_QUAI4bis']=24 - (duree_en_heures_depuis_minuit(HD24bis)-duree_en_heures_depuis_minuit(HF14bis))
                elif jour_data["nombre de navires en décharge_Q4bis"]==0:
                    jour_data['T0_QUAI4bis']=0
                    jour_data['TONNAGE Humide\nB/L_Q4bis']=0
                print(jour_data['T0_QUAI4bis'])
                print(jour_data['TONNAGE Humide\nB/L_Q4bis'])


                df=remlissage(jour_data,day,a,b,c,ET4,ET5,ET4bis,df,output)


                jour_data4=jour_data.copy()
                jour_data5=jour_data.copy()
                jour_data4bis=jour_data.copy()




                jour_info4 = pd.DataFrame([jour_data4])
                jour_info5 = pd.DataFrame([jour_data5])
                jour_info4bis = pd.DataFrame([jour_data4bis])

                jour_mei4=jour_data4.copy()
                jour_mei4["Arrêts Q4(Durée)"]=0
                jour_mei4["TRG"]=100
                jour_me4 = pd.DataFrame([jour_mei4])

                jour_mei5=jour_data5.copy()
                jour_mei5["Arrêts Q5(Durée)"]=0
                jour_mei5["TRG"]=100
                jour_me5 = pd.DataFrame([jour_mei5])

                jour_mau4=jour_data4.copy()
                jour_mau4["Arrêts Q4(Durée)"]=238
                jour_mau4["TRG"]=1.5
                jour_ma4 = pd.DataFrame([jour_mau4])

                jour_mau5=jour_data5.copy()
                jour_mau5["Arrêts Q5(Durée)"]=238
                jour_mau5["TRG"]=1.5
                jour_ma5 = pd.DataFrame([jour_mau5])

                # Préparer les données pour l'entraînement du modèle
                X4_days = baseSS4.drop(columns=['décharge Quai 4','décharge Quai 4 bis','décharge Quai 5'])
                X4bis_days = baseSS4bis.drop(columns=['décharge Quai 4','décharge Quai 4 bis','décharge Quai 5'])
                X5_days = baseSS5.drop(columns=['décharge Quai 4','décharge Quai 4 bis','décharge Quai 5'])
                y4_days = baseSS4['décharge Quai 4']
                y4bis_days = baseSS4bis['décharge Quai 4 bis']
                y5_days = baseSS5['décharge Quai 5']
                y4_days = y4_days.astype(int)
                y4bis_days = y4bis_days.astype(int)
                y5_days = y5_days.astype(int)
                print(y4_days)
                print(y4bis_days)
                print(y5_days)
                model_days4 = CatBoostRegressor(iterations=1000, learning_rate=0.1, depth=6, verbose=100)
                model_days4bis = CatBoostRegressor(iterations=1000, learning_rate=0.1, depth=6, verbose=100)
                model_days5 = CatBoostRegressor(iterations=1000, learning_rate=0.1, depth=6, verbose=100)
                model_days4.fit(X4_days, y4_days)
                model_days4bis.fit(X4bis_days, y4bis_days)
                model_days5.fit(X5_days, y5_days)
                # Créer un Pool pour l'ensemble complet


                full_pool4 = Pool(data=X4_days)
                full_pool4bis = Pool(data=X4bis_days)
                full_pool5 = Pool(data=X5_days)
                # Prédire sur l'ensemble complet
                baseSS4['Tonnage_Humide_Predit_Q4'] = model_days4.predict(full_pool4)
                baseSS4bis['Tonnage_Humide_Predit_Q4bis'] = model_days4bis.predict(full_pool4bis)
                baseSS5['Tonnage_Humide_Predit_Q5'] = model_days5.predict(full_pool5)
                for i in range(len(baseSS4)):
                    if baseSS4['Tonnage_Humide_Predit_Q4'][i]<0:
                        baseSS4['Tonnage_Humide_Predit_Q4'][i]=0
                    elif baseSS5['Tonnage_Humide_Predit_Q5'][i]<0:
                        baseSS5['Tonnage_Humide_Predit_Q5'][i]=0
                    elif baseSS4bis['Tonnage_Humide_Predit_Q4bis'][i]<0:
                        baseSS4bis['Tonnage_Humide_Predit_Q4bis'][i]=0
                print(baseSS4['décharge Quai 4'])
                print(baseSS4bis['décharge Quai 4 bis'])
                print(baseSS5['décharge Quai 5'])


                # Filtrer les jours où le tonnage humide réel est différent de zéro
                baseSS_non_zero4 = baseSS4[baseSS4['décharge Quai 4'] != 0]
                baseSS_non_zero4bis = baseSS4bis[baseSS4bis['décharge Quai 4 bis'] != 0]
                baseSS_non_zero5 = baseSS5[baseSS5['décharge Quai 5'] != 0]

                # Calculer l'erreur relative en pourcentage
                erreur_relative4 = ((baseSS_non_zero4['Tonnage_Humide_Predit_Q4'] - baseSS_non_zero4['décharge Quai 4']) / baseSS_non_zero4['décharge Quai 4']) * 100
                erreur_relative4bis = ((baseSS_non_zero4bis['Tonnage_Humide_Predit_Q4bis'] - baseSS_non_zero4bis['décharge Quai 4 bis']) / baseSS_non_zero4bis['décharge Quai 4 bis']) * 100
                erreur_relative5 = ((baseSS_non_zero5['Tonnage_Humide_Predit_Q5'] - baseSS_non_zero5['décharge Quai 5']) / baseSS_non_zero5['décharge Quai 5']) * 100

                # Calculer le RMSE en pourcentage
                rmse_pourcentage4 = np.sqrt(np.mean(erreur_relative4 ** 2))
                rmse_pourcentage4bis = np.sqrt(np.mean(erreur_relative4bis ** 2))
                rmse_pourcentage5 = np.sqrt(np.mean(erreur_relative5 ** 2))

                # Prédire avec le modèle
                predicted_tonnage4 = model_days4.predict(jour_info4)
                predicted_tonnage14 = model_days4.predict(jour_me4)
                predicted_tonnage24 = model_days4.predict(jour_ma4)
                print(jour_mau4)
                print(jour_data4)
                predicted_tonnage4bis = model_days4bis.predict(jour_info4bis)
                print(jour_data4bis)
                predicted_tonnage5 = model_days5.predict(jour_info5)
                predicted_tonnage15 = model_days5.predict(jour_me5)
                predicted_tonnage25 = model_days5.predict(jour_ma5)
                print(jour_mau5)
                print(jour_data5)
                if predicted_tonnage4[0]<0:
                    predicted_tonnage4[0]=0
                elif predicted_tonnage5[0]<0:
                    predicted_tonnage5[0]=0
                elif predicted_tonnage4bis[0]<0:
                    predicted_tonnage4bis[0]=0
                elif predicted_tonnage14[0]<0:
                    predicted_tonnage14[0]=0
                elif predicted_tonnage24[0]<0:
                    predicted_tonnage24[0]=0
                elif predicted_tonnage15[0]<0:
                    predicted_tonnage15[0]=0
                elif predicted_tonnage25[0]<0:
                    predicted_tonnage25[0]=0

                # Créer deux colonnes
                col3, col4 = st.columns(2)
                # Afficher la première sortie dans la colonne de gauche
                with col3:
                    # Créer une liste vide pour stocker les lignes du tableau
                    resultats = []

                    # Ajouter conditionnellement des lignes pour chaque quai en fonction de `jour_data`
                    if jour_data["nombre de navires en décharge_Q4"] != 0:
                        resultats.append({
                            "Quai": "Q4",
                            "Tonnage prédit": f"{predicted_tonnage4[0]:.2f}",
                            "Meilleures conditions": f"{predicted_tonnage14[0]:.2f}",
                            "Mauvaises conditions": f"{predicted_tonnage24[0]:.2f}",
                            "Erreur (RMSE%)": f"{rmse_pourcentage4:.2f}%"
                        })

                    if jour_data["nombre de navires en décharge_Q4bis"] != 0:
                        resultats.append({
                            "Quai": "Q4bis",
                            "Tonnage prédit": f"{predicted_tonnage4bis[0]:.2f}",
                            "Meilleures conditions": "N/A",  # Ajuster si nécessaire
                            "Mauvaises conditions": "N/A",
                            "Erreur (RMSE%)": f"{rmse_pourcentage4bis:.2f}%"
                        })

                    if jour_data["nombre de navires en décharge_Q5"] != 0:
                        resultats.append({
                            "Quai": "Q5",
                            "Tonnage prédit": f"{predicted_tonnage5[0]:.2f}",
                            "Meilleures conditions": f"{predicted_tonnage15[0]:.2f}",
                            "Mauvaises conditions": f"{predicted_tonnage25[0]:.2f}",
                            "Erreur (RMSE%)": f"{rmse_pourcentage5:.2f}%"
                        })

                    # Convertir la liste `resultats` en DataFrame pour l'affichage
                    resultats_df = pd.DataFrame(resultats)

                    # Afficher le DataFrame sous forme de tableau
                    st.header("Résultats de prédiction")
                    st.table(resultats_df)

