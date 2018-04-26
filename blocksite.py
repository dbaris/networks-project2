class SiteBlocker (): 
	def __init__(self):
		self.sites = set()

	def block_site(self, site) :
		self.sites.add(site) 
