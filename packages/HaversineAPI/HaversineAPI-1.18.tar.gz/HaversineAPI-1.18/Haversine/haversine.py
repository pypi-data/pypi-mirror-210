#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

# pip3 install boto credstash Spanners Argumental

import os, re, sys, json, requests
import pygeohash as pgh
from io import BytesIO
from tqdm import tqdm
from dotmap import DotMap
from Argumental.Argue import Argue

args = Argue() 

#________________________________________________________________________________________________
@args.command()
class Haversine(object):
	'''
	wrapper around the most excellent REST API by joao @ haversine
	https://haversine.com/webapi
	'''
	
	@args.property(default='https://haversine.com')
	def hostname(self): return
	
	@args.property(required=True, short='u', help='username at haversine.com')
	def username(self): return
	
	@args.property(required=True, short='p', help='password at haversine.com')
	def password(self): return

	@args.property(flag=True, short='v', help='display verbose output')
	def verbose(self): return
	
	@args.property(flag=True, short='i', help='use insecure mode for old clients with old cert trees, will remove later, developing on Pythonista')
	def insecure(self): return
	
	
#________________________________________________________________________________________________

@args.command(name='waypoints')
class Waypoints(Haversine):
	'''
	REST API for waypoints
	'''

	#____________________________________________________________________________________________
	@args.operation
	def list(self):
		'''
		return the full list of waypoints in json format
		'''
		
		url = f'{self.hostname}/webapi/waypoints'
		
		if self.verbose:
			sys.stdout.write(f'url={url}\n')
			
		response = requests.get(
			url, 
			auth=(self.username, self.password), 
			verify=not self.insecure,
			stream=True,
		)
		
		length = int(response.headers.get('content-length', 0))
		chunk_size=1024

		with BytesIO() as output, tqdm(
			desc=url.split('/')[-1], 
			total=length, 
			unit='iB', 
			unit_scale=True, 
			unit_divisor=chunk_size,
		) as bar:
			for data in response.iter_content(
				chunk_size=chunk_size
			):
				size = output.write(data)
				bar.update(size)	
			bytes = output.getvalue()

		result = json.loads(bytes.decode('UTF-8'))
		#print(f"{result['result']=}")

		if response.status_code == 200:
			if self.verbose:
				json.dump(result, sys.stdout,  indent='\t')
			return result['waypoints']

		# assume it failed at this point
		sys.stderr.write(f'{response}\n{response.text}\n')
		return
		

	#____________________________________________________________________________________________

	@args.operation
	@args.parameter(name='id', help='The point ID, max 7 chars')
	def get(self, id):
		'''
		get a single waypoint by id
		'''
		
		waypoints = dict(map(lambda x: (x['id'], x), self.list()))
		
		if id in waypoints.keys():
			return waypoints[id]
			
		return
		

	#____________________________________________________________________________________________
	
	@args.operation
	@args.parameter(name='id', help='The point ID, max 7 chars')
	@args.parameter(name='description', help='The point description, max 63 chars')
	@args.parameter(name='latitude', type=float, help='y=DDD.DDDDDDD')
	@args.parameter(name='longitude', type=float, help='x=DDD.DDDDDDD')
	@args.parameter(name='elevation', short='e', type=float, help='EEEE.EEEE in feet', default=0.0)
	def create(self, id, description, latitude, longitude, elevation=0.0):
		'''
		create a single waypoint
		'''
		
		request = dict(
			description=description,
			latitude=latitude,
			longitude=longitude,
			elevation=elevation,
		)
			
		url=f'{self.hostname}/webapi/waypoints/new/{id}'
		
		if self.verbose:
			sys.stdout.write(f'url={url}\nrequest=')
			json.dump(request, sys.stdout, indent='\t')
			
		response = requests.post(
			url, 
			auth=(self.username, self.password), 
			params=request, 
			verify=not self.insecure
		)
		
		if response.status_code == 200:
			if self.verbose:
				json.dump(response.json(), sys.stdout,  indent='\t')
			return response.json()['waypoint']
		
		sys.stderr.write(f'{response}\n{response.text}\n')
		return False


	#____________________________________________________________________________________________
	
	@args.operation
	@args.parameter(name='id', help='The point ID, max 7 chars')
	@args.parameter(name='description', help='The point description, max 63 chars')
	@args.parameter(name='latitude', type=float, help='y=DDD.DDDDDDD')
	@args.parameter(name='longitude', type=float, help='x=DDD.DDDDDDD')
	@args.parameter(name='elevation', short='e', type=float, help='EEEE.EEEE in feet', default=0.0)
	def update(self, id, description, latitude, longitude, elevation=0.0):
		'''
		update a single waypoint
		'''
		
		request = dict(
			description=description,
			latitude=latitude,
			longitude=longitude,
			elevation=elevation,
		)
		
		url=f'{self.hostname}/webapi/waypoints/update/{id}'
		
		if self.verbose:
			sys.stdout.write(f'url={url}\nrequest=')
			json.dump(request, sys.stdout, indent='\t')
										
		response = requests.post(
			url, 
			auth=(self.username, self.password), 
			params=request, 
			verify=not self.insecure
		)
		
		if response.status_code == 200:
			if self.verbose:
				json.dump(response.json(), sys.stdout,  indent='\t')
			return response.json()['waypoint']
		
		sys.stderr.write(f'{response}\n{response.text}\n')
		return False



	#____________________________________________________________________________________________
	
	@args.operation
	@args.parameter(name='id', help='The point ID, max 7 chars')		
	def delete(self, id):
		''' 
		delete a single waypoint by id
		'''
		
		url=f'{self.hostname}/webapi/waypoints/delete/{id}'
		
		if self.verbose:
			sys.stdout.write(f'url={url}\n')
			
		response = requests.post(
			url, 
			auth=(self.username, self.password), 
			params=dict(),
			verify=not self.insecure
		)
		
		if response.status_code == 200:
			if self.verbose:
				json.dump(response.json(), sys.stdout,  indent='\t')
			return response.json()
		
		sys.stderr.write(f'{response}\n{response.text}\n')
		return

	
#________________________________________________________________________________________________

@args.command(name='routes')
class Routes(Haversine):
	'''
	REST API for routes
	'''
	
	#____________________________________________________________________________________________
	@args.operation
	def list(self):
		''' 
		get routes, bit broken at the moment
		'''
		
		url=f'{self.hostname}/webapi/routes'
		
		if self.verbose:
			sys.stdout.write(f'url={url}\n')
			
		response = requests.get(
			url, 
			auth=(self.username, self.password), 
			verify=not self.insecure
		)
		
		if response.status_code == 200:
			if self.verbose:
				json.dump(response.json(), sys.stdout,  indent='\t')
			return response.json()['routes']
		
		sys.stderr.write(f'{response}\n{response.text}\n')
		return		


	#____________________________________________________________________________________________

	@args.operation
	@args.parameter(name='name', help='The route name to recover')
	def get(self, name):
		'''
		get a single route by name, reads whole list and filters
		'''
		routes = dict(map(lambda x: (x['name'], x), self.list()))
		
		if name in routes.keys():
			return routes[name]
		
		return
		

	#____________________________________________________________________________________________
	
	@args.operation
	@args.parameter(name='origin', help='ICAO of origin')
	@args.parameter(name='destination', help='ICAO of destination')
	@args.parameter(name='first', short='f', flag=True, help='take first suggestion and convert to importable route')
	@args.parameter(name='output', short='o', help='output to file name, null for stdout')
	def suggest(self, origin, destination, first=None, output=None):
		'''
		find a route from the origin to the destination
		'''
		
		request = dict(
			origin=origin,
			destination=destination,
		)
		
		url=f'{self.hostname}/webapi/routes/frequent'
		
		if self.verbose:
			sys.stdout.write(f'url={url}\nrequest=')
			json.dump(request, sys.stdout, indent='\t')
					
		response = requests.get(
			url, 
			auth=(self.username, self.password), 
			params=request, 
			verify=not self.insecure
		)
		
		if response.status_code == 200:
			result = response.json()
			
			if self.verbose:
				json.dump(result, sys.stdout,  indent='\t')
				
			if first:
				result['path'] = result['paths'][0]['path']
				del result['paths']
				s = DotMap(result)
				
				result = {
					'name': f'{s.origin}-{s.destination}',
					'origin': s.origin,
					'destination': s.destination,
					'path' : s.path,			
					'length': 0,						
				}
				
			if output:
				if self.verbose:
					print('output',output)
				with open(os.path.expanduser(output),'w') as _output:
					json.dump(result, _output, indent='\t')
													
			return result

		sys.stderr.write(f'{response}\n{response.text}\n')
		return

	@args.operation
	def sample(self):
		'''
		provide a sample route to be populated and used to create/update a route
		'''
		return {
			#Field					Type			Description	
			'name'					:'STRING (63)	A name for the route; it\'s unique key',
			'origin'				:'STRING (7)	The name of the first waypoint; typically the airport\'s ICAO',
			'departure_runway'		:'STRING (7)	May be NULL; otherwise the departire runway ID',
			'sid'					:'STRING (15)	May be NULL or SID (departure) identifier',
			'path'					:'STRING		May be NULL or empty, the sequence of points and airways along the route excluding procedures, runways and airports',
			'destination'			:'STRING (7)	The destination waypoint ID, typically the airport\'s ICAO',
			'star'					:'STRING (15)	May be NULL or STAR(arrival) identifier',
			'approach'				:'STRING (15)	May be NULL or IAP (approach) identifier',
			'arrival_runway'		:'STRING (7)	May be NULL; otherwise the arrival runway ID',
			'length'				:'DOUBLE		The calculated route length, may be incorrect and/or not precise, ROM',
			'flight_level'			:'INT			If specified (non NULL), the desired flight level in feet MSL, e.g. 35000 for FL350',
			'climb_descent_tas'		:'INT			If specified (non NULL), the climb and descent speed in knots of true air speed (TAS)',
			'vertical_speed_fpm'	:'INT			If specified (non NULL), the climb and descent vertical speed in feet per minute, e.g. 1800',
			'points ' 				: [ #POINTs			A sequence of route points
			{
				#Field				Type			Description
				'id'				:'STRING (7)	Point identifier',
				'type'		:[
					'one of the following;',
					'APT = Airport',
					'RW  = Runway',
					'ILS = ILS or localizer',
					'VOR = VOR navaid',
					'NDB = Enroute or Terminal NDB',
					'FIX = Enroute or Terminal Waypoint',
					'LOC = Locality',
					'CWP = Custom Waypoint',
					'POS = Position, a set of coordinates',
				],
				'latitude'			:'DOUBLE		Latitude',
				'longitude'			:'DOUBLE		Latitude',
				'elevation'			:'DOUBLE		Elevation in feet MSL at which to cross or NULL (if unspecified)',
			}]
		}	


	#____________________________________________________________________________________________
	def _create_or_update(self, input=None, route=None, path=None, update=False):
		'''
		create or update a new route
		'''
		if route:
			if route is dict:
				request = route
			else:
				request = json.loads(route)
		elif path:
			parts = path.split(' ')
			parts = list(filter(lambda x: x.lower() != 'dct', parts))
			#print(parts)
			request=dict(
				name=f'{parts[0]}-{parts[-1]}',
				origin=parts[0],
				destination=parts[-1],
				path=' '.join(parts[1:-1]),
			)
			#print(request)
		else:
			_input = sys.stdin
			if input and os.path.exists(os.path.expanduser(input)): 
				_input = open(os.path.expanduser(input))
			request = json.load(_input)
			if input != sys.stdin:
				_input.close()

		if update:
			url=f'{self.hostname}/webapi/routes/update/{request["name"]}'
		else:
			url=f'{self.hostname}/webapi/routes/new/{request["name"]}'
		
		if self.verbose:
			sys.stdout.write(f'url={url}\nroute=')
			json.dump(request, sys.stdout, indent='\t')
			
		response = requests.post(
			url,
			auth=(self.username, self.password),
			json=request,
			verify=not self.insecure,
		)		
		
		if response.status_code == 200:
			if self.verbose:
				json.dump(response.json(), sys.stdout,  indent='\t')
			return response.json()
			
		sys.stderr.write(f'{response}\n{response.text}\n')
		return
				
	#____________________________________________________________________________________________
	@args.operation
	@args.parameter(name='input', short='i', help='file with json route, or None for stdin')
	@args.parameter(name='route', short='r', help='dict or json as text route')
	@args.parameter(name='path', short='p', help='text based route including origin and destination')
	def create(self, input=None, route=None, path=None):
		'''
		create a new route from a file, dict or path
		'''
		return self._create_or_update(input=input, route=route, path=path, update=False)

	
	#____________________________________________________________________________________________
	@args.operation
	@args.parameter(name='input', short='i', help='file with json route, or None for stdin')
	@args.parameter(name='route', short='r', help='dict or json as text route')
	@args.parameter(name='path', short='p', help='text based route including origin and destination')
	def update(self, input=None, route=None, path=None):
		'''
		update a route from a file, dict or path
		'''
		return self._create_or_update(input=input, route=route, path=path, update=True)
			
	
	#____________________________________________________________________________________________

	@args.operation
	@args.parameter(name='origin', help='ICAO of origin')
	def delete(self, name):
		'''
		delete an existing route
		'''
		
		url=f'{self.hostname}/webapi/routes/delete/{name}'
		if self.verbose:
			sys.stdout.write(f'url={url}\n')
			
		response = requests.post(
			url,
			auth=(self.username, self.password),
			verify=not self.insecure
		)
		
		if response.status_code == 200:
			if self.verbose:
				json.dump(response.json(), sys.stdout,  indent='\t')
			return response.json()
		
		sys.stderr.write(f'{response}\n{response.text}\n')
		return		
		

#________________________________________________________________________________________________

if __name__ == '__main__': 
	json.dump(args.execute(), sys.stdout, indent='\t')
