import websocket
import threading
import ssl
import json 
from pydispatch import Dispatcher
from datetime import datetime

class CortexAdapter(Dispatcher):


    _events_ = ['inform_error', 'create_session_done', 'query_profile_done', 'setup_profile_done', 
                'save_profile_done', 'get_trained_actions_done', 'get_mc_active_action_done', 'mc_brainmap_done', 'mc_action_sensitivity_done', 
                'mc_training_threshold_done', 'create_record_done', 'stop_record_done', 'warn_cortex_stop_all_sub', 
                'inject_marker_done', 'update_marker_done', 'export_record_done', 'new_data_labels', 
                'new_com_data', 'new_fe_data', 'new_eeg_data', 'new_mot_data', 'new_dev_data', 
                'new_met_data', 'new_pow_data', 'new_sys_data', 'on_ready']

    def __init__(self, clientId, clientSecret, debug_mode=False):
        self.name = 'Cortex'
        self.socketUrl = 'wss://localhost:6868'
        self.clientId = clientId
        self.clientSecret = clientSecret
        
        self.debug = debug_mode

        self.username = ''
        self.access_granted = False
        self.token = ''

        # Message IDs
        self.CHECK_LOGIN_ID = 1
        self.CHECK_ACCESS_ID = 2
        self.AUTHORIZE_ID = 3
        self.QUERY_HEADSET_ID = 4
        self.HEADSET_STATUS_ID = 5
        self.CONNECT_HEADSET_ID = 6
        self.CREATE_SESSION_ID = 7
        self.QUERY_PROFILE_ID = 8
        self.SETUP_PROFILE_ID = 9
        self.SUB_REQUEST_ID = 10
        self.GET_TRAINED_ACTIONS_ID = 11
        self.TRAIN_REQUEST_ID = 12

        # Warning Codes
        self.HEADSET_CONNECTED_CODE = 104


    def open(self):
        self.ws = websocket.WebSocketApp(self.socketUrl, 
                                         on_message=self.on_message,
                                         on_open=self.on_open,
                                         on_error=self.on_error,
                                         on_close=self.on_close
                                         )
        
        threadName = "WebsockThread:-{:%Y%m%d%H%M%S}".format(datetime.utcnow())
        sslopt = {"cert_reqs": ssl.CERT_NONE}
        self.websock_thread = threading.Thread(target=self.ws.run_forever, args=(None, sslopt), name=threadName)
        self.websock_thread.start()
        # self.websock_thread.join()
    
    # Socket Events ---------------------------------------------------------------
    def on_open(self, *args):
        self.set_up_engine()
    
    def on_error(self, *args):        
        print(f"Error: {args[1]}")

    def on_close(self, *args):
        print("Socket closing...")
        print(args[1])
    
    def on_message(self, *args):
        recv_dic = json.loads(args[1])
        if 'sid' in recv_dic:
            self.handle_stream_data(recv_dic)
        elif 'result' in recv_dic:
            self.handle_result(recv_dic)
        elif 'error' in recv_dic:
            self.handle_error(recv_dic)
        elif 'warning' in recv_dic:
            self.handle_warning(recv_dic['warning'])
        else:
            raise KeyError

    # Sending messages ------------------------------------------------------
    def set_up_engine(self):
        self.check_login()
    
    def check_login(self):
        params = {}
        self.create_send_request("getUserLogin", params, self.CHECK_LOGIN_ID)
    
    def check_access(self):
        params = {
            "clientId": self.clientId, 
            "clientSecret": self.clientSecret
        }
        self.create_send_request("hasAccessRight", params, self.CHECK_ACCESS_ID)
    
    def authorize(self):
        params = {
            "clientId": self.clientId, 
            "clientSecret": self.clientSecret
        }
        self.create_send_request("authorize", params, self.AUTHORIZE_ID)
    
    def query_headsets(self):
        params = {}
        self.create_send_request("queryHeadsets", params, self.QUERY_HEADSET_ID)
    
    def get_headset_status(self, headsetId):
        params = {
            "id": headsetId
        }
        self.create_send_request("queryHeadsets", params, self.HEADSET_STATUS_ID)

    def connect_headset(self, headsetId):
        params = {
            "command": "connect",
            "headset": headsetId
        }
        self.create_send_request("controlDevice", params, self.CONNECT_HEADSET_ID)
    
    def create_session(self):
        params = {
            "cortexToken": self.token,
            "headset": self.headset_id, 
            "status": "active"
        }
        self.create_send_request("createSession", params, self.CREATE_SESSION_ID)
    
    def query_profile(self):
        params = {
            "cortexToken": self.token,
        }
        self.create_send_request("queryProfile", params, self.QUERY_PROFILE_ID)
    
    def setup_profile(self, profile, action):
        self.profile_name = profile
        params = {
            "cortexToken": self.token,
            "headset": self.headset_id, 
            "profile": profile,
            "status": action
        }
        self.create_send_request("setupProfile", params, self.SETUP_PROFILE_ID)
    
    def get_trained_actions(self, profile):
        params = {
            "cortexToken": self.token, 
            "profile": profile,  
            "detection": "mentalCommand"
        }
        self.create_send_request("getTrainedSignatureActions", params, self.GET_TRAINED_ACTIONS_ID)

    def start_streams(self, streams):
        params = {
            "cortexToken": self.token, 
            "session": self.session_id, 
            "streams": streams
        }
        self.create_send_request("subscribe", params, self.SUB_REQUEST_ID)
    
    def train_request(self, command, status):
        params = {
            "cortexToken": self.token,
            "detection": "mentalCommand",
            "session": self.session_id, 
            "action": command, 
            "status": status
        }
        self.create_send_request("training", params, self.TRAIN_REQUEST_ID)

    def create_send_request(self, method, params, request_id):
        cortex_request = {
            "jsonrpc": "2.0", 
            "id": request_id,
            "method": method,
            "params": params
        }

        self.ws.send(json.dumps(cortex_request, indent=4))
    
    # Handling Data ----------------------------------------------------------
    def handle_result(self, recv_dic):
        if self.debug:
            print(recv_dic)
        
        req_id = recv_dic['id']
        result_dic = recv_dic['result']

        if req_id == self.CHECK_LOGIN_ID:

            if len(result_dic) != 0:
                self.username = result_dic[0]['username']
                print(f"[Cortex message] User {self.username} is logged in.")
                
                self.check_access()
            else: 
                print("[Cortex message] No user is logged in.")
        
        elif req_id == self.CHECK_ACCESS_ID:
            self.access_granted = result_dic['accessGranted']
            
            if self.access_granted:
                print("[Cortex message] Access granted.")
                self.authorize()
            else:
                print("[Cortex message] Access not granted.")
                # Call request access     

        elif req_id == self.AUTHORIZE_ID:
            self.token = result_dic['cortexToken']
            print(f"[Cortex message] Authorized. Cortex token {self.token}")
            
            self.query_headsets()
        
        elif req_id == self.QUERY_HEADSET_ID:
            self.available_headsets = result_dic
            
            if (len(self.available_headsets) != 0):
                print('[Cortex message] Headsets found.')
                self.headset_id = self.available_headsets[0]['id']
                self.get_headset_status(self.headset_id)           
        
        elif req_id == self.HEADSET_STATUS_ID:
            if len(result_dic) > 0:
                headset_status = result_dic[0]['status']

                if headset_status == 'connected':
                    print('[Cortex message] Headset already connected.')
                    # If headset is connected, create a session
                    self.create_session()
                    
                elif headset_status == 'discovered':
                    print('[Cortex message] Connecting headset...')
                    self.connect_headset(self.headset_id)
                else:
                    print(f'[Cortex message] Headset status: {headset_status}')
        
        elif req_id == self.CREATE_SESSION_ID:
            if len(result_dic) > 0:
                self.session_id = result_dic['id']
                print(f'[Cortex message] Session created, id {self.session_id}')
                self.emit('create_session_done')
        
        elif req_id == self.QUERY_PROFILE_ID:
            profile_list = []
            for ele in result_dic:
                name = ele['name']
                profile_list.append(name)
            self.emit('query_profile_done', profiles=profile_list)

        elif req_id == self.SETUP_PROFILE_ID:
            action = result_dic['action']
            if action == 'load':
                print('[Cortex message] Profile loaded successfully.')
                self.emit('setup_profile_done', isLoaded=True)
            if action == 'create':
                profile_name = result_dic['name']
                print(f'[Cortex message] Profile {profile_name} created successfully.')
                if profile_name == self.profile_name:
                    self.setup_profile(profile_name, 'load')

        elif req_id == self.GET_TRAINED_ACTIONS_ID:
            trainedActions = result_dic['trainedActions']
            self.emit('get_trained_actions_done', actions=trainedActions)

        elif req_id == self.SUB_REQUEST_ID:
            # handle data label
            for stream in result_dic['success']:
                stream_name = stream['streamName']
                stream_labels = stream['cols']
                print('[Cortex message] The data stream ' + stream_name + ' is subscribed successfully.')

                if stream_name != 'com' and stream_name != 'fac':
                    self.extract_data_labels(stream_name, stream_labels)
    
    def handle_stream_data(self, result_dic):
        if result_dic.get('com') is not None:
            com_data = {}
            com_data['action'] = result_dic['com'][0]
            com_data['power'] = result_dic['com'][1]
            com_data['time'] = result_dic['time']
            self.emit('new_com_data', data=com_data)
        
        elif result_dic.get('eeg') is not None:
            eeg_data = {}
            eeg_data['eeg'] = result_dic['eeg']
            eeg_data['eeg'].pop()  # remove markers
            eeg_data['time'] = result_dic['time']
            self.emit('new_eeg_data', data=eeg_data)
        
        elif result_dic.get('dev') is not None:
            dev_data = {}
            dev_data['signal'] = result_dic['dev'][1]
            dev_data['dev'] = result_dic['dev'][2]
            dev_data['batteryPercent'] = result_dic['dev'][3]
            dev_data['time'] = result_dic['time']
            self.emit('new_dev_data', data=dev_data)

        elif result_dic.get('pow') is not None: 
            pow_data = {}
            pow_data['pow'] = result_dic['pow']
            pow_data['time'] = result_dic['time']
            self.emit('new_pow_data', data=pow_data)
        
        elif result_dic.get('sys') is not None:
            sys_data = result_dic['sys']
            self.emit('new_sys_data', data=sys_data)

    def extract_data_labels(self, stream_name, stream_cols):
        labels = {}
        labels['streamName'] = stream_name

        data_labels = []
        if stream_name == 'eeg':
            # remove MARKERS
            data_labels = stream_cols[:-1]
        elif stream_name == 'dev':
            # get cq header column except battery, signal and battery percent
            data_labels = stream_cols[2]
        else:
            data_labels = stream_cols

        labels['labels'] = data_labels
        self.emit('new_data_labels', data=labels)      

    def handle_error(self, recv_dic):
        req_id = recv_dic['id']
        print('handle_error: request Id ' + str(req_id))
        print(recv_dic['error'])
        self.emit('inform_error', error_data=recv_dic['error'])
    
    def handle_warning(self, warning_dic):
        if self.debug: 
            print(warning_dic)
        
        warning_code = warning_dic['code']
        warning_msg = warning_dic['message']
        
        if warning_code == self.HEADSET_CONNECTED_CODE:
            print('[Cortex message] Headset connected')
            self.get_headset_status(self.headset_id) 

# ----------------------------------------------------------------------------


    


    
