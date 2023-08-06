# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 12:01:13 2023

@author: Franco, Bruno Agustín 
         RCC Lab Development
         

Main module of MM-DP4+ probability method.

Tests:
    Solo C y solo H exp data
    (Un solo set wtl), (varios sets wtl), (sets wtl != cant isom)
    Label no encontrado 
    1 solo H o C (no puede escalar)
    ¡sp2 alert! 
    ¡massive error alert!
    output excel file already exists
    Deberia leer Hojas de calculo de open ofice en wtl??? (no solo xlsx)
    Normal termination check

Improve: 
    Mejorar como muestra la carpeta y el xlsx seleccionado en GUI
    Completar los docs string de las funciones y los modulos. Probar los help(*_module)
    
 AGREGAR DOCUMENTACION
 AGREGAR DOCUMENTACION
 AGREGAR DOCUMENTACION
"""
import shutil, os
import pandas as pd

from pathlib import Path

##### AGREGAR RELATIVE IMPORTS 
from . import main_gui_module as gui
from . import bugs_a_warning_module as trap
from . import dp4_module as dp4
from . import custom_gui_module as custom_gui
from . import custom_module as custom 
from . import output_module as output


def create_exe():
    '''Creates a direc acces executable file in the user desktop'''
    desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
    exe = shutil.which("dp4plus")
    
    shutil.copy(exe, desktop)
    return 

def main(): 
    '''AGREGAR DOCUMENTACION
    AGREGAR DOCUMENTACION
    AGREGAR DOCUMENTACION
    '''
    mode, inputs = gui.gui_input()    
    
    if ('Custom' in mode and
        type (inputs) is str and
        'reparametrize' in inputs) :
        
        inputs = custom_gui.custom_input()
        
        if 'Input' in inputs['mode']: 
            output.gen_out_custom(inputs['mode'], 
                                  inputs['name'], 
                                  inputs['C_TMS'],
                                  inputs['H_TMS'],
                                  inputs['param'])
        elif 'Load' in inputs['mode']:             
            
            trap.check_NormalTermination()
            for molec in inputs['set']:
                trap.xlsx_trap(inputs, sheet= molec)
                
                
            standard, parameters, command = custom.parametrize(inputs['xlsx'], inputs['set'])
        
            output.gen_out_custom(command, 
                                  inputs['name'], 
                                  standard['C'],
                                  standard['H'],
                                  parameters)
    
    else: 
        trap.xlsx_trap(inputs, sheet= 'shifts')
        trap.check_NormalTermination()
        
        if 'QM' in mode :
            data_base =  "data_base_QM.xlsx"
        elif 'MM' in mode:
            data_base =  "data_base_MM.xlsx"
        elif 'Custom' in mode:
            data_base =  "data_base_Custom.xlsx"
        
        data_base = (Path(__file__).parent / data_base).as_posix()
        
        stand = pd.read_excel(data_base,sheet_name='standard',index_col=0)
        stand = stand.loc[inputs['the_lev']]
        
        parameters = pd.read_excel(data_base,sheet_name=inputs['the_lev'],index_col=0)
        
        outputs = dp4.calc( inputs['isom'], inputs['xlsx'], stand, parameters)
     
        output.gen_out_dp4(mode, inputs, 
                           parameters, outputs, 
                           custom_mode = stand )
        
    gui.gui_end()   
    return
        

if __name__=='__main__': 

    main()