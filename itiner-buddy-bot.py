# Discord Bot - Itiner-Buddy-Bot
import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import datetime
import calendar
import sqlite3
import datetime as dt
from datetime import datetime
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = '!', case_insensitive=True,intents = intents, help_command=None)
bot_ID = 946553474651422761
currentReminderTime = ""
bot_token = '' # Hidden.

# Discord member ID will be stored into the SQLite Database once a discord member joins the server
@bot.event
async def on_member_join(member):
	await member.send('Welcome! I am Itenier-buddy-bot. All commands start with "!". Type "!help" for more instructions.') # greeting
	db = sqlite3.connect('itinerBuddyDB.sqlite')
	cursor = db.cursor()
	cursor.execute(f"INSERT INTO User (u_id) VALUES ({member.id});") # store memeber.id into User table
	db.commit()
	cursor.close()
	db.close()

@bot.command()
async def addMember(ctx, arg):
	print("addMember...")
	foundMember = False 
	async for member in ctx.guild.fetch_members(limit=150):
		if(member.name == arg):
			db = sqlite3.connect('itinerBuddyDB.sqlite')
			cursor = db.cursor()
			cursor.execute(f"INSERT INTO User (u_id) VALUES ({member.id});") # store memeber.id into User table
			db.commit()
			cursor.close()
			db.close()
			foundMember = True
	if foundMember == False:
		await ctx.send("Couldn't find member whose username is " + str(arg))

@bot.event
async def on_ready():
	checkingTimeEveryMinute.start()
	print('Bot is ready.')

# Helper function
# Run every minute to check if there is a meeting reminder set for the current time
# It will send a reminder to the server if needed
@tasks.loop(minutes=1)
async def checkingTimeEveryMinute():
	global currentReminderTime
	# channel = bot.get_channel(808787148647301210)
	channel = bot.get_channel(946571910425223211)
	dt_now = dt.datetime.now()
	hhmm = dt_now.strftime("%H:%M")
	print(str(hhmm[1:]))
	db = sqlite3.connect("itinerBuddyDB.sqlite")
	cursor = db.cursor()
	cursor.execute("SELECT m_id, m_start_time, m_reminder FROM Meeting_Info")
	meetings = cursor.fetchall()
	for meeting in meetings:
		if str(meeting[2]) == str(hhmm[1:]):
			await channel.send("This is a reminder for all members in meeting " + str(meeting[0]) + " start at " + str(meeting[1]) + ".")

# Helper function
# Checks if a member is holding the team manager role
# Asks the member to request the role if needed
# It will be run whenever a member tries to create, delete, update meetings, sets reminder, and gives the team manager role to another member.
async def checkIfTeamManager(ctx, messageSenderID):
	matchedRole = False
	
	for role in ctx.author.roles:
		print(role.name)
		if role.name == "Itiner-Buddy: Team Manager":
			matchedRole = True
		
	if matchedRole:
		return True
	else:
		await ctx.send("This command can't be called since you don't have the Itiner-Buddy: Team Manager role")
	
	while(True):
		await ctx.send("Would you like to ask for the role. yes/no or y/n")
		def check(msg):
			return msg.author == ctx.author and msg.channel == ctx.channel
		msg = await bot.wait_for("message", check = check)

		feedback = str(msg.content)
		print(feedback)
		
		if ((feedback.find("yes") != -1) | (feedback.find("y") != -1)):
			mentionRole = discord.utils.get(ctx.guild.roles,name="Itiner-Buddy: Team Manager")
			await ctx.send (mentionRole.mention + " " + msg.author.name + " would like to become a Team Manager.")
			break
		elif ((feedback.find("no") != -1) | (feedback.find("n") != -1)):
			await ctx.send ( "Understood.")
			break

# Set a reminder for a meeting with an amount of time before the meeting starts
# Syntax: !setReminder <Meeting ID>
# Note:
#	Only a team manager is allowed to set a reminder for a meeting
#	Users will be asked to pick an amount of time from given options
@bot.command()
async def setReminder(ctx, m_id):
	global currentReminderTime
	if await checkIfTeamManager(ctx, ctx.message.author.id) == True:
		if m_id.isnumeric() == False:
			await ctx.send(str(m_id) + " is not a number. Please provide the meeting's ID to set a reminder.")
			await ctx.send("You can find the meeting's ID using the ViewMeetings command.")
		else:
			bot_test2_channel = bot.get_channel(bot_ID)
			db = sqlite3.connect("itinerBuddyDB.sqlite")
			cursor = db.cursor()
			cursor.execute(f"SELECT * FROM Meeting_Info WHERE m_id = {m_id}")
			meetingRow = cursor.fetchone()
			if meetingRow == []:
				await ctx.send("Meeting cannot be found with number provided.")
				await ctx.send("You can find the meeting's ID using the ViewMeetings command.")
			else:
				await ctx.send("Setting reminder for meeting named: **" + meetingRow[2] + "**")
				await ctx.send("Reminder will send a notification to all meeting participants at X amount of time before the meeting.")
				await ctx.send("Currently the meeting is set to start at " + meetingRow[4] + " on " + meetingRow[3] + "\n_")
				await ctx.send("**Please select the time of reminder: 24hr, 12hr, 5hr, 1hr, 30mins, 15mins, 10min**")
				def check(msg):
					return msg.author == ctx.author and msg.channel == ctx.channel and msg.content in ["24hr","12hr", "5hr","1hr", "30mins", "15mins", "10min"]
				msg = await bot.wait_for("message", check = check)
				if msg.content == "1hr":
					time = "1:00"
					feedBack = "1 hour reminder was set. See you soon, space cowboy!"
				elif msg.content == "24hr":
					time = "24:00"
					feedBack = "24 hour reminder was set. See you soon, space cowboy!"
				elif msg.content == "12hr":
					time = "12:00"
					feedBack = "12 hour reminder was set. See you soon, space cowboy!"
				elif msg.content == "5hr":
					time = "5:00"
					feedBack = "5 hour reminder was set. See you soon, space cowboy!"
				elif msg.content == "30mins":
					time = "0:30"
					feedBack = "30 minutes reminder was set. See you soon, space cowboy!"
				elif msg.content == "15mins":
					time = "0:15"
					feedBack = "15 minutes reminder was set. See you soon, space cowboy!"
				elif msg.content == "10min":
					time = "0:10"
					feedBack = "10 minutes reminder was set. See you soon, space cowboy!"
				format = "%H:%M"
				if meetingRow[4] < time:
					await ctx.send("Reminder cannot be set since reminders cannot be set on a different day. Please redo command and select another time.")
				else:
					currentReminderTime = str(datetime.strptime(str(meetingRow[4]), format) - datetime.strptime(time, format))
					print(currentReminderTime[:-3])
					await checkingTimeEveryMinute()
					await ctx.send("Starting Time of this meeting is " + str(meetingRow[4]))
					await ctx.send("Reminder will appear at " + currentReminderTime[:-3] + " on " + str(meetingRow[3]))
					await ctx.send("Current time is " + str(dt.datetime.now())[11:16])
					await ctx.send(feedBack)
				cursor.execute("""UPDATE Meeting_Info SET m_reminder = ? WHERE m_id = ?;""", (currentReminderTime[:-3], m_id))
				db.commit()
				cursor.close()
				db.close()

# Gives the team manager role to a member
# Syntax: !applyRole <USERNAME>
# Note: Only a team manager is allowed to give the team manager role to another member
@bot.command()
async def applyRole(ctx, arg):
	foundMember = False 

	if await checkIfTeamManager(ctx, ctx.message.author.id) == True:
		async for member in ctx.guild.fetch_members(limit=150):
			if(member.name == arg):
				foundMember = True
				await member.add_roles(discord.utils.get(ctx.guild.roles,name="Itiner-Buddy: Team Manager"))
				await ctx.send(member.name + " is now a **Itiner-Buddy: Team Manager**")
		
		if foundMember == False:
			await ctx.send("Couldn't find member whose username is " + str(arg))
			await ctx.send("Be sure to use the member's username rather than nickname.")	

# Create a meeting
# Syntax: !createMeeting <Title: "(text)"> <Date: YYYY-MM-DD>
# Note: 
#	Time is not required to set at this point
#	Only a team manager is allowed to create a meeting
# Return: Meeting ID created
@bot.command()
async def createMeeting(ctx, title, date):
	if await checkIfTeamManager(ctx, ctx.message.author.id) == True:
		print(ctx.author.id)
		db = sqlite3.connect('itinerBuddyDB.sqlite')
		cursor = db.cursor()
		cursor.execute(f"SELECT COUNT(m_id) FROM Meeting_Info")
		rowCountBeforehand = cursor.fetchone()
		# m_id will be auto-increamented.
		cursor.execute(f"INSERT INTO Meeting_Info (host_id, m_title, m_date) VALUES (?, ?, ?);", (ctx.author.id, title, date))
		cursor.execute(f"SELECT COUNT(m_id) FROM Meeting_Info")
		rowCountAfterhand = cursor.fetchone()
		if rowCountAfterhand > rowCountBeforehand:
			cursor.execute(f"SELECT m_id FROM Meeting_Info WHERE m_id = (SELECT MAX(m_id) FROM Meeting_Info)")
			meetingID = cursor.fetchone()
			await ctx.send('Meeting created. Your meeting ID is {}'.format(meetingID[0]))
		else:
			await ctx.send('Failed to create. Please try again.')
		db.commit()
		cursor.close()
		db.close()

# Deletes a meeting
# Syntax: !deleteMeeting <Meeting ID: text(Int)>
# Note: Only the host of the meeting ID is allowed to delete the meeting
@bot.command()
async def deleteMeeting(ctx, mid):
	if await checkIfTeamManager(ctx, ctx.message.author.id) == True:
		db = sqlite3.connect('itinerBuddyDB.sqlite')
		cursor = db.cursor()
		cursor.execute("""SELECT host_id FROM Meeting_Info WHERE m_id = ?;""", mid)
		result = cursor.fetchone()
		if int(result[0]) == ctx.message.author.id:
			cursor.execute(f"SELECT COUNT(m_id) FROM Meeting_Info")
			rowCountBeforehand = cursor.fetchone()
			# Delete records with m_id from Meeting_Info
			cursor.execute(f"DELETE FROM Meeting_Info WHERE m_id = ?", (mid))
			cursor.execute(f"SELECT COUNT(m_id) FROM Meeting_Info")
			rowCountAfterhand = cursor.fetchone()
			if rowCountAfterhand[0] < rowCountBeforehand[0]:
				# Delete records with m_id from Meeting_scheduled 
				cursor.execute(f"DELETE FROM Meeting_scheduled WHERE m_id = ?", (mid))
				cursor.execute(f"SELECT COUNT(m_id) FROM Meeting_scheduled WHERE m_id = ?", (mid))
				rowCountAfterhand = cursor.fetchone()
				if rowCountAfterhand[0] == 0:
					await ctx.send('Meeting (ID={}) is deleted(canceled).'.format(mid))	
			else:
				await ctx.send('Failed to delete. Please try again.')
		db.commit()
		cursor.close()
		db.close()

# Update the title of a meeting
# Syntax: !updateMeetingTitle <Meeting ID: text(Int)> <title: "(text)">
# Note: Only the host of the meeting ID is allowed to delete the meeting
@bot.command()
async def updateMeetingTitle(ctx, mid, change):
	db = sqlite3.connect("itinerBuddyDB.sqlite")
	cursor = db.cursor()
	cursor.execute("""SELECT host_id FROM Meeting_Info WHERE m_id = ?;""", mid)
	result = cursor.fetchone()
	if int(result[0]) == ctx.message.author.id:
		cursor.execute("""UPDATE Meeting_Info SET m_title = ? WHERE m_id = ?;""", (change, mid))
		await ctx.send("The meeting(id=" + mid + ") title's changed to " + change + ".")
	db.commit()
	cursor.close()
	db.close()

# Update the start time of a meeting
# Syntax: !updateMeetingTime <Meeting ID: text(Int)>
# Note: 
#	Only the host of the meeting ID is allowed to delete the meeting
#	Available open time slots for the meeting's original date will be provided according to "findBestMeetingTimes..."
@bot.command()
async def updateMeetingTime(ctx, mid):
	db = sqlite3.connect("itinerBuddyDB.sqlite")
	cursor = db.cursor()
	cursor.execute("""SELECT host_id FROM Meeting_Info WHERE m_id = ?;""", mid)
	hostID = cursor.fetchone()

	# Save meeting info to 
	cursor.execute(f"SELECT m_date FROM Meeting_Info WHERE m_id = ?", (mid))
	originalDate = cursor.fetchone()
	cursor.execute(f"SELECT m_start_time FROM Meeting_Info WHERE m_id = ?", (mid))
	meetingTime = cursor.fetchone()

	if meetingTime[0] == None:
		print("none!")
		oldMeetingTime = "BLANK"
	else:
		oldMeetingTime = meetingTime[0]
	
	if int(hostID[0]) == ctx.message.author.id:
		# Closing db as findBestTimesForMeetingWithoutSendingMessage() opens it in it.
		db.commit()
		cursor.close()
		db.close()
		bestTimesList = await findBestTimesForMeetingWithoutSendingMessage(ctx, mid, originalDate[0])

		for i in bestTimesList:
			if i == meetingTime[0]:
				bestTimesList.remove(i)

		if not bestTimesList:
			print("List is empty")
			await ctx.send("Cannot move the meeting(ID=" + mid + ") to " + change + ". Some of participants are not available for another time on the day.\n")
		else:
			print("List is not empty")
			db = sqlite3.connect("itinerBuddyDB.sqlite")
			cursor = db.cursor()
			if len(bestTimesList) == 1: # There is only one available time block left for the given date
				while(True):
					await ctx.send("The only available time is " + bestTimesList[0] + ". Do you want to change the meeting time to " + bestTimesList[0] + "? (Y/N)")
					async def check(msg):
						return msg.author == ctx.author and msg.channel == ctx.channel
					msg = await bot.wait_for("message", check = check)
					answer3 = str(msg.content)

					if ((answer3.find("Y") != -1)): # Change time to the only choice for the given date
						cursor.execute("""UPDATE Meeting_Info SET m_start_time = ? WHERE m_id = ?;""", (bestTimesList[0], mid))
						await ctx.send("The meeting(id=" + mid + ") is moved to " + str(bestTimesList[0]) + " from " + oldMeetingTime + " on " + originalDate[0])
						break
					elif ((answer3.find("N") != -1)): # Cancel updating
						await ctx.send("Understood. Canceled to reschedule the time for the meeting(ID=" + mid + ").")
						break
					break
			else: # There are more than one available time blocks left for the given date
				while(True):
					await ctx.send("What time do you want? Pick and type one from " + str(bestTimesList) + "or C to cancel updating the meeting date.")
					async def check(msg):
						return msg.author == ctx.author and msg.channel == ctx.channel
					msg = await bot.wait_for("message", check = check)
					newMeetingTime = str(msg.content)
					if (len(newMeetingTime) == 2 and newMeetingTime[0:2].isnumeric()) or (len(newMeetingTime) == 5 and newMeetingTime[0:2].isnumeric() and newMeetingTime[3:5] == "00") :
						if len(newMeetingTime) == 2:
							newMeetingTime = newMeetingTime + ":00"
						count = 1
						for time2 in bestTimesList:
							print("111")
							count = count + 1
							if time2 == newMeetingTime:
								print("222\n")
								print("111")
								cursor.execute("""UPDATE Meeting_Info SET m_start_time = ? WHERE m_id = ?;""", (newMeetingTime, mid))
								await ctx.send("The meeting(id=" + mid + ") is moved to " + newMeetingTime + " from " + oldMeetingTime + " on " + originalDate[0])
								break
						if (count < len(bestTimesList)) & (oldMeetingTime != "BLANK"):
							await ctx.send("Not available. Pleast try again.")
					elif ((newMeetingTime.find("C") != -1)): # Cancel updating after atempting to pick another time
						await ctx.send("Understood. Canceled to reschedule the time for the meeting(ID=" + mid + ").")
						break
					else:	
						await ctx.send("Cannot understand. Please type in format of HH or HH:MM.")
					break
	db.commit()
	cursor.close()
	db.close()	

# Update the date of a meeting
# Syntax: !updateMeetingDate <Meeting ID: text(Int)> <Date: YYYY-MM-DD>
# Note: 
#	Only the host of the meeting ID is allowed to delete the meeting
#	Meeting time may also need to be updated if there is no more available option for the given date
# 	Alternative options will be provided according to "findBestMeetingTimes..."
@bot.command()
async def updateMeetingDate(ctx, mmid, change):
	# Issue: When m_id >= 10. Completely working for m_id < 10 so far.
	mid = mmid

	db = sqlite3.connect("itinerBuddyDB.sqlite")
	cursor = db.cursor()
	cursor.execute("""SELECT host_id FROM Meeting_Info WHERE m_id = ?;""", mid)
	hostID = cursor.fetchone()

	# Save meeting info to 
	cursor.execute(f"SELECT m_date FROM Meeting_Info WHERE m_id = ?", (mid))
	originalDate = cursor.fetchone()
	cursor.execute(f"SELECT m_start_time FROM Meeting_Info WHERE m_id = ?", (mid))
	meetingTime = cursor.fetchone()
	# Save participant's id
	cursor.execute(f"SELECT u_id FROM Meeting_scheduled WHERE m_id = ?", (mid))
	participants = cursor.fetchall()

	if int(hostID[0]) == ctx.message.author.id:
		# Closing db as findBestTimesForMeeting() opens it in it.
		db.commit()
		cursor.close()
		db.close()
		bestTimesList = await findBestTimesForMeetingWithoutSendingMessage(ctx, mid, change)
		if not bestTimesList:
			print("List is empty")
			await ctx.send("Cannot move the meeting(ID=" + mid + ") to " + change + ". Some of participants are not available on the day.\n")
		else:
			db = sqlite3.connect("itinerBuddyDB.sqlite")
			cursor = db.cursor()
			print("List is not empty")
			sameAvailable = False

			for time in bestTimesList:
				if(time == meetingTime[0]): # Same meeting time available
					sameAvailable = True

			if(sameAvailable == True):
				if len(bestTimesList) == 1: # There is only one available time block left for the given date
					while(True):
						await ctx.send("The same meeting time(" + meetingTime[0] + ") is the only available time for " + change + ". Do you want to keep the meeting time? (Y/N)")
						async def check(msg):
							return msg.author == ctx.author and msg.channel == ctx.channel
						msg = await bot.wait_for("message", check = check)
						answer4 = str(msg.content)

						if ((answer4.find("Y") != -1)): # Change date, keep time
							cursor.execute("""UPDATE Meeting_Info SET m_date = ? WHERE m_id = ?;""", (change, mid))
							await ctx.send("The meeting(id=" + mid + ") is moved to " + change + " from " + originalDate[0] + ".")
							break
						elif ((answer4.find("N") != -1)): # Cancel updating
							await ctx.send("Understood. Canceled to reschedule the meeting(ID=" + mid + ") to " + change + ".")
							break
						break
				else: # There are more than one available time blocks left for the given date
					while(True):
						await ctx.send("The same meeting time(" + meetingTime[0] + ") is available for " + change + ". Do you want to keep the meeting time? (Y/N)")
						async def check(msg):
							return msg.author == ctx.author and msg.channel == ctx.channel
						msg = await bot.wait_for("message", check = check)
						answer = str(msg.content)
						
						if ((answer.find("Y") != -1)):
							# Change date to givenDate, keep time
							cursor.execute("""UPDATE Meeting_Info SET m_date = ? WHERE m_id = ?;""", (change, mid))
							await ctx.send("The meeting(id=" + mid + ") is moved to " + change + " from " + originalDate[0] + ".")
							break
						elif ((answer.find("N") != -1)):
							# Change date to givenDate, ask for another time to change
							while(True):
								await ctx.send("What time do you want? Pick and type one from " + str(bestTimesList) + " or K to keep the original meeting time.")
								async def check(msg):
									return msg.author == ctx.author and msg.channel == ctx.channel
								msg = await bot.wait_for("message", check = check)
								newMeetingTime = str(msg.content)
								if (len(newMeetingTime) <= 2 and newMeetingTime[0:2].isnumeric()) or (len(newMeetingTime) == 5 and newMeetingTime[0:2].isnumeric() and newMeetingTime[3:5] == "00") or (len(newMeetingTime) == 4 and newMeetingTime[0:1].isnumeric() and newMeetingTime[2:4] == "00"):
									if len(newMeetingTime) <= 2:
										newMeetingTime = newMeetingTime + ":00"
									count = 1
									for time2 in bestTimesList:
										count = count + 1
										if time2 == newMeetingTime:
											cursor.execute("""UPDATE Meeting_Info SET m_date = ?, m_start_time = ? WHERE m_id = ?;""", (change, newMeetingTime, mid))
											await ctx.send("The meeting(id=" + mid + ") is moved to " + change + " at " + newMeetingTime + " from " + originalDate[0] + " at " + meetingTime[0])
											break
									if count > len(bestTimesList):
										await ctx.send("Not available. Pleast try again.")
								elif ((newMeetingTime.find("K") != -1)): # Keep the original meeting time
									cursor.execute("""UPDATE Meeting_Info SET m_date = ? WHERE m_id = ?;""", (change, mid))
									await ctx.send("The meeting(id=" + mid + ") is moved to " + change + " from " + originalDate[0] + ".")
									break
								else:	
									await ctx.send("Cannot understand. Please type in format of HH or HH:MM.")
								break
						else:
							await ctx.send("Not understood. Please try again.")
						break
			else: # Same meeting time is not available
				if len(bestTimesList) == 1: # There is only one available time block left for the given date
					while(True):
						await ctx.send("The same meeting time(" + meetingTime[0] + ") is not available for " + change + ".\nThe only available time is " + bestTimesList[0] + ". Do you want to change the meeting time to " + bestTimesList[0] + "? (Y/N)")
						async def check(msg):
							return msg.author == ctx.author and msg.channel == ctx.channel
						msg = await bot.wait_for("message", check = check)
						answer3 = str(msg.content)

						if ((answer3.find("Y") != -1)): # Change time to the only choice for the given date
							cursor.execute("""UPDATE Meeting_Info SET m_date = ?, m_start_time = ? WHERE m_id = ?;""", (change, bestTimesList[0], mid))
							await ctx.send("The meeting(id=" + mid + ") is moved to " + change + " at " + str(bestTimesList[0]) + " from " + originalDate[0] + " at " + meetingTime[0])
							break
						elif ((answer3.find("N") != -1)): # Cancel updating
							await ctx.send("Understood. Canceled to reschedule the meeting(ID=" + mid + ") to " + change + ".")
							break
						break
				else: # There are more than one available time blocks left for the given date
					while(True):
						await ctx.send("The same meeting time(" + meetingTime[0] + ") is not available for " + change + ". Do you want to pick another time? (Y/N)")
						async def check(msg):
							return msg.author == ctx.author and msg.channel == ctx.channel
						msg = await bot.wait_for("message", check = check)
						newMeetingTime2 = str(msg.content)

						if ((newMeetingTime2.find("Y") != -1)): # ask for another time to pick
							# Change date to givenDate, ask for another time to change
							while(True):
								await ctx.send("What time do you want? Pick and type one from " + str(bestTimesList) + "or C to cancel updating the meeting date.")
								async def check(msg):
									return msg.author == ctx.author and msg.channel == ctx.channel
								msg = await bot.wait_for("message", check = check)
								newMeetingTime = str(msg.content)
								if (len(newMeetingTime) == 2 and newMeetingTime[0:2].isnumeric()) or (len(newMeetingTime) == 5 and newMeetingTime[0:2].isnumeric() and newMeetingTime[3:5] == "00") :
									if len(newMeetingTime) == 2:
										newMeetingTime = newMeetingTime + ":00"
									count = 1
									for time2 in bestTimesList:
										count = count + 1
										if time2 == newMeetingTime:
											cursor.execute("""UPDATE Meeting_Info SET m_date = ?, m_start_time = ? WHERE m_id = ?;""", (change, newMeetingTime, mid))
											await ctx.send("The meeting(id=" + mid + ") is moved to " + change + " at " + newMeetingTime + " from " + originalDate[0] + " at " + meetingTime[0])
											break
									if count > len(bestTimesList):
										await ctx.send("Not available. Pleast try again.")

								elif ((newMeetingTime.find("C") != -1)): # Cancel updating after atempting to pick another time
									await ctx.send("Understood. Canceled to reschedule the meeting(ID=" + mid + ") to " + change + ".")
									break
								else:	
									await ctx.send("Cannot understand. Please type in format of HH or HH:MM.")
								break
							break
						elif ((newMeetingTime2.find("N") != -1)): # Cancel updating
							await ctx.send("Understood. Canceled to reschedule the meeting(ID=" + mid + ") to " + change + ".")
							break
						else:
							await ctx.send("Cannot understand. Please try again.")
						break
				# break
	db.commit()
	cursor.close()
	db.close()




# Invite members to a meeting
# Syntax: !invite
# Note: 
#	Users will be instructed next steps once the bot receives this command
#	Can invite users with username, role, or channel
@bot.command()
async def invite(ctx):
    #-- initialize function variables --#
    db = sqlite3.connect("itinerBuddyDB.sqlite")
    cursor = db.cursor()
    meetingID = ""
    
    #-- loop to get meeting id 
    #-- loop breaks on correct id
    while(True):
        await ctx.send("Please type the meeting ID, for the meeting you want to start inviting people to")
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        msg = await bot.wait_for("message", check = check)
        meetingID = msg.content
        
        cursor.execute("""SELECT * FROM Meeting_Info WHERE m_id = ?;""", meetingID)
        result = cursor.fetchall()
        if result is None:
            await ctx.send ( "I could not find that meeting, please try again")
        else:
            await ctx.send ( "Meeting found!")
            break
    
    #-- Loop to make sure proper inputs are reieved
    #-- Loop breaks after  users are added to db 
    while(True):
        userFound = False
        await ctx.send("Would you like to invite Users, everyone in a role, or everyone in the channel? (type users, role, channel or nevermind)")
        msg = await bot.wait_for("message", check = check)
        
        #-- Add individual users --#
        if msg.content == "users" :
            await ctx.send("Send the names individually and please send 'done' when done")
            #-- Add users loop
            while msg.content != "done":
                msg = await bot.wait_for("message", check = check)
                async for member in ctx.guild.fetch_members(limit=150):
                    if(member.name == msg.content):
                        memID = member.id
                        cursor.execute("""INSERT INTO Meeting_scheduled (m_id, u_id) VALUES (?, ?);""", (meetingID, memID))
                        userFound = True
                        await ctx.send("User **" + member.name + "** added.")
                        break;# out of for-loop
                        
                ## If the break statement was not reached we can assume the user was not found
                if not userFound:
                    await ctx.send("Couldnt find user, please try again")
                
            break # out of while loop
            
        #-- Add users who fall under a certain role  
        elif msg.content == "role":
            foundRole = False
            await ctx.send("Which role would you like to use for the invitation?")
            msg = await bot.wait_for("message", check = check)
            
            #-- loop through all roles available in guild
            for role in ctx.guild.roles:
                
                #-- if role is found, get all members who's role equates to ours
                if role.name == msg.content:
                    foundRole = True
                    async for member in ctx.guild.fetch_members(limit=150):
                        for memRole in member.roles:
                            if memRole == role:
                                memID = member.id
                                cursor.execute("""INSERT INTO Meeting_scheduled (m_id, u_id) VALUES (?, ?);""", (meetingID, memID))
                                await ctx.send("User **" + member.name + "** added.")
            
            if not foundRole:
                await ctx.send("Role not found")
            break # out of while loop
        
        #-- add everyone in this channel
        elif msg.content == "channel":
            for member in ctx.channel.members:
                memID = member.id
                cursor.execute("""INSERT INTO Meeting_scheduled (m_id, u_id) VALUES (?, ?);""", (meetingID, memID))
                await ctx.send("User **" + member.name + "** added.")
            break # out of while loop
        
        elif msg.content == "nevermind":
            return
        
        else:
            await ctx.send(" I didnt catch that, please try the command again")
            
    await ctx.send("Thank you")
    db.commit()
    cursor.close()
    db.close()		

# Calculate and display the list of suggestions (in range if applicable) for the start time of a given meeting
# Syntax: !findBestTimesForMeeting <MEETING ID> <MEETING DATE>
# Note: In addition, it will inform if there are members who have not set their preferred times for the given date yet. 
@bot.command()
async def findBestTimesForMeeting(ctx, mid, givenDate):	
	#Formats the string so there's only - separating the infomation
	numberOfDashs = 0
	for i in str(givenDate):
		if i == '/':
			numberOfDashs += 1
		elif i == '-':
			numberOfDashs += 1
			
	givenDate = str(givenDate).replace("/", "-")

	#Create a datetime from the input given 
	if numberOfDashs == 2:
		completeDate = datetime.strptime(givenDate, '%Y-%m-%d')
	elif numberOfDashs == 1:
		completeDate = datetime.strptime(givenDate, '%m-%d')
		completeDate = completeDate.replace(year=date.today().year)
		
	db = sqlite3.connect('itinerBuddyDB.sqlite')
	cursor = db.cursor()
	
	gettingRangeOfGoodTime = False
	
	goodTimes = ""
	goodTimesList = []

	minimumConflictingMembers = -1;
	
	someoneHasSetAvailableTimesOnDay = False 
	
	#Note: UPDATED
	members = []
	for row in cursor.execute(f"SELECT u_id FROM Meeting_scheduled WHERE m_id = {mid}"):
		print(row[0])
		members.append(int(row[0]))

	#members = await ctx.guild.fetch_members(limit=150).flatten()
	membersWithAvailableTimeOnDay = [];
	
	for i in range(24): #Iterates through all hours of the day
		conflictingMembers = 0	
			
		for member in members: 	
			timeWorksForMember = False
			memberHasSetAvailableTimesOnDay = False
		
			for row in cursor.execute(f"SELECT * FROM User_availability"):		
				if int(row[0]) == int(member): #Checks if the availabletime row is from a meeting participant 	
					matchedDay = False
					if row[4] == "true": #If the available time is weekly
						if completeDate.weekday() == datetime.strptime(str(row[1]), '%Y-%m-%d').weekday():
							matchedDay = True
					else: #Else the available time is only on a date
						if completeDate == datetime.strptime(str(row[1]), '%Y-%m-%d'):
							matchedDay = True
					
					if matchedDay == True:
						memberHasSetAvailableTimesOnDay = True
						someoneHasSetAvailableTimesOnDay = True 
						if ((i >= int(datetime.strptime(str(row[2]), '%H:%M').hour)) and (i <= int(datetime.strptime(str(row[3]), '%H:%M').hour - 1))): #If hour is within someone's available time
							
							timeConflictsWithDifferentMeeting = False 
							
							#Loop checks if the participant has another meeting at this time. 
							for meetingScheduledRow in cursor.execute(f"SELECT * FROM Meeting_scheduled"): 		 					
								if(int(meetingScheduledRow[1]) == int(member)):
									meetingCursor = cursor.execute(f"SELECT * FROM Meeting_Info WHERE m_id = {meetingScheduledRow[0]}")
									meetingCursor = cursor.fetchone()
									meetingDate = datetime.strptime(meetingCursor[3], '%Y-%m-%d')
									
									if(meetingDate.date() == completeDate.date()):
										if (meetingCursor[4] != None):
											meetingStartTime = datetime.strptime(meetingCursor[4],"%H:%M")
											meetingEndTime = meetingStartTime.replace(hour=(meetingStartTime.hour + 1))
											
											iTime = datetime.strptime(str(i),"%H")						
											
											if((iTime.time() >= meetingStartTime.time()) & (iTime.time() < meetingEndTime.time())):
												timeConflictsWithDifferentMeeting = True
												break
							
							if timeConflictsWithDifferentMeeting == False:
								timeWorksForMember = True 
			
			if (timeWorksForMember == False): #Note: Only one of someone's available times is needed for the hour to work for the meeting participant 
				if (memberHasSetAvailableTimesOnDay == True): 
					conflictingMembers += 1		
			
			if(memberHasSetAvailableTimesOnDay == True):
				if (member not in membersWithAvailableTimeOnDay):
					membersWithAvailableTimeOnDay.append(member)
			
		if conflictingMembers == 0:
			goodTimesList.append(str(i)+":00")
			if gettingRangeOfGoodTime == False:
				goodTimes += str(i) + ":00"	
				gettingRangeOfGoodTime = True
				
			if i == 23:
				goodTimes += " - 24:00\n"		
		else:
			if gettingRangeOfGoodTime == True:
				goodTimes += " - " + str(i) + ":00\n"
				gettingRangeOfGoodTime = False
			
			if minimumConflictingMembers == -1:
				minimumConflictingMembers = conflictingMembers
			elif conflictingMembers < minimumConflictingMembers:
				minimumConflictingMembers = conflictingMembers

	if someoneHasSetAvailableTimesOnDay:
		if goodTimes != "":
			embed=discord.Embed(title = "Best Times for Meetings on: " + str(completeDate.date()), color=0x109319)
			embed.add_field(name="Hours:", value=goodTimes, inline=False) 
			await ctx.send(embed=embed)
		else:
			await ctx.send("We couldn't find a good time on " + str(completeDate.date()) + " as it will conflict with at least " + str(minimumConflictingMembers)  + " participant(s)")
			
		numberOfMembersWhoHaveNotSetTime = len(members) - len(membersWithAvailableTimeOnDay)		
		
		if numberOfMembersWhoHaveNotSetTime != 0:
			await ctx.send("**Note:** " + str(numberOfMembersWhoHaveNotSetTime) + " meeting participant(s) haven't set their availability for that day.")
	else:
		await ctx.send("I couldn't find a good time on " + str(completeDate.date()) + " since none of the meeting participants set their availability for that day.")	
	return goodTimesList
	cursor.close()
	db.close()

# Same as findBestTimesForMeeting but it doesn't send any message to the server as not needed.
# It is just to use in updating meeting info(date and time)
# Note from Jo Eun: mid is added to get participants, open time slots will be saved in a list.
@bot.command()
async def findBestTimesForMeetingWithoutSendingMessage(ctx, mid, givenDate):	
	#Formats the string so there's only - separating the infomation
	numberOfDashs = 0
	for i in str(givenDate):
		if i == '/':
			numberOfDashs += 1
		elif i == '-':
			numberOfDashs += 1
			
	givenDate = str(givenDate).replace("/", "-")

	#Create a datetime from the input given 
	if numberOfDashs == 2:
		completeDate = datetime.strptime(givenDate, '%Y-%m-%d')
	elif numberOfDashs == 1:
		completeDate = datetime.strptime(givenDate, '%m-%d')
		completeDate = completeDate.replace(year=date.today().year)
		
	db = sqlite3.connect('itinerBuddyDB.sqlite')
	cursor = db.cursor()
	
	gettingRangeOfGoodTime = False
	
	goodTimes = ""
	goodTimesList = []

	minimumConflictingMembers = -1;
	
	someoneHasSetAvailableTimesOnDay = False 
	
	#Note: UPDATED
	members = []
	for row in cursor.execute(f"SELECT u_id FROM Meeting_scheduled WHERE m_id = {mid}"):
		print(row[0])
		members.append(int(row[0]))

	membersWithAvailableTimeOnDay = [];
	
	for i in range(24): #Iterates through all hours of the day
		conflictingMembers = 0	
			
		for member in members: 	
			timeWorksForMember = False
			memberHasSetAvailableTimesOnDay = False
		
			for row in cursor.execute(f"SELECT * FROM User_availability"):		
				if int(row[0]) == int(member): #Checks if the availabletime row is from a meeting participant 	
					matchedDay = False
					if row[4] == "true": #If the available time is weekly
						if completeDate.weekday() == datetime.strptime(str(row[1]), '%Y-%m-%d').weekday():
							matchedDay = True
					else: #Else the available time is only on a date
						if completeDate == datetime.strptime(str(row[1]), '%Y-%m-%d'):
							matchedDay = True
					
					if matchedDay == True:
						memberHasSetAvailableTimesOnDay = True
						someoneHasSetAvailableTimesOnDay = True 
						if ((i >= int(datetime.strptime(str(row[2]), '%H:%M').hour)) and (i <= int(datetime.strptime(str(row[3]), '%H:%M').hour - 1))): #If hour is within someone's available time
							
							timeConflictsWithDifferentMeeting = False 
							
							#Loop checks if the participant has another meeting at this time. 
							for meetingScheduledRow in cursor.execute(f"SELECT * FROM Meeting_scheduled"): 		 					
								if(int(meetingScheduledRow[1]) == int(member)):
									meetingCursor = cursor.execute(f"SELECT * FROM Meeting_Info WHERE m_id = {meetingScheduledRow[0]}")
									meetingCursor = cursor.fetchone()
									meetingDate = datetime.strptime(meetingCursor[3], '%Y-%m-%d')
									
									if(meetingDate.date() == completeDate.date()):
										if (meetingCursor[4] != None):
											print("haha=")
											print(meetingCursor[4])
											meetingStartTime = datetime.strptime(meetingCursor[4],"%H:%M")
											meetingEndTime = meetingStartTime.replace(hour=(meetingStartTime.hour + 1))
											
											iTime = datetime.strptime(str(i),"%H")						
											
											if((iTime.time() >= meetingStartTime.time()) & (iTime.time() < meetingEndTime.time())):
												timeConflictsWithDifferentMeeting = True
												break
							
							if timeConflictsWithDifferentMeeting == False:
								timeWorksForMember = True 
			
			if (timeWorksForMember == False): #Note: Only one of someone's available times is needed for the hour to work for the meeting participant 
				if (memberHasSetAvailableTimesOnDay == True): 
					conflictingMembers += 1		
			
			if(memberHasSetAvailableTimesOnDay == True):
				if (member not in membersWithAvailableTimeOnDay):
					membersWithAvailableTimeOnDay.append(member)
			
		if conflictingMembers == 0:
			goodTimesList.append(str(i)+":00")
			if gettingRangeOfGoodTime == False:
				goodTimes += str(i) + ":00"	
				gettingRangeOfGoodTime = True
				
			if i == 23:
				goodTimes += " - 24:00\n"		
		else:
			if gettingRangeOfGoodTime == True:
				goodTimes += " - " + str(i) + ":00\n"
				gettingRangeOfGoodTime = False
			
			if minimumConflictingMembers == -1:
				minimumConflictingMembers = conflictingMembers
			elif conflictingMembers < minimumConflictingMembers:
				minimumConflictingMembers = conflictingMembers

	if someoneHasSetAvailableTimesOnDay:
		if goodTimes != "":
			print("-------------FOUND---BestTimesForMeeting:")
			print(goodTimes)
			print("---------------------------------------")
		else:
			print("-------------NOT FOUND---BestTimesForMeeting:")			
		numberOfMembersWhoHaveNotSetTime = len(members) - len(membersWithAvailableTimeOnDay) - 1 #-1 is to discount bot itself		

	else:
		print("-------------NO ONE SET THEIR AVAILABLILITIES.\n")
	print(goodTimesList)
	return goodTimesList
	cursor.close()
	db.close()

# View the list of all upcoming meetings
# Syntax: !viewUpcomingMeetings
@bot.command()
async def viewUpcomingMeetings(ctx):
	db = sqlite3.connect('itinerBuddyDB.sqlite')
	cursor = db.cursor()
	meeting_info = ""
	now = dt.datetime.now()
	currentDate = now.strftime('%Y-%m-%d')
	currentTime = now.strftime('%H:%M')
	result = cursor.fetchall()
	for row in cursor.execute(f"SELECT * FROM Meeting_Info"):
		if (currentDate <= str(row[3]) and currentTime <= str(row[4])):
			async for member in ctx.guild.fetch_members(limit=150):
				if(str(member.id) == str(row[1])):
					meeting_info += "Meeting ID: " + str(row[0]) + "\nHost Name: " + member.name + "\nTitle: " + str(row[2]) + "\nDate: " + str(row[3]) + "\nStart Time: " + str(row[4]) + "\n\n"
	if meeting_info != "" :
		myembed=discord.Embed(title = "Meetings", color=0x109319)
		myembed.add_field(name="Meeting_info", value=meeting_info, inline=False) 
		await ctx.send(embed=myembed)
	cursor.close()

# Add time slots in a range for a given date into User_availability table
# Syntax: !addMyPreferredTime <GIVEN DAY> <START TIME> <END TIME>
@bot.command()
async def addMyPreferredTime(ctx, givenDay, startTime, endTime):
	numberOfDashs = 0

	weekly = False
	
	for i in str(givenDay):
		if i == '/':
			numberOfDashs += 1
		elif i == '-':
			numberOfDashs += 1
			
	givenDay = str(givenDay).replace("/", "-")

	#Create a datetime from the input given 
	if numberOfDashs == 2:
		givenDay = str(datetime.strptime(givenDay, '%Y-%m-%d').date())
	elif numberOfDashs == 1:
		givenDay = str((datetime.strptime(givenDay, '%m-%d').replace(year=date.today().year)).date())		

	db = sqlite3.connect('itinerBuddyDB.sqlite')
	cursor = db.cursor()
	cursor.execute(f"SELECT time FROM User_availability WHERE u_id = ? AND date = ? AND time = ? AND end_time = ? AND weeklyBool = ?", (ctx.author.id, givenDay, startTime, endTime, str(weekly).lower()))
	result = cursor.fetchone()
	if result == None:
		cursor.execute(f"INSERT INTO User_availability (u_id, date, time, end_time, weeklyBool) VALUES (?, ?, ?, ?, ?);", (ctx.author.id, givenDay, startTime, endTime, str(weekly).lower()))
		await ctx.send("Your available time on " + str(givenDay) +  ", from " + str(startTime) + " to " + str(endTime) + " has been added.")
	else:
		await ctx.send("We couldn't add your available time, " + str(startTime) + " to " + str(endTime) + " on " + str(givenDay) + ", since it has already been added.")

	db.commit()
	cursor.close()
	db.close()

# Add weekly time slots for a given day into User_availability table
# Syntax: !addMyPreferredTime <GIVEN DAY> <START TIME> <END TIME> <WEEKLY INDICATOR>
@bot.command()
async def addMyPreferredTimeWeekly(ctx, givenDay, startTime, endTime):
	numberOfDashs = 0
	
	weekly = True
	weekDays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	weekDayIndex = -1

	dayInt = -1
	if givenDay == "Mo":
		dayInt = 0
		weekDayIndex = 0
	elif givenDay == "Tu":
		dayInt = 1
		weekDayIndex = 1
	elif givenDay == "We":
		dayInt = 2
		weekDayIndex = 2
	elif givenDay == "Th":
		dayInt = 3
		weekDayIndex = 3
	elif givenDay == "Fr":
		dayInt = 4
		weekDayIndex = 4
	elif givenDay == "Sa":
		dayInt = 5
		weekDayIndex = 5
	elif givenDay == "Su":
		dayInt = 6
		weekDayIndex = 6


	today = datetime.now()
	todayDate = datetime.date(today)
	print(todayDate)

	days_ahead = dayInt - todayDate.weekday()

	if days_ahead <= 0:
		days_ahead += 7

	next_givenDay = todayDate + dt.timedelta(days_ahead) # 0 = Monday, 1=Tuesday, 2=Wednesday...

	db = sqlite3.connect('itinerBuddyDB.sqlite')
	cursor = db.cursor()
	cursor.execute(f"SELECT time FROM User_availability WHERE u_id = ? AND date = ? AND time = ? AND end_time = ? AND weeklyBool = ?", (ctx.author.id, next_givenDay, startTime, endTime, str(weekly).lower()))
	result = cursor.fetchone()
	if result == None:
		cursor.execute(f"INSERT INTO User_availability (u_id, date, time, end_time, weeklyBool) VALUES (?, ?, ?, ?, ?);", (ctx.author.id, next_givenDay, startTime, endTime, str(weekly).lower()))		
		await ctx.send("Your available time on " + str(weekDays[weekDayIndex]) +  "s, from " + str(startTime) + " to " + str(endTime) + " has been added.")
	else:
		await ctx.send("We couldn't add your available time, " + str(startTime) + " to " + str(endTime) + " on " + str(weekDays[weekDayIndex]) + "s, since it has already been added.")

	db.commit()
	cursor.close()
	db.close()

# Delete time slots in a range for a given date from User_availability table
# Syntax: !deleteMyPreferredTime <GIVEN DAY> <START TIME> <END TIME>
@bot.command()
async def deleteMyPreferredTime(ctx, givenDay, startTime, endTime):
	numberOfDashs = 0
	
	for i in str(givenDay):
		if i == '/':
			numberOfDashs += 1
		elif i == '-':
			numberOfDashs += 1
			
	givenDay = str(givenDay).replace("/", "-")

	#Create a datetime from the input given 
	if numberOfDashs == 2:
		givenDay = str(datetime.strptime(givenDay, '%Y-%m-%d').date())
	elif numberOfDashs == 1:
		givenDay = str((datetime.strptime(givenDay, '%m-%d').replace(year=date.today().year)).date())	
	
	today = datetime.now()
	dateFormatted = today.strftime("%Y-%m-%d")

	weekly = False
	weekDays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	weekDayIndex = -1

	for weekDay in weekDays:
		if givenDay in weekDay:
			weekDayIndex = weekDays.index(weekDay)
			givenDay = dateFormatted + str(weekDayIndex + 1)
			weekly = True		
	
	
	if weekly == True:
		dayName = weekDays[weekDayIndex] + "s"
	else:
		dayName = str(givenDay)

	await ctx.send("Deleting/editing available times on " + dayName + "...")
	
	db = sqlite3.connect('itinerBuddyDB.sqlite')
	cursor = db.cursor()
	
	sendNoteAboutConflictWithWeeklyTime = False
	
	rowsToCreate = []
	rowsToDelete = []
	
	for row in cursor.execute(f"SELECT * FROM User_availability"):
		
		if(int(ctx.author.id) == int(row[0])):
			dayMatched = False
			
			if(weekly == True):
				if weekDayIndex == datetime.strptime(str(row[1]), '%Y-%m-%d').weekday():
					if row[4] == "true":
						dayMatched = True
			else:
				if(str(givenDay) == str(row[1])):
					if row[4] == "false":
						dayMatched = True
			
			if(dayMatched == True):			
				if((datetime.strptime(str(startTime), '%H:%M').hour <= datetime.strptime(str(row[2]), '%H:%M').hour) & (datetime.strptime(str(endTime), '%H:%M').hour >= datetime.strptime(str(row[3]), '%H:%M').hour)):
					rowsToDelete.append(row)
				else:
					if(datetime.strptime(str(startTime), '%H:%M').hour > datetime.strptime(str(row[2]), '%H:%M').hour): 
						rowsToDelete.append(row)	
						firstRowNewEndTime = startTime
						
						rowsToCreate.append([row[0], row[1], row[2], firstRowNewEndTime, str(weekly).lower()])					
						if (datetime.strptime(str(endTime), '%H:%M').hour < datetime.strptime(str(row[3]), '%H:%M').hour):
							secondRowNewStartTime = endTime
							rowsToCreate.append([row[0], row[1], secondRowNewStartTime, row[3], str(weekly).lower()])	
					elif(datetime.strptime(str(endTime), '%H:%M').hour < datetime.strptime(str(row[3]), '%H:%M').hour):
						rowsToDelete.append(row)		
						newStartTime = endTime
						rowsToCreate.append([row[0], row[1], newStartTime, row[3], str(weekly).lower()])					
						
	hasDeletedTime = False
	
	for row in rowsToDelete:
		cursor.execute(f"DELETE FROM User_availability WHERE u_id = ? AND date = ? AND time = ? AND end_time = ? AND weeklyBool = ?", (row[0], row[1], row[2], row[3], row[4]))
		await ctx.send("| Your available time on " + dayName +  " that starts from " + row[2] + " to " + row[3] + " has been deleted.")
		hasDeletedTime = True
	
	for row in rowsToCreate:
		cursor.execute(f"INSERT INTO User_availability (u_id, date, time, end_time, weeklyBool) VALUES (?, ?, ?, ?, ?);", (row[0], row[1], row[2], row[3], row[4]))
		hasEditTimes = True
		await ctx.send("| One of your available times on " + dayName +  " has been updated to start from " + row[2] + " to " + row[3])
	
	if hasDeletedTime:
		await ctx.send("-\nDeleting/editing available times on " + dayName +  " has been done. Feel free to view your new availability using !viewMemberSchedule")
	else:
		await ctx.send("-\nNo available times on " + dayName +  " that starts from " + startTime + " to " + endTime + " has been found. Use !viewMemberSchedule to view your availability and specify the weekday if the available time is weekly.")
	
	db.commit()
	cursor.close()
	db.close()	

# Display all members' list of preferred time slots (in range if applicable)
# Syntax: !viewAllMembersPreferredTimes
@bot.command()
async def viewAllMembersPreferredTimes(ctx):
	await ctx.send("Getting all members' preferred times...")
	async for member in ctx.guild.fetch_members(limit=150):
		await printMemberPreferredTimes(ctx, member.id)

# Display a member's list of preferred time slots (in range if applicable)
# Syntax: !viewMemberPreferredTimes <USERNAME>
@bot.command()
async def viewMemberPreferredTimes(ctx, arg):
	foundUser = False
	
	async for member in ctx.guild.fetch_members(limit=150):
		if(member.name == arg):
			foundUser = True;
			await printMemberPreferredTimes(ctx, member.id)
			
	if (foundUser == False):
		await ctx.send(arg + " couldn't be matched to a user in server. \nMake sure to use true username, not nickname.")

# Display a member's list of preferred time slots (in range if applicable)
# Syntax: !viewMemberPreferredTimes <USERNAME>
@bot.command()
async def viewMyPreferredTimes(ctx):
	await printMemberPreferredTimes(ctx, ctx.author.id)
		
# Helper function used in "viewMemberPreferredTimes(ctx, arg)"
async def printMemberPreferredTimes(ctx, member):
	db = sqlite3.connect('itinerBuddyDB.sqlite')
	cursor = db.cursor()
	
	availableTimes = "";
	
	for row in cursor.execute(f"SELECT * FROM User_availability"):	
		if int(row[0]) == int(member):
			day = str(row[1]) #date
			if (row[4] == "true"): #WeeklyBool
				day = calendar.day_name[datetime.strptime(str(row[1]), '%Y-%m-%d').weekday()] + "s"  #day of the week
		
			availableTimes += "**Day:** " + day + "\n**Time:** " + str(row[2]) + " - " + str(row[3] + "\n\n")
	
	if availableTimes != "":
		embed=discord.Embed(title = str(await bot.fetch_user(member)), color=0x109319)
		embed.add_field(name="Available Times", value=availableTimes, inline=False) 
		await ctx.send(embed=embed)
	else:
		await ctx.send("User **" + str(await bot.fetch_user(member)) + "** hasn't set preferred times yet.")
	
	cursor.close()
	db.close()

# Display the list of all commands related to the meeting module with instructions
# Symtax: !help
@bot.command()
async def help(ctx):
	
	timeFormat = "TIME: hh:mm\n"
	dateFormat = "DATE: yyyy-mm-dd\n"
	commandName = []
	commandDescription = []
	commandFormat = []

	# Meeting related commands
	commandName.append("*********Meeting Related Commands:********* \n\n__**setReminder**__")
	commandDescription.append("DESCRIPTION: Sets a reminder to notify meeting participant at specified time before a meeting.\n")
	commandFormat.append("COMMAND FORMAT: !setReminder <MEETING ID>\n\n")
	
	commandName.append("__**applyRole**__")
	commandDescription.append("DESCRIPTION: Gives to the user the Itiner-Buddy: Team Manager role which allows them to create, edit and delete meetings.\n")
	commandFormat.append("COMMAND FORMAT: !applyRole <USERNAME>\n\n")
	
	commandName.append("__**createMeeting**__")
	commandDescription.append("DESCRIPTION: Creates a meeting on the specified date. A meeting ID is created to reference that meeting in commands. Time of meeting is set using !updateMeetingTime.\n")
	commandFormat.append("COMMAND FORMAT: !createMeeting '<MEETING TITLE>' <MEETING DATE>\n\n")

	commandName.append("__**deleteMeeting**__")
	commandDescription.append("DESCRIPTION: Delete the meeting specified by the meeting ID.\n")
	commandFormat.append("COMMAND FORMAT: !deleteMeeting <MEETING ID>\n\n")
	
	commandName.append("__**updateMeetingTitle**__")
	commandDescription.append("DESCRIPTION: Replaces meeting title.\n")
	commandFormat.append("COMMAND FORMAT: !updateMeetingTitle <MEETING ID> <NEW MEETING TITLE>\n\n")

	commandName.append("__**updateMeetingTime**__")
	commandDescription.append("DESCRIPTION: Changes meeting time.\n")
	commandFormat.append("COMMAND FORMAT: !updateMeetingTime <MEETING ID>\n\n")

	commandName.append("__**updateMeetingDate**__")
	commandDescription.append("DESCRIPTION: Changes meeting date.\n")
	commandFormat.append("COMMAND FORMAT: !updateMeetingDate <MEETING ID> <NEW DATE> \n\n")
	
	commandName.append("__**invite**__")
	commandDescription.append("DESCRIPTION: Adds users as participants in meeting.\n")
	commandFormat.append("COMMAND FORMAT: !invite \n\n")
	
	commandName.append("__**findBestTimesForMeeting**__")
	commandDescription.append("DESCRIPTION: Gives a list of times for a meeting that is within meeting participants' preferred times and doesn't conflicts with their meetings.\n")
	commandFormat.append("COMMAND FORMAT: !findBestTimesForMeeting <MEETING ID> <GIVEN DATE>\n\n")	
	
	commandName.append("__**viewUpcomingMeetings**__")
	commandDescription.append("DESCRIPTION: Shows a list of upcoming meetings.\n")
	commandFormat.append("COMMAND FORMAT: !viewUpcomingMeetings")

	# Preferred time related commands:	
	commandName.append("*********Preferred Time Related Commands:********* \n\n__**addMyPreferredTime**__")
	commandDescription.append("DESCRIPTION: Adds a time slots for a date that you prefer to join meetings.\n")
	commandFormat.append("COMMAND FORMAT: !addMyPreferredTime <GIVEN DATE> <START TIME> <END TIME>\n\n")

	commandName.append("__**addMyPreferredTimeWeekly**__")
	commandDescription.append("DESCRIPTION: Adds a weekly time slots for <GIVEN DAY>, starting from the next given day, that you prefer to join meetings. In the field <GIVEN DAY>, type 'Mo' for monday, 'Tu' for Tuesday, 'We' for Wednesday, 'Th' for Thursday, 'Fr' for Friday, 'Sa' for Saterday, 'Su' for Sunday.\n")
	commandFormat.append("COMMAND FORMAT: !addMyPreferredTimeWeekly <GIVEN DAY> <START TIME> <END TIME>\n\n")
	
	commandName.append("__**deleteMyPreferredTime**__")
	commandDescription.append("DESCRIPTION: Deletes/edits existing preferred times based on the time range provided.\n")
	commandFormat.append("COMMAND FORMAT: !deleteMyPreferredTime <GIVEN DAY> <START TIME> <END TIME>\n\n")

	commandName.append("__**viewAllMembersPreferredTimes**__")
	commandDescription.append("DESCRIPTION: Shows everyone's preferred times.\n")
	commandFormat.append("COMMAND FORMAT: !viewAllMembersPreferredTimes\n\n")
	
	commandName.append("__**viewMemberPreferredTimes**__")
	commandDescription.append("DESCRIPTION: Shows you preferred times set by the given member.\n")
	commandFormat.append("COMMAND FORMAT: !viewMemberPreferredTimes <USERNAME>\n\n")	
	
	commandName.append("__**viewMyPreferredTimes**__")
	commandDescription.append("DESCRIPTION: Shows your preferred times.\n")
	commandFormat.append("COMMAND FORMAT: !viewMyPreferredTimes\n\n")

	embed=discord.Embed(title = "Meeting & Preferred Time Related Commands: ", color=0x109319, inline=False) 
	embed.add_field(name="Time & Date Format: ", value = timeFormat + dateFormat + "_-_-_-_-_-_-_\n", inline=False) 
	
	for i in range(len(commandName)):		
		embed.add_field(name=str(commandName[i]), value=str(commandDescription[i]) + str(commandFormat[i]), inline=False) 
	
	await ctx.send(embed=embed)

bot.run(bot_token)