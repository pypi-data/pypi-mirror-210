class Paotung:
	"""
	คลาส Paotung คือ
	ข้อมูลที่เกี่ยวกับแมวมีเจ้าของที่ทำตัวเป็นแมวจร
	แล้วได้บังเอิญมาเจอกัน

	Example
	#------------------------------
	paotung = Paotung()
	paotung.show_name()
	paotung.show_web()
	paotung.about()
	paotung.show_art()
	#------------------------------

	"""

	def __init__(self):
		self.name = 'เป๋าตุง'
		self.web = 'https://lovepetjung.com/2021/01/05/%E0%B9%81%E0%B8%A1%E0%B8%A7%E0%B8%9E%E0%B8%B1%E0%B8%99%E0%B8%98%E0%B8%B8%E0%B9%8C-balinese-%E0%B9%80%E0%B8%9B%E0%B9%87%E0%B8%99%E0%B8%AD%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B9%84%E0%B8%A3/'

	def show_name(self):
		print('สวัสดี ผมชื่อ {}'.format(self.name))

	def show_web(self):
		print('https://lovepetjung.com/2021/01/05/%E0%B9%81%E0%B8%A1%E0%B8%A7%E0%B8%9E%E0%B8%B1%E0%B8%99%E0%B8%98%E0%B8%B8%E0%B9%8C-balinese-%E0%B9%80%E0%B8%9B%E0%B9%87%E0%B8%99%E0%B8%AD%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B9%84%E0%B8%A3/')

	def about(self):
		text = """
		สวัสดี ผมชื่อ เป๋าตุง เป็นแมวพันธุ์ Balinese หรือ บาหลี นั่นเองฮะ"""
		print(text)

	def show_art(self):
		text = """

		           __..--''``---....___   _..._    __
		 /// //_.-'    .-/";  `        ``<._  ``.''_ `. / // /
		///_.-' _..--.'_    \                    `( ) ) // //
		/ (_..-' // (< _     ;_..__               ; `' / ///
		 / // // //  `-._,_)' // / ``--...____..-' /// / //
     
    
		    -- Credit: asciiart.club --
		"""

		print(text)

if __name__ == '__main__':
	paotung = Paotung()
	paotung.show_name()
	paotung.show_web()
	paotung.about()
	paotung.show_art()
