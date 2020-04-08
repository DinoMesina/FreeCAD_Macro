#/-*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
***************************************************************************
*   Copyright (c) 2018-2019 <Dino del Favero dino@delfavero.it>                *
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
__title__   = "SuperWireParametric"
__author__  = "Dino"
__version__ = "0.3.2"
__date__    = "21/04/2019"

#
# 22/04/18: Prima stesura ok 
# 19/12/18: Modificato eliminando l'uso di SuperWire di DraftGeomUtils che funziona solo con linee ed archi 
# 25/03/19: Modificato tolleranza da Draft.tolerance(), troppo grande 0.01mm, in 0.00000001mm
# 30/04/19: Aggiunta la possibilità di scegliere il lato di inizio 

import FreeCAD, Part, Draft
#import DraftGeomUtils
#
STAT = False 
# 
TOLERANCE = 0.00000001

class SuperWireParametric:
	# Inizializzo 
	def __init__(self, obj, wires):
		obj.Proxy = self
		obj.addProperty("App::PropertyLinkList", "WirePercorso", "Percorso", "Percorso").WirePercorso = wires 
		obj.addProperty("App::PropertyBool", "IsClosed").IsClosed = False 
		obj.addProperty("App::PropertyBool", "UseStartPoint").UseStartPoint = False 
		obj.addProperty("App::PropertyVector", "StartPoint", "Percorso", "Punto di partenza").StartPoint 
		obj.setEditorMode("StartPoint", 2) # 0 = default mode, read and write  1 = read-only  2 = hidden

	# Esecuzione 		
	def execute(self, obj):
		# Statistiche? 
		if STAT:
			# salvo l'ora attuale 
			import time, datetime
			t1 = time.time()

		# Per i vecchi disegni che non avevano tutti i parametri 
		if not ("UseStartPoint" in obj.PropertiesList):
			obj.addProperty("App::PropertyBool", "UseStartPoint").UseStartPoint = False 
		if not ("StartPoint" in obj.PropertiesList):
			obj.addProperty("App::PropertyVector", "StartPoint", "Percorso", "Punto di partenza").StartPoint 
			obj.setEditorMode("StartPoint", 2) # 0 = default mode, read and write  1 = read-only  2 = hidden

		# Abilito il punto di inizio se UseStartPoint == True 
		if (obj.UseStartPoint == True):
			obj.setEditorMode("StartPoint", 0) # 0 = default mode, read and write  1 = read-only  2 = hidden
			
		# Se non ho aggiunto almeno una Wire non fare nulla 
		if (obj.WirePercorso == None):
			# mancano gli oggetti su cui lavorare, non fare nulla 
			FreeCAD.Console.PrintMessage("Mancano gli oggetti")
			return

		# Se ho selezionato un solo elemento ho già il percorso corretto altrimenti lo devo calcolare
		if (len(obj.WirePercorso) == 1):
			# Estraggo le edges 
			wire = Part.Wire(obj.WirePercorso[0].Shape)
		else:
			# creo la lista vuota 
			edgesPercorso = [] 
			# Creo il punto nullo 
			finalVertex = None

			# calcola il percorso 
			for w in obj.WirePercorso:
				# Estraggo le edges dalla wire
				edges = w.Shape.Edges
				# Ordino le Edges, utile per evitare problemi con le sezioni che spesso hanno le edges disordinate 
				edges = Part.sortEdges(edges)[0] # non funziona in FreeCAD_0.16 :(
				
				# Controllo se le entità sono concatenate
				if (finalVertex != None):
					# Se il punto successivo non corrisponde con l'inizio dell'attuale devo modificare le entità 
					if ((finalVertex.Point - edges[0].Vertexes[0].Point).Length >= TOLERANCE): #> Draft.tolerance()):
						# Controllo se non corrisponde nemmeno con il punto finale 
						if ((finalVertex.Point - edges[-1].Vertexes[-1].Point).Length >= TOLERANCE): #> Draft.tolerance()):
							# Devo creare un segmento di unione tra gli elementi
							# Lo creo tra i punti più vicini 
							if ((finalVertex.Point - edges[0].Vertexes[0].Point).Length < (finalVertex.Point - edges[-1].Vertexes[-1].Point).Length):
								line = Part.makeLine(finalVertex.Point, edges[0].Vertexes[0].Point)
								#print("Creato linea tra ", finalVertex.Point, edges[0].Vertexes[0].Point)
							else:
								line = Part.makeLine(finalVertex.Point, edges[-1].Vertexes[-1].Point)
								#print("Creato linea tra ", finalVertex.Point, edges[-1].Vertexes[-1].Point)
							# Aggiungo la linea alle edges
							edges.insert(0, line)
				
				# Aggiungo alla lista le nuove edges
				for e in edges:
					edgesPercorso.append(e)
					
				# Ordino tutte le edges
				edgesPercorso = Part.sortEdges(edgesPercorso)[0] # non funziona in FreeCAD_0.16 :(

				# CONTROLLO se i punti finali ed iniziali all' interno del persorso coincidono 
				for i in range((len(edgesPercorso) - 1)):
					if ((edgesPercorso[i].Vertexes[-1].Point - edgesPercorso[i + 1].Vertexes[0].Point).Length > 0.01):
						FreeCAD.Console.PrintWarning("I PUNTI NON COINCIDONO")
						FreeCAD.Console.PrintWarning(edgesPercorso[i].Vertexes[-1].Point)
						FreeCAD.Console.PrintWarning(edgesPercorso[i + 1].Vertexes[0].Point)
						FreeCAD.Console.PrintWarning("SISTEMARE")
					
				# Salvo il punto finale così da poter controllare se l'entità successiva è concatenata 
				# Controllo se ho settato il punto di partenza 
				#print(obj.StartPoint)
				#print((obj.StartPoint - edgesPercorso[-1].Vertexes[-1].Point).Length)
				if (finalVertex == None):
					if (obj.UseStartPoint == True):
						if ((obj.StartPoint - edgesPercorso[-1].Vertexes[-1].Point).Length < 0.1):
							finalVertex = edgesPercorso[0].Vertexes[0]
						else:	
							finalVertex = edgesPercorso[-1].Vertexes[-1]
						#print(finalVertex.Point)
				else:
					#if (obj.UseStartPoint == True):
					#	if ((obj.StartPoint - edgesPercorso[-1].Vertexes[-1].Point).Length < 0.1):
					#		finalVertex = edgesPercorso[0].Vertexes[0]
					#else:	
					finalVertex = edgesPercorso[-1].Vertexes[-1]
				#print
			
			wire = Part.Wire(edgesPercorso)

		# Ricreo la wire tenendo conto anche della variabile booleana obj.IsClosed 
		if (obj.IsClosed):
			# SISTEMARE!!!!
			FreeCAD.Console.PrintWarning("TODO: Per ora non chiude!!!\n")
		
		# Setta placement
		wire.Placement = obj.Placement
		obj.Shape = wire
		
		if STAT:
			# salvo l'ora attuale
			t2 = time.time()
			# scrivo il tempo impiegato al calcolo 
			FreeCAD.Console.PrintMessage("Tempo impiegato a calcolare: " + str(datetime.datetime.fromtimestamp(t2) - datetime.datetime.fromtimestamp(t1)) + "\n")
		