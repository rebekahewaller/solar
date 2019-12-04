#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 00:45:26 2019

@author: bekah
"""

import pandas as pd
import datetime as dt

import tkinter
from tkinter import filedialog

root = tkinter.Tk()
root.wm_withdraw()

def make_df():
    """Create pandas dataframe for data file"""
    
    data_file = filedialog.askopenfilename(parent=root)
    df = pd.read_csv(data_file)

    return df
    
    root.destroy()

def time_range():
    """Remove iv curve measurements outside of desired time range"""
    
    df = make_df()

    df['time'] = pd.DatetimeIndex(df['time'])
    df.set_index(keys='time', inplace=True)
    
    start = dt.time(6,0,0)
    end = dt.time(18,0,0)
    
    df_range = df.between_time(start,end)
    return df_range
            
def boo_time(t):
    """Return boolean for comparing timedelta values"""
    
    t1 = dt.timedelta(minutes=1)
    boo = t > t1
    
    return boo


def curve_counter():
    """Count iv curve measurement in data set"""
    
    df = time_range()
    
    df['tvalue'] = df.index
    df['elapsed_minutes'] = (df['tvalue']-df['tvalue'].shift()).fillna(0)
    df['curve_id'] = 1 
        
    for i in range(len(df['elapsed_minutes'])):
           
        crv = df['curve_id'][i]

        boo = boo_time(df['elapsed_minutes'][i])
        
        if boo is True:
           df['curve_id'][i] = df['curve_id'][i-1] + 1
           crv = df['curve_id'][i]
        
        else:
            df['curve_id'][i] = df['curve_id'][i-1]
    
    return df
        
def env_data():
    """Index and clean up environmental data from datalogger"""
    
    print("Select environmental data csv file")
    df_env = make_df()
    df_env['TIMESTAMP'] = pd.DatetimeIndex(df_env['TIMESTAMP'])
    df_env.set_index(keys='TIMESTAMP', inplace=True)
    
    df_env_clean = df_env._get_numeric_data()
    df_env_clean[df_env_clean < 0] = 0
        
    return df_env_clean
    
def match_env():
    """Match corresponding environmental measurement to IV curve measurement"""
    
    print("Select opv data file")
    df_opv = curve_counter()
    
    df_env = env_data()

    m = pd.merge(df_opv, df_env, how='inner',left_index=True,right_index=True)
    
    return m

def process_data():
    """Process data for each IV curve measurement"""
    
    df = match_env()
    
    df_out = pd.DataFrame(columns=['opv',
                                   'curve_id',
                                   'time',
                                   'hour',
                                   'voc',
                                   'jsc',
                                   'mpp',
                                   'ff',
                                   'radiation', 
                                   'area (m2)',
                                   'eff (%)',
                                   'air_temp',
                                   'rel_hum',
                                   ])
    
    max_curve_id = df['curve_id'].max()
    curve_id_count = 1

    for i in range(max_curve_id):

        curve = df.loc[lambda df: df['curve_id'] == curve_id_count]
    
        opv = curve['opv'][0]
        time = curve['tvalue'][0] # start time of IV curve measurement
        hour = curve['tvalue'][0].hour + curve['tvalue'][0].minute / 60
        voc = curve['volts'].max()
        jsc = curve['current'].max()
        mpp = curve['power'].max()
        ff = mpp / (voc * jsc)
        rad = curve['radiation'][0]
        area = 3.396
        eff = (mpp / (rad * area)) * 100
        air = curve['air_temp'][0]
        rh = curve['rel_hum'][0]
        
        df_out = df_out.append({
                'opv': opv,
                'curve_id': curve_id_count,
                'time': time,
                'hour': hour,
                'voc': voc,
                'jsc': jsc,
                'mpp': mpp,
                'ff': ff,
                'radiation': rad,
                'area (m2)': area,
                'eff (%)': eff,
                'air_temp': air,
                'rel_hum': rh,
                }, ignore_index = True)
        
        curve_id_count += 1
                
    return df_out

def write_out():
    """Write out processed data file to csv"""
    
    df = process_data()
    
    opv = 'opv' + str(df['opv'][0])
    date = str(df['time'][0].month) + '-' + str(df['time'][0].day) + '-' + str(df['time'][0].year)
    
    df.to_csv(path_or_buf= '/Users/bekah/Desktop/opv_data/ivcurve_measurements/final_data/' + opv + '_' + date + '.csv')
    
def main():
    
    write_out()
    root.mainloop()
    

    
    
    
    
    