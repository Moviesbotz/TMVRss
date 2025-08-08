import asyncio
import re
import requests
import time
import os
from bs4 import BeautifulSoup
from telegram import Update
from telegram.constants import ParseMode
from telegram import Bot
from urllib.parse import urlparse, parse_qs

from keep_alive import keep_alive

username = os.environ['REPL_OWNER']
# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = os.environ['BOT_TOKEN']
# Replace 'YOUR_CHAT_ID' with the chat ID where you want to send the new links
# chat_id = '-1001765000487'
chat_id = os.environ['CHAT_ID']
# Website URL to monitor for new links
website_url = os.environ['WEBSITE_URL']  #TMV
global arr
global magnet_arr
arr = []
magnet_arr = []


def get_magnet_links(url):
  try:
    response = requests.get(url)
    if response.status_code == 200:
      soup = BeautifulSoup(response.content, "html.parser")
      magnet_links = []

      # Find all anchor tags with magnet links using regular expression
      for anchor in soup.find_all("a",
                                  href=re.compile(r"magnet:\?xt=urn:btih:")):
        magnet_link = anchor["href"]

        # Parse the magnet link to extract the text
        parsed_url = urlparse(magnet_link)
        params = parse_qs(parsed_url.query)
        text = params.get(
            'dn',
            [''])[0]  # 'dn' is the query parameter that contains the text

        magnet_links.append((text, magnet_link))

      return magnet_links

    else:
      print("Error: Failed to fetch the website.")
      return []

  except Exception as e:
    print("Error:", e)
    return []


def get_website_content(url):
  try:
    response = requests.get(url)
    if response.status_code == 200:
      return response.content

    print("Error: Failed to fetch the website.")
    return None

  except Exception as e:
    print("Error:", e)
    return None


def extract_links_from_content(content):
  try:
    soup = BeautifulSoup(content, "html.parser")
    links = []
    count = 0
    for element in soup.find_all("a", href=True):
      link = element["href"]
      if ("forums" in link and "topic" in link and "-" in link
          and not link.endswith("/") and "1tamilmv" in link
          or "1tamilblasters" in link) and count < 10:
        links.append(link)
        count += 1

    return links

  except Exception as e:
    print("Error:", e)
    return []


async def send_new_links_to_telegram(link):
  if not link:
    return
  # Create a bot instance using the token
  bot = Bot(token=bot_token)
  try:
    await bot.send_message(chat_id=chat_id,
                           text=f"New link:\n\n{link}",
                           parse_mode=ParseMode.HTML)
  except:
    await asyncio.sleep(60)
    await bot.send_message(chat_id=chat_id,
                           text=f"New link:\n\n{link}",
                           parse_mode=ParseMode.HTML)


async def send_magnet_to_telegram(title, link):
  if not link:
    return
  # Create a bot instance using the token
  bot = Bot(token=bot_token)
  try:
    if title:
      message = f"<b>Name:</b> <i>{title}</i>\n\n<b>URL:</b> <code>{link}</code>"
      await bot.send_message(chat_id=chat_id,
                             text=message,
                             parse_mode=ParseMode.HTML)
    else:
      await bot.send_message(chat_id=chat_id,
                             text=f"<code>{link}</code>",
                             parse_mode=ParseMode.HTML)
  except:
    await asyncio.sleep(60)
    # await bot.send_message(
    #     chat_id=chat_id,
    #     text=
    #     f"<b>Name: </b><i>{title}</i>\n\n<b>Magnet Link: </b><code>{link}</code>",
    #     parse_mode=ParseMode.HTML)
    await bot.send_message(chat_id=chat_id,
                           text=f"<b>Name: </b><i>{title}</i>",
                           parse_mode=ParseMode.HTML)
    await bot.send_message(chat_id=chat_id,
                           text=f"<code>{link}</code>",
                           parse_mode=ParseMode.HTML)


def check_for_new_links():
  print("✅ Bot Started... Monitoring site for new links.")
  content = get_website_content(website_url)
  # print(f"content: \n{content}")
  links = extract_links_from_content(content)
  # print(f"links: \n{links}")
  for link in links:
    arr.append(link)
    magnet_links = get_magnet_links(link)
    if magnet_links:
      for mlink in magnet_links:
        magnet_arr.append(mlink[1])
  asyncio.run(send_magnet_to_telegram(None, "Restarting..."))
  print("Credits to Developer: ", username)
  asyncio.run(send_magnet_to_telegram(None, "Credits to Developer: " + username))
  while True:
    content = get_website_content(website_url)
    links = extract_links_from_content(content)
    for link in links:
      if link not in arr:
        arr.append(link)
        print(link)
        asyncio.run(send_new_links_to_telegram(link))
      magnet_links = get_magnet_links(link)
      if magnet_links:
        for text, link in magnet_links:
          if link not in magnet_arr:
            magnet_arr.append(link)
            asyncio.run(send_magnet_to_telegram(text, link))

    time.sleep(300)  # Wait for 5 minutes before checking again


keep_alive()
if __name__ == "__main__":
  check_for_new_links()
