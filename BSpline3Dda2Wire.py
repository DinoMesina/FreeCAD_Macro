# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
***************************************************************************
*   Copyright (c) 2018-2020 <Dino del Favero dino@delfavero.it>                *
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
# NOTA: Questo file crea la classe python, per comodità utilizzare 
#  CreaBSpline3Dda2Wire.FCMacro per popolare la classe
#
# Crea una classe per realizzare dinamicamente una bspline3d partendo
# da due figure geometriche piane (in XY) una contenente la proiezione
# sul piano XY della pianta e una del profilo 
#
__title__   = "BSpline3Dda2Wire"
__author__  = "Dino"
__version__ = "0.5.5"
__date__    = "19/01/2020"

import FreeCAD, Part, Draft, DraftGeomUtils
#
STAT = False 
# 
#
class BSpline3Dda2Wire:
	def __init__(self, obj, wireBase, wireAltezza):
		# Inizializzo 
		obj.Proxy = self
		
		obj.addProperty("App::PropertyLink", "WireBase", "Base").WireBase = wireBase 
		obj.addProperty("App::PropertyLink", "WireAltezza", "Altezza").WireAltezza = wireAltezza 
		obj.addProperty("App::PropertyInteger", "Number", "Numero punti calcolati").Number = 300 

		#obj.addProperty("App::PropertyLinkList", "Sections")
		#obj.addProperty("App::PropertyBool", "IsClosed").IsClosed=False 

	def execute(self, obj):
				
		if STAT:
			# salvo l'ora attuale 
			import time, datetime
			t1 = time.time()

		# per i vecchi disegni che non avevano 'Number'
		if not ("Number" in obj.PropertiesList):
			obj.addProperty("App::PropertyInteger", "Number", "Numero punti calcolati").Number = 300 

		# Ricavo i punti sulla base
		points0 = obj.WireBase.Shape.discretize(Number=obj.Number)
		nPoints = len(points0)
		print("Numero punti ricavati: " + str(nPoints))
		# Ricavo i punti sull'altezza
		points1 = obj.WireAltezza.Shape.discretize(Number=nPoints)
		# setto l'altezza 
		for i in range(nPoints):
			points0[i][2] = points1[i][1]

		# Creo la bSpline
		curve = Part.BSplineCurve()
		curve.interpolate(points0)
		#bspline = Draft.makeBSpline(points0,closed=obj.IsClosed)
		obj.Shape = curve.toShape()

		if STAT:
			# salvo l'ora attuale
			t2 = time.time()
			# scrivo il tempo impiegato al calcolo 
			FreeCAD.Console.PrintMessage("Tempo impiegato a calcolare: " + str(datetime.datetime.fromtimestamp(t2) - datetime.datetime.fromtimestamp(t1)) + "\n")
