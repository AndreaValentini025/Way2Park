import requests
from geopy.distance import geodesic
from .models import Parcheggio

'''
input: 
parks -> lista di parcheggi con attributi addr, lat, long, capienza, occupazione, id, costo 
searchedLat e searchedLong-> destinazione
positionLat e positionLong-> posizione attuale

ritorna bestPark, freePark e nearestPark
'''
#
# parks = [
#     {'id': 1, 'lat': 44.6948425936889, 'long': 10.6262177853485, 'capacity': 50, 'occupancy': 0, 'cost': 1.5,
#      'address': 'Piazza Fiume'},
#     {'id': 2, 'lat': 44.69447504787002, 'long': 10.635647773039532, 'capacity': 50, 'occupancy': 0, 'cost': 1.5,
#      'address': 'Piazza Giuseppe Grasselli'},
#     {'id': 3, 'lat': 44.693183691084094, 'long': 10.629544566251525, 'capacity': 50, 'occupancy': 0, 'cost': 1.5,
#      'address': 'Piazza Armando Diaz'},
#     {'id': 4, 'lat': 44.70282306924046, 'long': 10.627198485691872, 'capacity': 50, 'occupancy': 0, 'cost': 1.5,
#      'address': 'Piazzale Lancieri d\'Aosta'},
#     {'id': 5, 'lat': 44.704743890892246, 'long': 10.634114803152752, 'capacity': 50, 'occupancy': 0, 'cost': 0,
#      'address': 'Via Avvenire Paterlini'},
#     {'id': 6, 'lat': 44.69143247200662, 'long': 10.624144424121614, 'capacity': 790, 'occupancy': 0, 'cost': 0,
#      'address': 'Piazzale A. Catellani'},
#     {'id': 7, 'lat': 44.69500442498985, 'long': 10.611608742739552, 'capacity': 50, 'occupancy': 0, 'cost': 0,
#      'address': 'Via Spagna, Le Querce'},
#     {'id': 8, 'lat': 44.69886349048182, 'long': 10.625537052396147, 'capacity': 20, 'occupancy': 0, 'cost': 1.5,
#      'address': 'Piazza dei Servi'}
# ]
parcheggi = Parcheggio.objects.all()
parcheggi =  [p.__dict__ for p in parcheggi]

# università del seminario viale timavo
searchedLat = 44.693479
searchedLong = 10.627910

# casa mia

positionLat = 44.685870
positionLong = 10.654490


# mette in parks tutti i parcheggi che hanno distanza minore di 5km a piedi
def get_nearby_parks(parking_list, searched_lat, searched_long):
    parks = []
    for park in parking_list:
        park_lat = park["lat"]
        park_long = park["long"]
        distance = geodesic((searched_lat, searched_long), (park_lat, park_long)).km
        if distance <= 5:
            parks.append(park)
    return parks


# calcola distanza a piedi e tempo di percorrenza a piedi dalla posizione del parcheggio alla destinazione
def calculate_walking_distance(park_lat, park_long, searched_lat, searched_long):
    base_url = "http://router.project-osrm.org/route/v1/foot/"
    coordinates = str(park_long) + "," + str(park_lat) + ";" + str(searched_long) + "," + str(searched_lat)
    response = requests.get(base_url + coordinates)
    if response.status_code == 200:
        result = response.json()
        if result['code'] == "Ok":
            distance = result['routes'][0]['distance']
            time = result['routes'][0]['duration']
            return distance, time
        else:
            return None
    else:
        return None


# calcola distanza in macchina e tempo di percorrenza dalla posizione attuale al parcheggio
def calculate_driving_distance(pos_lat, pos_long, park_lat, park_long):
    base_url = "http://router.project-osrm.org/route/v1/car/"
    coordinates = str(pos_long) + "," + str(pos_lat) + ";" + str(park_long) + "," + str(park_lat)
    response = requests.get(base_url + coordinates)
    if response.status_code == 200:
        result = response.json()
        if result['code'] == "Ok":
            distance = result['routes'][0]['distance']
            time = result['routes'][0]['duration']
            return distance, time
        else:
            return None
    else:
        return None


def main(searchedLat, searchedLong, positionLat, positionLong):
    # prendo tutti i parcheggi dell'elenco a meno di 5km
    parks = get_nearby_parks(parcheggi, searchedLat, searchedLong)

    # creo un array di dizionari con tutte le info
    park_list = []
    for park in parks:
        walking_distance, walking_time = calculate_walking_distance(park['lat'], park['long'], searchedLat,
                                                                    searchedLong)
        driving_distance, driving_time = calculate_driving_distance(positionLat, positionLong, park['lat'],
                                                                    park['long'])
        park_info = {
            'id': park['id'],
            'address': park['indirizzo'],
            'lat': park['lat'],
            'long': park['long'],
            'capacity': park['capienza'],
            'occupancy': park['occupazione'],
            'cost': park['costo'],
            'walking_distance': walking_distance,
            'walking_time': walking_time,
            'driving_distance': driving_distance,
            'driving_time': driving_time
        }
        park_list.append(park_info)

    parks = park_list

    # ordino per distanza a piedi
    parks = sorted(parks, key=lambda x: x['walking_distance'])

    # nearest_park -> il più vicino a piedi
    nearest_park = parks[0] if parks else None

    # per minore carico computazionale tengo solo i primi 10
    parks = parks[:10]

    '''
    di questi associa a ciascuno un valore di VICINANZA
    0 se la distanza a piedi è tra 0 e 300m 
    N dove N è numero di centinaia di metri extra ai 300m (quindi tra 301 e 400 vale 1, tra 401 e 500 vale 2 etc)
    
    poi associa anche un valore di DISPONIBILITA' che è :
    0 se la percentuali di posti liberi del parcheggio è tra 0% e 70%
    1 tra 70 e 80
    2 tra 80 e 85
    4 tra 85 e 90
    7 tra 90 e 95
    10 tra 95 e 98
    1000 tra 98 e 100
    '''

    for park in parks:
        park['vicinanza'] = 0 if park['walking_distance'] <= 300 else (park['walking_distance'] - 300) // 100 + 1
        percentage = (park['occupancy']) / park['capacity'] * 100
        if percentage <= 70:
            park['disponibilità'] = 0
        elif percentage <= 80:
            park['disponibilità'] = 1
        elif percentage <= 85:
            park['disponibilità'] = 2
        elif percentage <= 90:
            park['disponibilità'] = 4
        elif percentage <= 95:
            park['disponibilità'] = 7
        elif percentage <= 98:
            park['disponibilità'] = 10
        elif percentage <= 100:
            park['disponibilità'] = 10000

    # ordino per priorità = disponibilità + vicinanza, in caso di parità ordino per tempo totale da posizione attuale a destinazione
    parks = sorted(parks, key=lambda x: (x['disponibilità'] + x['vicinanza'], x['driving_time'] + x['walking_time']))

    # free_park -> parcheggio con costo 0 migliore
    free_park = next((park for park in parks if park['cost'] == 0), None)

    # best_park -> parcheggio migliore
    best_park = parks[0] if parks else None

    return [free_park,nearest_park,best_park]
    # print('Da casa mia all\'università ex seminario:')
    # print('free park: ' + str(free_park))
    # print('nearest park: ' + str(nearest_park))
    # print('freePark: ' + str(best_park))
