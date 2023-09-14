
import random
from time import strftime

import pymysql
import werkzeug.exceptions
from pymysql import cursors
from flask import Flask, render_template, request, session, url_for, redirect
import search
import hashlib
import datetime
from datetime import datetime
from datetime import date

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='AirSystem',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

app.secret_key = "secret"

@app.route('/')
def landing():
    filtered_data = search.getPublicData()
    if filtered_data:
        no_search = False
    else:
        no_search = True

    return render_template('landing_page.html', flights=filtered_data, err=no_search)


@app.route('/psearch', methods=['POST'])
def psearch():
    search_type = request.args.get('type')
    prev_page = request.args.get('prev')
    level = request.args.get('sec')
    search_tags = request.form['psearchf']

    if (level == "user"):
        username = session['username']
    else:
        username = None


    if (search_type == "source"):
        print("searching for source", search_tags)
        data = search.search_source_airport(search_tags, username)
    elif (search_type == "dest"):
        print("searching for dest", search_tags)
        data = search.search_dest_airport(search_tags, username)

    elif (search_type == "dates"):
        recon = search_tags[0:10]
        recon += " " + search_tags[11:] + ":00"
        search_tags = recon
        data = search.search_dept_date(search_tags, username)
    else:
        data = None

    return render_template('psearch.html', field=search_tags, data=data, prev=prev_page)


# HOMEPAGES

@app.route('/chome')
def chome():
    username = session['username']
    cursor = conn.cursor()

    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, username)

    # public flight data
    full_info = cursor.fetchone()
    name = full_info['first_name'] + " " + full_info['last_name']

    filtered_public_data = search.getPublicData()




    # customer's flight data
    query = 'SELECT * FROM flight WHERE flight_number IN ' \
            '(SELECT flight_number FROM ticket WHERE customer_email = %s)'


    cursor.execute(query, username)

    customer_flights = cursor.fetchall()


    filtered_customer_flights = []
    filtered_future_customer_flights = []
    customer_spending = []
    total_spending = None

    query = 'SELECT * FROM ticket WHERE customer_email = %s'
    cursor.execute(query, username)
    customer_tickets = cursor.fetchall()

    if (customer_tickets):
        for ticket in customer_tickets:
            to_append = [ticket['ticket_id'], ticket['flight_number']]

            today = datetime.today()

            flight_info = []

            flight_status = "Unknown"

            for flight in customer_flights:
                if (flight['flight_number'] == ticket['flight_number']):
                    flight_info += [flight['departure_airport_code'],
                                  flight['departure_date_time'][0:10],
                                  flight['arrival_airport_code'],
                                  flight['arrival_date_time'][0:10]]
                    flight_status = flight['flight_status']


            arrive_day = datetime.strptime(flight_info[3], '%Y-%m-%d')

            if today > arrive_day:
                flight_status = "Complete"

            to_append.append(flight_status)
            to_append += flight_info


            to_append += [ticket['airline_name'], ticket['travel_class'],
                          "$"+str(ticket['sold_price'])]


            filtered_customer_flights.append(to_append)



        # customer's future flights
        query = 'SELECT * FROM ticket WHERE date(departure_date_time) > DATE %s AND customer_email = %s'

        now = datetime.now()
        dt_string = now.strftime("%Y/%m/%d")

        cursor.execute(query, (dt_string, username))
        cust_future_flights = cursor.fetchall()

        print("future flights", cust_future_flights)



        if (cust_future_flights):
            for ticket in cust_future_flights:

                to_append = []

                rest = []
                found = False
                for flight in customer_flights:
                    if (flight['flight_number'] == ticket['flight_number'] and not found):
                        to_append.append(ticket['ticket_id'])


                        rest = [ticket['airline_name'], ticket['travel_class'],
                                "$"+str(ticket['sold_price'])]
                        found = True

                        to_append += [flight['flight_number'],
                                     flight['flight_status'],
                                     flight['departure_airport_code'],
                                     flight['departure_date_time'][0:10],
                                     flight['arrival_airport_code'],
                                     flight['arrival_date_time'][0:10]]
                to_append += rest
                filtered_future_customer_flights.append(to_append)

        # customer spending
        total_spending = 0

        for ticket in customer_tickets:
            to_append = [ticket['purchase_date_time'].strftime("%m/%d/%Y"),
                         ticket['ticket_id'],
                         ticket['flight_number'],
                         "$"+str(ticket['sold_price']),
                         ]
            total_spending += ticket['sold_price']
            customer_spending.append(to_append)
        total_spending = "$" + str(total_spending)


    cursor.close()

    # check for errors
    try:
        fail_to_cancel = request.args['cancel_error']
    except werkzeug.exceptions.BadRequestKeyError:
        fail_to_cancel = None

    try:
        cancel_success = request.args['cancel_success']
    except werkzeug.exceptions.BadRequestKeyError:
        cancel_success = None

    return render_template('chome.html', username=name, public_flights=filtered_public_data,
                           cust_flights=filtered_customer_flights, fail_cancel=fail_to_cancel,
                           cancel_success=cancel_success, future_flights=filtered_future_customer_flights,
                           spending=customer_spending, spending_total=total_spending)

@app.route('/shome')
def shome():
    username = session['username']
    cursor = conn.cursor()
    # public flight data

    filtered_public_data = search.getPublicData()

    return render_template('shome.html', username=username, public_flights=filtered_public_data)


# BOOKING/CANCELING TICKETS

@app.route('/buy_ticket_redirect')
def buy_ticket_redirect():
    step = request.args.get('step')
    if (step == "listings"):
        future_flights = search.getAllFutureFlights()


        # packaged and formatted (in this order)
        packaged_data = []
        for flight in future_flights:

            flight_no = flight[0]
            flight_stat = flight[1]
            dept_date = flight[2][0:10]
            arr_date = flight[7][0:10]
            airline_name = flight[3]
            dept_code = flight[5]
            arr_code = flight[6]
            price = flight[8]

            packaged_data.append([flight_no, flight_stat, dept_date, arr_date,
                                  airline_name, dept_code, arr_code, price])

        return render_template('flight_listings.html', data=packaged_data)

    else:
        flight_info = request.args.getlist('flight_info')
        flight_number = flight_info[0]
        price = flight_info[7]
        dept = flight_info[5]
        arr = flight_info[6]


        return render_template('book_ticket_form.html', flight_number=flight_number, price=price,
                               departure=dept, arrival=arr)


@app.route('/buy_ticket', methods=['post'])
def buy_ticket():
    username = session['username']
    cursor = conn.cursor()

    flight_number = request.args.get('flight_number')
    price = request.form['final_cost']

    # get departure date
    query = 'SELECT date(departure_date_time) FROM flight WHERE flight_number = %s'
    cursor.execute(query, flight_number)

    data = cursor.fetchone()

    print(data)

    departure = data['date(departure_date_time)']

    # get airline hosting the flight
    query = 'SELECT airline_name FROM flight WHERE flight_number = %s'
    cursor.execute(query, flight_number)
    airline_name = cursor.fetchone()['airline_name']


    travel_class = request.form['class']

    purchase_date = datetime.now()
    dt_string = purchase_date.strftime("%Y/%m/%d %H:%M:%S")



    card = request.form['card_type']
    name = request.form['name_card']
    exp = request.form['expiry']

    exp_year = exp[0:4]
    exp_month = exp[5:7]

    mod_expiry = exp_year + '-' + exp_month + '-01'

    uniqueID = False
    ticket_id = 0
    # check for dupe id
    while(not uniqueID):
        ticket_id = random.randint(0, 10000000)
        query = 'SELECT ticket_id FROM ticket WHERE ticket_id = %s'
        cursor.execute(query, ticket_id)
        data = cursor.fetchone()
        if (data):
            pass
        else:
            uniqueID = True

    info = (ticket_id, username, travel_class, airline_name, flight_number,
                           departure, float(price), dt_string, card, name, mod_expiry)


    query = 'INSERT INTO ticket VALUES(%s, %s, %s, %s, %s, %s,' \
            '%s, %s, %s, %s, %s)'
    cursor.execute(query, info)
    conn.commit()
    cursor.close()
    return redirect(url_for('chome'))

@app.route('/cancel_flight', methods=["post"])
def cancel_flight():
    email = session['username']
    cursor = conn.cursor()
    ticket_id = request.form['selected_ticket']

    print("Attempting to cancel ticket " + ticket_id)

    query = 'SELECT date(departure_date_time) FROM flight WHERE flight_number IN' \
            '(SELECT flight_number FROM ticket WHERE ticket_id = %s)'
    cursor.execute(query, ticket_id)



    data = cursor.fetchone()

    print(data)

    departure = data['date(departure_date_time)']

    now = date.today()
    print(departure)

    departure_datetime = departure

    time_diff = departure_datetime - now
    time_diff_hours = divmod(time_diff.total_seconds(), 3600)[0]

    print("Flight in " + str(time_diff_hours))


    if (time_diff_hours < 24.0):
        return redirect(url_for('chome', cancel_error="You may not cancel a ticket less than 24 hours prior "
                                                      "to takeoff."))



    # ensure ticket belongs to logged in customer
    query = 'SELECT customer_email FROM ticket WHERE ticket_id = %s'
    cursor.execute(query, int(ticket_id))
    ticket_email = cursor.fetchone()

    if (email == ticket_email['customer_email']):
        pass
    else:
        return redirect(url_for('chome', cancel_error="Unable to cancel ticket!"))

    query = 'DELETE FROM ticket WHERE ticket_id = %s'
    cursor.execute(query, ticket_id)
    conn.commit()
    return redirect(url_for('chome', cancel_success="Ticket " + ticket_id + " canceled successfully."))

# RATINGS

@app.route('/ratings')
def ratings():
    cursor = conn.cursor()
    flight_number = request.args.get('flight_number')
    query = 'SELECT * FROM ratings WHERE flight_number = %s'


    try:
        post_err = request.args.get('post_err')
    except werkzeug.exceptions.BadRequestKeyError:
        post_err = None

    try:
        delete_err = request.args.get('delete_message')
    except werkzeug.exceptions.BadRequestKeyError:
        delete_err = None

    cursor.execute(query, flight_number)

    rating_data = cursor.fetchall()

    print(rating_data)

    compiled_data = []

    for entry in rating_data:
        compiled_data.append([entry['customer_email'],
                             entry['rating'],
                             entry['comments']])


    return render_template('ratings.html', data=compiled_data, flight_number=flight_number,
                           post_err=post_err, delete_message=delete_err)

@app.route('/post_rating', methods=['post'])
def post_rating():
    username = session['username']

    cursor = conn.cursor()

    # check for pre existing comment

    query = 'SELECT * FROM ratings WHERE customer_email = %s'
    cursor.execute(query, username)
    preexisting_rating = cursor.fetchone()
    flight_number = request.form['flight_number']

    if (preexisting_rating):
        print("Pre existing comment!")
        return redirect(url_for('ratings', flight_number=flight_number,
                                post_err="You may only have one rating at a time. Please " \
                                "delete your comment first."))

    comment = request.form['comment']

    rating = request.form['score']




    query = 'INSERT INTO ratings VALUES (%s, %s, %s, %s)'
    cursor.execute(query, (flight_number, username,
                           rating, comment))

    conn.commit()


    return redirect(url_for('ratings', flight_number=flight_number))

@app.route('/delete_rating', methods=['post'])
def delete_rating():
    username = session['username']
    flight_number = request.form['flight_number']

    cursor = conn.cursor()

    query = 'SELECT * FROM ratings WHERE customer_email = %s'
    cursor.execute(query, username)
    preexisting_rating = cursor.fetchone()

    if (preexisting_rating):

        query = 'DELETE FROM ratings WHERE customer_email = %s'
        cursor.execute(query, username)
        conn.commit()
        return redirect(url_for('ratings', flight_number=flight_number, delete_message="Comment deleted."))

    else:
        return redirect(url_for('ratings', flight_number=flight_number, delete_message="No comment to delete."))




# STAFF FLIGHT MANAGEMENT

@app.route('/create_new_flight')
def create_new_flight():

    future_flights = search.getAllFutureFlights()

    # packaged and formatted (in this order)
    packaged_data = []
    for flight in future_flights:
        flight_no = flight[0]
        flight_stat = flight[1]
        dept_date = flight[2][0:10]
        arr_date = flight[7][0:10]
        airline_name = flight[3]
        dept_code = flight[5]
        arr_code = flight[6]
        price = flight[8]

        packaged_data.append([flight_no, flight_stat, dept_date, arr_date,
                              airline_name, dept_code, arr_code, price])


    return render_template('create_flight.html', data=packaged_data)

@app.route("/newFlight", methods=['post'])
def newFlight():

    cursor = conn.cursor()
    flight_no = request.form['flight_number']
    flight_status = request.form['flight_status']
    dept_datetime = request.form['departure_date']
    arri_datetime = request.form['arrival_date']
    airline = request.form['airline']
    airplane = request.form['airplane_id']
    dept_code = request.form['dept_code']
    arriv_code = request.form['arriv_code']
    base_price = request.form['base_price']

    # checks if duplicate flight number
    query = 'SELECT * FROM flight WHERE flight_number = %s'
    cursor.execute(query, flight_no)
    dup_flight = cursor.fetchone()
    if (dup_flight):
        cursor.close()
        return render_template('create_flight.html', error="Duplicate flight number")
    else:
        query = 'INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (flight_no, flight_status, dept_datetime, airline,
                               airplane, dept_code, arriv_code, arri_datetime, base_price))
        conn.commit()
        cursor.close()
        return render_template('create_flight.html', success="Flight" + flight_no + "created!")


@app.route('/change_status_of_flight')
def change_status_of_flight():
    return render_template('change_status.html')


# LOGIN


@app.route("/changeStatus", methods=['post'])
def changeStatus():
    cursor = conn.cursor()
    flight_num = request.form['flight_number']
    flight_status = request.form['flight_status']
    query = 'SELECT * FROM flight WHERE flight_number = %s'
    cursor.execute(query, flight_num)
    flight_exist = cursor.fetchone()

    if (flight_exist):
        query2 = 'UPDATE flight SET flight_status  = %s WHERE flight_number = %s'
        cursor.execute(query2, (flight_status, flight_num))
        cursor.close()
        return render_template('change_status.html', success="Status of " + flight_num + " has been changed!")
    else:

        return render_template('change_status.html', error="Invalid flight number!")


@app.route('/add_airplane')
def add_airplane():
    cursor = conn.cursor()
    query3 = 'SELECT airline_name FROM airline'
    cursor.execute(query3)
    airline_list = cursor.fetchall()
    cursor.close()
    return render_template('add_plane.html', airline_list=airline_list)


@app.route('/addPlane', methods=['post'])
def addPlane():
    cursor = conn.cursor()
    airplane_id = request.form['airplane_id']
    num_of_seats = request.form['num_of_seats']
    manu = request.form['manufacturer']
    age = request.form['age']
    airline = request.form['airline']
    query = 'SELECT * FROM airplane WHERE airplane_id = %s'
    cursor.execute(query, airplane_id)
    dup_plane = cursor.fetchone()

    if (dup_plane):
        return render_template('add_plane.html', error="This airplane already exists!")
    else:
        query2 = 'INSERT INTO airplane VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query2, (airplane_id, num_of_seats, manu, age, airline))

        query1 = 'SELECT * FROM airplane WHERE airline_name = %s'
        cursor.execute(query1, airline)
        data = cursor.fetchall()

        cursor.close()
        filtered_data = []

        for elem in data:
            filtered_data.append([elem['airplane_id'], elem['num_of_seats'],
                                  elem['manufacturer'], elem['age'], elem['airline_name']])

        cursor.close()
        return render_template('add_plane_confirmation.html', airplanes=filtered_data)

@app.route('/add_airport')
def add_airport():
    return render_template('add_new_airport.html')

@app.route("/addAirport", methods=['post'])
def addAirport():
    cursor = conn.cursor()
    airport_code = request.form['airport_code']
    airport_name = request.form['airport_name']
    country = request.form['country']
    city = request.form['city']
    type = request.form['type']
    query = 'SELECT * FROM airport WHERE airport_code = %s'
    cursor.execute(query, airport_code)
    airport_exist = cursor.fetchone()

    if (airport_exist):
        cursor.close()
        return render_template('add_new_airport.html', error="This airport already exists!")

    else:

        query2 = 'INSERT INTO airport VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query2, (airport_code, airport_name, country, city, type))
        cursor.close()

        return render_template('add_new_airport.html', success="Airport " + airport_code + " has been added!")


@app.route('/view_report')
def view_report():
    return render_template('view_report.html')


@app.route("/viewReport", methods=['post'])
def viewReport():
    username = session['username']
    cursor = conn.cursor()
    query0 = 'SELECT airline_name FROM airline_staff WHERE username=%s'
    cursor.execute(query0, username)
    airline_ = cursor.fetchone()
    airline = airline_['airline_name']

    last = request.form['last']

    if last == 'last_month':
        query1 = 'SELECT COUNT(*) as num_tickets_sold FROM ticket WHERE airline_name=%s AND date(purchase_date_time) >\
             subdate(CURRENT_DATE, INTERVAL 1 MONTH)'
        cursor.execute(query1, airline)
        result = cursor.fetchone()
        query4 = 'SELECT distinct MONTH(purchase_date_time) AS month FROM ticket WHERE airline_name=%s AND date(purchase_date_time) >\
             subdate(CURRENT_DATE, INTERVAL 1 MONTH)'
        cursor.execute(query4, airline)
        data = cursor.fetchall()
        months = []
        for each in data:
            months.append(each['month'])

        nums = []
        for i in months:
            query5 = 'SELECT COUNT(*) AS num FROM ticket WHERE airline_name=%s AND MONTH(purchase_date_time) = %s'
            cursor.execute(query5, (airline, i))
            data2 = cursor.fetchone()
            nums.append(data2)
    elif last == 'last_year':
        query2 = 'SELECT COUNT(*) as num_tickets_sold FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR)'
        cursor.execute(query2, airline)
        result = cursor.fetchone()
        query4 = 'SELECT distinct MONTH(purchase_date_time) AS month FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR)'
        cursor.execute(query4, airline)
        data = cursor.fetchall()
        months = []
        for each in data:
            months.append(each['month'])

        nums = []
        for i in months:
            query5 = 'SELECT COUNT(*) AS num FROM ticket WHERE airline_name=%s AND MONTH(purchase_date_time) = %s'
            cursor.execute(query5, (airline, i))
            data2 = cursor.fetchone()
            nums.append(data2)

    elif last == 'between':
        date1 = request.form['date1']
        date2 = request.form['date2']
        query3 = 'SELECT COUNT(*) as num_tickets_sold FROM ticket WHERE airline_name= %s AND date(purchase_date_time) BETWEEN %s AND %s'
        cursor.execute(query3, (airline, date1, date2))
        result = cursor.fetchone()
        query4 = 'SELECT distinct MONTH(purchase_date_time) AS month FROM ticket WHERE airline_name=%s AND date(purchase_date_time) BETWEEN %s AND %s '
        q = ''
        cursor.execute(query4, (airline, date1, date2))
        data = cursor.fetchall()
        months = []
        for each in data:
            months.append(each['month'])

        nums = []
        for i in months:
            query5 = 'SELECT COUNT(*) AS num FROM ticket WHERE airline_name=%s AND MONTH(purchase_date_time) = %s'
            cursor.execute(query5, (airline, i))
            data2 = cursor.fetchone()
            nums.append(data2)
    else:
        return render_template('view_report_result.html', error='You must make a choice!')

    result_num = result['num_tickets_sold']

    cursor.close()

    return render_template('view_report_result.html', number=result_num, months=months, nums=nums)


@app.route('/view_top_des')
def view_top_des():
    return render_template('view_top_des.html')


@app.route("/viewDes", methods=['post'])
def viewDes():
    username = session['username']
    cursor = conn.cursor()
    query0 = 'SELECT airline_name FROM airline_staff WHERE username=%s'
    cursor.execute(query0, username)
    airline_ = cursor.fetchone()
    airline = airline_['airline_name']

    last = request.form['last']

    if last == 'last_three_month':
        query1 = 'SELECT airport.city AS city, arrival_airport_code AS des_code,  COUNT(ticket_id) AS num_ticket FROM ticket, \
        flight, airport WHERE ticket.airline_name=%s AND ticket.flight_number=flight.flight_number AND flight.arrival_airport_code=airport.airport_code \
        AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 3 MONTH) GROUP BY arrival_airport_code \
        ORDER BY num_ticket DESC LIMIT 3'
        cursor.execute(query1, airline)
        data = cursor.fetchall()
    elif last == 'last_year':
        query2 = 'SELECT airport.city AS city, arrival_airport_code AS des_code,  COUNT(ticket_id) AS num_ticket FROM ticket, flight, \
        airport WHERE ticket.airline_name=%s AND ticket.flight_number=flight.flight_number AND flight.arrival_airport_code=airport.airport_code AND \
        date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR) GROUP BY arrival_airport_code ORDER BY num_ticket DESC LIMIT 3'
        cursor.execute(query2,airline)
        data = cursor.fetchall()
    else:
        return render_template('view_top_des.html', error="You must make a choice!")

    filtered_data = []
    for elem in data:
        filtered_data.append([elem['city'], elem['des_code'], elem['num_ticket']])
    cursor.close()
    return render_template('view_top_des_result.html', data=filtered_data)

@app.route('/view_revenue')
def view_revenue():
    username = session['username']
    cursor = conn.cursor()
    query0 = 'SELECT airline_name FROM airline_staff WHERE username=%s'
    cursor.execute(query0, username)
    airline_ = cursor.fetchone()
    airline = airline_['airline_name']
    query1 = 'SELECT SUM(sold_price) as total_revenue_m FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 MONTH)'
    query2 = 'SELECT SUM(sold_price) as total_revenue_y FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR)'
    cursor.execute(query1, airline)
    mdata = cursor.fetchone()
    cursor.execute(query2, airline)
    ydata = cursor.fetchone()

    print(mdata)
    print(ydata)
    cursor.close()
    return render_template('view_revenue.html', mdata=mdata, ydata=ydata)

@app.route('/view_revenue_class')
def view_revenue_class():
    username = session['username']
    cursor = conn.cursor()
    query0 = 'SELECT airline_name FROM airline_staff WHERE username=%s'
    cursor.execute(query0, username)
    airline_ = cursor.fetchone()
    airline = airline_['airline_name']
    query11 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_m\
     FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 MONTH) AND travel_class = 'First Class'"
    query12 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_m\
     FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 MONTH) AND travel_class = 'Business Class'"
    query13 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_m\
     FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 MONTH) AND travel_class = 'Economy Class'"
    query21 =  "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_y\
     FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR) AND travel_class= 'First Class'"
    query22 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_y\
     FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR) AND travel_class= 'Business Class'"
    query23 = "SELECT (CASE WHEN SUM(sold_price) is not null THEN SUM(sold_price) ELSE 0 END) as total_revenue_y\
     FROM ticket WHERE airline_name=%s AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR) AND travel_class= 'Economy Class'"
    cursor.execute(query11, airline)
    mdata1 = cursor.fetchone()
    cursor.execute(query12, airline)
    mdata2 = cursor.fetchone()
    cursor.execute(query13, airline)
    mdata3 = cursor.fetchone()
    cursor.execute(query21, airline)
    ydata1 = cursor.fetchone()
    cursor.execute(query22, airline)
    ydata2 = cursor.fetchone()
    cursor.execute(query23, airline)
    ydata3 = cursor.fetchone()

    cursor.close()
    return render_template('view_revenue_class.html', mdata1=mdata1, mdata2=mdata2, mdata3=mdata3,
                           ydata1=ydata1, ydata2=ydata2, ydata3=ydata3)

@app.route('/view_ratings')
def view_ratings():
    username = session['username']
    cursor = conn.cursor()
    query0 = 'SELECT airline_name FROM airline_staff WHERE username=%s'
    cursor.execute(query0, username)
    airline_ = cursor.fetchone()
    airline = airline_['airline_name']

    query = 'SELECT ratings.flight_number, AVG(rating) as average_rating FROM ratings, flight WHERE \
    flight.flight_number=ratings.flight_number\
     AND flight.airline_name=%s GROUP BY flight_number'
    cursor.execute(query, airline)
    data = cursor.fetchall()
    cursor.close()
    filtered_data = []
    for elem in data:
        filtered_data.append([elem['flight_number'], elem['average_rating']])
    return render_template('view_ratings.html', ratings=filtered_data)


@app.route('/viewRC', methods=['post'])
def view_RC():
    cursor = conn.cursor()
    flight_num = request.form['flight_number']
    query = 'SELECT flight_number, rating, comments, customer_email as customer FROM ratings WHERE flight_number=%s'
    cursor.execute(query, flight_num)
    data = cursor.fetchall()
    cursor.close()
    filtered_data = []
    for elem in data:
        filtered_data.append([elem['flight_number'], elem['rating'], elem['comments'], elem['customer']])
    return render_template('view_ratings_by_flight.html', ratingcomment=filtered_data)

@app.route('/view_frequent_customers')
def view_frequent_customers():

    username = session['username']
    cursor = conn.cursor()
    query0 = 'SELECT airline_name FROM airline_staff WHERE username=%s'
    cursor.execute(query0, username)
    airline_ = cursor.fetchone()
    airline = airline_['airline_name']
    query1 = 'SELECT DISTINCT customer_email FROM ticket WHERE airline_name=%s \
    AND date(purchase_date_time) > subdate(CURRENT_DATE, INTERVAL 1 YEAR) group by customer_email \
    ORDER BY COUNT(customer_email) DESC LIMIT 1'
    cursor.execute(query1, airline)
    fc_ = cursor.fetchone()
    print(fc_)
    fc = fc_['customer_email']

    cursor.close()
    return render_template('view_frequent_customers.html', fc=fc)

@app.route('/view_fc_list', methods=['post'])
def view_fc_list():
    username = session['username']
    cursor = conn.cursor()
    query0 = 'SELECT airline_name FROM airline_staff WHERE username=%s'
    cursor.execute(query0, username)
    airline_ = cursor.fetchone()
    airline = airline_['airline_name']
    customer = request.form['customer']
    query1 = 'SELECT flight_number FROM ticket WHERE customer_email=%s AND airline_name=%s AND date(departure_date_time) < CURRENT_DATE'
    cursor.execute(query1, (customer, airline))
    data = cursor.fetchall()
    fil_data = []
    for elem in data:
        fil_data.append(elem['flight_number'])
    cursor.close()
    return render_template('view_fc_list.html', fcl=fil_data)

# LOGIN

@app.route('/logout')
def logout():
    session.pop('username')
    return render_template('customerlogin.html')

@app.route('/loginRedirect/<acc_type>')
def loginRedirect(acc_type):

    if (acc_type == "customer"):
        return(render_template('customerlogin.html'))
    elif(acc_type == "staff"):
        return (render_template('stafflogin.html'))
    else:
        redirect(url_for('landing'))

@app.route('/registerRedirect/<acc_type>')
def registerRedirect(acc_type):
    if (acc_type == "customer"):
        return(render_template('customerregister.html'))
    elif(acc_type == "staff"):
        return (render_template('staffregister.html'))
    else:
        redirect(url_for('landing'))

#Authenticates the login
@app.route('/sloginAuth', methods=['GET', 'POST'])
def sloginAuth():
    #grabs information from the forms
    username = request.form['susername']
    password = request.form['spassword']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s and md5(s_password) = %s'
    cursor.execute(query, (username, hashlib.md5(password.encode()).hexdigest()))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('shome'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('stafflogin.html', error=error)

@app.route('/cloginAuth', methods=['GET', 'POST'])
def cloginAuth():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['cpassword']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE email = %s and md5(c_password) = %s'
    cursor.execute(query, (email, (hashlib.md5(password.encode())).hexdigest()))
    #stores the results in a variable
    data = cursor.fetchone()

    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        # the username of customers is the email
        # it's possible we have 2 customers with the same name!!
        session['username'] = email
        return redirect(url_for('chome'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or email'
        return render_template('customerlogin.html', error=error)


#Authenticates the register
@app.route('/cregisterAuth', methods=['GET', 'POST'])
def cregisterAuth():
    #grabs information from the forms
    email = request.form['email']
    fname = request.form['fname']
    lname = request.form['lname']
    password = request.form['password']
    state = request.form['state']
    city = request.form['city']
    street = request.form['street']
    building = request.form['building']
    phone = request.form['phone']
    passnum = request.form['passnum']
    passexpi = request.form['passexpi']
    passcountry = request.form['passcountry']
    dob = request.form['dob']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        cursor.close()
        return render_template('customerregister.html', error = error)
    else:
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (email, fname, lname, password, state, city, street, building, phone, passnum,
                             passexpi, passcountry, dob))
        conn.commit()
        cursor.close()
        return render_template('customerlogin.html')

@app.route('/sregisterAuth', methods=['GET', 'POST'])
def sregisterAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    airline_name = request.form['airline_name']
    fname = request.form['fname']
    lname = request.form['lname']
    dob = request.form['dob']
    phone = request.form['phone']


    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        cursor.close()
        return render_template('staffregister.html', error = error)
    else:
        ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, airline_name, fname, lname, dob))
        ins2 = 'INSERT INTO airline_staff_phone_number VALUES(%s, %s)'
        for each in phone:
            cursor.execute(ins2, (username, each))
        conn.commit()
        cursor.close()
        return render_template('stafflogin.html')





if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)