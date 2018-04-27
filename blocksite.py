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

    def print(self):
        for s in self.sites:
            print(s)

    def blocked(self, site):
        print("looking for: " + site)
        if site in self.sites:
            return True
        return False

    def not_allowed(self, site):
        head = "<head><title>Not Allowed</title></head>"
        body = "<body><h1>URL Blocked By Filter: " + site + "<h1></body>"
        return "<!DOCTYPE html>" + head + body + "</html>"
