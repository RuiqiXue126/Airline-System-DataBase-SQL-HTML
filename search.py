from datetime import datetime

import pymysql
from pymysql import cursors

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='AirSystem',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

def getPublicData(add = None):
    cursor = conn.cursor()
    query = 'SELECT * FROM flight'

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    filtered_data = []

    for elem in data:
        to_append = [elem['airline_name'], elem['flight_number'],
                            elem['departure_date_time'][0:10], elem['arrival_date_time'][0:10],
                            elem['flight_status'], elem['departure_airport_code'],
                            elem['arrival_airport_code']]
        if (add):
            to_append.append([elem[add]])

        filtered_data.append(to_append)

    return filtered_data

def getAllFutureFlights():
    cursor = conn.cursor()

    now = datetime.now()
    print(now)
    dt_string = now.strftime("%Y/%m/%d")

    query = 'SELECT * FROM flight WHERE departure_date_time > DATE %s'
    cursor.execute(query, dt_string)
    data = cursor.fetchall()

    cursor.close()

    big_list = []

    print(data)

    for flight in data:
        to_append = []
        for atom in flight:
            to_append.append(flight[atom])

        big_list.append(to_append)


    return big_list;

def searchData(arg, username = None):
    cursor = conn.cursor()
    if (username):
        query = 'SELECT * FROM flight WHERE airline_name = %s OR departure_airport_code = %s OR arrival_airport_code = %s ' \
                'OR departure_date_time = %s OR arrival_date_time = %s AND flight_number ' \
                'IN (SELECT flight_number FROM ticket WHERE customer_email = %s)'
        cursor.execute(query, (arg, arg, arg, arg, arg, username))
    else:
        # public
        query = 'SELECT * FROM flight WHERE airline_name = %s OR departure_airport_code = %s OR arrival_airport_code = %s ' \
                'OR departure_date_time = %s OR arrival_date_time = %s'
        cursor.execute(query, (arg, arg, arg, arg, arg))

    filtered_data = []
    data = cursor.fetchall()
    for elem in data:
        filtered_data.append([elem['airline_name'], elem['flight_number'],
                              elem['departure_date_time'][0:10], elem['arrival_date_time'][0:10]])

    return filtered_data

def search_source_airport(arg, username = None):
    cursor = conn.cursor()

    if (username):
        query = 'SELECT * FROM flight WHERE departure_airport_code IN ' \
                '(SELECT airport_code FROM airport WHERE ' \
                'airport_name = %s OR city = %s OR country = %s OR ' \
                'airport_code = %s) AND flight_number IN ' \
                '(SELECT flight_number FROM ticket WHERE customer_email = %s)'
        cursor.execute(query, (arg, arg, arg, arg, username))

    else:
        query = 'SELECT * FROM flight WHERE departure_airport_code IN ' \
                '(SELECT airport_code FROM airport WHERE ' \
                'airport_name = %s OR city = %s OR country = %s OR ' \
                'airport_code = %s)'
        cursor.execute(query, (arg, arg, arg, arg))

    filtered_data = []
    data = cursor.fetchall()
    for elem in data:
        filtered_data.append([elem['airline_name'], elem['flight_number'],
                              elem['departure_date_time'][0:10], elem['arrival_date_time'][0:10]])

    cursor.close()
    return filtered_data




def search_dest_airport(arg, username=None):
    cursor = conn.cursor()

    if (username):
        query = 'SELECT * FROM flight WHERE arrival_airport_code IN ' \
                '(SELECT airport_code FROM airport WHERE ' \
                'airport_name = %s OR city = %s OR country = %s OR ' \
                'airport_code = %s) AND flight_number IN ' \
                '(SELECT flight_number FROM ticket WHERE customer_email = %s)'
        cursor.execute(query, (arg, arg, arg, arg, username))

    else:
        query = 'SELECT * FROM flight WHERE arrival_airport_code IN ' \
                '(SELECT airport_code FROM airport WHERE ' \
                'airport_name = %s OR city = %s OR country = %s OR ' \
                'airport_code = %s)'
        cursor.execute(query, (arg, arg, arg, arg))

    filtered_data = []
    data = cursor.fetchall()
    for elem in data:
        filtered_data.append([elem['airline_name'], elem['flight_number'],
                              elem['departure_date_time'][0:10], elem['arrival_date_time'][0:10]])

    cursor.close()
    return filtered_data


def search_dept_date(arg, username=None):
    cursor = conn.cursor()
    print("dept", arg[0:10])


    if (username):
        query = 'SELECT * FROM flight WHERE departure_date_time = %s' \
                ' AND flight_number IN ' \
                '(SELECT flight_number FROM ticket WHERE customer_email = %s)'
        cursor.execute(query, (arg[0:10], username))

    else:
        query = 'SELECT * FROM flight WHERE departure_date_time = %s'
        cursor.execute(query, (arg[0:10]))

    filtered_data = []
    data = cursor.fetchall()
    for elem in data:
        filtered_data.append([elem['airline_name'], elem['flight_number'],
                              elem['departure_date_time'][0:10], elem['arrival_date_time'][0:10]])

    cursor.close()
    return filtered_data

def search_arriv_date(arg, username=None):
    cursor = conn.cursor()


    if (username):
        query = 'SELECT * FROM flight WHERE arrival_date_time = %s' \
                ' AND flight_number IN ' \
                '(SELECT flight_number FROM ticket WHERE customer_email = %s)'
        cursor.execute(query, (arg[0:10], username))

    else:
        query = 'SELECT * FROM flight WHERE arrival_date_time = %s'
        cursor.execute(query, (arg[0:10]))

    filtered_data = []
    data = cursor.fetchall()
    for elem in data:
        filtered_data.append([elem['airline_name'], elem['flight_number'],
                              elem['departure_date_time'][0:10], elem['arrival_date_time'][0:10]])

    cursor.close()
    return filtered_data