#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Nume: Romsun - Generator sunete pentru texte în română.
# Autor: Paul Nechifor <irragal@gmail.com>
# Inceput: 01.08.2009
# Terminat: 12.08.2009

u"""Romsun - Generator sunete pentru texte în română.

Acest script python transformă texte scrise în limba română în fișiere .pho care
pot fi citite de către programul mbrola pentru a produce fișiere audio.

Folosire: python romsun.py [opțiuni]

Opțiuni:
  -t ..., --text=...       Fișierul care va fi citit. Dacă nu este specificat,
                           se citește de la intrarea standard.
  -s ..., --scriere=...    Unde va fi scris fișierul. Dacă nu este specificat,
                           se scrie la ieșirea standard.
  -v xx, --viteza=xx       Coeficientul cu care este înmulțită durata sunetelor.
                           Dacă nu este specificat valoarea va fi 0,75.
  -p xx, --spatii=xx       Coeficientul cu care este înmulțită durata spațiilor.
                           Dacă nu este specificat valoarea va fi 0,20.
  -h, --help               Arată textul ăsta.

Exemple:
  ./romsun.py -t exemplu.txt -s exemplu.pho
  ./romsun.py --viteza=0,50 -t exemplu.txt -s exemplu.pho
"""

import random, os, sys, types, getopt

_viteza = 0.75
_vspatii = 0.20
dictionar = {}
for linie in open('dictionar', 'r'):
	p = unicode(linie.strip(), 'utf-8').split('=')
	if len(p[0]) > 0: dictionar[p[0]] = p[1]

class EroareNumar(Exception): pass
class EroareSunet(Exception): pass
class EroareCitire(Exception): pass
class EroarePereche(Exception): pass

def urm(s, i):
	if i < len(s) and i >= 0: return s[i]
	else: return ""

def scriereNumar(n, m=True, nr=True):
	u"""Scrie cum se citește un număr primit ca int sau float în parametrul n."""

	p = ['zero', 'unu', 'doi', 'trei', 'patru', 'cinci', u'șase', u'șapte', 'opt', u'nouă', 'zece', \
		'unsprezece', 'doisprezece', 'treisprezece', 'paisprezece', 'cincisprezece', u'șaisprezece', \
		u'șaptisprezece', 'optisprezece', u'nouăsprezece']
	zeci = (u'douăzeci', u'treizeci', u'patruzeci', u'cincizeci', u'șaizeci', u'șaptezeci', u'optzeci', u'nouăzeci')
	ms = ('o mie', 'un milion', 'un miliard', 'un trilion')
	mp = ('mii', 'milioane', 'miliarde', 'trilioane')

	if m:
		if nr: pass
		else:
			p[0] = 'niciun'
			p[1] = 'un'
	else:
		p[1] = 'o'
		p[2] = u'două'
		p[12] = u'douăsprezece'
		if nr: p[1] = 'una'
		else:
			p[0] = 'nicio'
			p[1] = 'o'

	if n == 0:
		return p[0]
	elif type(n) == types.FloatType:
		s = str(n).split(".")
		return scriereNumar(int(s[0]), m, nr) + u' virgulă ' + scriereNumar(int(s[1]), m, nr)
	elif n < 0:
		return 'minus ' + scriereNumar(abs(n), m, nr)
	elif n < 20:
		return p[n]
	elif n < 100:
		if n % 10 == 0: return zeci[n/10 - 2]
		if m: p[1] = 'unu'
		else: p[1] = 'una'
		return  zeci[n/10 - 2] + u' și ' + p[n%10]
	elif n < 1000:
		f = ''
		primul = n / 100
		if primul == 1: f += u'o sută'
		elif primul == 2: f += u'două sute'
		else: f += p[primul] + ' sute'
		n %= 100
		if n == 0: return f
		if m: p[1] = u'unu'
		else: p[1] = u'și una'
		if n < 20: return f + ' ' + p[n]
		if not m: p[1] = 'una'
		if n % 10 == 0: return f + ' ' + zeci[n/10 - 2]
		return f + ' ' + zeci[n/10 - 2] + u' și ' + p[n%10]
	else:
		gr = []
		f = ''
		while n > 0:
			gr.append(n % 1000)
			n /= 1000
		if len(gr) > len(mp)+1:
			return u'Nu știu să citesc număr așa de mare'
		for i in xrange(len(gr)):
			if i == 0:
				if gr[0] == 0: pass
				elif gr[0] == 1: f = u'și una'
				else: f = scriereNumar(gr[0], m, nr)
			else:
				if gr[i] == 0: pass
				elif gr[i] == 1:
					if f == '':	f = ms[i-1]
					else: f = ms[i-1] + ' ' + f
				else: 
					if gr[i] % 100 >= 20: de = ' de'
					else: de = ''
					f = scriereNumar(gr[i], m, nr) + de + ' ' + mp[i-1] + ' ' + f
		return f
		
def scriereNumarString(n, m=True, nr=True):
	u"""Scrie cum se citește un număr care este primit ca string de forma 1234,56 în 
	parametrul n. Se poate și punct în loc de virgulă."""

	n = n.replace(',', '.')
	if n.count('.') > 1: raise EroareNumar, u'Nu poate fi decât un singur punct sau virgulă'.encode('utf-8')
	if not n.replace('.', '').isdigit(): raise EroareNumar, u'Nu este parte de număr'.encode('utf-8')
	if n.count('.') == 0: return scriereNumar(int(n), m, nr)
	else: return scriereNumar(float(n), m, nr)

class Sunet:
	"""Gestionează un sunet.
	   
	Simbolurile pentru sunetele posibile sunt:
		- vocale = i, I, e, a, @, o, u, 1
		- semivocale = j, E, w, O
		- consoane = p, b, t, d, k, g, T, C, G, f, v, s, z, S, J, h, m, n, l, r
	"""
	sunete = ('_', 'i', 'I', 'e', 'a', '@', 'o', 'u', '1', 'j', 'E', 'w', 'O', 'p', 'b', 't', \
			'd', 'k', 'g', 'T', 'C', 'G', 'f', 'v', 's', 'z', 'S', 'J', 'h', 'm', 'n', 'l', 'r')
	def __init__(self, valoare, durata = 100, mod = []):
		if not valoare in self.__class__.sunete: raise EroareSunet, (u"nu există sunetul '%s'" % valoare).encode('utf-8')
		if durata < 0: raise EroareSunet, u'durata nu poate fi mai mică de zero'.encode('utf-8')
		if len(mod) % 2 != 0: raise EroareSunet, u'numărul de modificări trebuie să fie par'.encode('utf-8')
		self.valoare =  valoare
		self.durata = durata
		self.mod = mod

	def text(self):
		if self.mod == []: mod = ""
		else: mod = " " + " ".join(self.mod)
		if self.valoare == '_': m = _vspatii
		else: m = _viteza
		return self.valoare + " " + str(int(self.durata * m)) + mod

class Discurs:
	u"""Gestionează o listă de sunete și afișarea lor."""

	def __init__(self):
		self.sunete = [Sunet("_")]

	def adauga(self, sunet):
		u"""Adaugă sunetul primit ca parametru in lista de sunete a discursului."""

		# trebuie să verific să nu fie vreo pereche imposibilă
		penultimul = self.sunete[-1].valoare
		ultimul = sunet.valoare

		if penultimul == 'a' and ultimul == 'e': raise EroarePereche, 'Nu se poate a-e!'
		if penultimul == 'I' and ultimul == 'i': raise EroarePereche, 'Nu se poate I-i!'
		if penultimul == 'O' and ultimul != 'a': raise EroarePereche, 'Nu se poate O-%s!' % ultimul
		if penultimul == 'E':
			if ultimul != 'a' and ultimul != 'o':
				raise EroarePereche, 'Nu se poate E-%s!' % ultimul
		if ultimul == 'I':
			if penultimul in ('_', 'a', '@', 'e', 'i', '1', 'j', 'o', 's', 'u', 'w'):
				raise EroarePereche, 'Nu se poate %s-I!' % penultimul
		if ultimul == 'E':
			if penultimul in ('@', 'i', '1', 'o', 'u', 'w'):
				raise EroarePereche, 'Nu se poate %s-E!' % penultimul
		if ultimul == '_':
			if penultimul == 'C' or penultimul == 'G':
				raise EroarePereche, 'Nu se poate %s-_!' % penultimul

		self.sunete.append(sunet)

	def text(self):
		return '\n'.join([x.text() for x in self.sunete]) + '\n'

class Cititor:
	u"""Citește câte un cuvânt. Citirea unui cuvânt este căutată într-un dicționar. Dacă nu este găsit cuvântul,
	citirea este formată după niște reguli simple, care nu dau de multe ori răspunsul corect."""

	citire = {'a':'a',  u'ă':'@',  u'â':'1',   'b':'b',   'd':'d',   'e':'e',   'f':'f',            u'î':'1', \
			  'j':'J',   'k':'k',   'l':'l',   'm':'m',   'n':'n',   'o':'o',   'p':'p',   'q':'k',  'r':'r', \
			  's':'s',  u'ș':'S',   't':'t',  u'ț':'T',   'u':'u',   'v':'v',   'w':'v',   'y':'i',  'z':'z'}

	def __init__(self, discurs):
		self.discurs = discurs

	def adaugaCuvant(self, cuv):
		global dictionar

		if cuv == '': return

		# dacă nu a fost adaugată o pauză trebuie să o adaug
		if self.discurs.sunete[-1].valoare != '_': self.crud('_')

		try:
			self.crud(dictionar[cuv])
		except KeyError:
			pronuntare = ""
			for i in xrange(len(cuv)):
				try:
					pronuntare += self.__class__.citire[cuv[i]]
				except KeyError:
					if cuv[i] == 'i':
						if urm(cuv, i+1) == "" and not (pronuntare[-1] in ('a', '@', 'e', 'i', '1', 'j', 'o', 's', 'u', 'w')): pronuntare += 'I'
						else: pronuntare += 'i'
					elif cuv[i] == 'c':
						if urm(cuv, i+1) in ('e', 'i'): pronuntare += 'C'
						else: pronuntare += 'k'
					elif cuv[i] == 'g':
						if urm(cuv, i+1) in ('e', 'i'): pronuntare += 'G'
						else: pronuntare += 'g'
					elif cuv[i] == 'h':
						if urm(cuv, i-1) in ('c', 'g'): pass
						else: pronuntare += 'h'
					elif cuv[i] == 'x':
						pronuntare += 'ks'
					elif cuv[i] == '-' or cuv[i] == "'": pass
					else: raise EroareCitire, (u"Nu este parte de cuvânt '%s' din '%s'!" % (cuv[i], cuv)).encode('utf-8')
			self.crud(pronuntare)

	def crud(self, cuv):
		lista = cuv.split("#")
		if len(lista) == 1:
			for c in lista[0]:
				self.discurs.adauga(Sunet(c))
		else:
			numere = lista[1].split("|")
			if len(numere) != len(lista[0]):
				raise EroareCitire, (u"Trebuie să se potrivească literele și numerele! (%s, %s)" % (numere, lista[0])).encode('utf-8')
			sir = []
			for n in numere:
				if n == "": sir.append([])
				else: sir.append([ int(x) for x in n.split(",") ])

			for i in range(len(lista[0])):
				if len(sir[i]) == 0:
					self.discurs.adauga(Sunet(lista[0][i]))
				elif len(sir[i]) == 1:
					self.discurs.adauga(Sunet(lista[0][i], sir[i][0], sir[i][1:]))

class Procesor(Cititor):
	u"""Citește orice text prin extragerea cuvintelor."""

	atomCuvant = ('a', u'ă', u'â', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', u'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', \
					'q', 'r', 's', u'ș', 't', u'ț', 'u', 'v', 'w',  'x', 'y', 'z', '-', "'")

	def __init__(self, discurs, deInceput=''):
		self.discurs = discurs
		if deInceput != '': self.proceseaza(deInceput)

	def proceseaza(self, text):
		text = self.inlocuiesteNumere(text.lower().replace('\n', ''))
		i = 0
		cuvant = ''
		while i < len(text):
			if text[i] in self.__class__.atomCuvant:
				cuvant += text[i]
				i += 1
			else:
				self.adaugaCuvant(cuvant)
				cuvant = ''
				if text[i] == ' ': pauza = 100
				elif text[i] in (',', ':'): pauza = 150
				elif text[i] == u'—': pauza = 250 # linie de pauză
				else: pauza = 200
				self.discurs.adauga(Sunet('_', pauza))
				while i < len(text) and not (text[i] in self.__class__.atomCuvant): i += 1
		if len(cuvant) > 0: self.adaugaCuvant(cuvant)

	def inlocuiesteNumere(self, text):
		# TODO: să citească corect și numerele negative sau cu virgulă XXX
		nr = ""
		textNou = ""
		for c in text:
			if ord(c) >= ord('0') and ord(c) <= ord('9'):
				nr += c
			else:
				if len(nr) > 1:
					textNou += scriereNumarString(nr)
					nr = ""
				textNou += c
		if len(nr) > 1: textNou += scriereNumarString(nr)
		return textNou

# ================================================== MAIN ================================================== 

if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], 't:s:v:p:h', ['text=', 'scriere=', 'viteza=', 'spatii=', 'help'])
	except getopt.GetoptError:
		print __doc__
		exit(2)
	text = sys.stdin
	scriere = sys.stdout
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print __doc__
			exit()
		elif opt in ('-t', '--text'):
			text = open(arg)
		elif opt in ('-s', '--scriere'):
			scriere = open(arg)
		elif opt in ('-v', '--viteza'):
			_viteza = float(arg.replace(',', '.'))
		elif opt in ('-p', '--spatii'):
			_vspatii = float(arg.replace(',', '.'))

	d = Discurs()
	p = Procesor(d)
	p.proceseaza(unicode(text.read(), 'utf-8'))	
	scriere.write(d.text())
