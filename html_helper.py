
def grab_html_content(url):
	if not url :
		return None

	request_counter = [ 0 ]
	def request_content(user_agent = 'Chrome'):
		if request_counter[0] > REQUEST_COUNT:
			return None

		request_counter[0] += 1

		try:
			req = urllib2.Request(url, headers={'User-Agent': user_agent})
			con = urllib2.urlopen(req)
			return con
		except Exception as e:
			# if forbidden, try it 5 more times
			return request_content(random.sample('abcdefghijklmnopqrstuvwxyz', 10))

	con = request_content()

	if con.code != 200:
		raise Exception("http code returns abnormally")

	return con.read()
