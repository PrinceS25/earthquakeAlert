import os
import re
import sys
import time
import datetime
import json
import traceback
import urllib.request, urllib.error, urllib.parse


# Global Variables
DEBUG    = False             
LOG      = True             # Log Earthquake data for past 15 min
MINMAG   = 2.5              # Minimum magnitude to alert on
AUDIO    = True             # Sound
WAV      = "chime.wav"      # Path to Sound file
PAUSE    = 5                # Display each Earthquake for X seconds
OS       = ""

# <Lat, Long> coordinates to center of circle. 
# Raduis of circle in Kilometers 
LAT = 34.0522
LONG = -118.2437
MAX_RADIUS_KM = 200 * 1.609     # Miles to KM


# Plays sound, sets volume based on Magnitude for linux and mac
def playSound(wav, vol = 6): # Play a sound
  cmd = ""
  if OS == "linux" or OS == "mac":
    # Sets volume
    vol = str((int(vol) * 5) + 50)
    cmd = "sudo amixer -q sset PCM,0 "+ str(vol)+"%"
    if DEBUG:
      cmd = "sudo amixer sset PCM,0 "+ str(vol)+"%"
    os.system(cmd)

    time.sleep(1)

    # Plays sound
    if OS == "linux":
      cmd = "aplay -q "+ str(wav) + "&"
    elif OS == "mac":
      cmd = "afplay -q "+ str(wav) + "&"
    os.system(cmd)

  elif OS == "win":
    import winsound
    winsound.PlaySound(wav, winsound.SND_ASYNC)

  if DEBUG:
    print(OS, cmd)
  return



if __name__ == '__main__':

  if len(sys.argv) !=  2:
    print("Usage: python earthquakeAlert.py <win | linux | mac>")
    exit(1)

  OS = sys.argv[1]
  if OS not in ["win", "linux", "mac"]:
    print("Usage: python earthquakeAlert.py <win | linux | mac>")
    exit(1)


  pauseVar = PAUSE
  old_data = {}
  while True:

    # Get data from now to last 30 minutes
    utcnow = datetime.datetime.utcnow()
    utcnow_15 = utcnow - datetime.timedelta(minutes = 15)
    utcnow_30 = utcnow - datetime.timedelta(minutes = 30)
    utcnow_45 = utcnow - datetime.timedelta(minutes = 45)
    utcnow_test = utcnow - datetime.timedelta(hours = 24)
    starttime = utcnow_30.strftime('%Y-%m-%dT%H:%M:%S')   
    endtime = utcnow.strftime('%Y-%m-%dT%H:%M:%S')

    URL = "http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime="+starttime +"&endtime="+endtime +"&minmagnitude="+str(MINMAG)\
      +"&latitude="+str(LAT) +"&longitude="+str(LONG) +"&maxradiuskm="+str(MAX_RADIUS_KM) +"&orderby=time"
    if DEBUG:
      print(URL)


    # Call USGS API. timeout in seconds (USGS response time can be slow!)
    while True:
      try:
        tmout = 120
        response = urllib.request.urlopen(URL, timeout=tmout)
        body = response.read()
        data = json.loads(body.decode('utf-8'))
        
        if DEBUG:
            print("--------------")
            print(data)
            print("--------------")
        pasueVar = PAUSE
        break

      except:
        if LOG:
          print("Timeout waiting for USGS")
          print("Retrying..\n\n")
        time.sleep(pauseVar)
        if pauseVar < PAUSE * 10:
          pauseVar += pauseVar


    flag = True # Plays sound once
    if data['metadata']['count'] != 0 and old_data != data['features']:
      old_data = data['features']
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
          if AUDIO and flag:
            playSound(WAV, mag)
            flag = False

          time.sleep(PAUSE/4)
          pauseVar = PAUSE

        except Exception as e:
          print("Unexpected error:", sys.exc_info()[0])
          if DEBUG:
              print((traceback.format_exc()))

    elif data['metadata']['count'] == 0: 
      if LOG:
        print("No earthquakes in the last 30 min")
      if DEBUG:
        print("pauseVar in count:", pauseVar)
      time.sleep(pauseVar)  # Wait longer before refreshing
      if pauseVar < PAUSE * 20:
        pauseVar += pauseVar

    elif old_data == data['features']:
      if LOG:
        print("No new earthquakes in the last 30 min")
      if DEBUG:
        print("pauseVar in old_data:", pauseVar)
      time.sleep(pauseVar)  # Wait longer before refreshing
      if pauseVar < PAUSE * 10:
        pauseVar += pauseVar


    if DEBUG:
      print("END OF RUN")
      break
