from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import AllSlotsReset, Restarted
import pandas as pd 
class TrainerSearch(Action):

    def name(self) -> Text:
        return "action_trainer_search"
    def run (self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        skill = tracker.get_slot("skill")
        agence = tracker.get_slot("agence")
        print (skill)
        print (agence)
        df = pd.read_csv('bdd/Export Skillz 2022-06-27 - Feuille 1.csv').dropna()
        df_collaborator_agency_name=df['collaborator_agency_name']
        mask2= df['skill_level']>4
        if (skill):
            print (skill)
            mask1 = df['skill_name'].str.casefold() == skill.casefold()
            df_trainers_skill=df[(mask1 & mask2)]
        if (agence):
            print (agence)
            mask3 = df_collaborator_agency_name.str.casefold() == agence.casefold()
            df_trainers_agence=df[(mask2 & mask3)]
            
        emails = False
        emails_agence_skill= False
        emails_skill=False
        if (not skill and not agence):
            dispatcher.utter_message(" Nous n'avons pas compris votre demande. Prière de l'affiner en ajoutant le skill cherché et l'agence si vous voulez")

        elif (skill and not agence):
            if (len(df_trainers_skill)==0 ):
                dispatcher.utter_message(" Nous sommes désolés, nous n'avons pas de formateur {}".format(skill))
            elif (len(df_trainers_skill)== 1):
                dispatcher.utter_message(" Vous pouvez contacter cet adresse {}"+ df_trainers_skill['collaborator_email']+" pour apprendre {}".format(skill))
            else:
                df_trainers_emails= df_trainers_skill[['collaborator_email','collaborator_agency_name']].drop_duplicates(keep='first').values.tolist()
                emails_skill= True
                dispatcher.utter_message(" Vous pouvez contacter l'une de ces adresses pour apprendre {}".format(skill))

        elif (not skill and agence):
            if (len(df_trainers_agence) == 0):
                dispatcher.utter_message(" Nous sommes désolés, nous n'avons pas de formateur {}".format(agence))
            elif (len(df_trainers_agence)== 1):
                dispatcher.utter_message(" Vous pouvez contacter cet adresse {}"+ df_trainers_agence['collaborator_email']+ df_trainers_agence['skill_name']+" de l'agence {}".format(agence))
            else:
                #df_trainers_agence[['collaborator_email','skill_name']]= df_trainers_agence[['collaborator_email','skill_name']].drop_duplicates(keep='first').groupby('collaborator_email').skill_name.apply(list)
                #df_trainers_emails= df_trainers_agence[['collaborator_email','skill_name']].values.tolist()
                df_trainers_emails= df_trainers_agence[['collaborator_email','skill_name']].groupby('skill_name').collaborator_email.apply(list).reset_index(name='collaborator_email').to_numpy().tolist()
                
                print(df_trainers_agence[['collaborator_email','skill_name']].drop_duplicates(keep='first').groupby('collaborator_email').skill_name.apply(list))
                emails_agence_skill= True
                dispatcher.utter_message(" Vous pouvez contacter l'un de ces formateurs de l'agence de {}".format(agence))
        else:
            df_trainers_skill_and_agence=df[(mask1 & mask2 & mask3)]
    
            if (len(df_trainers_skill_and_agence)==0):
                dispatcher.utter_message(" Nous sommes désolés, nous n'avons pas de formateur {}".format(skill) +" à l'agence {}".format(agence))
            elif (len(df_trainers_skill_and_agence)== 1):
                dispatcher.utter_message(" Vous pouvez contacter cet adresse {}"+ df_trainers_skill_and_agence['collaborator_email']+ df_trainers_agence['skill_name']+" pour apprendre {}".format(skill))
            else:
                
                df_trainers_emails= df_trainers_skill_and_agence['collaborator_email'].drop_duplicates(keep='first').values.tolist()
                emails= True
                dispatcher.utter_message(" Vous pouvez contacter l'une de ces adresses pour apprendre {}".format(skill) +" à l'agence de {}".format(agence))
        if(emails):
            for trainer_email in df_trainers_emails:
                dispatcher.utter_message ( "{}".format(trainer_email))
        if(emails_agence_skill):
            for trainer_email in df_trainers_emails:
                dispatcher.utter_message ( "{}".format(trainer_email[0]) +" : formateur(s) {}".format(trainer_email[1]))
        if(emails_skill):
            for trainer_email in df_trainers_emails:
                dispatcher.utter_message ( "{}".format(trainer_email[0]) +" : formateur basé à {}".format(trainer_email[1]))
       
        return [AllSlotsReset()]


class ActRestarted(Action):
    """ This is for restarting the chat""" 
    def name(self):
        return "action_act_restarted"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("Au revoir")
        return [Restarted()]

        

        
