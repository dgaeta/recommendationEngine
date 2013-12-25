#a dictionary of movie critics and a their ratings of a small set of movies 

from math import sqrt


critics = {'Lisa Rose': {'Lady in the Water' : 2.5, 'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 'The Night Listener': 3.0}, 'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
      'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
      'You, Me and Dupree': 3.5},
     'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
      'Superman Returns': 3.5, 'The Night Listener': 4.0},
     'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
      'The Night Listener': 4.5, 'Superman Returns': 4.0,
      'You, Me and Dupree': 2.5},
     'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
      'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
      'You, Me and Dupree': 2.0},
     'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
      'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
     'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}


#returns a distance based similiarity score for person1 and person2

def sim_distance( prefs, person1, person2):
	#get the list of shared items 
	si = {}
	for item in prefs[person1]:
		if item in prefs[person2]:
			si[item] = 1
		
	#if they have no ratings in common, return 0
	if len(si)==0: return 0
	
	#add up the squares of all the differences 
	sum_of_squares = sum( [pow(prefs[person1][item]-prefs[person2][item],2)
                          for item in prefs[person1] if item in prefs[person2]])

	return 1/(1+sum_of_squares)

def sim_pearson( prefs, person1, person2):

	#get the list of mutually rated items 
	si = {}
	for item in prefs[person1]:
		if item in prefs[person2]: si[item] = 1
	
	#find the number of elements 
	n = len(si)
	
	#if they have no ratings in common, return 0
	if n==0: return 0

	#Add up all the preferences individual scores 
	sum1 = sum( [prefs[person1][it] for it in si])
	sum2 = sum( [prefs[person2][it] for it in si])

	# Sum up the square of each score
       	sum1Sq=sum([pow(prefs[person1][it],2) for it in si])
       	sum2Sq=sum([pow(prefs[person2][it],2) for it in si])
       
	# Sum up the products of (scoreOfP1 *scoreOfP2)
       	pSum=sum([prefs[person1][it]*prefs[person2][it] for it in si])
       
	# Calculate Pearson score
       	num=pSum-(sum1*sum2/n)
       	den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
       
	if den==0: return 0
	
	r=num/den
	return r	


# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similiarity=sim_pearson):
	scores = [(similiarity(prefs, person, other), other) 
				for other in prefs if other!=person]

	#sort the list so the highest scores appear at the top
	scores.sort()
	scores.reverse()
	return scores[0:n]

	
#get recommendations for a person by using a weighted average of every
#user's rankings 
def getRecommendations(prefs, person, similiarity=sim_pearson):
	totals={}
	simSums={}

	for other in prefs:
		#dont compare me to myself!
		if other==person: continue
		
		sim=similiarity(prefs, person, other)

		#ignore scores of zero or lower
		if sim<=0: continue
				
		for item in prefs[other]:

			#only score movies I haven't seen yet
			if item not in prefs[person] or prefs[person][item]==0:
				#similiarity * score
				totals.setdefault(item, 0)
				totals[item]+=prefs[other][item]*sim
				#sum of similiarities
				simSums.setdefault(item,0)
				simSums[item]+=sim

		#Create the normalized list
		rankings=[(total/simSums[item],item) for item, total in totals.items()]

		#Return the sorted list
		rankings.sort()
		rankings.reverse()
		return rankings


	

def transformPrefs(prefs):
	result={}
	#loop through each person
	for person in prefs:
		#get each item 
		for item in prefs[person]:
			result.setdefault(item, {})

			#flip the item and person from prefs
			result[item][person]=prefs[person][item]
	return result



def calculateSimiliarItems(prefs,n=10):
	# Create a dictionary of items showing which other items they are most similiar to 
	result={}

	# Invert the preference matrix to be item-centric
	itemPrefs=transformPrefs(prefs)
	c=0
	for item in itemPrefs:
		# Status updates for large datasets
		c+=1
		if c%100==0: print "%d / %d" % (c,len(itemPrefs))
		# Fine the most similiar items to this one 
		scores=topMatches(itemPrefs,item,n=n,similiarity=sim_distance)
		result[item]=scores
	
	return result


def getRecommendedItems(prefs,itemMatch,user):
	userRatings=prefs[user]
	scores={}
	totalSim={}

	# Loop over items rated by this user
	for (item,rating) in userRatings.items():
		
		# Loop over items similiar to this one
		for (similiarity,item2) in itemMatch[item]:

			# Ignore if this user has already rated this item
			if item2 in userRatings:continue

			# Weighted sum of rating times similiarity
			scores.setdefault(item2,0)
			scores[item2]+=similiarity*rating

			# Sum of all the similiarities
			totalSim.setdefault(item2,0)
			totalSim[item2]+=similiarity

	# Divide each total score by the total weighting to get an average 
	rankings=[(score/totalSim[item],item) for item,score in scores.items()]

	# Return the rankings for highest to lowest
	rankings.sort()
	rankings.reverse()
	return rankings


def loadMovieLens(path='./movielens'):
	
	# Get movie titles
	movies={}
	for line in open(path+'/u.item'):
		(id,title)=line.split('|')[0:2]
		movies[id]=title

	# Load data
	prefs={}
	for line in open(path+'/u.data'):
		(user,movieid,rating,ts)=line.split('\t')
		prefs.setdefault(user,{})
		prefs[user][movies[movieid]]=float(rating)
	return prefs


		









