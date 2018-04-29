class ContentFilter():
    def __init__(self, config_file):
        self.head = ""
        self.current_page = ""
        self.keywords = {}
        self.firstMsg = True
        self.inBody = False
        self.pastBody = False

        with open(config_file, "r") as fp:
            for line in fp:
                if line != "[ Keywords ]\n":
                    self.addKeyword(line.replace("\n", ""))
                if line == "[ Blocked ]\n":
                    return
        self.keywords.pop("")

    def addKeyword(self, word):
        self.keywords[word.lower()] = "Low"

    def _updateContentLength(self):
        content_len = len(self.current_page)
        split_on_head = self.head.split("Content-Length: ")
        if len(split_on_head) == 1:
            return
        h1, h2 = split_on_head
        h2 = "\n".join(h2.split("\n")[1:])

        self.head = h1 + "Content-Length: " + str(content_len) + h2

    def filterPage(self, html):
        print("here")
        if self.pastBody:
            print("past")
            return html
        
        if self.firstMsg:
            split_delim = html.split("\r\n\r\n")
            self.head = split_delim[0] + "\r\n\r\n"
            html = "\r\n\r\n".join(split_delim[1:])
            self.firstMsg = False

        # Filter body
        if "<html" in html or self.inBody:
            self.inBody = True
            self._rateHTML(html)
            self.current_page += html

            if "</html>" in html:
                print('hello??')
                self.inBody = False
                self.pastBody = True
                self.current_page = self._addPopupHeader(self.current_page)
                self._updateContentLength()
                # print(self.head)
                return self.head + self.current_page
            else:
                return ""

        return html

    def _addPopupHeader(self, html):
        kstring = ""
        keyword_results = self.keywords
        # print(html)
        for k in keyword_results.keys():
            if keyword_results[k] != "Low":
                if kstring != "":
                    kstring += ", "
                kstring += keyword_results[k] + " risk of keyword " + k

        if kstring == "":
            return html

        split_on_head = html.split("<head>")
        head = split_on_head[0]
        body = "<head>".join(split_on_head[1:])
        alert = "<script>alert(\"Content Warning: " + kstring + "\")</script>"
        # print(body + alert + "</body>" + footer)
        return head + "<head>" + alert + body

    def _rateHTML(self, html):
        for k in self.keywords.keys():
            if (self.keywords[k] == "High"):
                continue

            # Check for correct number of keywords
            k_len = len(k.split(" "))
            html_words = html.split(" ")
            html_pieces = []

            for i in range(0, len(html_words) - k_len):
                test = " ".join(html_words[i:i + k_len])
                html_pieces.append(test.lower())

            for h in html_pieces:
                if len(h) == 0 or len(k) == 0:
                    continue
                if self._levenshteinDistance(k, h) <= 1:
                    self.keywords[k] = "High"
                elif (h[0] == k[0] and
                      self._percentSim(k, h) > .75 and 
                      self._levenshteinDistance(k, h) <= 3):
                    self.keywords[k] = "Medium"
                    print("medium: %s, %s" % (k, h))

    def _percentSim(self, s1, s2):
        total = len(s1)
        count = 0
        for s in s1:
            if s in s2:
                count += 1

        return count / total

    # Implementation of levenshtein distance from stackoverflow:
    #   https://stackoverflow.com/questions/2460177/edit-distance-in-python
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


# def test():
#   c = ContentFilter()
#   c.addKeyword("ski")
#   c.addKeyword("mountains")
#   c.addKeyword("popcorn")
#   with open("testhtml.html", "r") as f:
#       html = f.read()
#       newHtml = c.filterPage(html)

#       with open("output.html", "w") as output:
#           output.write(newHtml)


# test()
