# lastfm_scrobblefix
A simple python script to correct any incorrect data of last.fm scrobbles: Fixes the annoying issue where scrobbles with multiple artists combine into one singular artist via a comma. Also removes remaster tags.

# How to use:
You will need a last.fm account with last.fm pro to utilize this script. 
Get an API_KEY and API_SECRET from last.fm and plug them in to the script along with your last.fm username and password. The script also requires selenium to work.

# What it actually does:
Observes a last.fm profile's most recent scrobbles and detects any incorrect scrobble data. When incorrect data is detected, a duplicate scrobble with correct data is created and the old scrobble with incorrect data is deleted via selenium.

# Useful links:
https://www.last.fm/api/authentication


