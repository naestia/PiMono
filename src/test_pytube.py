from pytube import Search

s = Search("billy boss nova")

for item in s.results:
    print(item.title)