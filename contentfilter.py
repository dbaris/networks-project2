class ContentFilter():
    def __init__(self):
        self.head = ""
        self.current_page = ""
        self.keywords = {}
        self.firstMsg = True
        self.inBody = False
        self.pastBody = False

    def addKeyword(self, word):
        self.keywords[word.lower()] = "Low"

    def _updateContentLength(self):
        content_len = len(self.current_page)
        h1, h2 = self.head.split("Content-Length: ")
        h2 = "\n".join(h2.split("\n")[1:])

        self.head = h1 + "Content-Length: " + str(content_len) + h2

    def filterPage(self, html):
        if self.firstMsg:
            split_delim = html.split("\r\n\r\n")
            self.head = split_delim[0] + "\r\n\r\n"
            html = "\r\n\r\n".join(split_delim[1:])
            self.firstMsg = False

        if self.pastBody:
            return html

        # Filter body
        if "<html" in html or self.inBody:
            self.inBody = True
            self._rateHTML(html)
            self.current_page += html

            if "</html>" in html:
                self.inBody = False
                self.pastBody = True
                self.current_page = self._addPopupHeader(self.current_page)
                self._updateContentLength()
                print(self.head)
                return self.head + self.current_page
            else:
                return ""

        return html

    def _addPopupHeader(self, html):
        print("HI I AM HEREEEEEE IN POPUP1")
        kstring = ""
        keyword_results = self.keywords
        # print(html)
        for k in keyword_results.keys():
            if keyword_results[k] != "Low":
                if kstring != "":
                    kstring += ", "
                kstring += keyword_results[k] + " risk of " + k

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
                html_pieces.append(test)

            for h in html_pieces:
                if self._levenshteinDistance(k, h.lower()) <= 1:
                    self.keywords[k] = "High"
                elif self._levenshteinDistance(k, h.lower()) <= 3:
                    self.keywords[k] = "Medium"

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

    # def _colorCodeKeywords(self, html, keyword_results):
    #     newHtml = html
    #     for k in keyword_results.keys():
    #         updatedHTML = ""
    #         if keyword_results[k] == "High":
    #             # print(k)
    #             split_on_k = newHtml.split(k)
    #             i = 1
    #             for instance in split_on_k:
    #                 updatedHTML += instance
    #                 if i < len(split_on_k):
    #                     updatedHTML += "<span style=\"color:red\">" +
    #                                     k + "</span>"
    #             newHtml = updatedHTML
    #     return newHtml


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
