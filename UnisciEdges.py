# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
***************************************************************************
*   Copyright (c) 2018 <Dino del Favero dino@delfavero.it>                *
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
# Unisce tutte le geometrie che hanno i vertici vicini tra loro
# utile importando file DXF
# 0.1.1 Lascio le geometrie originali selezionate 

__title__   = "UnisciEdges"
__author__  = "Dino"
__version__ = "0.1.1"
__date__    = "03/03/2018"

import FreeCAD, Part, Draft

# Tolleranza entro la quale i punti vengono considerati coincidenti
TOL = 0.0001

# I punti sono vicini?
def vicino(a, b, delta = TOL):
	return ((a - b).Length <= delta)

# Ricrea la linea o l'arco in base alla Shape passata 
# spostando il punto di inizio in begin e quello di fine in end
def ricreaShapeElementare(sh, begin, end):
	# controllo il tipo passato 
	# Wire?
	if isinstance(sh, Part.Wire):
		# Estraggo le edges
		edges = sh.Edges
		if (len(edges) == 1):
			# Ho una sola edge, la converto con i nuovi punti di inizio e fine ed esco 
			return([ricreaShapeElementare(edges[0], begin, end)])
		elif (len(edges) >1):
			# Ho più edges, converto la prima con il nuovo inizio e l'ultima con la nuova fine, le altre senza modificare inizio e fine 
			list = ricreaShapeElementare(edges[0], begin, edges[0].valueAt(edges[0].LastParameter))
			for e in edges[1:-1]:
				list.append(ricreaShapeElementare(e, e.valueAt(e.FirstParameter), e.valueAt(e.LastParameter)))
			list.append(ricreaShapeElementare(edges[-1], edges[-1].valueAt(edges[-1].FirstParameter), end))
			return(list)
	# Edge?
	elif isinstance(sh, Part.Edge):
		# Line?
		if isinstance(sh.Curve, Part.Line):
			return([Part.LineSegment(begin, end).toShape()])
		# Circle?
		elif isinstance(sh.Curve, Part.Circle):
			return([Part.ArcOfCircle(begin, sh.valueAt((sh.FirstParameter + sh.LastParameter) / 2.0), end).toShape()])
		else:
			print("Part.Edge ma non Line o Circle :-o")
			print(sh.ShapeType)
			print(sh.Curve)
			return([])
	else:
		print("Né Wire né Line o Circle")
		return([])

# Analizzo gli oggetti 
sel = FreeCAD.Gui.Selection.getSelection()
#objects = FreeCAD.ActiveDocument.findObjects("Part::Part2DObject")
objects = FreeCAD.ActiveDocument.findObjects("Part::Feature")

# Concateno e unisco gli elementi 
if ((len(sel) < 1) or (not sel[0] in objects)):
	# Non ci sono abbastanza informazioni 
	FreeCAD.Console.PrintMessage("Selezionare un arco o una linea\n")
elif (len(sel) == 1):
	# Cerco e aggiungo tutti gli elementi collegati a quello selezionato
	# Converto l'elemento selezionato e lo aggiungo alla lista 
	chain = ricreaShapeElementare(sel[0].Shape, sel[0].Shape.valueAt(sel[0].Shape.FirstParameter), sel[0].Shape.valueAt(sel[0].Shape.LastParameter))
	# cancello l'elemento che è già nella lista 
	objects.remove(sel[0])
	# ricavo i punti iniziale e finale 
	inizio = chain[0].valueAt(chain[0].FirstParameter)
	fine = chain[-1].valueAt(chain[-1].LastParameter)
	# che elemento non ho modificato (serve per ricreare correttamente l'ultimo elemento in caso la figura sia chiusa)
	# puntatore == 0 inizio del primo elemento
	# puntatore == 1 fine del primo elemento
	# puntatore == 2 inizio dell'ultimo elemento
	# puntatore == 3 fine dell'ultimo elemento
	puntatore = 0 

	# Scorro tutti gli elementi nel documento
	for i in range(len(objects)):
		for obj in objects:
			#print(obj.Name)
			#print(obj.Shape.ShapeType)
			# Se trovo un elemento collegato al precedente lo concateno, ricreo e unisco il precedente all'attuale
			# Se l'elemento è una linea o un arco controllo se è collegato agli altri 
			if (isinstance(obj.Shape, Part.Wire) or isinstance(obj.Shape, Part.Edge)):
				# Se è collegato lo agguingo alla lista edges
				# Controllo se obj è vicino all'ultimo o al primo elemento della lista chain
				if (vicino(obj.Shape.Edges[0].valueAt(obj.Shape.Edges[0].FirstParameter), fine)):
					# coincidono inizio di obj con la fine 
					#print("Trovato coincide con l'ultimo " + obj.Name)
					# Aggiungo l'oggetto alla fine della lista 
					chain.extend(ricreaShapeElementare(obj.Shape, fine, obj.Shape.Edges[0].valueAt(obj.Shape.Edges[0].LastParameter)))
					# su che elemento ho lavorato 
					puntatore = 3
					# aggiorno il punto finale 
					fine = chain[-1].valueAt(chain[-1].LastParameter)
					# Seleziono l'elemento 
					FreeCAD.Gui.Selection.addSelection(obj)
					# cancello l'elemento che è già nella lista 
					objects.remove(obj)
	
				elif (vicino(obj.Shape.Edges[0].valueAt(obj.Shape.Edges[0].FirstParameter), inizio)):
					# coincidono inizio di obj con l'inizio 
					#print("Trovato coincide con il primo " + obj.Name)
					# Aggiungo l'oggetto all'inizio della lista 
					#### Vengono inseriti in ordine inverso (se più si uno) ma non dovrebbe essere un problema
					for o in ricreaShapeElementare(obj.Shape, inizio, obj.Shape.Edges[0].valueAt(obj.Shape.Edges[0].LastParameter)):
						chain.insert(0, o)
					# su che elemento ho lavorato 
					puntatore = 1
					# aggiorno il punto iniziale 
					inizio = chain[0].valueAt(chain[0].LastParameter)
					# Seleziono l'elemento 
					FreeCAD.Gui.Selection.addSelection(obj)
					# cancello l'elemento che è già nella lista 
					objects.remove(obj)
	
				elif (vicino(obj.Shape.Edges[-1].valueAt(obj.Shape.Edges[-1].LastParameter), fine)):
					# coincidono fine di obj con la fine 
					#print("Trovato coincide con l'ultimo " + obj.Name)
					# Aggiungo l'oggetto alla fine della lista 
					chain.extend(ricreaShapeElementare(obj.Shape, obj.Shape.Edges[-1].valueAt(obj.Shape.Edges[-1].FirstParameter), fine))
					# su che elemento ho lavorato 
					puntatore = 2
					# aggiorno il punto finale 
					fine = chain[-1].valueAt(chain[-1].FirstParameter)
					# Seleziono l'elemento 
					FreeCAD.Gui.Selection.addSelection(obj)
					# cancello l'elemento che è già nella lista 
					objects.remove(obj)
	
				elif (vicino(obj.Shape.Edges[-1].valueAt(obj.Shape.Edges[-1].LastParameter), inizio)):
					# coincidono fine di obj con l'inizio 
					#print("Trovato coincide con il primo " + obj.Name)
					# Aggiungo l'oggetto all'inizio della lista 
					#### Vengono inseriti in ordine inverso (se più si uno) ma non dovrebbe essere un problema
					for o in ricreaShapeElementare(obj.Shape, obj.Shape.Edges[-1].valueAt(obj.Shape.Edges[-1].FirstParameter), inizio):
						chain.insert(0, o)
					# su che elemento ho lavorato 
					puntatore = 0
					# aggiorno il punto iniziale 
					inizio = chain[0].valueAt(chain[0].FirstParameter)
					# Seleziono l'elemento 
					FreeCAD.Gui.Selection.addSelection(obj)
					# cancello l'elemento che è già nella lista 
					objects.remove(obj)
				# Refresh 
				FreeCAD.Gui.updateGui()
			else:
				# cancello l'elemento che non mi interessa 
				objects.remove(obj)
		
	# Controllo se la figura è chiusa, il punto finale è vicino all'inizio
	if (vicino(inizio, fine)):
		# ricavo i punti corretti per modificare l'elemento
		if (puntatore == 0): # inizio del primo elemento
			# Modifico il punto di inizio del primo elemento 
			chain[0] = ricreaShapeElementare(chain[0], fine, chain[0].valueAt(chain[0].LastParameter))[0]
		elif (puntatore == 1): # fine del primo elemento
			# Modifico il punto di fine del primo elemento 
			chain[0] = ricreaShapeElementare(chain[0], chain[0].valueAt(chain[0].FirstParameter), fine)[0]
		elif (puntatore == 2): #  inizio dell'ultimo elemento
			# Modifico il punto di inizio dell'ultimo elemento 
			chain[-1] = ricreaShapeElementare(chain[1], inizio, chain[-1].valueAt(chain[-1].LastParameter))[0]
		elif (puntatore == 3): # fine dell'ultimo elemento
			# Modifico il punto di fine dell'ultimo elemento 
			chain[-1] = ricreaShapeElementare(chain[-1], chain[-1].valueAt(chain[-1].FirstParameter), inizio)[0]

	# Creo e visualizzo la wire risultante
	chain = Part.sortEdges(chain)[0]
	Part.show(Part.Wire(chain))

else:
	# Non fa nulla 
	FreeCAD.Console.PrintMessage("Selezionare un solo elemento")
