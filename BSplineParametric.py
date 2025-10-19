# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
# Crea una Bspline discretizzando in maniera dinamica la geometria passata
# 06/06/2019: v 0.0.1
# 03/07/2019 Funziona anche con le sezioni di due superfici in FC0.18 (0.17no)

__title__   = "BsplineParametric"
__author__  = "dino@mesina.net"
__version__ = "0.1.0"
__date__    = "06/06/2019"

# 06/06/19: v 0.1.0

import FreeCAD, Part

class BSplineParametric:
	# Inizializzo 
	def __init__(self, obj, wire):
		obj.Proxy = self
		obj.addProperty("App::PropertyLink", "Wire", "Wire", "Wire").Wire = wire 
		obj.addProperty("App::PropertyLength", "Deflection", "Deviazione massima").Deflection = 0.001 

	# Esecuzione 		
	def execute(self, obj):

		# discretizza gli elementi che compongono il bordo separatamente (dopo averli ordinati)
		points = [] 
		# Ordino le Edges, utile per evitare problemi con le sezioni che spesso hanno le edges disordinate 
		Edges = Part.sortEdges(obj.Wire.Shape.Edges)[0]
		for edges in Edges:
			# aggiungo i punti escluso l'ultimo 
			if (points != []):
				points.pop() # elimino l'ultimo punto se la lista non è vuota 
			for e in (edges.discretize(Deflection=obj.Deflection)):
				points.append(e)

		# Creo la BSpline 
		bspline = Part.BSplineCurve()
		bspline.interpolate(points)

		# creo la Shape
		obj.Shape = bspline.toShape()

