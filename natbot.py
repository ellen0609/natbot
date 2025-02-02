#!/usr/bin/env python3
#
# natbot.py
#
# Set OPENAI_API_KEY to your API key, and then run this from a terminal.
#

from playwright.sync_api import sync_playwright
from sys import argv, exit, platform
from revChatGPT.V1 import Chatbot
from Crawler import Crawler
from ChatGPTRecord import ChatGPTRecord

import configparser, time
	
def write_file(filename, text):
	try:
		with open(filename,"w", encoding="utf-8") as f:
			f.write(text)
	except Exception as e:
		print(e)
		print("write failed.")

def read_file(filename):
	try:
		with open(filename,"r", encoding="utf-8") as f:
			content = f.read()
		return content
	except Exception as e:
		print(e)
		print("read failed.")

def chatGPT(prompt):
	config = configparser.ConfigParser()
	config.read('config.ini')

	chatbot = Chatbot(config={
		"access_token": config['chatGPT']['access_token'],
		# "conversation_id": config['chatGPT']['conversation_id'],
		# "parent_id": config['chatGPT']['parent_id'],
		# "proxy": config['chatGPT']['proxy'],
		"model": config['chatGPT']['model'], # gpt-4-browsing, text-davinci-002-render-sha, gpt-4, gpt-4-plugins
		# "plugin_ids" : [config['chatGPT']['plugin_ids']],   # Wolfram Alpha example
		# "disable_history": [config['chatGPT']['disable_history']],
	})
	
	for data in chatbot.ask(prompt):
		response = data["message"]

	chatbot.delete_conversation(chatbot.conversation_id)
	
	return response

def get_gpt_prompt(objective, url, previous_command, browser_content):
	# prompt = prompt_template
	prompt = read_file("./prompt_template/natbot_prompt_template.txt")
	prompt = prompt.replace("$objective", objective)
	prompt = prompt.replace("$url", url[:100])
	prompt = prompt.replace("$previous_command", previous_command)
	prompt = prompt.replace("$browser_content", browser_content[:4500])
	
	return prompt

def run_cmd(cmd, _crawler):
	cmd = cmd.split("\n")[0]

	if cmd.startswith("SCROLL UP"):
		_crawler.scroll("up")
	elif cmd.startswith("SCROLL DOWN"):
		_crawler.scroll("down")
	elif cmd.startswith("CLICK"):
		commasplit = cmd.split(",")
		id = commasplit[0].split(" ")[1]
		_crawler.click(id)
	elif cmd.startswith("TYPE"):
		spacesplit = cmd.split(" ")
		id = spacesplit[1]
		text = spacesplit[2:]
		text = " ".join(text)
		# Strip leading and trailing double quotes
		text = text[1:-1]

		if cmd.startswith("TYPESUBMIT"):
			text += '\n'
		_crawler.type(id, text)

	time.sleep(2)

def print_help():
	print(
		"(g) to visit url\n(u) scroll up\n(d) scroll down\n(c) to click\n(t) to type\n(e) to exit\n" +
		"(h) to view commands again\n(r/enter) to run suggested command\n(o) change objective"
	)

quiet = False
if len(argv) >= 2:
	if argv[1] == '-q' or argv[1] == '--quiet':
		quiet = True
		print(
			"Running in quiet mode (HTML and other content hidden); \n"
			+ "exercise caution when running suggested commands."
		)

if (__name__ == "__main__"):
	_crawler = Crawler()
	objective = "Make a reservation for 2 at 7pm at bistro vida in menlo park"
	print("\nWelcome to natbot! What is your objective?")

	# judge input number
	i = input()
	if len(i) > 0:
		objective = i

	# init state
	gpt_response = ""
	prev_response = ""
	chatGPTRecord = ChatGPTRecord(objective)
	_crawler.start_trace_action() # playwright trace automation
	_crawler.go_to_page("google.com")
	try:
		while True:
			browser_content = "\n".join(_crawler.crawl())
			_crawler.fetch_screenshot(chatGPTRecord.filepath, chatGPTRecord.objective, chatGPTRecord.id)
			#print(browser_content)
			#break
			prev_response = gpt_response
			gpt_prompt = get_gpt_prompt(objective, _crawler.page.url, prev_response, browser_content)
			gpt_response = chatGPT(gpt_prompt)
			gpt_response = gpt_response.strip()
			chatGPTRecord.add_record(gpt_prompt, gpt_response)
			# exit()

			if not quiet:
				print("URL: " + _crawler.page.url)
				print("Objective: " + objective)
				print("----------------\n" + browser_content + "\n----------------\n")
			if len(gpt_response) > 0:
				print("Suggested command: " + gpt_response)
			
			print_help()
			command = input()
			if command == "r" or command == "":
				run_cmd(gpt_response, _crawler)
			elif command == "g":
				url = input("URL:")
				_crawler.go_to_page(url)
			elif command == "u":
				_crawler.scroll("up")
				time.sleep(1)
			elif command == "d":
				_crawler.scroll("down")
				time.sleep(1)
			elif command == "c":
				id = input("id:")
				_crawler.click(id)
				time.sleep(1)
			elif command == "t":
				id = input("id:")
				text = input("text:")
				_crawler.type(id, text)
				time.sleep(1)
			elif command == "o":
				objective = input("Objective:")
			elif command == "e":
				_crawler.end_trace_action(chatGPTRecord.filepath)
				chatGPTRecord.convert_to_text()
				exit(0)
			else:
				print_help()
	except Exception as e:
		print(e)
		if("code: 500" in str(e)):
			chatGPTRecord.add_record(gpt_prompt, "OpenAI:  (code: 500)")
		chatGPTRecord.convert_to_text()
		_crawler.end_trace_action(chatGPTRecord.filepath)
