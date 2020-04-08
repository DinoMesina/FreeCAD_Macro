# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
***************************************************************************
*   Copyright (c) 2019 <Dino del Favero dino@delfavero.it>                *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 3 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the LICENCE text file.                                 *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this macro; if not, write to the Free Software     *
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
*   USA                                                                   *
***************************************************************************
"""
__title__   = "WireSplitted"
__author__  = "Dino"
__version__ = "0.1.0"
__date__    = "10/02/2019"

import FreeCAD, Part, Draft, DraftGeomUtils, math

class WireSplitted:
	def __init__(self, obj, wire):
		# Inizializzo 
		obj.Proxy = self
		
		obj.addProperty("App::PropertyLink", "Wire", "Wire").Wire = wire
		obj.addProperty("App::PropertyFloatList", "FloatList", "Lista numeri").FloatList = [1.0]

	def onChanged(self, obj, prop):
		'''Ricalcola se ci sono state delle modifiche ai parametri'''
#		FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
		if (str(prop) == "FloatList"):
			self.execute(obj)

	def execute(self, obj):
		'''Esegui'''
		w = self.creaSpezzoni(obj.Wire.Shape.Edges[0], obj.FloatList, [])
		obj.Shape = Part.Wire(w)

	def creaSpezzoni(self, wire, floatList, wireSplitted):
		'''Restituisce una lista di wire'''

		# Se la lista dei valori è maggiore di 1 devo spezzare la wire nei punti corretti ed aggiungere i pezzi
		# altrimenti aggiungo il pezzo e restituisco la lista 
		if (len(floatList) > 1):
			wSplit = wire.split(wire.FirstParameter + (1.0 * (self.calcolaRapportiSplit(floatList))[0] * (wire.LastParameter - wire.FirstParameter)))
			wireSplitted.append(wSplit.Edges[0])
			self.creaSpezzoni(wSplit.Edges[1], floatList[1:], wireSplitted)
		else:
			wireSplitted.append(wire)

		return(wireSplitted)


	def calcolaRapportiSplit(self, lista):
		'''Calcola i rapporti tra il primo elemento e tutti gli altri nella lista;restituisce una lista con due valori'''
		if (len(lista) == 1):
			return([1.0, 0.0]) 
		else:
			# calcola la somma di tutti i valori nella lista
			somma = 0.0
			for i in range(len(lista)):
				# rendo positivi i valori
				lista[i] = math.fabs(lista[i])
				somma += lista[i]
			return([(lista[0]/somma), (1.0 - (lista[0]/somma))])
