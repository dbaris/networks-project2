class SiteBlocker (): 
    def __init__(self, config_file):
        self.sites = set()

        with open(config_file, "r") as fp:
            save = False
            for line in fp:
                if line == "[ Blocked ]\n":
                    save = True
                    continue
                elif not save:
                    continue
                self.block_site(line.replace("\n", ""))

        # print(self.sites)

    def block_site(self, site) :
        # self.sites.add(site.split("//")[1].replace("/", "")) 
        self.sites.add(site)

    def isBlocked(self, site):
        return site in self.sites

    def print(self):
        for s in self.sites:
            print(s)

    def addHead(self, site, msg):
        length = str(len(msg))
        head = "HTTP/1.1 200 OK\nAccept-Ranges: bytes\n" + \
               "Cache-Control: public, max-age=3600, s-maxage=3600\n" + \
               "Content-Type: text/html; charset=utf-8\nContent-Length: " + length
        return head + "\r\n\r\n" + msg


    def not_allowed(self, site):
        head = "<head><title>Not Allowed</title></head>"
        body = "<body><h1>URL Blocked By Filter: " + site + "<h1></body>"
        msg = "<!DOCTYPE html>" + head + body + "</html>"
        return self.addHead(site, msg)
