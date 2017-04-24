# -*- coding: utf-8 -*-

#--------------------------------------- AUTHORS ------------------------------------------------------------------------
# Javier Villarreal Rodríguez
# Christian González Jiménez


#--------------------------------------- DESCRIPTION --------------------------------------------------------------------

# This bot was programed for a Smartcities Proyect in UCM at 2017. This will be available in @smartcityoverseer_bot

#--------------------------------------- END DESCRIPTION ----------------------------------------------------------------

# -------------------------------------- LIBRARIES ----------------------------------------------------------------------
import telebot
import pyemtmad
import math
import sys
from pymongo import MongoClient
from pyemtmad import Wrapper
from pyemtmad import util
from pyemtmad import types as emt #set types of emt with alias emt
import datetime
#-------------------------------------- END LIBRARIES IMPORT ------------------------------------------------------------

#-------------------------------------- VARIABLES -----------------------------------------------------------------------

now = datetime.datetime.now().strftime('%d/%m/%Y') # set the now date
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d/%-m/%Y') #set the yesterday date
uri = "YOUR URI" #set the uri of server with mongodbprocess for smartcitydata
TOKEN = 'YOUR BOT FATHER TOKEN' # Token of the bot generated at @BotFather in Telegram
bot = telebot.TeleBot(TOKEN) #Create the instance of the bot token

#-------------------------------------- END VARIABLES -------------------------------------------------------------------

#-------------------------------------- DICTIONARIES OF THE NOISE AND AIR STATIONS --------------------------------------

stations = {'1': '035', '2':'004','3':'039', '4':'008', '5':'038', '6':'011', '7':'040','8':'016','9':'017','10':'018','11':'036','12':'024','13':'027','14':'047','15':'048','16':'049','17':'050','18':'054','19':'055','20':'056','21':'057','22':'058','23':'059','24':'060'}
stationsn = {'1': '035', '2':'004','3':'039', '4':'008', '5':'038', '6':'011', '7':'040','8':'016','9':'017','10':'018','11':'036','12':'024','13':'027','14':'047','15':'048','16':'049','17':'050','18':'054','19':'055','20':'056','21':'057','22':'058','23':'059','24':'060'}

#-------------------------------------- END DICTIONARIES ----------------------------------------------------------------


#-------------------------------------- LISTENER ------------------------------------------------------------------------
def listener(messages): #create the listener for take the message and print this message
	for message in messages:
		cid = message.chat.id
		print("[" + str(cid) + "]: " + str(message.text))

bot.set_update_listener(listener)#set the listener
def extract_unique_code(text):
	return text.split()[1] if len(text.split()) > 1 else None

#--------------------------------------END LISTENER ---------------------------------------------------------------------


#-------------------------------------- COMMANDS ------------------------------------------------------------------------
# Description:
#	start - Start the bot
#	info - Send the info of the bot

# Handler '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
	unique_code=extract_unique_code(message.text)#code of the telegram user
	cid = message.chat.id # Save de id for the reply
	print (unique_code) #print the code in console
	bot.send_message(cid, "Welcome message") #send action for reply /start
	main_keyboard(cid) #Go to main_keyboard function

#Handler /info
@bot.message_handler(commands=['info'])
def send_info(message):
	unique_code=extract_unique_code(message.text)
	cid = message.chat.id 
	print (unique_code)
	bot.send_message(cid, "info message") #send action for reply /info

#-------------------------------------- END COMMANDS --------------------------------------------------------------------

#-------------------------------------- MAIN KEYBOARD -------------------------------------------------------------------

def main_keyboard(cid):#Keyboard function for display the keyboard in the bot
	markup = telebot.types.ReplyKeyboardRemove(selective=False)#set keyboard selective
	markup = telebot.types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=True)#set keyboard dimensions
	markup.add('Estado del aire','Farmacias de guardia')#add one row of options
	markup.add('Ruido de la ciudad','Incidencias')
	markup.add('Eventos','Paradas EMT')
	msg = bot.send_message(cid, "Selecciona una acción: ", reply_markup=markup)#send the message with the keyboard to the user

#-------------------------------------- END MAIN KEYBOARD ----------------------------------------------------------------


#-------------------------------------- AIR FUNCTIONS --------------------------------------------------------------------

@bot.message_handler(func=lambda message: message.text == "Estado del aire")#handler to detect the "Estado del aire" option
def air_pollution(message):#Function to display the options of air pollution
	unique_code=extract_unique_code(message.text)
	cid=message.chat.id
	bot.send_message(cid, "1 - Pza. del Carmen\n2 - Pza. de España\n3 - Barrio del Pilar\n4 - Escuelas Aguirre\n5 - Cuatro Caminos\n6 - Av. Ramón y Cajal\n7 - Vallecas\
		\n8 - Arturo Soria\n9 - Villaverde Alto\n10 - C/Farolillo\n11 - Moratalaz\n12 - Casa de Campo\n13 - Barajas\n14 - Méndez Álvaro\n15 - Pº. Castellana\n16 - Retiro\
		\n17 - Pza. Castilla\n18 - Ensanche de Vallecas\n19 - Urb. Embajada(Barajas)\n20 - Pza. Fdez.Ladrea\n21 - Sanchinarro\n22 - El Pardo\n23 - Parque Juan Carlos 1\
		\n24 - Tres Olivos")#send the options to user
	markup = telebot.types.ReplyKeyboardRemove(selective=False)
	markup = telebot.types.ReplyKeyboardMarkup(row_width=6,one_time_keyboard=True)	
	markup.add('1','2','3','4','5','6')
	markup.add('7','8','9','10','11','12')
	markup.add('13','14','15','16','17','18')
	markup.add('19','20','21','22','23','24')
	msg = bot.send_message(cid, "Selecciona una estación: ", reply_markup=markup)
	bot.register_next_step_handler( msg, air_query)#register the next function handler for this option

def air_query(message):#function for query at the DB
	cid = message.chat.id
	db = MongoClient(uri) #DB connection
	try:
		id = stations[message.text]+","+ now + ",01"
		result = db.smartcity["air_pollution"].find({"_id" : id })
		array = []
		for query in result:
			for i in range(1,25):
				array.append("hour" + str(i) + ":  " + query["values"]["hour"+str(i)] + " NO2")
		if(len(array) > 0):
			result_message= "\n".join(array)
		else:
			result_message= "No hay información asociada a esa estación"
		bot.send_message(cid,result_message)
	except:
		msg = bot.send_message(cid,'La estación no está activa o no existe.')
	main_keyboard(cid)

#-------------------------------------- END AIR FUNCTIONS --------------------------------------------------------------

#-------------------------------------- CHEMIST FUNCTION ---------------------------------------------------------------
@bot.message_handler(func=lambda message: message.text == "Farmacias de guardia")
def farmacias(message):
	unique_code=extract_unique_code(message.text)
	cid = message.chat.id
	db = MongoClient(uri) #DB connection
	result = db.smartcity["chemists"].find()
	for event in result:
		date = event["_id"].split(',')[1]
		today = datetime.datetime.now().strftime('%d/%m/%Y')

		if date == today:
			direction = event["direction"] if event["direction"] is not None else " "
			timetable = event["timetable"] if event["timetable"] is not None else " "
			phone = event["phone"] if event["phone"] is not None else " "
			msg = bot.send_message(cid,"Ubicada en " + direction + " con horario de " + timetable + " y telefono " + phone ) 
	main_keyboard(cid)
	
#-------------------------------------- END CHEMIST FUNCTION ------------------------------------------------------------

#-------------------------------------- EVENTS FUNCTION -----------------------------------------------------------------
@bot.message_handler(func=lambda message: message.text == "Eventos")
def eventos(message):
	unique_code=extract_unique_code(message.text)
	cid = message.chat.id
	db = MongoClient(uri) #DB connection
	result = db.smartcity["events"].find() #save the query result in result
	for event in result:
		dateIni = datetime.datetime.strptime(event["dateIni"],'%Y-%m-%d %H:%M:%S.%f')
		dateFin = datetime.datetime.strptime(event["dateFin"],'%Y-%m-%d %H:%M:%S.%f')
		if((dateIni in (datetime.datetime.now(),datetime.datetime.now()+datetime.timedelta(days=7))) or (dateFin in (datetime.datetime.now(),datetime.datetime.now()+datetime.timedelta(days=7))) or ((dateIni <= datetime.datetime.now()) and (dateFin >= datetime.datetime.now()+datetime.timedelta(days=7)))):
			title = event["title"] if event["title"] is not None else " "
			ini = dateIni.strftime('%d/%m/%Y') if dateIni.strftime('%d/%m/%Y') is not None else " "
			fin = dateFin.strftime('%d/%m/%Y') if dateFin.strftime('%d/%m/%Y') is not None else " "
			instalation = event["instalation"] if event["instalation"] is not None else " "
			msg = bot.send_message(cid,title + " en " + instalation + " " + ini + " - " + fin ) 
	main_keyboard(cid)
#-------------------------------------- END EVENTS FUNCTION ------------------------------------------------------------

#-------------------------------------- EMT BUS FUNCTION ---------------------------------------------------------------
@bot.message_handler(func=lambda message: message.text == "Paradas EMT")
def EMT(message):
	unique_code=extract_unique_code(message.text)
	cid = message.chat.id
	msg=bot.send_message(cid, "Introduce tu número de parada a consultar: ")
	bot.register_next_step_handler( msg, EMT_query)	
	
def EMT_query(message):
	unique_code=extract_unique_code(message.text)
	cid = message.chat.id
	ARGS =  { 'stop_number' : message.text, 'lang' : 'es' }
	wrapper = Wrapper('WEB.SERV.EMT ACCOUNT', 'EMT TOKEN')
	arrival_info =  wrapper.geo.get_arrive_stop(**ARGS)[1]
	
	try:
		for emt.row in arrival_info:
			time = emt.row.time_left/60
			minutes = math.floor(time)
			diference = time - minutes
			seconds = round(diference*60)
			if(minutes <= 20):
				msg = bot.send_message(cid,'%s %s - %i minutes %i seconds - %f,%f' % (emt.row.line_id, emt.row.destination, minutes, seconds, emt.row.latitude, emt.row.longitude))	
			else:
				msg = bot.send_message(cid,'%s %s - +20 minutes - %f,%f' % (emt.row.line_id, emt.row.destination, emt.row.latitude, emt.row.longitude))
	except:
		msg = bot.send_message(cid,'La parada no está activa o no existe')
	main_keyboard(cid)


#-------------------------------------- END EMT BUS FUNCTIOn --------------------------------------------------------



#-------------------------------------- NOISE FUNCTIONS --------------------------------------------------------------

@bot.message_handler(func=lambda message: message.text == "Ruido de la ciudad")
def noise_pollution(message):
	unique_code=extract_unique_code(message.text)
	cid = message.chat.id
	bot.send_message(cid, "1 - Pza. del Carmen\n2 - Pza. de España\n3 - Barrio del Pilar\n4 - Escuelas Aguirre\n5 - Cuatro Caminos\n6 - Av. Ramón y Cajal\n7 - Vallecas\
		\n8 - Arturo Soria\n9 - Villaverde Alto\n10 - C/Farolillo\n11 - Moratalaz\n12 - Casa de Campo\n13 - Barajas\n14 - Méndez Álvaro\n15 - Pº. Castellana\n16 - Retiro\
		\n17 - Pza. Castilla\n18 - Ensanche de Vallecas\n19 - Urb. Embajada(Barajas)\n20 - Pza. Fdez.Ladrea\n21 - Sanchinarro\n22 - El Pardo\n23 - Parque Juan Carlos 1\
		\n24 - Tres Olivos")#send the options to user
	markup = telebot.types.ReplyKeyboardRemove(selective=False)
	markup = telebot.types.ReplyKeyboardMarkup(row_width=6,one_time_keyboard=True)	
	markup.add('1','2','3','4','5','6')
	markup.add('7','8','9','10','11','12')
	markup.add('13','14','15','16','17','18')
	markup.add('19','20','21','22','23','24')
	msg = bot.send_message(cid, "Selecciona una estación: ", reply_markup=markup)
	bot.register_next_step_handler( msg, noise_query)	

def noise_query(message):
	cid = message.chat.id
	db = MongoClient(uri) #DB connection
	try:
		id = stationsn[message.text]+","+ yesterday+",T"
		result = db.smartcity["noise_pollution"].find({"_id" : id }) #save the query result in result

		array = []
		for query in result:
			array.append("Value total:  " + query["values"]["las1"] + " dB")
		if(len(array) > 0):
			result_message= "\n".join(array)
		else:
			result_message= "No hay información asociada a esa estación"
		bot.send_message(cid,result_message)
	except:
		msg = bot.send_message(cid,'La estación no está activa o no existe.')
	main_keyboard(cid)

#-------------------------------------- END NOISE FUNCTIONS ----------------------------------------------------------

#-------------------------------------- INCIDENTS FUNCTION -----------------------------------------------------------

@bot.message_handler(func=lambda message: message.text == "Incidencias")
def incidents(message):
	unique_code=extract_unique_code(message.text)
	cid = message.chat.id
	db = MongoClient(uri) #DB connection
	result = db.smartcity["incidents_publicroad"].find() #save the query result in result
	for event in result:
		dateIni = datetime.datetime.strptime(event["fechaini"][:19],'%Y-%m-%dT%H:%M:%S')
		dateFin = datetime.datetime.strptime(event["fechafin"][:19],'%Y-%m-%dT%H:%M:%S')
		if((dateIni in (datetime.datetime.now(),datetime.datetime.now()+datetime.timedelta(days=7))) or (dateFin in (datetime.datetime.now(),datetime.datetime.now()+datetime.timedelta(days=7))) or ((dateIni <= datetime.datetime.now()) and (dateFin >= datetime.datetime.now()+datetime.timedelta(days=7)))):
			msg = bot.send_message(cid,event["description"] + " " + dateIni.strftime('%d/%m/%Y') + " - " + dateFin.strftime('%d/%m/%Y'))
	main_keyboard(cid)

#-------------------------------------- END INCIDENTS FUNCTION -------------------------------------------------------

bot.polling( none_stop = True)#bot active always
