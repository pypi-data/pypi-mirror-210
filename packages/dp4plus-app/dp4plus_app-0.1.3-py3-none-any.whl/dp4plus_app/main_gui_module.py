# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 01:21:17 2022

@author: Franco, Bruno Agustín 
 

Graphical user interface (GUI) designed for inputting data in correlation 
NMR calcs. 
The function gui_input() is made to be used as widget in calc scripts. 
Besides gui_end() is there to give neat conclusion of the programme. 

"""

import tkinter as tk
import pandas as pd
import os, shutil, webbrowser, glob

from collections import Counter
from pathlib import Path
from sys import exit
from tkinter import filedialog
from random import sample, randint

def gui_input():
    '''Main structure of the widget app (GUI). 
    The window design is placed here, while the funtions of each element are 
    defined apart. Each element is globaled to be controled during decisions. 
    The result are not return untill the app is quit in the last step (run_calc())
    
        Returns
    mode: 'QM', 'MM' or 'Custom'
    for 'Custom' the other variable indicates the TheLev or if it's a reparametrization
    for 'QM' and 'MM', it gives the inputs for the DP4 calculation
    '''
    global root
    root = tk.Tk()      #define the widget
    root.wm_title("DP4+ App")
    root.geometry("750x260")
    
    title = tk.Label( root, text= 'DP4+ App')
    title.place(x=20, y= 5)
    title.config(font = ("Times", "35", "bold"))
    
    title = tk.Label( root, text= 'A tool to facilitate your DP4+ calculations')
    title.place(x=250, y= 15)
    title.config(font = ("Times", "11"),justify='right')
    
    title = tk.Label( root, text= '- - - - - - - - - - - - - - - - - - - - - - - - - - - -')
    title.place(x=250, y= 34)
    title.config(font = ("Times", "11", 'bold'),justify='right')
    #-----------------------------------------------------------------
    button_userguide = tk.Button(root, text='User Guide', 
                               command=user_guide).place(x=650,y=10)
    #-----------------------------------------------------------------
    button_example = tk.Button(root, text='Create Example', 
                               command=example).place(x=635,y=42)
    #-----------------------------------------------------------------
    button_end = tk.Button(root, text='Exit', 
                           command=exit).place(x=665,y=217)
    #-----------------------------------------------------------------
    global button_run
    button_run = tk.Button(root, text='Run',
                                font=("Arial Black", 10),
                                command=lambda: run_calc(),
                                state='disabled')
    button_run.place(x=20,y=215)    
    #-----------------------------------------------------------------
    global mode_list, mode_ddl #ddl: DropDownList
    mode_list = tk.StringVar(root)
    mode_list.set('Mode')
    mode_ddl = tk.OptionMenu(root, mode_list,  
                             command = lambda x: select_mode(),
                             *['QM (B3LYP/6-31G*)', 'MM (MMFF)','Custom'])
    mode_ddl.configure(state='active', width = 17)
    mode_ddl.place(x=20,y=70)
    #-----------------------------------------------------------------
    global func_list, func_ddl #ddl: DropDownList
    func_list = tk.StringVar(root)
    func_list.set('Functional')
    func_list.trace('w',lambda x,y,z: decisions())
    func_ddl = tk.OptionMenu(root, func_list, '')
    func_ddl.configure(state='disabled', width = 15)
    func_ddl.place(x=170,y=70)
    #-----------------------------------------------------------------
    global base_list, base_ddl #ddl: DropDownList
    base_list = tk.StringVar(root)
    base_list.set('Basis Set')
    base_list.trace('w',lambda x,y,z: decisions())
    base_ddl = tk.OptionMenu(root, base_list, '')
    base_ddl.configure(state='disabled', width = 15)
    base_ddl.place(x=310,y=70)
    #-----------------------------------------------------------------
    global solv_list, solv_ddl #ddl: DropDownList
    solv_list = tk.StringVar(root)
    solv_list.set('Solvatation')
    solv_list.trace('w',lambda x,y,z: decisions())
    solv_ddl = tk.OptionMenu(root, solv_list, '')
    solv_ddl.configure(state='disabled', width = 15)
    solv_ddl.place(x=450,y=70)

    #-----------------------------------------------------------------
    global button_xlsx, button_dir
    button_xlsx = tk.Button(root, text='Select Excel',
                           font=("Helvetica", 10),
                           command=lambda: select_xlsx (),
                           state='disabled')
    button_xlsx.place(x=20,y=180)
    #-----------------------------------------------------------------
    button_dir = tk.Button(root, text='Select Directory',
                           font=("Helvetica", 10),
                           command=lambda: select_dir (),
                           state='disabled')
    button_dir.place(x=20,y=110)
    #-----------------------------------------------------------------
    root.mainloop() #keep the window open while programme is running
    
    if 'reparametrize' in the_lev : 
        return mode, the_lev
    else: 
        return mode, {'isom':isomer_list,
                      'the_lev': the_lev,
                      'xlsx': xlsx,
                      'G09command': G09command,
                      'warn': warn}
    

def user_guide():
    '''Open user guide documentation
    '''
    file = (Path(__file__).parent / "UserGuide" /"UserGuide.pdf").as_posix()
    webbrowser.open_new(file)
    return
    
def example(): 
    '''Copy an example folder into the user Desktop for trying the programm
    '''
    desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
    example_fold = (Path(__file__).parent / "nmr_examples").as_posix()
    
    dst_folder = os.path.join(desktop,"nmr_examples")
    if  os.path.exists(dst_folder):
        dst_folder = dst_folder+f'_{str(randint(0, 100))}'
    shutil.copytree(example_fold, dst_folder)
    
    root.quit()
    
    examp_add = tk.Tk()
    examp_add.wm_title("DP4+ App")
    tk.Label(examp_add,text = u' Folder Copy \u2713', 
             font = ("Arial Black", "12")).grid(row=0)
    tk.Label(examp_add,text ='"nmr_examples" has been created in your desktop', 
             font = ("Arial Bold", "10")).grid(row=1, pady=10)
    tk.Label(examp_add,text ='The program will restarts. Follow the user guide instructions to process the data', 
             font = ("Arial Bold", "10")).grid(row=2, padx=10)
    tk.Button(examp_add, text='Ok', 
              command= exit).grid(row=3, pady=5 )
    
    examp_add.mainloop()

    return

def select_dir():
    '''Select directory. If it doesn't find .log and/or well rotulated 
    elements doesnt enable next button.
    It changes the working directory to the path selected
    '''
    root.direc = filedialog.askdirectory(title='Select directory')
    
    tk.Label(root,text='\n   \n', width=60, height=15 ).place(x=145,y=120)
    
    singboard = tk.Label(root, text='')
    singboard.place(x=148,y=115)
    
    if root.direc == '':
        singboard.config( text='<- Select a folder                                     ')
        button_run['state'] = 'disable'
        return
    
    os.chdir(root.direc)
    
    if not glob.glob('*nmr*.log') + glob.glob('*nmr*.out'):
        singboard.config( text='"_nmr" G09 files not found. Try again')
        button_run['state'] = 'disable'
        return
    
    sing = root.direc[:9]+'  . . .  '+root.direc[-50:]
    singboard.config( text=sing)
    
    global isomer_list
    isomer_list, cant_comp = isomer_count() 
    
    tk.Label(root, text=f'Isomeric Candidates:  {isomer_list}').place(x=160,y=138)
    button_xlsx['state']='active'
    
    thlev_id()
    
    return    

def select_xlsx():
    '''Select xlsx file with experimental data and asignation labels. 
    If it doesn't find "shifts" sheet, ask again and doesn't enable next button
    Returns the path of the selected file as str
    '''
    global xlsx
    xlsx = root.xlsx = filedialog.askopenfilename(title='Select Excel',
                                   filetypes=[('Excel files',['*.xlsx','*.xls','*.xlsm','*.xlsb']),
                                              ('OpenOffice files',['*.ods','*.odt','*.odf']),
                                              ('All files','*')])
    
    singboard = tk.Label(root,text = '',  width=60, anchor = 'w')
    singboard.place(x=148,y=185)
    
    if root.xlsx == '':
        singboard ['text'] = '<- Select exp. data file'
        button_run['state'] = 'disable'
        return
    elif 'shifts' not in pd.ExcelFile(root.xlsx).sheet_names: 
        singboard ['text'] = '"shifts" sheet was not found. Try again'
        root.xlsx = ''
        button_run['state'] = 'disable'
        return
    else:
        sing = root.xlsx[:9]+'  . . .  '+root.xlsx[-50:]
        singboard ['text'] = sing
        button_run['state']='active'  
        
    return

def select_mode():
    '''Response actions according to the selected mode
    In QM and MM modes, enables the right funtional, basis set, solvatation 
    to avoid incorrect use of the theory levels. 
    In 'Custom' mode enable parametrized method (by user) or create a new one
    '''
    func_ddl['menu'].delete(0,'end')
    base_ddl['menu'].delete(0,'end')
    solv_ddl['menu'].delete(0,'end')
    
    tk.Label(root,text='\n   \n', width=60, height=15 ).place(x=145,y=120)
    
    button_dir ['state'] = 'disable'
    button_xlsx['state'] = 'disable'
    button_run['state'] = 'disable'
    button_run ['text'] = 'Run'
    
    if 'Custom' in mode_list.get():
        data_base = (Path(__file__).parent / 'data_base_Custom.xlsx').as_posix()
        levels = pd.ExcelFile(data_base).sheet_names
        levels.append('+ new')
        
        for choice in levels:
            if choice == 'standard' :  continue
            func_ddl['menu'].add_command(label=choice, command=tk._setit(func_list, choice))
        func_ddl['state']='active'
        base_ddl['state']='disable'
        solv_ddl['state']='disable'
        
        func_list.set('Level')
        base_list.set('--')
        solv_list.set('--')
        
        return
    
    elif 'MM' in mode_list.get():
        for choice in ['B3LYP', 'M062x', 'mPW1PW91', 'wB97XD']:
            func_ddl['menu'].add_command(label=choice, command=tk._setit(func_list, choice))
        for choice in ['6-31G(d,p)', '6-31+G(d,p)','6-311+G(d,p)']:
            base_ddl['menu'].add_command(label=choice, command=tk._setit(base_list, choice))
        for choice in ['GAS', 'PCM','SMD']:
            solv_ddl['menu'].add_command(label=choice, command=tk._setit(solv_list, choice))
    
    
    elif 'QM' in mode_list.get(): 
        for choice in ['B3LYP','mPW1PW91']:
            func_ddl['menu'].add_command(label=choice, command=tk._setit(func_list, choice))
        for choice in ['6-31G(d)','6-31G(d,p)','6-31+G(d,p)', '6-311G(d,p)','6-311+G(d,p)']:
            base_ddl['menu'].add_command(label=choice, command=tk._setit(base_list, choice))
        for choice in ['GAS', 'PCM']:
            solv_ddl['menu'].add_command(label=choice, command=tk._setit(solv_list, choice))
    
    func_ddl['state']='active'
    base_ddl['state']='active'
    solv_ddl['state']='active'
    
    func_list.set('Functional')
    base_list.set('Basis Set')
    solv_list.set('Solvatation')

        
    return

def decisions():
    '''Response to the selected mode that will indicate the main funtion what
    to do.'Run' indicates DP4+ calc and 'Reparametrize' training a new 
    theory level
    '''
    button_dir ['state'] = 'disable'
    button_xlsx ['state'] = 'disable'
    button_run ['state'] = 'disable'
    tk.Label(root,text='\n   \n', width=60, height=15 ).place(x=145,y=120)
    
    if 'new' in func_list.get(): 
        button_run ['text'] = 'Reparametrize'
        button_run ['state'] = 'active'
        
    elif ('Functional' not in func_list.get() and
          'Basis' not in base_list.get() and
          'Solv' not in solv_list.get() and
          '--' not in base_list.get()) : 
        
        button_run ['text'] = 'Run'
        button_dir ['state'] = 'active'
        
    if ('Custom' in mode_list.get() and
        'new' not in func_list.get() and
        'Level' not in func_list.get()): 
        
        button_run ['text'] = 'Run'
        button_dir ['state'] = 'active'
        
    
    return

def run_calc():
    '''Accordint to the last button label, prepare the variable response to
    be return to the main program. 
    '''
    global mode
    mode = mode_list.get()
    
    if button_run['text'] == 'Run':
        global the_lev
        if 'Custom' in mode : 
            the_lev = func_list.get()
        elif 'GAS' in solv_list.get():
            the_lev = func_list.get()+"."+base_list.get()
        else: 
            the_lev = func_list.get()+"."+base_list.get()+"."+solv_list.get()
        
        tk.Label(root,text='Processing . . .').place(x=70,y=220)
        root.after(2000, root.quit)
        #Tiempo de espera para cerrar GUI. Es para que el usuario no le de ansiedat
        #Se frena el script, pero la GUI puede modificar sus carteles, es decir, 
        #corre las lineas siguientes 
        
    elif button_run['text'] == 'Reparametrize':
        tk.Label(root,text='Redirecting . . .').place(x=150,y=220)
        the_lev = 'reparametrize'
        root.after(1000, root.destroy)
    
    for button in [button_dir, button_xlsx, button_run,
                   mode_ddl, func_ddl, base_ddl, solv_ddl]:
        button['state']='disabled'
        
    return 

def isomer_count():
    '''Determine the amount of isomeric candidates to be evaluated
    The files must be named by: isomerID_ * .log '''
    files= glob.glob('*nmr*.log') + glob.glob('*nmr*.out')
    isomer_list =[]
    for file in files:
        if file.split('_',1)[0] not in isomer_list:
            isomer_list.append(file.split('_',1)[0])
        else:
            continue
    isomer_list.sort() ##RG
    isomer_list.sort(key=lambda s: len(s)) #RG    
    return isomer_list, len(isomer_list)

def thlev_id():
    '''It chooses 10% random files and check if the user theory level input
    match the G09 calcs command lines. 
    First assumption is there are no mistakes (wanr is empty). If 
    inconsistencies are found the appropiate warning is added to the list.
    '''
    files= glob.glob('*nmr*.log') + glob.glob('*nmr*.out')
    
    choose = sample(files, (len(files)//10)+1 )
    
    singboard = tk.Label(root, text='')
    singboard.place(x=160,y=160)    
    
    global warn, G09command
    warn = []
    
    if 'Custom' in mode_list.get(): 
        warn.append('Custom mode. Theory Level not checked')
    
    for file in choose: 
        with open(file,'r') as to_read: 
            
                for G09command in to_read.readlines(): 
                    if '#' in G09command:   break
                
                if 'Custom' in mode_list.get(): 
                    warn.append('Custom mode. Theory Level not checked')
                    continue
                    
                if (func_list.get()).casefold() not in G09command.casefold(): 
                    warn.append(f'{func_list.get()} does not match')
                
                gto, polar = (base_list.get()).split('(')
                if (gto.casefold() not in G09command.casefold()): 
                    warn.append(f'{base_list.get()} does not match') 
                
                if 'd,p' in polar: 
                    if ('d,p' not in G09command.casefold() and
                        '**' not in G09command.casefold()): 
                        warn.append(f'{base_list.get()} does not match')
                else: 
                    if ('d' not in G09command.casefold() and
                        '*' not in G09command.casefold()): 
                        warn.append(f'{base_list.get()} does not match')
                    elif ('d,p' in G09command.casefold() or
                        '**' in G09command.casefold()): 
                        warn.append(f'{base_list.get()} does not match')
               
                if 'GAS' in solv_list.get():
                    if 'pcm' in G09command.casefold(): 
                        warn.append('Not GAS method')
                else: 
                    if ('chloroform' not in G09command.casefold() and
                        'chcl3' not in G09command.casefold()):
                        warn.append('chloroform(chcl3) not used as solvent')
                    if 'pcm' not in G09command.casefold(): 
                        warn.append('Not PCM method')
                    if 'PCM' in solv_list.get(): 
                        if 'smd' in G09command.casefold(): 
                            warn.append('Calcs in SMD do not match PCM method')
                    else: 
                        if 'smd' not in G09command.casefold():
                            warn.append('SMD does not match')
                        
                
    if not warn : singboard['text'] = u'Theory level has been corroborated \u2713'
    
    elif 'Custom' in mode_list.get(): 
        singboard['text'] = 'Custom mode. Theory Level not cheked'
    
    else: 
        warn = Counter(warn)
        singboard['text'] = u'Theory level entered does not match with the files \u2716'
    
        warn_add = tk.Toplevel()
        warn_add.wm_title("DP4+ App")

        tk.Label(warn_add,text = '¡ Warning !', 
                 font = ("Arial Black", "12")).grid(row=1)
        tk.Label(warn_add,text = 'The selected level of theory does not match the one in the calculations.',
                 font = ("Arial Bold", "10")).grid(row=2, pady=10)
        tk.Label(warn_add,text ='It is recommended to correct the inconsistency.', 
                 font = ("Arial Bold", "10")).grid(row=3, padx=10)
        tk.Button(warn_add, text='Ok', 
                  command=warn_add.destroy).grid(row=4, pady=5, padx =10)
        warn_add.wait_window()
    return
    

def gui_end():
    '''Final window to politely finish the programe'''
    byby = tk.Tk()
    byby.wm_title("DP4+ App")
    
    tk.Label(byby,text = u' Procces completed \u2713', 
             font = ("Arial Black", "12")).grid(row=0,padx=10, pady=(10,0))
    tk.Label(byby,text ='Press Exit to finish', 
             font = ("Arial Bold", "10")).grid(row=1,padx=10, pady=5)
    tk.Button(byby, text='Exit', 
              command= exit).grid(row=3, pady=(5,10))
    
    byby.mainloop()
    
    return
