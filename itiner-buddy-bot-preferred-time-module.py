# Discord Bot - Itiner-Buddy-Bot
# Preferred Time Module
# Final Demo - 4/27/2021
# Sean Vonnegut, George Tackie, Jo Eun Kim, Ryan Law

import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import datetime
import sqlite3
import datetime as dt
from datetime import datetime
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = '!', case_insensitive=True,intents = intents, help_command=None)
bot_ID = 808787148647301210

# Author: Sean
# Add time slots in a range for a given date into User_availability table
# Syntax: !addMyPreferredTime <GIVEN DAY> <START TIME> <END TIME>
@bot.command()
async def addMyPreferredTime(ctx, givenDay, startTime, endTime):
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
	
	weekly = False
	weekDays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	weekDayIndex = -1
	
	for weekDay in weekDays:
		if givenDay in weekDay:
			weekDayIndex = weekDays.index(weekDay)
			givenDay = "2021-02-0" + str(weekDayIndex + 1)
			weekly = True			

	db = sqlite3.connect('testdb4.sqlite')
	cursor = db.cursor()
	cursor.execute(f"SELECT start_time FROM User_availability WHERE u_id = ? AND date = ? AND start_time = ? AND end_time = ? AND weekly = ?", (ctx.author.id, givenDay, startTime, endTime, str(weekly).lower()))
	result = cursor.fetchone()
	if result == None:
		cursor.execute(f"INSERT INTO User_availability (u_id, date, start_time, end_time, weekly) VALUES (?, ?, ?, ?, ?);", (ctx.author.id, givenDay, startTime, endTime, str(weekly).lower()))
		
		if(weekly == True):	
			await ctx.send("Your available time on " + str(weekDays[weekDayIndex]) +  "s, from " + str(startTime) + " to " + str(endTime) + " has been added.")
		else:
			await ctx.send("Your available time on " + str(givenDay) +  ", from " + str(startTime) + " to " + str(endTime) + " has been added.")
	else:
		if(weekly == True):	
			await ctx.send("We couldn't add your available time, " + str(startTime) + " to " + str(endTime) + " on " + str(weekDays[weekDayIndex]) + "s, since it has already been added.")
		else:
			await ctx.send("We couldn't add your available time, " + str(startTime) + " to " + str(endTime) + " on " + str(givenDay) + ", since it has already been added.")
	db.commit()
	cursor.close()
	db.close()

# Author: Sean
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
	
	
	weekly = False
	weekDays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	weekDayIndex = -1

	for weekDay in weekDays:
		if givenDay in weekDay:
			weekDayIndex = weekDays.index(weekDay)
			givenDay = "2021/04/0" + str(weekDayIndex + 1)
			weekly = True		
	
	
	if weekly == True:
		dayName = weekDays[weekDayIndex] + "s"
	else:
		dayName = str(givenDay)

	await ctx.send("Deleting/editing available times on " + dayName + "...")
	
	db = sqlite3.connect('testdb4.sqlite')
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
		cursor.execute(f"DELETE FROM User_availability WHERE u_id = ? AND date = ? AND start_time = ? AND end_time = ? AND weekly = ?", (row[0], row[1], row[2], row[3], row[4]))
		await ctx.send("| Your available time on " + dayName +  " that starts from " + row[2] + " to " + row[3] + " has been deleted.")
		hasDeletedTime = True
	
	for row in rowsToCreate:
		cursor.execute(f"INSERT INTO User_availability (u_id, date, start_time, end_time, weekly) VALUES (?, ?, ?, ?, ?);", (row[0], row[1], row[2], row[3], row[4]))
		hasEditTimes = True
		await ctx.send("| One of your available times on " + dayName +  " has been updated to start from " + row[2] + " to " + row[3])
	
	if hasDeletedTime:
		await ctx.send("-\nDeleting/editing available times on " + dayName +  " has been done. Feel free to view your new availability using !viewMemberSchedule")
	else:
		await ctx.send("-\nNo available times on " + dayName +  " that starts from " + startTime + " to " + endTime + " has been found. Use !viewMemberSchedule to view your availability and specify the weekday if the available time is weekly.")
	
	db.commit()
	cursor.close()
	db.close()	
	
# Author: Sean
# Display all members' list of preferred time slots (in range if applicable)
# Syntax: !viewAllMembersPreferredTimes
@bot.command()
async def viewAllMembersPreferredTimes(ctx):
	await ctx.send("Getting all members' preferred times...")
	async for member in ctx.guild.fetch_members(limit=150):
		await printMemberPreferredTimes(ctx, member.id)
	
# Author: Sean & George
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
		
# Helper function used in "viewMemberPreferredTimes(ctx, arg)"
# Author: Sean
async def printMemberPreferredTimes(ctx, member):
	db = sqlite3.connect('testdb4.sqlite')
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
		await ctx.send("User **" + str(await bot.fetch_user(member)) + "** hasn't set their preferred times yet.")
	
	cursor.close()
	db.close()

# Author: Sean
# Display the list of all commands related to the preferred time module with instructions
# Symtax: !help
@bot.command()
async def help(ctx):
	timeFormat = "TIME: hh:mm\n"
	dateFormat = "DATE: yyyy-mm-dd\n"
	commandName = []
	commandDescription = []
	commandFormat = []
	
	commandName.append("__**addMyPreferredTime**__")
	commandDescription.append("DESCRIPTION: Adds a time that you prefer to join meetings.\n")
	commandFormat.append("COMMAND FORMAT: !addMyPreferredTime <GIVEN DAY> <START TIME> <END TIME>\n\n")
	
	commandName.append("__**deleteMyPreferredTime**__")
	commandDescription.append("DESCRIPTION: Deletes/edits existing preferred times based on the time range provided.\n")
	commandFormat.append("COMMAND FORMAT: !deleteMyPreferredTime <GIVEN DAY> <START TIME> <END TIME>\n\n")

	commandName.append("__**viewAllMembersPreferredTimes**__")
	commandDescription.append("DESCRIPTION: Shows everyone's preferred times.\n")
	commandFormat.append("COMMAND FORMAT: !viewAllMembersPreferredTimes\n\n")
	
	commandName.append("__**viewMemberPreferredTimes**__")
	commandDescription.append("DESCRIPTION: Shows you preferred times.\n")
	commandFormat.append("COMMAND FORMAT: !viewMemberPreferredTimes <USERNAME>\n\n")
	
	embed=discord.Embed(title = "Preferred Time Commands: ", color=0x109319, inline=False) 
	embed.add_field(name="Time & Date Format: ", value = timeFormat + dateFormat + "_-_-_-_-_-_-_\n", inline=False) 
	
	for i in range(len(commandName)):
		embed.add_field(name=str(commandName[i]), value=str(commandDescription[i]) + str(commandFormat[i]), inline=False) 
	
	await ctx.send(embed=embed)
	
bot.run('ODEwOTQ0NDQ5OTExNzE3OTE5.YCrA3w.FYn-U7jii5FnR8PvascyXb2IwQo')