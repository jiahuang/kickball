'''
kickball - an unoffical API for kickstarter

todo: 
add in people browsing
'''
from BeautifulSoup import BeautifulSoup
import urllib
from datetime import datetime
import re
from xml.dom.minidom import parseString

class KickBall:
	def __init__(self, urlBase='http://www.kickstarter.com', silent=False):
		self.urlBase = urlBase
		self.silent = silent
		self.categoryTypes = ['art', 'comics', 'dance', 'design', 
			'fashion', 'film%20&%20video', 'food', 'games', 
			'music', 'photography', 'publishing', 'technology', 
			'theater', 'all']
		self.projectTypes = ['recommended', 'popular', 'successful', 
			'most-funded', 'all']
		self.scrapeTypes = ['default', 'detailed', 'updates', 'backers', 
			'comments', 'all']
	
	def updates(self, url):
		# check rss feed
		sock = urllib.urlopen(url)
		soup = BeautifulSoup(sock)
			
		updates = []
		entries = soup.findAll('entry')
		for entry in entries:
			update = {}
			update['content'] = entry.find('content').contents[0]
			update['publish_date'] = entry.find('published').contents[0]
			update['url'] = entry.find('link')["href"]
			update['title'] = entry.find('title').contents[0]
			updates.append(update)
		return updates, len(entries)
	
	def comments(self, url):
		sock = urllib.urlopen(url)
		soup = BeautifulSoup(sock)
			
		commentsProject = []
		comments = soup.findAll('li', {'class':re.compile(r'\comment\b')})
		for comment in comments:
			commentDict = {}
			main = comment.find('div', {'class':'main'})
			commentDict['author'] = main.find('a', {'class':'author'}).contents[0]
			commentDict['url'] = main.find('a', {'class':'author'})['href']
			commentDict['date'] = main.find('span', {'class':'date'}).contents[0]
			commentDict['comment'] = main.findAll(text=True)[3]
			commentsProject.append(commentDict)
		return commentsProject, len(comments)	
			
	def backers(self, url):
		sock = urllib.urlopen(url)
		soup = BeautifulSoup(sock)
			
		backersProject = []
		backers = soup.findAll('div', {'class':'NS-backers-backing-row'})
		for backer in backers:
			backerDict = {}
			meta = backer.find('div', {'class':'meta'})
			backerDict['name'] = meta.find('a').contents[0]
			backerDict['url'] = meta.find('a')['href']
			backerDict['date'] = meta.find('div', {'class':'date'}).contents[0]
			backersProject.append(backerDict)
		return backersProject, len(backers)	
			
	def detailed(self, url):
		sock = urllib.urlopen(url)
		soup = BeautifulSoup(sock)
		
		name = soup.find('h1', {'id':'name'}).find('a').contents[0]
		author = soup.find('a', {'id':'byline'}).contents[0]
		author_url = soup.find('a', {'id':'byline'})['href']
		moneyHeader = soup.find('div', {'id':'moneyraised'}).findAll('div', {'class':'num'})
		detailedProject = {}
		detailedProject['author'] = {}
		detailedProject['author']['name'] = author
		detailedProject['author']['url'] = author_url
		detailedProject['num_backers'] = moneyHeader[0].contents[0]
		detailedProject['pledged'] = moneyHeader[1].contents[0]
		detailedProject['daysLeft'] = moneyHeader[2].contents[0]
		return detailedProject
	
	def project(self, url, scrapeType="all", project={}):
		if not self.silent:
			print "scraping project", url, 'at', datetime.utcnow()
		
		#make sure url follows convention /projects/<somenumber>/
		
		if scrapeType.lower() not in self.scrapeTypes:
			raise Exception('Scrape type is not one of '+str(self.scrapeTypes))
			
		url = self.urlBase + url
		project['url'] = url
		
		if scrapeType.lower() in ['detailed', 'all']:
			detailedProject = self.detailed(url)
			project.update(detailedProject)	
		
		if scrapeType.lower() in ['updates', 'all']:
			updatesProject, num_updates = self.updates(url+'/posts.atom')
			project['updates'] = updatesProject
			project['num_updates'] = num_updates
					
		if scrapeType.lower() in ['comments', 'all']:
			commentsProject, num_comments = self.comments(url+'/comments')
			project['comments'] = commentsProject
			project['num_comments'] = num_comments
			
		if scrapeType.lower() in ['backers', 'all']:
			backersProject, num_backers = self.backers(url+'/backers')
			project['backers'] = backersProject
			project['num_backers'] = num_backers
		
		print project
		return project

	def category(self, categoryType, projectType, scrapeType="all", maxPages=100):
		if not self.silent:
			print "scraping category", projectType, 'with option', categoryType, 'at', datetime.utcnow()
		
		# make sure project type is valid
		if categoryType.lower() not in self.categoryTypes:
			raise Exception('Category type is not one of '+str(self.categoryTypes))
		if projectType.lower() not in self.projectTypes:
			raise Exception('Project type is not one of '+str(self.projectTypes))
		if scrapeType.lower() not in self.scrapeTypes:
			raise Exception('Scrape type is not one of '+str(self.scrapeTypes))
				
		# put together url
		url = self.urlBase+'/discover/categories/'+categoryType+'/'+projectType+'?page='
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
					projectDict['author'] = project.find('span').contents[0].rpartition('by')[2].strip()
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
	
k = KickBall()
#k.category('art', 'recommended', 'all')
k.project('/projects/1264285084/swoon-iv-the-techno-logy-issue')
