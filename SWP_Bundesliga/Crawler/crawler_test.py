import crawler_class

c1 = crawler_class.Crawler("https://www.openligadb.de/api/getmatchdata/bl1/", 2016)
c1.get_match_data()