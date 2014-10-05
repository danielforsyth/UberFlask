from flask import Flask, render_template, request, url_for
import requests
import urllib2
import json 
import datetime

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form_submit.html')

@app.route('/estimate/', methods=['POST'])
def get_estimate():

    #Retrieve addresses from form
    start_address=request.form['address1']
    end_address=request.form['address2']
    short_address = short_address = [x.strip() for x in end_address.split(',')]
    short_address = short_address[0]

    #Strip whitespace for use with google maps api
    stripped_start_address = start_address.replace(" ", "+")
    stripped_end_address = end_address.replace(" ", "+")

    #retrieve coordinates from google maps api
    start_address_url="http://maps.googleapis.com/maps/api/geocode/json?address=%s" % stripped_start_address
    end_address_url="http://maps.googleapis.com/maps/api/geocode/json?address=%s" % stripped_end_address

    start_response = urllib2.urlopen(start_address_url)
    end_response = urllib2.urlopen(end_address_url)
    jsonstart = start_response.read()
    jsonend = end_response.read()

    start_obj= json.loads(jsonstart)    
    start_coordinate = [start_obj['results'][0]['geometry']['location']['lat'],start_obj['results'][0]['geometry']['location']['lng']]
    
    end_obj = json.loads(jsonend)
    end_coordinate = [end_obj['results'][0]['geometry']['location']['lat'],end_obj['results'][0]['geometry']['location']['lng']]
    
    #connect to Uber price API and request price data with given
    #coordinates
    price_url = 'https://api.uber.com/v1/estimates/price'

    price_parameters = {
	'server_token': '',
    'start_latitude': start_coordinate[0],
    'start_longitude': start_coordinate[1],
    'end_latitude': end_coordinate[0],
    'end_longitude':  end_coordinate[1],}

    response = requests.get(price_url,params=price_parameters)

    price_data = response.json()

    clean_price = str(price_data['prices'][0]['estimate'])


    # Same with time data
    time_url = 'https://api.uber.com/v1/estimates/time'

    time_parameters = {
    'server_token': '',
    'start_latitude': start_coordinate[0],
    'start_longitude': start_coordinate[1],
    }

    response = requests.get(time_url,params=time_parameters)

    time_data = response.json()

    vehicle_one = time_data['times'][0]['display_name']
    vehicle_two = time_data['times'][1]['display_name']

    estimate_one = time_data['times'][0]['estimate']
    estimate_two = time_data['times'][1]['estimate']

    time_estimate1 = str(datetime.timedelta(seconds=estimate_one))
    time_estimate2 = str(datetime.timedelta(seconds=estimate_two))


    # clean_time = time_data


    #Return Data to new form
    return render_template('form_action.html',end_address = short_address,
         price_estimate=clean_price,
        time_estimate = time_estimate1)

# Run the app 
if __name__ == '__main__':
	app.run(debug=True)