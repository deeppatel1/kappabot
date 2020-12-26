import sched, time, schedule, discord
from datetime import datetime, timedelta
from get_animes_and_mangas import call_anilist_api
from post_discord_webhook import sendWebhookListEmbeds


class AnimeObject:
    def __init__(self, title, status, image, thumbnail, total_episodes, next_airing_episode, next_airing_date, four_anime_url):
        self.title = title
        self.status = status
        self.image = image
        self.thumbnail = thumbnail
        self.total_episodes = total_episodes
        self.next_airing_episode = next_airing_episode
        self.next_airing_date = next_airing_date
        self.four_anime_url = four_anime_url


def post_anime_episodes():

    with open("animeList.txt") as fp:
        line = fp.readline()
        cnt = 1
        while line:
            line_info = line.split(',')
            anilist_id = line_info[1].strip('\n')
            anime_name = line_info[0]

            anilist_resp = call_anilist_api(anilist_id)
            anime_object = get_next_airing_date(anilist_resp, anime_name)
            
            if anime_object:
                do_reminders(anime_object)


            line = fp.readline()
            cnt += 1


def do_reminders(anime_object):
    airing_date = anime_object.next_airing_date
    airing_datetime = datetime.fromtimestamp(airing_date)

    anime_title = anime_object.title
    episode = anime_object.next_airing_episode
    total_episodes = anime_object.total_episodes
    four_anime_url = anime_object.four_anime_url
    thumbnail_url = anime_object.thumbnail
    image = anime_object.image

    if (airing_datetime - datetime.now()).days == 0:
        airing_datetime = airing_datetime + timedelta(minutes=30)
        hours = airing_datetime.hour
        minutes = airing_datetime.minute

        if hours < 10:
            hours = "0" + str(hours)
        if minutes < 10:
            minutes = "0" + str(minutes)

        hour_minutes_str = str(hours) + ":" + str(minutes)

        # schedule.every(2).seconds.do(set_reminder, airing_datetime, anime_title, episode, total_episodes,  four_anime_url, thumbnail_url, image)
        schedule.every().day.at(hour_minutes_str).do(set_reminder, airing_datetime, anime_title, episode, total_episodes,  four_anime_url, thumbnail_url, image)


def set_reminder(airing_datetime, anime_title, episode, total_episodes, four_anime_url_name, thumbnail, image):

    message = "Episode " + str(episode) + "/" + str(total_episodes) + " has aired! CLICK TO WATCH"

    if episode < 10:
        episode_str = "0" + str(episode)
    else:
        episode_str = str(episode)

    url = "https://4anime.to/" + four_anime_url_name + "-episode-" + episode_str

    embed = discord.Embed(title=message, url=url, timestamp=airing_datetime)
    embed.set_image(url=image)
    embed.set_footer(text="Aired")

    sendWebhookListEmbeds(username=anime_title, avatar_url=thumbnail, embeds=[embed])
    
    return


def get_next_airing_date(anilist_resp, four_anime_url):
    response = anilist_resp
    if response.status_code == 200:
        response = response.json()
        if response.get("data") and response.get("data").get("Media"):
            type = response.get("data").get("Media").get("type")
            if type == "ANIME":
                next_airing_date = None
                
                next_episode_dict = response.get('data').get('Media').get('nextAiringEpisode')
                if next_episode_dict and isinstance(next_episode_dict, dict):
                    title = response.get('data').get('Media').get('title').get('romaji')
                    status = response.get('data').get('Media').get('status')
                    image = response.get('data').get('Media').get('bannerImage')
                    thumbnail = response.get('data').get('Media').get('coverImage').get('medium')
                    total_episodes = response.get('data').get('Media').get('episodes')

                    next_episode_dict = response.get('data').get('Media').get('nextAiringEpisode')

                    if next_episode_dict and isinstance(next_episode_dict, dict):
                        episode = next_episode_dict.get("episode")
                        next_airing_date = next_episode_dict.get("airingAt")

                        anime_obj = AnimeObject(title = title, status = status, image = image, thumbnail = thumbnail, total_episodes = total_episodes, next_airing_episode = episode, next_airing_date= next_airing_date, four_anime_url = four_anime_url)
                        return anime_obj

    return None


# At startup, run this once:
post_anime_episodes()

while 1:
    schedule.run_pending()
    time.sleep(300)