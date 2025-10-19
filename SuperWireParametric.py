#/-*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2018-2019 <Dino del Favero dino@delfavero.it>           *
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
# Crea una SuperWireParametric unendo tutte le geometrie passate

__title__   = "SuperWireParametric"
__author__  = "dino@mesina.net"
__version__ = "0.5.0"
__date__    = "05/02/2025"
#
# 22/04/18: 
# 19/12/18: Modificato eliminando l'uso di SuperWire di DraftGeomUtils che funziona solo con linee ed archi 
# 25/03/19: Modificato tolleranza da Draft.tolerance(), troppo grande 0.01mm, in 0.00000001mm 
# 30/04/19: Aggiunta la possibilità di scegliere il lato di inizio 
# 08/12/24: Aggiunta la possibilità di convertire le BSpline in archi tangenti 
# 24/01/25: Modificato ordinamento edges 
# 05/02/25: Corretto ricerca verso percorrenza 

import FreeCAD, Part, Draft
#import DraftGeomUtils
#
STAT = False 
# 
#TOLERANCE = 0.01

class SuperWireParametric:
	#
	# Inizializzazione 
	#
	def __init__(self, obj, wires):
		obj.Proxy = self
		obj.addProperty("App::PropertyLinkList", "WirePercorso", "Percorso", "Percorso").WirePercorso = wires 
		
		obj.addProperty("App::PropertyBool", "UseStartPoint", "Parametri", "Uso il prunto di partenza insetito").UseStartPoint = False 
		obj.addProperty("App::PropertyVector", "StartPoint", "Parametri", "Punto di partenza").StartPoint 
		obj.setEditorMode("StartPoint", 2) # 0 = default mode, read and write  1 = read-only  2 = hidden
		obj.addProperty("App::PropertyBool", "BSpline2Arcs", "Parametri", "Converto le BSpline in archi tangenti").BSpline2Arcs = True
		obj.addProperty("App::PropertyLength", "Deflection", "Parametri", "Deflessione massima").Deflection = 0.002
		#obj.addProperty("App::PropertyBool", "IsClosed", "Parametri").IsClosed = False 
	
	
	#
	# Esecuzione
	#
	def execute(self, obj):
		# Statistiche? 
		if STAT:
			# salvo l'ora attuale 
			import time, datetime
			t1 = time.time()
		
		# Per i vecchi disegni che non avevano tutti i parametri 
		if not ("UseStartPoint" in obj.PropertiesList):
			obj.addProperty("App::PropertyBool", "UseStartPoint", "Parametri").UseStartPoint = False
		if not ("StartPoint" in obj.PropertiesList):
			obj.addProperty("App::PropertyVector", "StartPoint", "Percorso", "Punto di partenza").StartPoint
			obj.setEditorMode("StartPoint", 2) # 0 = default mode, read and write  1 = read-only  2 = hidden
		if not ("BSpline2Arcs" in obj.PropertiesList):
			obj.addProperty("App::PropertyBool", "BSpline2Arcs", "Parametri").BSpline2Arcs = False
			obj.addProperty("App::PropertyLength", "Deflection", "Parametri").Deflection = 0.002
		
		# Abilito il punto di inizio se decido il punto di partenza 
		if obj.UseStartPoint:
			obj.setEditorMode("StartPoint", 0) # 0 = default mode, read and write  1 = read-only  2 = hidden
		else:
			obj.setEditorMode("StartPoint", 2) # 0 = default mode, read and write  1 = read-only  2 = hidden
		
		# Abilito la deflessione solo se voglio convertire le bspline in archi tangenti
		if obj.BSpline2Arcs:
			obj.setEditorMode("Deflection", 0) # 0 = default mode, read and write  1 = read-only  2 = hidden
		else:
			obj.setEditorMode("Deflection", 2) # 0 = default mode, read and write  1 = read-only  2 = hidden
		
		# Se non ho aggiunto almeno una Wire non fare nulla 
		if (obj.WirePercorso == None):
			# mancano gli oggetti su cui lavorare, non fare nulla 
			FreeCAD.Console.PrintMessage("Mancano gli oggetti")
			return
		
		# creo la wire 
		wire = Part.Wire(self.calcola_NEW(obj))
		#wire = Part.Wire(self.calcola_OLD(obj))
		
		# Ricreo la wire tenendo conto anche della variabile booleana obj.IsClosed 
		#if obj.IsClosed:
		#	# SISTEMARE!!!!
		#	FreeCAD.Console.PrintMessage("Per ora non chiude!!!")
		
		# Setta placement
		wire.Placement = obj.Placement
		obj.Shape = wire
		
		if STAT:
			# salvo l'ora attuale
			t2 = time.time()
			# scrivo il tempo impiegato al calcolo 
			FreeCAD.Console.PrintMessage("Tempo impiegato a calcolare: " + str(datetime.datetime.fromtimestamp(t2) - datetime.datetime.fromtimestamp(t1)) + "\n")
	
	
	#
	# Nuovo metodo di calcolo
	#
	def calcola_NEW(self, obj):
		# Creo la lista contenete tutte le edges 
		edgesPercorso = [] 
		# Estraggo le edges e le converto in archi se necessario 
		for w in obj.WirePercorso:
			# Estraggo le edges dalla wire 
			edges = w.Shape.Edges
			# Devo convertire le BSpline in archi tangenti? 
			if obj.BSpline2Arcs:
				i = 0
				while (i < len(edges)):
					# controllo il tipo, se BSplineCurve la aprossimo con archi tangenti 
					if isinstance(edges[i].Curve, Part.BSplineCurve):
						arcs = edges[i].Curve.toBiArcs(obj.Deflection)
						edges.pop(i)
						for arc in arcs:
							edges.append(arc.toShape())
					else:
						i += 1
			edgesPercorso.extend(edges)
		
		# Estraggo tutte le edge e le ordino (ottengo una lista ordinata con gli spezzoni ordinati)
		edgesPercorso = Part.sortEdges(edgesPercorso)
		
		# Setto il punto iniziale 
		if obj.UseStartPoint:
			spoint = obj.StartPoint
		else: 
			spoint = Part.Vertex(1000.0, 0.0, 0.0).Point # NON è il top!
		
		# ordino i vertici di tutti gli spezzoni e creo il segmento di unione tra i punti più vicini
		if (len(edgesPercorso) > 1):
			vert = []
			for edges in edgesPercorso:
				vert.append([])
				for e in edges:
					vert[-1].extend(e.Vertexes)
				# ordino i vertici 
				vert[-1] = sorted(vert[-1], key=lambda p: (spoint.x - p.Point.x)**2 + (spoint.y - p.Point.y)**2 + (spoint.z - p.Point.z)**2)
			
			# ora in vert ho una lista di liste ordinate dei vertici
			#for l in vert:
			#	print()
			#	for p in l:
			#		print(p.Point)
			#print()
			
			# se gli spezzoni non sono uniti creo il segmento che li congiunge 
			for i in range(len(vert)-1):
				# controllo se due punti già coincidono 
				if ((vert[i][0].Point - vert[i+1][0].Point).Length > TOLERANCE)and ((vert[i][0].Point - vert[i+1][-1].Point).Length > TOLERANCE) and ((vert[i][-1].Point - vert[i+1][0].Point).Length > TOLERANCE) and ((vert[i][-1].Point - vert[i+1][-1].Point).Length > TOLERANCE):
					# cerco i due punti più vicini 
					if ((vert[i][0].Point - vert[i+1][0].Point).Length < (vert[i][0].Point - vert[i+1][-1].Point).Length):
						if ((vert[i][-1].Point - vert[i+1][0].Point).Length < (vert[i][-1].Point - vert[i+1][-1].Point).Length):
							if ((vert[i][0].Point - vert[i+1][0].Point).Length < (vert[i][-1].Point - vert[i+1][0].Point).Length):
								# il segmento più corto è 0,0
								line = Part.makeLine(vert[i][0].Point, vert[i+1][0].Point)
								#print("1 Creato linea tra ", vert[i][0].Point, vert[i+1][0].Point)
								edgesPercorso.append([line])
							else: 
								# il segmento più corto è -1,0
								line = Part.makeLine(vert[i][-1].Point, vert[i+1][0].Point)
								#print("2 Creato linea tra ", vert[i][-1].Point, vert[i+1][0].Point)
								edgesPercorso.append([line])
						elif ((vert[i][0].Point - vert[i+1][0].Point).Length < (vert[i][-1].Point - vert[i+1][-1].Point).Length):
							# il segmento più corto è 0,0
							line = Part.makeLine(vert[i][0].Point, vert[i+1][0].Point)
							#print("3 Creato linea tra ", vert[i][0].Point, vert[i+1][0].Point)
							edgesPercorso.append([line])
						else: 
							# il segmento più corto è -1,-1
							line = Part.makeLine(vert[i][-1].Point, vert[i+1][-1].Point)
							#print("4 Creato linea tra ", vert[i][-1].Point, vert[i+1][-1].Point)
							edgesPercorso.append([line])
					elif ((vert[i][0].Point - vert[i+1][-1].Point).Length < (vert[i][-1].Point - vert[i+1][0].Point).Length):
						# il segmento più corto è 0,-1
						line = Part.makeLine(vert[i][0].Point, vert[i+1][-1].Point)
						#print("5 Creato linea tra ", vert[i][0].Point, vert[i+1][-1].Point)
						edgesPercorso.append([line])
					else: 
						# il segmento più corto è -1,0
						line = Part.makeLine(vert[i][-1].Point, vert[i+1][0].Point)
						#print("6 Creato linea tra ", vert[i][-1].Point, vert[i+1][0].Point)
						edgesPercorso.append([line])
				else:
					print("coincidono")
		# in edgesPercorso ho la lista di tutte le liste di edge
		#print(edgesPercorso)
		
		# Ordino tutte le edges di tutta la lista e metto tutto in un unica lista 
		percorso = edgesPercorso[0]
		for part in edgesPercorso[1:]:
			percorso.extend(part)
		percorso = Part.sortEdges(percorso)[0]
		# controllo se il percorso ha verso corretto, altrimenti inverto tutte le parti 
		if (obj.UseStartPoint and (percorso[0].Edges[0].Vertexes[0].Point - obj.StartPoint).Length >= (TOLERANCE * 10.0)):
			percorso.reverse()
			# inverto l'orientamento di tutti i tratti, penso che serve perché poi creo una wire ed ordina per conto suo
			#for e in percorso:
			#	e.reverse()
		return(percorso)
	
	
	#
	# Vecchio metodo di calcolo (prima del 24/01/25)
	#
	def calcola_OLD(self, obj):
		# Creo la lista vuota 
		edgesPercorso = [] 
		# Creo il punto nullo 
		finalVertex = None
		# calcola il percorso 
		for w in obj.WirePercorso:
			# Estraggo le edges dalla wire
			# Ordino le Edges, utile per evitare problemi con le sezioni che spesso hanno le edges disordinate 
			edges = Part.sortEdges(w.Shape.Edges)[0]
			# devo convertire le BSpline in archi tangenti?
			if (obj.BSpline2Arcs):
				# scorro tutti le edges
				for i in range(len(edges)):
					# controllo il tipo, se BSplineCurve la aprossimo con archi perché altrimenti non crea il loft 
					if isinstance(edges[i].Curve, Part.BSplineCurve):
						arcs = edges[i].Curve.toBiArcs(obj.Deflection)
						del edges[i]
						arcs.reverse() # inverto la lista perché inserisco senza avanzare (probabilmente inutile) 
						for arc in arcs:
							edges.insert(i, arc.toShape())
			# Riordino le Edges, non si sa mai 
			edges = Part.sortEdges(edges)[0]

			# Controllo se le entità sono concatenate
			if (finalVertex != None):
				# Se il punto successivo non corrisponde con l'inizio dell'attuale devo modificare le entità
				# controllo anche il punto finale perché potrei avere delle edge "invertite" 
				if ((finalVertex.Point - edges[0].Vertexes[0].Point).Length >= TOLERANCE) and ((finalVertex.Point - edges[0].Vertexes[-1].Point).Length >= TOLERANCE): 
					# Controllo se non corrisponde nemmeno con il punto finale 
					# controllo anche il punto finale perché potrei avere delle edge "invertite" 
					if ((finalVertex.Point - edges[-1].Vertexes[-1].Point).Length >= TOLERANCE) and ((finalVertex.Point - edges[-1].Vertexes[0].Point).Length >= TOLERANCE): 
						#print("Non coincide!!!")
						#print(finalVertex.Point)
						#print(edges[0].Vertexes[0].Point)
						#print(edges[0].Vertexes[-1].Point)
						#print(edges[-1].Vertexes[0].Point)
						#print(edges[-1].Vertexes[-1].Point)
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
			edgesPercorso = Part.sortEdges(edgesPercorso)[0]
			# CONTROLLO se i punti finali ed iniziali all' interno del percorso coincidono 
			for i in range((len(edgesPercorso) - 1)):
				if ((edgesPercorso[i].Vertexes[-1].Point - edgesPercorso[i + 1].Vertexes[0].Point).Length > 0.01):
					FreeCAD.Console.PrintWarning("I PUNTI NON COINCIDONO")
					FreeCAD.Console.PrintWarning(edgesPercorso[i].Vertexes[-1].Point)
					FreeCAD.Console.PrintWarning(edgesPercorso[i + 1].Vertexes[0].Point)
					FreeCAD.Console.PrintWarning("SISTEMARE")
				
			# Salvo il punto finale così da poter controllare se l'entità successiva è concatenata 
			# Controllo se ho settato il punto di partenza 
			if (finalVertex == None):
				if (obj.UseStartPoint == True):
					if ((obj.StartPoint - edgesPercorso[-1].Vertexes[-1].Point).Length < 0.1):
						finalVertex = edgesPercorso[0].Vertexes[0]
					else:	
						finalVertex = edgesPercorso[-1].Vertexes[-1]
					#print(finalVertex.Point)
			else:
				finalVertex = edgesPercorso[-1].Vertexes[-1]
		
		return(Part.Wire(edgesPercorso))
