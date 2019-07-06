import os
import re
import sys
import time
import datetime
import json
import traceback
import urllib.request, urllib.error, urllib.parse


# Global Variables
DEBUG    = 1                # Debug 0 off, 1 on
LOG      = 1                # Log Earthquake data for past 15 min
MINMAG   = 5.0              # Minimum magnitude to alert on
AUDIO    = 0                # Sound 0 off, 1 on
WAV      = "chime.wav"      # Path to Sound file
PAUSE    = 5                # Display each Earthquake for X seconds


def volume(val): # Set Volume based on Magnitude
  vol = str((int(val) * 5) + 50)
  cmd = "sudo amixer -q sset PCM,0 "+ str(vol)+"%"
  if DEBUG:
      cmd = "sudo amixer sset PCM,0 "+ str(vol)+"%"
  print(cmd)
  os.system(cmd)
  return

def sound(val): # Play a sound
  time.sleep(1)
  cmd = "/usr/bin/aplay -q "+ str(val)
  if DEBUG:
    print(cmd)
  os.system(cmd)
  return



if __name__ == '__main__':

  if AUDIO:
    volume(6)
    sound(WAV)

  # Get data from now to last 30 minutes
  utcnow = datetime.datetime.utcnow()
  utcnow_15 = utcnow - datetime.timedelta(minutes = 15)
  utcnow_30 = utcnow - datetime.timedelta(minutes = 30)
  utcnow_45 = utcnow - datetime.timedelta(minutes = 45)
  utcnow_test = utcnow - datetime.timedelta(hours = 24)
  starttime = utcnow_test.strftime('%Y-%m-%dT%H:%M:%S')
  endtime = utcnow.strftime('%Y-%m-%dT%H:%M:%S')

  lat = 34.0522
  long = -118.2437
  maxradiuskm = 300 * 1.609     # Miles to KM

  URL = "http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime="+starttime +"&endtime="+endtime +"&minmagnitude="+str(MINMAG)\
    +"&latitude="+str(lat) +"&longitude="+str(long) +"&maxradiuskm="+str(maxradiuskm) +"&orderby=time"
  if LOG:
    print(URL)

  # Call USGS API. timeout in seconds (USGS response time can be slow!)
  try:
    tmout = 120
    response = urllib.request.urlopen(URL, timeout=tmout)
    body = response.read()
    data = json.loads(body.decode('utf-8'))

    if DEBUG:
        print("--------------")
        print(data)
        print("--------------")
  except:
    print("Timeout waiting for USGS")

  if data['metadata']['count'] != 0:
    for feature in data['features']:
      try:
        tm  = feature['properties']['time']
        tm = tm/1000
        utime = datetime.datetime.utcfromtimestamp(int(tm)).strftime('%Y-%m-%d %H:%M:%S')
        mag = feature['properties']['mag']
        title = feature['properties']['title']
        place = feature['properties']['place']
        loc = feature['geometry']['coordinates']

        if LOG:
          print(mag)
          print(utime)
          print(place)
          print(loc)
          print(title)
          print("--------------")

        # Sound
        if AUDIO:
          volume(mag)
          sound(WAV)

        time.sleep(PAUSE)

      except NameError:
        print("No "+str(MINMAG)+" magnitude earthquakes in past 15 minutes")
        if DEBUG:
            print((traceback.format_exc()))

      except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        if DEBUG:
            print((traceback.format_exc()))
  else: 
    if LOG:
      print("No quakes in the last 30 min")

  time.sleep(PAUSE)

  if DEBUG:
    print("END OF RUN")