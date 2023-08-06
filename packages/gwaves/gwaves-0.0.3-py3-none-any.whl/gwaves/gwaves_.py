'''
get_data_gwosc
function
for getting the data from gwaves free's
Author: Reinan_Br
start: 13/11/2021 14:06
'''

import pandas as pd
import requests as rq
from bs4 import BeautifulSoup as bs
import os
import h5py
import matplotlib.pyplot as plt
import soundfile as sf
import numpy as np
from astropy.time import Time

class Gwaves_Data():
  def __init__(self,dir='.data_gwaves',file_data='data_gw',type_data='xlsx'):
    if os.path.isdir(dir):
      self.dir = dir
    else:
      os.mkdir(dir)
      self.dir = dir
    
    path_data =  f'{dir}/{file_data}.{type_data}'
    self.path_data = path_data
    
    if os.path.isfile(path_data):
      if type_data=='xlsx':
        data_gw = pd.read_excel(path_data)
    
    else:
      url_gwosc_base = 'https://www.gw-openscience.org'
      index_gwtc = '/eventapi/html/GWTC/'
      url_table = url_gwosc_base+index_gwtc
      
      ##getting the links_gwave##
      page_source = bs(rq.get(url_table).text,features='html.parser')
      links_gwave_index = [a['href'] for a in page_source.find('table').find_all('a', href=True) if a.text]
      links_gwave = []
      for index_gwave in links_gwave_index:
        links_gwave.append(url_gwosc_base+index_gwave)
      self.links_gwave=links_gwave

      ##getting the data table gtwc##
      data_gw = pd.read_html('https://www.gw-openscience.org/eventapi/html/GWTC/')[0]

      ## getting date ##
      dt = Time(data_gw['GPS'],format='gps').isot
      data_gw['Date']=dt
    
      ##addidng the link from an waves##
      assert len(data_gw['Name'])==len(links_gwave),"size of data gwaves e links from it's dataset is diference!"
      data_gw['Link']=links_gwave
      
      if type_data=='xlsx':
        data_gw.to_excel(path_data)

    ##creating a dict of gwaves_names_data##
    dict_gwaves = {}
    for i in range(len(data_gw['Name'])):
      dict_gwaves[data_gw['Name'][i]] = {'mass1':data_gw['Mass 1 (M☉)'][i],'mass2':data_gw['Mass 2 (M☉)'][i],
                                              'final_mass':data_gw['Final Mass (M☉)'][i],'distance':data_gw['Distance (Mpc)'][i],
                                              'link':data_gw['Link'][i],'date':data_gw['Date'][i]}
    
    ##saving on the class important variables##
    self.dict_gw = dict_gwaves
    self.data_gw = data_gw
    self.durations = ['32','4906']
    self.detectors = ['L1',"H1","V1"]
    self.freqs = ['32KHZ',"16KHZ"]
    self.filetypes = ['gwf','hdf','txt']
    self.dict_freq = {'32KHZ':32_000,'16KHZ':16_000}


  def get_dataframe_gwaves(self):
    return self.data_gw
  

  def get_dict_gwaves(self):
    return self.dict_gw


  def get_url_data(self,name_gwave,duration='32',detector='L1',freq='16KHZ',filetype='txt'):

    assert duration in self.durations,f'ERROR: duration {duration} not founded on the dataset: \ndurations:[{self.durations}]'
    assert freq in self.freqs, f'ERROR:  freq {freq} not founded in the dataset: \nfreqs:[{self.freqs}]'
    assert detector in self.detectors, f'ERROR: detector {detector} not founded in the dataset: \ndetectors:[{self.detectors}]'
    assert name_gwave in list(self.data_gw['Name']),f"ERROR: name gwave {name_gwave} not founded in the dataset: \nNames:[{self.data_gw['Name']}]"
    assert filetype in self.filetypes, f'ERROR: filetype {filetype} not founded in the dataset: \nfiletypes:[{self.filetypes}]'
    
    ##starting the show##
    url_gwave = self.dict_gw[name_gwave]['link']
    td=bs(rq.get(url_gwave).text).find_all('td')
    ld = [a.find('a')['href'] for a in td if a.find('a')]
    ldt = [link for link in ld if filetype in link and f'{duration}.' in link and detector in link and freq in link]

    return ldt
    
  def download_file(self,name_gwave,duration='32',detector='L1',freq='16KHZ',typefile='hdf',filename=None):
    assert name_gwave in list(self.data_gw['Name']),f"ERROR: name gwave {name_gwave} not founded in the dataset: \nNames:[{self.data_gw['Name']}]"
    assert typefile == 'hdf', f"in the moment, just 'hdf' typefile is accept to work, and not '{typefile}'"
    
    ## getting content file to download ##
    url_gwave = self.get_url_data(name_gwave,filetype=typefile,detector=detector,freq=freq,duration=duration)[0]
    content_file = rq.get(url_gwave).content
    size = len(content_file)
    if filename:
      path = f"{self.dir}/{filename}.hdf5"
      with open(path,'wb') as file_hdf:
        file_hdf.write(content_file)
    else:
      path = f"{self.dir}/{name_gwave}.hdf5"
      with open(path,'wb') as file_hdf:
        file_hdf.write(content_file)
    
    return {'pathfile':path,'size':size,'typefile':typefile,'freq':freq,'detector':detector}

  
  def get_gwave(self,name_gwave,duration='32',detector='L1',freq='16KHZ'):
    fil = self.download_file(name_gwave,detector=detector,freq=freq,duration=duration)
    pathfile=fil['pathfile']
    size = fil['size']
    detector = fil['detector']
    data = h5py.File(pathfile, 'r')
    wave = np.array((data['strain']['Strain']))
    return {'strain':wave,'freq':self.dict_freq[freq],'name':name_gwave,'date':self.dict_gw[name_gwave]['date'],'size':size,'detector':detector}


  def plot_from_gwname(self,name_gwave,duration='32',detector='L1',freq='16KHZ',figsize=(12,8)):
    wave = self.get_gwave(name_gwave,detector=detector,freq=freq,duration=duration)['strain']
    p = plt
    p.figure(figsize=figsize)
    p.style.context('science')
    time = np.linspace(0,1,len(wave))
    p.plot(time,wave)
    title = f"{name_gwave} [{detector}]\n{self.dict_gw[name_gwave]['date']}"
    p.grid()
    p.ylabel('strain')
    p.xlabel('time (s)')
    p.title(title)
    return p

  
  def plot_gwave(self,gwave,figsize=(12,8)):
    wave = gwave['strain'] #self.get_strain(name_gwave,detector=detector,freq=freq,duration=duration)['wave']
    p = plt
    p.figure(figsize=figsize)
    p.style.context('science')
    time = np.linspace(0,1,len(wave))
    p.plot(time,wave)
    name_gwave=gwave['name']
    detector=gwave['detector']
    title = f"{name_gwave} [{detector}]\n{self.dict_gw[name_gwave]['date']}"
    p.grid()
    p.ylabel('strain')
    p.xlabel('time (s)')
    p.title(title)
    return p



  def plot_psd_from_gwname(self,name_gwave,duration='32',detector='L1',freq='16KHZ'):
    strain = self.get_gwave(name_gwave,detector=detector,freq=freq,duration=duration)
    wave = strain['strain']
    Fs = strain['freq']
    NFFT = 4*Fs
    p = plt
    p.psd(wave,NFFT=NFFT,Fs=Fs)
    return p


  def psd_gwave(self,gwave):
      wave = gwave['strain']
      Fs = gwave['freq']
      NFFT = 4*Fs
      p = plt
      p.psd(wave,NFFT=NFFT,Fs=Fs)
      return p


  def get_audio_from_gwname(self,name_gwave,duration='32',detector='L1',freq='16KHZ',soundtime=8,path=None,vol=1e18,play=False):
    strain = self.get_gwave(name_gwave,detector=detector,freq=freq,duration=duration)
    wave = strain['wave']
    wave_sf = np.array(wave)*vol
    #wwave_sf+=derive*1e5

    fr = int(wave_sf.size/soundtime)
    wf = wave_sf #10* np.log10(wave_sf**2)
    #plt.plot(wf)
    if path:
      sf.write(path,wf,fr)
      if play:
        pass
      else:
        return path

    else:
      path = name_gwave+'.wav'
      sf.write(path,wf,fr)
      if play:
        pass
      else:
        return path

  def get_audio_gwave(self,gwave,soundtime=8,path=None,vol=1e17,play=False):
      wave = gwave['strain']
      name_gwave=gwave['name']
      wave_sf = np.array(wave)*vol
      #wwave_sf+=derive*1e5

      fr = int(wave_sf.size/soundtime)
      wf = wave_sf #10* np.log10(wave_sf**2)
      #plt.plot(wf)
      if path:
        sf.write(path,wf,fr)
        if play:
          pass
        else:
          return path

      else:
        path = name_gwave+'.wav'
        sf.write(path,wf,fr)
        if play:
          pass
        else:
          return path




  def __str__(self):
    print(self.data_gw.head())
    return ''
  



  


  



