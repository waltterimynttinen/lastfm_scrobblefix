import requests
import xml.etree.ElementTree as ET
import hashlib
import re
import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

# Replace the API key, API secret, and username with your own
API_KEY = 'API_KEY'
API_SECRET = 'API_SECRET'
USERNAME = 'YOUR_USERNAME'
PASSWORD = 'YOUR_PASSWORD'

# The Last.fm API URL
API_URL = 'https://ws.audioscrobbler.com/2.0/'

# The method to obtain a session key
METHOD1 = 'auth.getMobileSession'

# The method to change the track
METHOD2 = 'track.updateNowPlaying'

# The method to change the track
METHOD3 = 'track.scrobble'

# Set API endpoint and parameters
endpoint = 'http://ws.audioscrobbler.com/2.0/'
params = {
    'method': 'user.getrecenttracks',
    'user': USERNAME,
    'api_key': API_KEY,
    'limit': '5',
    'format': 'xml'
}

# Generate the signature for the authentication request
api_sig1 = 'api_key' + API_KEY + 'method' + METHOD1 + 'password' + PASSWORD + 'username' + USERNAME + API_SECRET
api_sig1 = api_sig1.encode('utf-8')
api_sig1 = hashlib.md5(api_sig1).hexdigest()

# Request a session key from the Last.fm API
response = requests.post(API_URL, data={
    'method': METHOD1,
    'api_key': API_KEY,
    'username': USERNAME,
    'password': PASSWORD,
    'api_sig': api_sig1
})

# Parse the session key from the response
session_key = response.text.split('<key>')[1].split('</key>')[0]

# Create a list for exceptions and a boolean variable, a few examples added 

exceptionlist = ["Tyler, the Creator", "Black Country, New Road"]
exception = False   

def getTrackInformation():
    # Send request to Last.fm API
    response = requests.get(endpoint, params=params)

    # Parse response XML and extract track information
    root = ET.fromstring(response.text)
    tracks = root.find('recenttracks').findall('track')
    return tracks

def to_delete_exists(driver):
    print("Examining page for incorrect scrobbles")
    try:
        # Find the list of scrobbles
        scrobbles = driver.find_elements(By.CLASS_NAME, 'chartlist-row')

        # Extract and print the last 5 scrobbles
        for scrobble in scrobbles[1:5]:
            title = scrobble.find_element(By.CLASS_NAME, 'chartlist-name').text
            artist = scrobble.find_element(By.CLASS_NAME, 'chartlist-artist').text
            # Check if the scrobble title contains 'Remaster'
            if re.search('remaster', title, re.IGNORECASE):
                print('Incorrect track found!')
                # Hover over the scrobble to reveal the options button
                ActionChains(driver).move_to_element(scrobble).perform()

                # Find and click the options button (represented by three dots)
                options_button = scrobble.find_element(By.CLASS_NAME, 'chartlist-more-button')
                options_button.click()

                delete_button = scrobble.find_element(By.CLASS_NAME, 'more-item--delete')
                delete_button.click()
                print('Incorrect track deleted!')
            if re.search(',', artist):
                print('Incorrect track found!')
                # Hover over the scrobble to reveal the options button
                ActionChains(driver).move_to_element(scrobble).perform()

                # Find and click the options button (represented by three dots)
                options_button = scrobble.find_element(By.CLASS_NAME, 'chartlist-more-button')
                options_button.click()

                delete_button = scrobble.find_element(By.CLASS_NAME, 'more-item--delete')
                delete_button.click()
                print('Incorrect track deleted!')
    except Exception as e:
        print(f"Error fetching scrobbles: {e}")
        
    
      
def deleteScrobbles():
    print("deleting duplicate scrobbles")
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.last.fm/login')
    driver.find_element(by = By.ID, value = "id_username_or_email").send_keys(USERNAME)
    driver.find_element(by = By.ID, value = "id_password").send_keys(PASSWORD)

    WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "button[name='submit']")))
    try:
        # Find and click the "Accept All" button for cookies
        accept_cookies_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
        accept_cookies_button.click()
        print(f"Cookies accepted")
    except Exception as e:
        print(f"Error accepting cookies: {e}")

    while True:
            try:
                driver.find_element(by = By.CSS_SELECTOR, value = "button[name='submit']").click()
                break
            except:
                print("\nERROR! Can't access the webpage. You need to accept the cookies popup!")
                try:
                    # Find and click the "Accept All" button for cookies
                    accept_cookies_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
                    accept_cookies_button.click()
                    print(f"cookies accepted")
                except Exception as e:
                    print(f"Error accepting cookies: {e}")
    
    to_delete_exists(driver)
    driver.close()


# Function for removing ugly remaster tags

def remove_remaster_tag(input_string):
    pattern = r'(\[.*?Remaster.*?\])|(\(.*?Remaster.*?\))|(\[.*?mix.*?\])|(\(.*?mix.*?\))'
    result = re.sub(pattern, '', input_string, flags=re.IGNORECASE)
    return result.strip()

def updateNowPlaying(tracks):
    track_name = tracks[0].find('name').text
    artist = tracks[0].find('artist').text
    album_name = tracks[0].find('album').text
    if ',' in artist and not exception:
        corrected_artist = artist.split(',')[0]
        print(f'Incorrect artist name: {artist} ({track_name}).')
        artist = corrected_artist

        params = {
            'method': METHOD2,
            'artist': artist,
            'track': track_name,
            'album': album_name,
            'api_key': API_KEY,
            'sk': session_key,
        }
        # Generate the signature for the authentication request
        api_sig3 = ''.join([f'{key}{params[key]}' for key in sorted(params)])
        api_sig3 += API_SECRET
        api_sig3 = api_sig3.encode('utf-8')
        api_sig3 = hashlib.md5(api_sig3).hexdigest()

        # Add the api_sig to the parameters
        params['api_sig'] = api_sig3

        # Send request to Last.fm API
        response = requests.post(API_URL, data=params)

        print(f'Currently playing: ', track_name)

    if re.search('remaster', track_name, re.IGNORECASE):
        print(f'Incorrect track name playing: {track_name}.')
        corrected_track_name = remove_remaster_tag(track_name)
        track_name = corrected_track_name

        #also check the album name
        if re.search('remaster', album_name, re.IGNORECASE):
            print(f'Incorrect album name playing: {album_name}).')
            corrected_album_name = remove_remaster_tag(album_name)
            album_name = corrected_album_name

        params = {
            'method': METHOD2,
            'artist': artist,
            'track': track_name,
            'album': album_name,
            'api_key': API_KEY,
            'sk': session_key,
        }
        # Generate the signature for the authentication request
        api_sig3 = ''.join([f'{key}{params[key]}' for key in sorted(params)])
        api_sig3 += API_SECRET
        api_sig3 = api_sig3.encode('utf-8')
        api_sig3 = hashlib.md5(api_sig3).hexdigest()

        # Add the api_sig to the parameters
        params['api_sig'] = api_sig3

        # Send request to Last.fm API
        response = requests.post(API_URL, data=params)

        print(f'Currently playing: ', track_name)    

# Loop through tracks and fix any incorrect artist names
def fixScrobbles(tracks):
    del tracks[0]
    for track in tracks:
        artist = track.find('artist').text
        track_name = track.find('name').text
        album_name = track.find('album').text

        print(f'Scrobble:', artist, track_name, album_name)

        print

        if artist in exceptionlist:
            exception = True
            print('An artist with a comma in their name spotted!')
        else:
            exception = False
        
        # Check if the artist name contains a comma
        if ',' in artist and not exception:
            corrected_artist = artist.split(',')[0]
            print(f'Incorrect artist name: {artist} ({track_name}).')
            artist = corrected_artist

            #Timestamp shit w datetime
            timestamp = int(track.find('date').get('uts'))

            params = {
                'method': METHOD3,
                'artist': artist,
                'timestamp': timestamp,
                'track': track_name,
                'albumArtist': artist,
                'album': album_name,
                'api_key': API_KEY,
                'sk': session_key,
            }

            # Generate the signature for the authentication request
            api_sig2 = ''.join([f'{key}{params[key]}' for key in sorted(params)])
            api_sig2 += API_SECRET
            api_sig2 = api_sig2.encode('utf-8')
            api_sig2 = hashlib.md5(api_sig2).hexdigest()

            # Add the api_sig to the parameters
            params['api_sig'] = api_sig2

            # Send request to Last.fm API
            response = requests.post(API_URL, data=params)
            
            print(f'Corrected to: {corrected_artist}')
            time.sleep(5)
            deleteScrobbles()

        if re.search('remaster', track_name, re.IGNORECASE):
            print(f'Incorrect track name: {track_name}).')
            corrected_track_name = remove_remaster_tag(track_name)
            #Timestamp shit w datetime
            timestamp = int(track.find('date').get('uts'))
            track_name = corrected_track_name

            #also check the album name
            if re.search('remaster', album_name, re.IGNORECASE):
                print(f'Incorrect album name: {album_name}).')
                corrected_album_name = remove_remaster_tag(album_name)
                album_name = corrected_album_name

            params = {
                'method': METHOD3,
                'artist': artist,
                'timestamp': timestamp,
                'track': track_name,
                'albumArtist': artist,
                'album': album_name,
                'api_key': API_KEY,
                'sk': session_key,
            }

            # Generate the signature for the authentication request
            api_sig2 = ''.join([f'{key}{params[key]}' for key in sorted(params)])
            api_sig2 += API_SECRET
            api_sig2 = api_sig2.encode('utf-8')
            api_sig2 = hashlib.md5(api_sig2).hexdigest()

            # Add the api_sig to the parameters
            params['api_sig'] = api_sig2

            # Send request to Last.fm API
            response = requests.post(API_URL, data=params)
            
            print(f'Corrected to: {corrected_track_name}')
            time.sleep(5)
            deleteScrobbles()

while True:
    print("Checking scrobbles...")
    updateNowPlaying(getTrackInformation())
    fixScrobbles(getTrackInformation())
    print("Scrobbles are correct")
    #Can be changed to modify how often scrobbles are checked"
    time.sleep(10)