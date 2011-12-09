'''
kickball - an unoffical API for kickstarter

string project[name]
string project[author]
string project[author][url]
string project[url]
boolean project[funded]
datetime project[date_funded] # todo for just projects
int project[num_backers]
array project[backers]
project[backers][0][name],[url]
int project[pledged]
array project[updates]
array project[comments]

todo: 
add in updates
add in people browsing
'''
from BeautifulSoup import BeautifulSoup
import urllib
from datetime import datetime
import re

class KickBall:
	def __init__(self, urlBase='http://www.kickstarter.com', silent=False):
		self.urlBase = urlBase
		self.silent = silent
		self.categories = ['art', 'comics', 'dance', 'design', 
			'fashion', 'film%20&%20video', 'food', 'games', 
			'music', 'photography', 'publishing', 'technology', 
			'theater', 'all']
		self.projectTypes = ['recommended', 'popular', 'successful', 
			'most-funded', 'all']
		self.scrapeTypes = ['default', 'detailed', 'updates', 'backers', 
			'comments', 'all']
	
	#def updates(self, url):
		# check rss feed
	
	def comments(self, sock):
		commentsProject = []
		comments = sock.findAll('li', {'class':re.compile(r'\comment\b')})
		for comment in comments:
			commentDict = {}
			main = comment.find('div', {'class':'main'})
			commentDict['author'] = main.find('a', {'class':'author'}).contents[0]
			commentDict['url'] = main.find('a', {'class':'author'})['href']
			commentDict['date'] = main.find('span', {'class':'date'}).contents[0]
			commentDict['comment'] = main.findAll(text=True)[3]
			commentsProject.append(commentDict)
		return commentsProject, len(comments)	
			
	def backers(self, sock):
		backersProject = []
		backers = sock.findAll('div', {'class':'NS-backers-backing-row'})
		for backer in backers:
			backerDict = {}
			meta = backer.find('div', {'class':'meta'})
			backerDict['name'] = meta.find('a').contents[0]
			backerDict['url'] = meta.find('a')['href']
			backerDict['date'] = meta.find('div', {'class':'date'}).contents[0]
			backersProject.append(backerDict)
		return backersProject, len(backers)	
			
	def detailed(self, sock):
		name = sock.find('h1', {'id':'name'}).find('a').contents[0]
		author = sock.find('a', {'id':'byline'}).contents[0]
		moneyHeader = sock.find('div', {'id':'moneyraised'}).findAll('div', {'class':'num'})
		detailedProject = {}
		detailedProject['author'] = author
		detailedProject['num_backers'] = moneyHeader[0].contents[0]
		detailedProject['pledged'] = moneyHeader[1].contents[0]
		detailedProject['daysLeft'] = moneyHeader[2].contents[0]
		return detailedProject
	
	def project(self, url, scrapeType="all", project={}):
		if not self.silent:
			print "scraping project", url, 'at', datetime.utcnow()
		url = self.urlBase + url
		project['url'] = url
		
		#if scrapeType.lower() in ['updates', 'all']:
		#	self.updates(url+'/posts.atom')
		
		if scrapeType.lower() in ['detailed', 'all']:
			sock = urllib.urlopen(url)
			soup = BeautifulSoup(sock)
			detailedProject = self.detailed(soup)
			project.update(detailedProject)	
				
		if scrapeType.lower() in ['comments', 'all']:
			sock = urllib.urlopen(url+'/comments')
			soup = BeautifulSoup(sock)
			commentsProject, num_comments = self.comments(soup)
			project['comments'] = commentsProject
			project['num_comments'] = num_comments
			
		if scrapeType.lower() in ['backers', 'all']:
			sock = urllib.urlopen(url+'/backers')
			soup = BeautifulSoup(sock)
			backersProject, num_backers = self.backers(soup)
			project['backers'] = backersProject
			project['num_backers'] = num_backers
		print project
		return project

	def category(self, projectType, categoryType, scrapeType="all", maxPages=100):
		if not self.silent:
			print "scraping category", projectType, 'with option', categoryType, 'at', datetime.utcnow()
			
		# put together url
		url = self.urlBase+'/discover/categories/'+projectType+'/'+categoryType+'?page='
		for i in range(1, maxPages):
			print url+str(i)
			sock = urllib.urlopen(url+str(i))
			soup = BeautifulSoup(sock)
			# keep on paging until we find no more projects
			projects = soup.findAll('li', {"class" : "project"})
			projectsRes = []
			if not projects:
				break
			for project in projects:
				projectDict = {}	
				if scrapeType.lower() in ['default', 'all']:
					# grab as much as we can from the default pages
					projectDict['name'] = project.findAll('a')[1].contents[0]
					#projectDict['author'] = #eh, i'll add this in eventually. for now use detailed settings
					projectDict['successful'] = True if project.find('div', {'class':'project-pledged-successful'}) else False
					stats = project.find('ul', {'class':'project-stats'})
					projectDict['funding_percent'] = stats.findAll('li')[0].find('strong').contents[0]
					projectDict['pledged'] = stats.findAll('li')[1].find('strong').contents[0]
					if stats.findAll('li')[2].find('strong').contents[0] == 'Funded':
						projectDict['funded'] = True
						projectDict['fund_date'] = stats.findAll('li')[2].findAll(text=True)[2].strip()
					else:
						projectDict['funded'] = False					
						projectDict['daysLeft'] = stats.findAll('li')[2].find('strong').contents[0]
				
				# parse through and find url of individual projects
				if scrapeType.lower() != 'default':
					details = self.project(project.find('a')['href'].rpartition('?ref=')[0], scrapeType)
					projectDict.update(details)
				projectsRes.append(projectDict)
		
		return projectsRes
	
#k = KickBall()
#k.category('dance', 'recommended', 'all')
#k.project('/projects/joshharker/crania-anatomica-filigre-me-to-you')
