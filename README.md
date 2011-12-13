# Kickball scrapes Kickstarter for project information

Kickball allows for the following scrapes:

	on categories : ['art', 'comics', 'dance', 'design', 'fashion', 'film%20&%20video', 'food', 'games', 'music', 'photography', 'publishing', 'technology', 'theater', 'all']
	on project types : ['recommended', 'popular', 'successful', 'most-funded', 'all']
	on scrape types : ['default', 'detailed', 'updates', 'backers', 'comments', 'all']
	
Scrape by project:

	kb = Kickball()
	p = kb.project(url = '/projects/2068026266/ghost-pirates-a-board-game-of-ship-to-ship-tactica', scrapeType = 'all')

By default kickball scrapes for "all" regarding a project. p is a dictionary with the following:

	p['url']
	p['successful']
	p['author']['name'][#]['url']
	p['backers'][#]['date']
	p['backers'][#]['name']
	p['num_comments']
	p['comments']
	p['comments'][#]['author']['url']
	p['comments'][#]['author']['name']
	p['comments'][#]['author']['name']	
	p['updates']
	p['updates'][#]['content']
	p['updates'][#]['url']
	p['updates'][#]['publish_date']
	p['updates'][#]['title']

Scrape by category:

	kb = Kickball()
	p = kb.category(categoryType='art', projectType = 'recommended', scrapeType = 'all', maxPages=100)

This paginates through all the recommended projects in the art category until maxPages is reached or there are no more projects. This calls kickball.project() and returns a list of dictionaires.
