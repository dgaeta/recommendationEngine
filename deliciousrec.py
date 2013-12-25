#
#Building a dataset of delicious posts tagged as 'programming'
#


from pydelicious import get_popular,get_userposts,get_urlposts






#takes an article tag and returns a dict on articles
#@params-string (tag), int(how many articles to return)
#@returns- dict

def initializeUserDict(tag, count=5):
	user_dict={}

	#get the top count' popular post
	for p1 in get_popular(tag=tag)[0:count]:
		#final all user who posted this
		for p2 in get_urlposts(p1['url']):
			user=p2['user']
			user_dict[user]={}

	return user_dict


import time

def fillItems(user_dict):
	all_items={}
	#find links posted by all users
	for user in user_dict:
		for i in range(3):
			try:
				posts=get_userposts(user)
				for post in posts:
					url=post['url']
					user_dict[user][url]=1.0
					all_items[url]=1
				break
			except:
				print "Failed user "+user+", retrying"
				time.sleep(4)

	#Fill in missing items with 0
	for ratings in user_dict.values():
		for item in all_items:
			if item not in ratings:
				ratings[item]=0.0



