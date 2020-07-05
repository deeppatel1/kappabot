import discord
import requests
import glob
import asyncio
import datetime
from bs4 import BeautifulSoup

#client = discord.Client()

all_embeds = []

def call_anilist_api(id, watch_anime_url):
    print('333')
    graph_ql_query = """
        query($id: Int!) {
            Media(id: $id) {
                id
                    type
                    title {
                        romaji
                        english
                        native
                        userPreferred
                    }
                    siteUrl
                    status
                    nextAiringEpisode {
                        airingAt
                        timeUntilAiring
                        episode
                    }
                    coverImage {
                        large
                        medium
                    }
                    bannerImage
                    status
                    episodes
                    chapters
                    volumes
            }
        }
    """
    url = 'https://graphql.anilist.co'

    response = requests.post(url, json={'query': graph_ql_query, 'variables': {'id': id}})

    process_embed(response, watch_anime_url)
    print('!!!!')
    print(id)
    print('!!!!')
    print(response.json())
    return response

def process_embed(response, watch_anime_url):
    ##print('===')
    if response.status_code == 200:
        response = response.json()
        if response.get("data"):
            if response.get("data").get("Media"):
                type = response.get("data").get("Media").get("type")
                if type == "ANIME":
                    title = response.get('data').get('Media').get('title').get('romaji')
                    status = response.get('data').get('Media').get('status')
                    image = response.get('data').get('Media').get('bannerImage')
                    thumbnail = response.get('data').get('Media').get('coverImage').get('medium')
                    total_episodes = response.get('data').get('Media').get('episodes')
                    episode = None
                    next_airing_date = None
                    
                    next_episode_dict = response.get('data').get('Media').get('nextAiringEpisode')

                    if next_episode_dict and isinstance(next_episode_dict, dict):
                        episode = next_episode_dict.get("episode")
                        next_airing_date = next_episode_dict.get("airingAt")

                    create_anime_embed(name=title, status=status, airdate=next_airing_date, next_episode=episode, image=image, thumbnail=thumbnail, total_episodes=total_episodes, watch_anime_url=watch_anime_url)
                if type == "MANGA":
                    title = response.get('data').get('Media').get('title').get('romaji')
                    image = response.get('data').get('Media').get('bannerImage')
                    deal_with_manga(title, image, watch_anime_url)

def deal_with_manga(title, image_link, watch_anime_url):
    r = requests.get("https://www.mangaeden.com/en/en-manga/" + watch_anime_url)
    data = r.text

    last_5_chapters = []
    last_5_chapters_link = []
    came_out_strings = []
    counter = 0
    soup = BeautifulSoup(data)
    for table_row in soup.find_all("tr"):
        if table_row.findAll("td", class_="chapterDate") and counter < 2:
            chapter_and_name = table_row.findAll("b")[0].text
            chapter_link = table_row.find("a")["href"]
            came_out = table_row.find("td", class_="chapterDate").text

            came_out_strings.append(came_out)
            last_5_chapters.append(chapter_and_name)
            last_5_chapters_link.append(chapter_link)
            counter = counter + 1
                
    create_manga_embed(title, image_link, last_5_chapters, last_5_chapters_link, came_out_strings)

def create_manga_embed(name, image_link, mangas_and_chapter, links, came_out_strings):
    embed = discord.Embed(description="Manga - " + name)
    embed.set_image(url=image_link)
    embed.set_footer(text="Last chapter came out " + came_out_strings[0])
        
    for x in range(0, len(mangas_and_chapter)):
        manga = mangas_and_chapter[x]
        link = "https://www.mangaeden.com/" + links[x]
        embed.add_field(name=manga, value="[Read this chapter](" + link +")")
    
    all_embeds.append(embed)

def create_anime_embed(name, status, airdate, next_episode, image, thumbnail, total_episodes, watch_anime_url):
    last_episode_aired_str = "0"
    second_last_episode_str = "0"

    if next_episode:
        if next_episode < 10:
            last_episode_aired_str = "0" + str(next_episode-1)
            if (next_episode - 2 > 0):
                second_last_episode_str = "0" + str(next_episode - 2)
            else:
                second_last_episode_str = None
        else:
            last_episode_aired_str = str(next_episode-1)
            second_last_episode_str = str(next_episode-2)

        if last_episode_aired_str:
            last_episode_aired_str = "https://4anime.to/" + watch_anime_url + "-episode-" + last_episode_aired_str
        if second_last_episode_str:
            second_last_episode_str = "https://4anime.to/" + watch_anime_url + "-episode-" + second_last_episode_str

    else:
        last_episode_aired_str = str(total_episodes)
        second_last_episode_str = str(total_episodes-1)
                
        last_episode_aired_str = "https://4anime.to/" + watch_anime_url + "-episode-" + last_episode_aired_str
        second_last_episode_str = "https://4anime.to/" + watch_anime_url + "-episode-" + second_last_episode_str
            
    if status == "FINISHED":
        embed = discord.Embed(description="Anime - " + name)
        embed.set_image(url=image)
        embed.set_footer(text="Season complete!")
        if last_episode_aired_str:
            embed.add_field(name="Watch episode " + str(total_episodes), value="[Watch this episode](" + str(last_episode_aired_str) + ")")
        if second_last_episode_str:
            embed.add_field(name="Watch episode " + str(total_episodes - 1), value="[Watch this episode](" + str(second_last_episode_str) + ")")
            

    else:
        embed = discord.Embed(description="Anime - " + name, timestamp=datetime.datetime.utcfromtimestamp(airdate))
        embed.set_image(url=image)
        embed.set_footer(text="Episode " + str(next_episode) + " will air ")
        if last_episode_aired_str:
            embed.add_field(name="Watch episode " + str(next_episode - 1), value="[Watch this episode](" + str(last_episode_aired_str) + ")")
        if second_last_episode_str:
            embed.add_field(name="Watch episode " + str(next_episode - 2), value="[Watch this episode](" + str(second_last_episode_str) + ")")
    
    all_embeds.append(embed)
    
def load_all_embeds():
    with open("animeList.txt") as fp:
        line = fp.readline()
        cnt = 1
        print('222')
        while line:
            line_info = line.split(',')
            call_anilist_api(line_info[1].strip('\n'), line_info[0])
            line = fp.readline()
            cnt += 1
'''
@client.event
async def on_message(message):
    if message.content.startswith('!hello'):
        load_all_embeds()
        for embed in all_embeds:
            await message.channel.send(embed=embed)
        all_embeds.clear()

client.run('MzEzODM4NTA1Mzc1ODI1OTIw.Xv6yEw.V5JRLBtztRXstP49z4BCAAHrG-k')
'''