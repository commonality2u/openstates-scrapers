from billy.scrape.committees import CommitteeScraper, Committee

import lxml.html

class WICommitteeScraper(CommitteeScraper):
    jurisdiction = 'wi'

    def scrape_committee(self, name, url, chamber):
        com = Committee(chamber, name)
        com.add_source(url)
        data = self.urlopen(url)
        doc = lxml.html.fromstring(data)

        for leg in doc.xpath('//p/a[contains(@href, "2015/legislators")]/text()'):
            leg = leg.replace('Representative ', '')
            leg = leg.replace('Senator ', '')
            leg = leg.strip()
            if ' (' in leg:
                leg, role = leg.split(' (')
                if 'Vice-Chair' in role:
                    role = 'vice-chair'
                elif 'Co-Chair' in role:
                    role = 'co-chair'
                elif 'Chair' in role:
                    role = 'chair'
                else:
                    raise Exception('unknown role: %s' % role)
            else:
                role = 'member'
            com.add_member(leg, role)

        self.save_committee(com)


    def scrape(self, term, chambers):
        for chamber in chambers+["joint"]:
            url = 'http://docs.legis.wisconsin.gov/2015/committees/'
            if chamber == 'joint':
                url += "joint"
            elif chamber == 'upper':
                url += 'senate'
            else:
                url += 'assembly'
            data = self.urlopen(url)
            doc = lxml.html.fromstring(data)
            doc.make_links_absolute(url)

            for a in doc.xpath('.//div[starts-with(@id,"committee-")]/h5/a'):
                self.scrape_committee(a.text, a.get('href'), chamber)