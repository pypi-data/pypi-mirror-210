import os, random, re
try:
	import requests
except:
	os.system("pip3 install requests")

class iptv:
	def generate_iptv():
		cookies = {"uername": str(random.randrange(9999999999))}
		headers = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"Accept-Language": "ar-AE,ar;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6",
			"Cache-Control": "max-age=0",
			"Connection": "keep-alive",
			"Content-Type": "application/x-www-form-urlencoded",
			"Origin": "http://iptv.journalsat.com",
			"Referer": "http://iptv.journalsat.com/get.php",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36"}
		params = {"do": "cccam"}
		data = {"do": "cccam","doccam": "generate"}
		response = requests.post("http://iptv.journalsat.com/get.php",params=params, cookies=cookies, headers=headers, data=data, verify=False)
		iptv = re.findall(r'class="text-white">(.*?)<', response.text)
		m3u = f"http://{iptv[0]}/get.php?username={iptv[1]}&password={iptv[2]}&type=m3u_plus"
		results = {
		"host":iptv[0],
		"username":iptv[1],
		"password":iptv[2],
		"m3u_plus":m3u}
		return results
	def search(search_word, playlist):
		iptv = requests.get(playlist, verify=False).text
		lines = iptv.split("\n")
		result = []
		for i in range(len(lines)):
			if lines[i].startswith("#EXTINF"):
				link = lines[i+1].strip()
				title = lines[i].split(",")[1]
				if search_word.lower() in title.lower():
					result.append({"tvg-name": title, "link": link})
		return result

class akwam:
	def search(query, section):
		params = {"q": query, "section": section}
		q = requests.get("https://dev-maspero.pantheonsite.io/T1TVs",params=params)
		return q.json()
	def get_movie(movie_url):
		params = {"movie": movie_url}
		movie = requests.get("https://dev-maspero.pantheonsite.io/T1TVs",params=params)
		return movie.json()
	def get_serise(series_url):
		params = {"series": series_url}
		series = requests.get("https://dev-maspero.pantheonsite.io/T1TVs",params=params)
		return series.json()
	def get_episodes(series_url):
		params = {"episodes": series_url}
		episodes = requests.get("https://dev-maspero.pantheonsite.io/T1TVs",params=params)
		return episodes.json()
	def get_seasons(series_url):
		params = {"seasons": series_url}
		seasons = requests.get("https://dev-maspero.pantheonsite.io/T1TVs",params=params)
		return seasons.json()
	def get_download(url):
		params = {"download": url}
		download = requests.get("https://dev-maspero.pantheonsite.io/T1TVs",params=params)
		return download.json()
class mycima:
	def search(query, section):
		params = {"q": query, "section": section}
		q = requests.get("https://dev-maspero.pantheonsite.io/T1TVs/mycima",params=params)
		return q.json()
	def get_movie(movie_url):
		params = {"movie": movie_url}
		movie = requests.get("https://dev-maspero.pantheonsite.io/T1TVs/mycima",params=params)
		return movie.json()
	def get_serise(series_url):
		params = {"series": series_url}
		series = requests.get("https://dev-maspero.pantheonsite.io/T1TVs/mycima",params=params)
		return series.json()
	def get_episodes(series_url):
		params = {"episodes": series_url}
		episodes = requests.get("https://dev-maspero.pantheonsite.io/T1TVs/mycima",params=params)
		return episodes.json()
	def get_seasons(series_url):
		params = {"seasons": series_url}
		seasons = requests.get("https://dev-maspero.pantheonsite.io/T1TVs/mycima",params=params)
		return seasons.json()
	def get_download(url):
		params = {"download": url}
		download = requests.get("https://dev-maspero.pantheonsite.io/T1TVs/mycima",params=params)
		return download.json()