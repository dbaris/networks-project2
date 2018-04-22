# import Levenshtein

class ContentFilter():
	def __init__(self):
		self.current_page = ""
		self.keywords = []

	# Add popup to html page to ask for 
	def addKeyword(self, word):
		self.keywords.append(word.lower())

	def filterPage(self, html):
		rating, found_keywords = self._rateHTML(html)

		if rating > 0:
			newHtml = self._addBasicPopup(html, found_keywords)
		else: 
			newHtml = html

		# Final chunk
		if "</html>" in html or html.endswith('\r\n\r\n'):
			return newHtml
		else:
			# this might need to change
			print("found a chunk")
			self.current_page += filteredPage 
			return None


	def _addBasicPopup(self, html, found_keywords):
		kstring = ""
		for k in found_keywords:
			if kstring != "":
				kstring += ", "
			kstring += k

		head, body = html.split("</head>")
		alert = "<script>alert(\"Content Warning: " + kstring + "\")</script>"
		newHtml = head + alert + "</head>" + body
		return newHtml


	# This algorithm needs to be better
	def _rateHTML(self, html):
		rating = 0
		keywords = []
		for k in self.keywords:
			for h in html.split(" "):
				if self._levenshteinDistance(k, h.lower()) <= 3:
					rating += 1
					if k not in keywords:
						keywords.append(k)

		return (rating, keywords)

	# Code from stackoverflow: 
	# 	https://stackoverflow.com/questions/2460177/edit-distance-in-python
	def _levenshteinDistance(self, s1, s2):
	    if len(s1) > len(s2):
	        s1, s2 = s2, s1

	    distances = range(len(s1) + 1)
	    for i2, c2 in enumerate(s2):
	        distances_ = [i2+1]
	        for i1, c1 in enumerate(s1):
	            if c1 == c2:
	                distances_.append(distances[i1])
	            else:
	                distances_.append(1 + min((distances[i1], 
	                						   distances[i1 + 1], 
	                						   distances_[-1])))
	        distances = distances_
	    return distances[-1]


def test():
	c = ContentFilter()
	c.addKeyword("ski")
	c.addKeyword("race")
	c.addKeyword("popcorn")
	with open("testhtml.html", "r") as f:
		html = f.read()
		newHtml = c.filterPage(html)

		with open("output.html", "w") as output:
			output.write(newHtml)
		
		
test()
