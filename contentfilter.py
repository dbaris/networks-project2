import gzip

class ContentFilter():
    def __init__(self, config_file):
        self.head = ""
        self.current_page = b""
        self.keywords = {}
        self.firstMsg = True
        self.inBody = False
        self.pastBody = False
        self.gzip = False
        self.current_length = 0
        self.totalLength = 0

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
        content_len = str(len(self.current_page))
        split_on_head = self.head.split(b"Content-Length: ")
        if len(split_on_head) == 1:
            return
        h1, h2 = split_on_head
        h2 = b"\r\n" + b"\n".join(h2.split(b"\n")[1:])

        self.head = h1 + b"Content-Length: " + content_len.encode() + h2

    def storeData(self, html):
        if self.firstMsg:
            split_delim = html.split(b"\r\n\r\n")
            self.head = split_delim[0] + b"\r\n\r\n"
            html = b"\r\n\r\n".join(split_delim[1:])
            try:
                self.totalLength = int(self.head.split(b"Content-Length: ")[1].split(b"\r\n")[0].decode())
            except IndexError:
                print(self.head)
            self.firstMsg = False
            if b"gzip" in self.head:
                self.gzip = True
        self.current_page += html
        self.current_length += len(html)
        if self.current_length == self.totalLength:
            return self.getFilteredData()
        else:
            return "".encode()

    def getFilteredData(self):
        try:
            html_string = self.current_page.decode()
            self._rateHTML(html_string)
            html_with_popup = self._addPopupHeader(html_string)
            self._updateContentLength()
            return self.head + html_with_popup.encode()
        except UnicodeDecodeError:
            try:
                html_string = gzip.decompress(self.current_page).decode()
                self._rateHTML(html_string)
                html_with_popup = self._addPopupHeader(html_string)
                self._updateContentLength()
                return self.head + gzip.compress(html_with_popup.encode())
            except UnicodeDecodeError:
                return self.head + self.current_page

    def notGZIPPath(self, path):
        skiptype = [".css", ".js", ".png", ".gif", ".aspx", ".jpg"]
        for s in skiptype:
            if s in path:
                return True
        return False

    def _addPopupHeader(self, html):
        kstring = ""
        keyword_results = self.keywords
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
