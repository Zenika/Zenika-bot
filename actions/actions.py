from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import pandas as pd
import numpy as np
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset

class ActionTrainerSearch(Action):

    def name(self) -> Text:
        return "action_trainer_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:
        skill = tracker.get_slot("skill") #Récupère l'entité "skill" repérée par le bot 
        agence = tracker.get_slot("agence") #Récupère le nom de l'agence
               
        df = pd.read_csv('bdd/Export Skillz 2022-06-27 - Feuille 1.csv', sep=',', encoding='utf-8')
        df_platon = pd.read_csv('bdd/Export Platon Sessions  Formations.csv', sep=',', encoding='utf-8').dropna()
        
        df_collaborator_agency_name=df['collaborator_agency_name']
        
        df = df.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))
        df['skill_name'] = df['skill_name'].apply(str.lower)
        df['skill_level'] = df['skill_level'].astype(int)
        df.columns = df.columns.str.strip() #Enleve les espaces en "bord" de chaque colonne du dataframe
        mask2= df['skill_level']>3 #Msasque pour que seules les compétences de niveau 4 ou 5 des utilisateurs soient retenues
        
        #Probleme pour les skills "anglais" et "espagnol" car présence d'emojis drapeau dans le fichier .csv (maintenant enlevé et reconnus normalement mais le code ne veut toujours pas repérer la ligne...)
        #Reste à voir comment récupérer les caractères spéciaux comme (+,#,>,<) avec un tokenizer personalisé mais il faut arriver à le connecter
        
        df_platon = df_platon.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))
        df_platon['training_subject'] = df_platon['training_subject'].apply(str.lower)
        df.columns = df.columns.str.strip() #Enleve les espaces en "bord" de chaque colonne du dataframe
        
                
        if (skill):
            print (skill)
            df_skill_name = df['skill_name']
            mask1 = (df_skill_name).str.casefold() == skill.casefold()
            df_trainers_skill = df[(mask1 & mask2)]
            
            #df_platon_training_title = df_platon['training_title']
            #df_platon_training_subject = df_platon['training_subject']
            
            #print(df_platon_training_title,df_platon_training_subject)
            
            #mask_p = (df_platon_skill_name).str.casefold() == skill.casefold()
            #mask_p= df_platon['primary_trainer'] == "TRUE"
            #df_platon_trainers_skill = df_platon[(mask_p)]
            
            #print(df_platon_trainers_skill)
        
        if (agence):
            print (agence)
            mask3 = df_collaborator_agency_name.str.casefold() == agence.casefold()
            df_trainers_agence=df[(mask2 & mask3)]
        
        if (not skill and not agence): #Si pas de précision
            dispatcher.utter_message(" Nous n'avons pas compris votre demande. Veuillez la préciser en ajoutant la compétence recherchée.")

        elif (not skill and agence): #Si on cherche des gens d'une agence
            if (len(df_trainers_agence) == 0):
                dispatcher.utter_message(" Nous sommes désolés, nous n'avons pas de formateur {}".format(agence))
            elif (len(df_trainers_agence)== 1):
                dispatcher.utter_message(" Vous pouvez contacter cet adresse {}"+ df_trainers_agence['collaborator_email']+ df_trainers_agence['skill_name']+" de l'agence {}".format(agence))
            else:
                df_trainers_emails= df_trainers_agence[['collaborator_email','skill_name']].drop_duplicates(keep='first').values.tolist()
                dispatcher.utter_message(" Vous pouvez contacter l'un de ces formateurs de l'agence de {}".format(agence))
                
                
            for trainer_email in df_trainers_emails:
                dispatcher.utter_message ( "{}".format(trainer_email[0]) +" : formateur {}".format(trainer_email[1]))            

        else: #Si on cherche un skill en particulier
            if (len(df_trainers_skill)==0): #and len(df_platon_trainers_skill)==0
                dispatcher.utter_message(" Nous sommes désolés, nous n'avons pas de formateur {}".format(skill))
            else:
                df_trainers_emails = df_trainers_skill['collaborator_email'].drop_duplicates(keep='first').values.tolist()
                #df_platon_trainers_emails = df_platon_trainers_skill['trainer_email'].drop_duplicates(keep='first').values.tolist()
             
                df_trainers_agency_name = df_trainers_skill['collaborator_agency_name'].values.tolist()
                #df_platon_trainers_agency_name = df_platon_trainers_emails['trainer_agency_name'].values.tolist()
                
                #Nouvelle liste contenant skill + agence du collaborateur
                df_trainers_skill_and_agency = [(df_trainers_emails[i], df_trainers_agency_name[i]) \
                    for i in range(len(df_trainers_emails))]
                
                #df_platon_trainers_skill_and_agency = [(df_platon_trainers_emails[i], df_platon_trainers_agency_name[i]) \
                #    for i in range(len(df_platon_trainers_emails))]
                
                #emails_agence_skill = True
                dispatcher.utter_message(" Vous pouvez contacter l'une de ces adresses pour apprendre {}".format(skill))
                
                #Envoie du message avec le mail et l'agence
                for trainer in df_trainers_skill_and_agency:
                    dispatcher.utter_message ( "{}".format(trainer[0]) +" à : l'agence de {}".format(trainer[1]))
                
                #for trainer in df_platon_trainers_skill_and_agency:
                #    dispatcher.utter_message ( "{}".format(trainer[0]) +" à : l'agence de {}".format(trainer[1]))


        return [AllSlotsReset()]