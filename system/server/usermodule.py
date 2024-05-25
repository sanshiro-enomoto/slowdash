#! /usr/bin/env python3
# Created by Sanshiro Enomoto on 24 October 2022 #

import sys, os, time, logging, traceback
import importlib.machinery
import threading


class UserThread:
    def __init__(self, run_func, halt_func=None):
        self.run_func = run_func
        self.halt_func = halt_func
        self.thread = None

        
    def start(self):
        try:
            self.thread = threading.Thread(target=self.run_func)
            self.thread.start()
            logging.info('started user module run function')
        except Exception as e:
            logging.error('user module error: start(): %s' % str(e))
            logging.error(traceback.format_exc())

            
    def halt(self):
        if self.thread is not None:
            logging.info('stoping user module run function')
            if self.halt_func is not None:
                try:
                    self.halt_func()
                except Exception as e:
                    logging.error('user module error: halt(): %s' % str(e))
                    logging.error(traceback.format_exc())
                
            self.thread.join()
            self.thread = None
            logging.info('stopped user module run function')

            

class UserLoopThread(threading.Thread):
    def __init__(self, loop_func):
        threading.Thread.__init__(self)
        self.loop_func = loop_func
        self.is_stop_requested = False

        
    def run(self):
        logging.info('started user module loop function')
        while not self.is_stop_requested:
            try:
                self.loop_func()
            except Exception as e:
                logging.error('user module error: LoopThread.run(): %s' % str(e))
                logging.error(traceback.format_exc())
            time.sleep(0.01)

            
    def halt(self):
        self.is_stop_requested = True
        self.join()
        logging.info('stopped user module loop function')
            

            
class UserModule:        
    def _get_func(self, name):
        if (name in self.module.__dict__) and callable(self.module.__dict__[name]):
            return self.module.__dict__[name]
        else:
            return None
        
    def __init__(self, module, params):
        self.module = module
        self.func_get_channels = self._get_func('get_channels')
        self.func_get_data = self._get_func('get_data')
        self.func_process_command = self._get_func('process_command')
        self.func_initialize = self._get_func('initialize')
        self.func_finalize = self._get_func('finalize')
        self.func_run = self._get_func('run')
        self.func_halt = self._get_func('halt')
        self.func_loop = self._get_func('loop')

        self.user_thread = None
        
        if self.func_get_channels and self.func_get_data:
            logging.info('loaded user module data interface')
        if self.func_process_command:
            logging.info('loaded user module command processor')
                
        if self.func_initialize:
            try:
                self.func_initialize(params)
            except Exception as e:
                logging.error('user module error: func_initialize(): %s' % str(e))
                logging.error(traceback.format_exc())
                return

        if self.func_loop:
            if self.func_run is not None:
                logging.error('user module error: loop() and run() cannot be used at the same time')
            else:
                self.user_thread = UserLoopThread(self.func_loop)
                self.user_thread.start()
        elif self.func_run:
            if self.func_halt is None:
                logging.error('user module error: run() used without halt()')
            else:
                self.user_thread = UserThread(self.func_run, self.func_halt)
                self.user_thread.start()

                    
    def __del__(self):
        if self.user_thread is not None:
            self.user_thread.halt()
            
        if self.func_finalize is not None:
            try:
                self.func_finalize()
            except Exception as e:
                logging.error('user module error: __del__(): %s' % str(e))
                logging.error(traceback.format_exc())


                
    def get_channels(self):
        if self.func_get_channels:
            try:
                return self.func_get_channels()
            except Exception as e:
                logging.error('user module error: get_channels(): %s' % str(e))
                logging.error(traceback.format_exc())
        return None


    
    def get_data(self, channel):
        if self.func_get_data:
            try:
                return self.func_get_data(channel)
            except Exception as e:
                logging.error('user module error: get_data(): %s' % str(e))
                logging.error(traceback.format_exc())
        return None

    
    
    def process_command(self, params):
        if not self.func_process_command:
            return None
        
        try:
            return self.func_process_command(params)
        except Exception as e:
            logging.error('user module error: process_command(): %s' % str(e))
            logging.error(traceback.format_exc())
            return {'status': 'error', 'message': str(e) }


    
def load(ModuleClass, filepath, project_config, params):
    if os.path.exists(filepath):
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        try:
            module = importlib.machinery.SourceFileLoader(module_name, filepath).load_module()
        except Exception as e:
            logging.error('unable to load user module: %s' % str(e))
            logging.error(traceback.format_exc())
            return None

        usermodule = ModuleClass(module, params)
        usermodule.filepath = filepath

        return usermodule
