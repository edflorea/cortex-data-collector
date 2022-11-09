from cortexPyAdapter import CortexAdapter
import csv
from datetime import datetime
import time
import os
import pygame

class Train():
    def __init__(self, client_id, client_secret, user_events, **kwargs):
        self.cortex = CortexAdapter(client_id, client_secret, debug_mode=False)
        self.cortex.bind(create_session_done=self.on_create_session_done)
        self.cortex.bind(query_profile_done=self.on_query_profile_done)
        self.cortex.bind(setup_profile_done=self.on_setup_profile_done)
        self.cortex.bind(get_trained_actions_done=self.on_get_trained_actions_done)
        self.cortex.bind(new_data_labels=self.on_new_data_labels)
        self.cortex.bind(new_sys_data=self.on_new_sys_data)
        self.cortex.bind(new_com_data=self.on_new_com_data)
        self.cortex.bind(new_pow_data=self.on_new_pow_data)
        self.cortex.bind(new_eeg_data=self.on_new_eeg_data)

        self.pygame_events = user_events

        self.trainingInstances = {
            "neutral": 0,
            "push": 0,
            "pull": 0
        }


        self.save_data = False
        self.com_data = []
        self.pow_data = []
        self.eeg_data = []

        self.parent_dir = os.getcwd()
        self.start_time = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        self.save_dir = os.path.join(self.parent_dir, f'data/{self.start_time}')
        os.mkdir(self.save_dir)

    
    def setup(self, profileName):
        self.profile = profileName

        self.cortex.open()
        return

    def train(self, command):
        self.command = command
        self.trainingInstances[command] += 1
        self.train_mc_action('start')


    def train_mc_action(self, action):
        print(f'[Train message] {action} command {self.command}.')
        self.cortex.train_request(self.command, action)
    
    def on_create_session_done(self, *args, **kwargs):
        self.cortex.query_profile()


    def on_query_profile_done(self, *args, **kwargs):
        profiles = kwargs.get('profiles')
        if self.profile in profiles:
            print(f'[Train message] Profile {self.profile} found. Loading profile.')
            self.cortex.setup_profile(self.profile, 'load')
        else: 
            print(f'[Train message] Profile {self.profile} not found. Creating profile')
            self.cortex.setup_profile(self.profile, 'create')
    
    def on_setup_profile_done(self, *args, **kwargs):
        is_loaded = kwargs.get('isLoaded')
        if is_loaded:
            self.cortex.get_trained_actions(self.profile)

    def on_get_trained_actions_done(self, *args, **kwargs):
        self.trainedActions = kwargs.get('actions')
        print(self.trainedActions)
        self.cortex.start_streams(['com', 'eeg', 'pow', 'sys'])

    def on_new_data_labels(self, *args, **kwargs):
        data = kwargs.get('data')
        if data['streamName'] == 'sys':
            print('[Train message] Ready for training.')
            pygame.event.post(pygame.event.Event(self.pygame_events[0]))

            # self.train_mc_action('start')
    
    def on_new_sys_data(self, *args, **kwargs):
        data = kwargs.get('data')
        train_event = data[1]

        if train_event == 'MC_Started':
            print("[Train message] Training started...")    
            self.save_data = True
            for i in range(8):
                print(f'{8-i}...')
                time.sleep(1)
        
        elif train_event == 'MC_Succeeded':
            print("[Train message] Training successful.")
            self.save_data = False 
            self.train_mc_action("accept")
        
        elif train_event == 'MC_Failed':
            self.train_mc_action("reject")

        elif train_event == 'MC_Completed' or train_event == 'MC_Rejected':
            print('[Train message] Training done.')

            # parent_dir = os.getcwd()
            # date_time = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
            # os.mkdir(os.path.join(parent_dir, f'data/training_{self.command}_{date_time}'))

            if len(self.com_data) != 0:
                self.write_to_csv('com', self.com_data)
            if len(self.pow_data) != 0:
                self.write_to_csv('pow', self.pow_data)
            if len(self.eeg_data) != 0:
                self.write_to_csv('eeg', self.eeg_data)
            
            print('[Train message] Done saving data.')
            pygame.event.post(pygame.event.Event(self.pygame_events[1]))

    
    def write_to_csv(self, type, data):
        print(f'[Train message] Saving {type} data...')
        trainNum = self.trainingInstances[self.command]

        if type == 'com':
            file_name = f'{self.save_dir}/training_{self.command}_{trainNum}_com.csv'
            # file_name = f'./data/com/training_{date_time}.csv'
            field_names = ['action', 'power', 'time']
        elif type == 'pow':
            file_name = f'{self.save_dir}/training_{self.command}_{trainNum}_pow.csv'
            field_names = ['pow', 'time']
        elif type == 'eeg':
            file_name = f'{self.save_dir}/training_{self.command}_{trainNum}_eeg.csv'
            field_names = ['eeg', 'time']

        with open(file_name, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(data)
        
    def on_new_com_data(self, *args, **kwargs):
        data = kwargs.get('data') 
        if self.save_data:
            self.com_data.append(data)

    def on_new_pow_data(self, *args, **kwargs):
        data = kwargs.get('data') 
        if self.save_data:
            self.pow_data.append(data)  

    def on_new_eeg_data(self, *args, **kwargs):
        data = kwargs.get('data') 
        if self.save_data:
            self.eeg_data.append(data)



def main():

    # Please fill your application clientId and clientSecret before running script
    your_app_client_id = 'jL4BOpvLmHsF0ypsOMKhYitdXuyCxfDFxo6XtA1J'
    your_app_client_secret = 'sqQ5ttXBkRWiJSudvOB0c63ecz3Ucbziu1kRxA6gVw2yEXU26ZSLGFAtInHIfWYePoAhevWyoe8SxyMT8zoRGsV9lO42VtNuDaMFv6YwtRL9BS92Qdiaz5w5GWlloxib'

    # Init Train
    t = Train(your_app_client_id, your_app_client_secret)

    profile_name = 'EricaTest' 

    t.setup(profile_name, 'push')


if __name__ == '__main__':
    main()