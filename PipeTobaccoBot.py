#!/usr/bin/python

from HTMLParser import HTMLParser
from ReddiWrap import ReddiWrap
import re
import time
import urllib2

tobaccoName = ""

class MyHTMLParser(HTMLParser):
	
	def handle_starttag(self, tag, attrs):
		global tobaccoName
		if(tag == "meta"):
			if 'itemprop' in dict(attrs):
				if dict(attrs)['itemprop'] == "itemreviewed":
					tobaccoName = dict(attrs)['content']


reddit = ReddiWrap(user_agent='ReddiWrap')

USERNAME = 'PipeTobaccoBot'
PASSWORD = 'pipetobaccobot.py'
MOD_SUB  = 'PipeTobacco' # A subreddit moderated by USERNAME

# Load cookies from local file and verify cookies are valid
reddit.load_cookies('cookies.txt')

# If we had no cookies, or cookies were invalid, 
# or the user we are logging into wasn't in the cookie file:
if not reddit.logged_in or reddit.user.lower() != USERNAME.lower():
	print('logging into %s' % USERNAME)
	login = reddit.login(user=USERNAME, password=PASSWORD)
	if login != 0:
		# 1 means invalid password, 2 means rate limited, -1 means unexpected error
		print('unable to log in: %d' % login)
		print('remember to change USERNAME and PASSWORD')
		exit(1)
	# Save cookies so we won't have to log in again later
	reddit.save_cookies('cookies.txt')

print('logged in as %s' % reddit.user)

uinfo = reddit.user_info()
print('\nlink karma:    %d' % uinfo.link_karma)
print('comment karma: %d' % uinfo.comment_karma)
	

# Retrieve posts in a subreddit
posts = reddit.get('/r/%s' % MOD_SUB)
print('posts in subreddit /r/%s:' % MOD_SUB)
for post in posts:
	if(post.clicked is False):
		reddit.fetch_comments(post)
		for comment in post.comments:
			words = re.split("\?|\ |,|!|\n",comment.body)
			for word in words:
				if "http://www.tobaccoreviews.com" in word:
					linkURL = word
					if "/blend/" in word:
						webtry = urllib2.urlopen(word)
						html = webtry.read()
						parser = MyHTMLParser()
						parser.feed(html)
						replyMessage = "["+tobaccoName+"]("+word+")"+"\n\n"
						reddit.reply(comment,replyMessage)
		post.clicked = True
