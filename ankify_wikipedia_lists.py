"""
	This script takes a Wikipedia list article 
	and attempts to make an Anki deck out of it.
	Each entry in the list should make a card, where the front
	is the article main image and the back is the article title. 

	It's super hacky and not at all guaranteed to work for every list,
	but here's how to use it:

	- Update LIST_URL to point to the list you want to Anki-fy.
	- Update ANKI_IMG_DIR to point to your Anki media directory.
	- Run the script. Depending on list size, maybe go have a coffee break. Don't close the console!
	- When the script finishes, open Anki and make a new deck. 
	- Go to File --> Import. Pick your CSV file. 
	- Make sure "Allow HTML in Fields" is checked and that the "Deck" field points to your new deck.
	- Press "OK". 
	- Now check the console output. It'll list out any pages it failed to make cards for. You can
	  manually create these cards and add them to your deck if you want. My birds deck
	  ended up with 366 birds in it, one of which I had to make manually. 
	- Enjoy!

"""


import re
import os.path
import urllib.request
import html.parser 

# The URL of the list to scrape cards from.
LIST_URL = "http://en.wikipedia.org/wiki/List_of_birds_of_British_Columbia"

# The directory to output the images into.
ANKI_IMG_DIR = r"D:\Documents\Anki\User 1\collection.media\\"

# The file to output the anki csv file to
ANKI_CSV_FILE = r'C:\ankified_list_csv.txt'

# Pattern to find links to each article.
# We assume that each relevant link is an anchor tag directly inside a list. 
link_pattern = r"\<li\>\<a href=\"([^\":]+)\"[^>]+>[^<]+\</a>"

# Pattern to find the page title. We'll use this as the card answer.
title_pattern = r"<title>(.+) - Wikipedia, the free encyclopedia</title>"

# Pattern to find the main image. We'll use the first jpeg on the page.
# (Some pages have png icons at the top inside banners, e.g., when a page is locked.)
image_pattern = r"<img (?:alt=\"[^\"]+\")? src=\"([^\"]+\.jpe?g)\""


# Read the list source
response = urllib.request.urlopen(LIST_URL)
list_text = str(response.read())

# Look for links to the articles. 
matches = re.findall(link_pattern, list_text)
csv = ""
for match in matches:
	# Grab the page referenced in the link.
	response = urllib.request.urlopen("http://en.wikipedia.org" + match)
	html_text = str(response.read())

	# Get the page title
	title = re.search(title_pattern, html_text).group(1)

	# Try to find an image on the page
	try:
		image = "http:"+re.search(image_pattern, html_text, re.IGNORECASE).group(1)
	except:
		# Didn't find an image, can't really make a card then.
		# Print out the name of the thing so the user can manually make a card if they want.
		print("No image found for %s" % title)
		continue
	imageBasename = os.path.basename(image)

	# Grab the image we found and store it in the image directory.
	urllib.request.urlretrieve(image, ANKI_IMG_DIR+imageBasename)

	# Add the card to our csv string.
	imageLink = "<img src='%s'>"  % imageBasename
	csv += "%s,%s\n" % (imageLink, title)

# Save our csv file.
f = open(ANKI_CSV_FILE,'w')
print(csv, file=f)