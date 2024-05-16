import telebot
import configure
import sqlite3
from telebot import types
import threading
from requests import get
from time import sleep
from texts import hello

client = telebot.TeleBot(configure.config['token'])
db = sqlite3.connect('baza.db', check_same_thread=False)
sql = db.cursor()
lock = threading.Lock()
#api = QApi(token=configure.config['tokenqiwi'], phone=configure.config['phoneqiwi'])
markdown = """
    *bold text*
    _italic text_
    [text](URL)
    """

#database

sql.execute("""CREATE TABLE IF NOT EXISTS users (id BIGINT, nick TEXT, cash INT, access INT, bought INT)""")
sql.execute("""CREATE TABLE IF NOT EXISTS shop (id INT, name TEXT, price INT, tovar TEXT, whobuy TEXT)""")
db.commit()

@client.message_handler(commands=['start'])
def start(message):
	try:
		getname = message.from_user.first_name
		cid = message.chat.id
		uid = message.from_user.id

		sql.execute(f"SELECT id FROM users WHERE id = {uid}")
		if sql.fetchone() is None:
			sql.execute(f"INSERT INTO users VALUES ({uid}, '{getname}', 0, 0, 0)")
			client.send_message(cid, f"🛒 | Добро пожаловать, {getname}! {hello} ")
			db.commit()
		else:
			client.send_message(cid, f"⛔️ | Ты уже зарегистрирован! Пропиши /help чтобы узнать команды.")
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['profile', 'myinfo', 'myprofile'])
def myprofile(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
		if getaccess == 0:
			accessname = 'Пользователь'
		elif getaccess == 1:
			accessname = 'Администратор'
		elif getaccess == 777:
			accessname = 'Разработчик'
		for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
			client.send_message(cid, f"*📇 | Твой профиль:*\n\n*👤 | Ваш ID:* {info[0]}\n*💸 | Баланс:* {info[2]} ₽\n*👑 | Уровень доступа:* {accessname}\n*🛒 | Куплено товаров:* {info[4]}\n\n*🗂 Чтобы посмотреть список купленных товаров напишите /mybuy*", parse_mode='Markdown')
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['users'])
def allusers(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
		accessquery = 1
		if getaccess < accessquery:
			client.send_message(cid, '⚠️ | У вас нет доступа!')
		else:
			text = '*🗃 | Список всех пользователей:*\n\n'
			idusernumber = 0
			for info in sql.execute(f"SELECT * FROM users"):
				if info[3] == 0:
					accessname = 'Пользователь'
				elif info[3] == 1:
					accessname = 'Администратор'
				elif info[3] == 777:
					accessname = 'Разработчик'
				idusernumber += 1
				text += f"*{idusernumber}. {info[0]} ({info[1]})*\n*💸 | Баланс:* {info[2]} ₽\n*👑 | Уровень доступа:* {accessname}\n*✉️ | Профиль:*" + f" [{info[1]}](tg://user?id="+str(info[0])+")\n\n"
			client.send_message(cid, f"{text}",parse_mode='Markdown')
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['mybuy'])
def mybuy(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		text = '*🗂 | Список купленных товаров:*\n\n'
		for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
			for infoshop in sql.execute(f"SELECT * FROM shop"):
				if str(info[0]) in infoshop[4]:
					text += f"*{infoshop[0]}. {infoshop[1]}*\nТовар: {infoshop[3]}\n\n"
		client.send_message(cid,f"{text}",parse_mode='Markdown',disable_web_page_preview=True)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['getprofile', 'info'])
def getprofile(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
		accessquery = 1
		if getaccess < accessquery:
			client.send_message(cid, '⚠️ | У вас нет доступа!')
		else:
			for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
				msg = client.send_message(cid, f'Введите ID пользователя:\nПример: {info[0]}')
				client.register_next_step_handler(msg, getprofile_next)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def getprofile_next(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			getprofileid = message.text
			for info in sql.execute(f"SELECT * FROM users WHERE id = {getprofileid}"):
				if info[3] == 0:
					accessname = 'Пользователь'
				elif info[3] == 1:
					accessname = 'Администратор'
				elif info[3] == 777:
					accessname = 'Разработчик'
				client.send_message(cid, f"*📇 | Профиль {info[1]}:*\n\n*ID пользователя:* {info[0]}\n*Баланс:* {info[2]} ₽\n*Уровень доступа:* {accessname}\n*Куплено товаров:* {info[4]}",parse_mode='Markdown')
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')


@client.message_handler(commands=['buy'])
def buy(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id

		text = '🛒 | *Список товаров*\n\n'
		for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
			for infoshop in sql.execute(f"SELECT * FROM shop"):
				text += f"{infoshop[0]}. {infoshop[1]}\nЦена: {infoshop[2]}\n\n"
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✅', callback_data='firstbuytovaryes')
			item_no = types.InlineKeyboardButton(text='❌', callback_data='firstbuytovarno')
			rmk.add(item_yes, item_no)
			msg = client.send_message(cid, f'{text}*Вы хотите перейти к покупке товара?*',parse_mode='Markdown',reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def buy_next(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global tovarid
			tovarid = int(message.text)
			for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
				for infoshop in sql.execute(f"SELECT * FROM shop WHERE id = {tovarid}"):
					if info[2] < infoshop[2]:
						client.send_message(cid, '⚠️ | У вас недостаточно средств для приобретения товара!\n\nЧтобы пополнить счёт напишите /donate')
					else:
						rmk = types.InlineKeyboardMarkup()
						item_yes = types.InlineKeyboardButton(text='✅',callback_data='buytovaryes')
						item_no = types.InlineKeyboardButton(text='❌',callback_data='buytovarno')
						rmk.add(item_yes, item_no)
						msg = client.send_message(cid, f"💸 | Вы подверждаете покупку товара?\n\nВернуть средства за данный товар НЕВОЗМОЖНО.",reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(lambda call: call.data == 'firstbuytovaryes' or call.data == 'firstbuytovarno')
def firstbuy_callback(call):
	try:
		if call.data == 'firstbuytovaryes':
			msg = client.send_message(call.message.chat.id, f"*Введите ID товара который хотите купить:*",parse_mode='Markdown')
			client.register_next_step_handler(msg, buy_next)
		elif call.data == 'firstbuytovarno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"🚫 | Вы отменили покупку товара")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')


@client.callback_query_handler(lambda call: call.data == 'buytovaryes' or call.data == 'buytovarno')
def buy_callback(call):
	try:
		if call.data == 'buytovaryes':
			for info in sql.execute(f"SELECT * FROM users WHERE id = {call.from_user.id}"):
				for infoshop in sql.execute(f"SELECT * FROM shop WHERE id = {tovarid}"):
						cashtovar = int(info[2] - infoshop[2])
						boughttovar = int(info[4] + 1)
						whobuytovarinttostr = str(info[0])
						whobuytovar = str(infoshop[4] + whobuytovarinttostr + ',')
						sql.execute(f"SELECT * FROM users WHERE id = {call.from_user.id}")
						client.delete_message(call.message.chat.id, call.message.message_id-0)
						client.send_message(call.message.chat.id, f"✅ | Вы успешно купили товар\n\nНазвание товара: {infoshop[1]}\nЦена: {infoshop[2]}\n\nКомментарий🎀: Сейчас с Вами свяжется администратор и выдаст Вам товар\n\nСпасибо за покупку!")
						client.send_message(1426198031,f"✉️ | Пользователь {getusername} оплатил товар : {infoshop[0]}\nЦена: {infoshop[1]}.")
						sql.execute(f"UPDATE users SET cash = {cashtovar} WHERE id = {call.from_user.id}")
						sql.execute(f"UPDATE users SET bought = {boughttovar} WHERE id = {call.from_user.id}")
						sql.execute(f"SELECT * FROM shop WHERE id = {tovarid}")
						sql.execute(f"UPDATE shop SET whobuy = '{whobuytovar}' WHERE id = {tovarid}")
						db.commit()
		elif call.data == 'buytovarno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"❌ | Вы отменили покупку товара!")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['donate'])
def donate(message):
	try:
		cid = message.chat.id
		global uid
		uid = message.from_user.id
		msg = client.send_message(cid, f"*💰 | Введите сумму для пополнения:*",parse_mode='Markdown')
		client.register_next_step_handler(msg, donate_value)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def donate_value(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global donatevalue
			global commentdonate
			global getusername
			global getuserdonateid
			getusername = message.from_user.first_name
			getuserdonateid = message.from_user.id
			sql.execute(f"SELECT * FROM users WHERE id = {uid}")
			commentdonate = sql.fetchone()[0]
			donatevalue = int(message.text)
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✅',callback_data='donateyes')
			item_no = types.InlineKeyboardButton(text='❌',callback_data='donateno')
			rmk.add(item_yes, item_no)
			msg = client.send_message(cid, f"🔰 | Заявка на пополнение средств успешно создана\n\nВы действительно хотите пополнить средства?",parse_mode='Markdown',reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def donateyesoplacheno(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		removekeyboard = types.ReplyKeyboardRemove()
		if message.text == '✅ Оплачено':
			client.send_message(cid, f"✉️ | Ваш запрос отправлен администраторам, ожидайте одобрения и выдачи средств.",reply_markup=removekeyboard)
			client.send_message(1426198031, f"✉️ | Пользователь {getusername} оплатил заявку на пополнение средств\n\nID пользователя: {getuserdonateid}\nСумма: {donatevalue}₽\nКомментарий: {commentdonate}\n\nПерепроверьте верность оплаты затем подтвердите выдачу средств.")
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(lambda call: call.data == 'donateyes' or call.data == 'donateno')
def donate_result(call):
	try:
		removekeyboard = types.ReplyKeyboardRemove()
		rmk = types.ReplyKeyboardMarkup(resize_keyboard=True)
		rmk.add(types.KeyboardButton('✅ Оплачено'))
		if call.data == 'donateyes':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			msg = client.send_message(call.message.chat.id, f"➖➖➖➖➖➖➖➖➖➖➖➖\n☎️ Карта для оплаты: 2202 2023 5769 1728 \n💰 Сумма: {donatevalue}₽\n💭 Комментарий: {commentdonate}\n*⚠️ВАЖНО⚠️* Комментарий и сумма должны быть *1в1*\n➖➖➖➖➖➖➖➖➖➖➖➖",parse_mode='Markdown',reply_markup=rmk)
			client.register_next_step_handler(msg, donateyesoplacheno)
		elif call.data == 'donateno':
			client.send_message(call.message.chat.id, f"❌ | Вы отменили заявку на пополнение средств",reply_markup=removekeyboard)
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['getcid'])
def getcid(message):
	client.send_message(message.chat.id, f"ID чата | {message.chat.id}\nТвой ID | {message.from_user.id}")

@client.message_handler(commands=['help'])
def helpcmd(message):
	cid = message.chat.id
	uid = message.from_user.id
	with lock:
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
	if getaccess >= 1:
		client.send_message(cid, '*Помощь по командам:*\n\n/profile - Посмотреть свой профиль\n/help - Посмотреть список команд\n/buy - Купить товар\n/donate - Пополнить счёт\n/mybuy - Посмотреть список купленных товаров\n/teh - Связаться с тех.поддержкой\n\nАдмин-команды:\n\n/ot - Ответить пользователю (отправить сообщение)',parse_mode='Markdown')
	else:
		client.send_message(cid, '*Помощь по командам:*\n\n/profile - Посмотреть свой профиль\n/help - Посмотреть список команд\n/buy - Купить товар\n/donate - Пополнить счёт\n/mybuy - Посмотреть список купленных товаров\n/teh - Связаться с тех.поддержкой',parse_mode='Markdown')


@client.message_handler(commands=['teh'])
def teh(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		msg = client.send_message(cid, f"*📨 | Введите текст который хотите отправить тех.поддержке*",parse_mode='Markdown')
		client.register_next_step_handler(msg, teh_next)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def teh_next(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			global tehtextbyuser
			global tehnamebyuser
			global tehidbyuser
			tehidbyuser = int(message.from_user.id)
			tehnamebyuser = str(message.from_user.first_name)
			tehtextbyuser = str(message.text)
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✉️',callback_data='tehsend')
			item_no = types.InlineKeyboardButton(text='❌',callback_data='tehno')
			rmk.add(item_yes, item_no)
			msg = client.send_message(cid, f"✉️ | Данные об отправке:\n\nТекст для отправки: {tehtextbyuser}\n\nВы действительно хотите отправить это тех.поддержке?",parse_mode='Markdown',reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(func=lambda call: call.data == 'tehsend' or call.data == 'tehno')
def teh_callback(call):
	try:
		if call.data == 'tehsend':
			for info in sql.execute(f"SELECT * FROM users WHERE id = {call.from_user.id}"):
				client.delete_message(call.message.chat.id, call.message.message_id-0)
				client.send_message(call.message.chat.id, f"✉️ | Ваше сообщение отправлено тех.поддержке, ожидайте ответа.")
				client.send_message(1426198031, f"✉️ | Пользователь {tehnamebyuser} отправил сообщение в тех.поддержку\n\nID пользователя: {tehidbyuser}\nТекст: {tehtextbyuser}\n\nЧтобы ответить пользователю напишите /ot")
		elif call.data == 'tehno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"🚫 | Вы отменили отправку сообщения тех.поддержке")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['ot'])
def sendmsgtouser(message):
	try:
		cid = message.chat.id

		msg = client.send_message(cid, f"👤 | Введите ID пользователя которому хотите отправить сообщение:")
		client.register_next_step_handler(msg, sendmsgtouser_next)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def sendmsgtouser_next(message):
	try:
		cid = message.chat.id

		if message.text == message.text:
			global getsendmsgtouserid
			getsendmsgtouserid = int(message.text)
			msg = client.send_message(cid, f"📨 | Введите текст который хотите отправить пользователю:")
			client.register_next_step_handler(msg, sendmsgtouser_next_text)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def sendmsgtouser_next_text(message):
	try:
		cid = message.chat.id

		if message.text == message.text:
			global getsendmsgtousertext
			getsendmsgtousertext = str(message.text)
			rmk = types.InlineKeyboardMarkup()
			item_yes = types.InlineKeyboardButton(text='✅',callback_data='sendmsgtouseryes')
			item_no = types.InlineKeyboardButton(text='❌',callback_data='sendmsgtouserno')
			rmk.add(item_yes, item_no)
			msg = client.send_message(cid, f"🔰 | Данные об отправке сообщения:\n\nID пользователя: {getsendmsgtouserid}\nТекст для отправки: {getsendmsgtousertext}\n\nОтправить сообщение?",reply_markup=rmk)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.callback_query_handler(func=lambda call: call.data == 'sendmsgtouseryes' or call.data == 'sendmsgtouserno')
def sendmsgtouser_callback(call):
	try:
		if call.data == 'sendmsgtouseryes':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"✉️ | Сообщение отправлено!")
			client.send_message(getsendmsgtouserid, f"✉️ | Администратор прислал вам сообщение:\n\n{getsendmsgtousertext}")
		elif call.data == 'sendmsgtouserno':
			client.delete_message(call.message.chat.id, call.message.message_id-0)
			client.send_message(call.message.chat.id, f"🚫 | Вы отменили отправку сообщения пользователю")
		client.answer_callback_query(callback_query_id=call.id)
	except:
		client.send_message(call.message.chat.id, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['getid'])
def getiduser(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
		accessquery = 1
		if getaccess < accessquery:
			client.send_message(cid, f"⚠️ | У вас нет доступа!")
		else:
			msg = client.send_message(cid, 'Введите никнейм пользователя:')
			client.register_next_step_handler(msg, next_getiduser_name)
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

def next_getiduser_name(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		if message.text == message.text:
			getusername = message.text
			sql.execute(f"SELECT * FROM users WHERE nick = '{getusername}'")
			result = sql.fetchone()[0]
			client.send_message(cid, f'👤 | ID пользователя: {result}')
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')



client.polling(none_stop=True,interval=0)