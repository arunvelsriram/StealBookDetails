import mechanize
from bs4 import BeautifulSoup

url = "http://opac.ssn.net/opac/index.asp"
browser = mechanize.Browser()
browser.set_proxies({})
browser.set_handle_robots(False) # ignore robots
browser.open(url)
browser.select_form(name="query")
browser["location"] = "CSE DEPARTMENT LIBRARY"
response = browser.submit()

books = []
book = []
while True:
	count = 0
	soup = BeautifulSoup(response.read())
	# print soup.prettify()
	flag = False
	td = soup.find_all("td")
	i = 0
	while i < len(td):
		link = td[i].findChild("a")
		# ignoring code till first book
		if not flag and link is not None and "accnos" in link.get("href"):
			flag = True
		# storing book details as books[[book]]
		if flag:
			font = td[i].findChild("font")
			if font != None:
				if font.findChild("input") is not None:
					i += 1;
					continue
				else:
					if count < 9:
						book.append(font.getText().strip())
						count += 1
					else:
						count = 0
						books.append(book)
						book = []
						continue
		i += 1
	if book not in books:
		books.append(book)
	next = soup.find("img", {"onclick" : "Nex()"})
	if next is None:
		# print next
		break
	else:
		response = browser.open("http://opac.ssn.net/opac/simresultnext.asp?PrevorNext=next")
		book = []
with open("PopulateBooks.sql", "w") as output_file:
	for book in books:
		# escape single quotes
		q = book[0].find("'")
		if q!= -1:
			book[0] = book[0][:q] + "'" + book[0][q:]
			q = -1
		l = book[2].find("'")
		if l!= -1:
			book[2] = book[2][:l] + "'" + book[2][l:]
			l = -1
		#query = "insert into books(title, edition, author, location, call_no, acc_no, price, status, type) values('{0}', '{1}', '{2}', '{3}', '{4}', {5}, {6}, '{7}', '{8}');\n".format(book[0], book[1], book[2], book[3], book[4], book[5], book[6], book[7], book[8])
		query = "insert into book(access_no, call_no, title, edition, author, price, status) values('{0}', '{1}', '{2}', '{3}', '{4}', {5}, '{6}');\n".format(book[5], book[4], book[0], book[1], book[2], book[6], book[7])
		output_file.write(query)