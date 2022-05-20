import os
from git import Repo
import feedparser
import json
from datetime import datetime

repo = Repo(os.getenv('.'))
assert not repo.bare

commits = list(repo.iter_commits(grep="^.\{11\}$"))

commits_set = set()

for commit in commits:
    commits_set.add(commit.message.replace('\n', ''))

youtube_rss_url = 'https://www.youtube.com/feeds/videos.xml?channel_id=' + os.getenv('YOUTUBE_CHANNEL_ID')
youtube_rss_feed = feedparser.parse(youtube_rss_url)

# clean YouTube id string
print('--Cleaning YouTube ID string')
for entry in youtube_rss_feed.entries:
    entry['id'] = entry['id'].replace('yt:video:', '')
    print(entry['id'] + ': ' + entry['title'])

print('--Finding new videos')
for entry in reversed(youtube_rss_feed.entries):
    if entry['id'] not in commits_set:
        print(entry['id'] + ': ' + entry['title'])
        podcast_json_obj = json.dumps({'id': entry['id'], 'title': entry['title'], 'description': entry['description'], 'published': entry['published']})

        with open("episode.json", "w") as file:
            file.write(podcast_json_obj)

        # Commit changes
        os.system(f'git add episode.json')
        # Commit message and push
        os.system(f'git commit -m "{entry.id}" && git push')

