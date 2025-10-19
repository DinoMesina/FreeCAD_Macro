#/-*- coding: utf-8 -*-
#
# 06/06/19: v 0.0.1

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
