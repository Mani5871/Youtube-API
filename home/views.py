import json
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
import requests
import time
import aiohttp
import asyncio
from asgiref.sync import sync_to_async
import random
from .models import Video

# Create your views here.
# Index view to display the front page
def index(request):
    return render(request, 'index.html')


# Creates a New Video object by taking all the necessary parameters
@sync_to_async
def create_object(entry, category):
    id = entry['id']['videoId']
    title = entry['snippet']['title']
    description = entry['snippet']['description']
    thumbnail = entry['snippet']['thumbnails']['medium']['url']
    date = entry['snippet']['publishTime']
    date = date[0:10]
    width = entry['snippet']['thumbnails']['medium']['width']
    height = entry['snippet']['thumbnails']['medium']['height']
    print(id)
    
    try:
        video = Video.objects.create(id = id, title=title, description=description, thumbnail=thumbnail , date = date, width = width, height = height, category = category)
        video.save()
    except:
        pass
    

# Async method to store the required videos of all the mentioned categories
async def get_names_async(number):
    search_url = 'https://www.googleapis.com/youtube/v3/search'

    # Took a list of famous categories to generate the data
    categories = ['Comedy', 'Entertainment', 'Music', 'News', 'Sports', 'Tech', 'Travel', 'Education', 'Business', 'Food', 'Gaming', 'Howto', 'Nonprofit', 'Science', 'Shows', 'Trailers']

    async with aiohttp.ClientSession() as session:
        # Runs 5 time and generates the data for random categories in the above list
        for num in range(0, 5):
            category = categories[random.randint(0, len(categories)-1)]
            print(category)
            search_params = {
            'part' : 'snippet',
            'q' : category,
            'key' : settings.YOUTUBE_API_KEY,
            'liveBroadcastContent' : 'None',
            'maxResults' : number,
            'publishedAfter' : '2015-01-01T00:00:00Z',
            'type' : 'video'
        }
            # Gets the data from the API using asyncio
            async with session.get(search_url, params=search_params) as resp:
                results = await resp.json()
                results = results['items']
                for entry in results:
                    id = entry['id']['videoId']
                    title = entry['snippet']['title']
                    description = entry['snippet']['description']
                    thumbnail = entry['snippet']['thumbnails']['medium']['url']
                    date = entry['snippet']['publishTime']
                    date = date[0:10]
                    width = entry['snippet']['thumbnails']['medium']['width']
                    height = entry['snippet']['thumbnails']['medium']['height']

                    # checking whether the object is already present in the database
                    # If existed, there will be no exception and the object will not be created as there is continue keyword
                    try:
                        obj = sync_to_async(Video.objects.get(pk = id))
                        continue
                    except:
                        pass
                    
                    # Adjusting the Lengths of attributes
                    if len(title) > 100:
                        entry['snippet']['title'] = title[:100] + '...'
                    if len(description) > 100:
                        entry['snippet']['description'] = description[:100] + '...'
                    if len(thumbnail) > 100:
                        entry['snippet']['thumbnails']['medium']['url'] = thumbnail[:100] + '...'
                    
                    # Creating the object and saving it by creating a task
                    asyncio.create_task(create_object(entry, category))
                #waiting for 5 seconds
                await asyncio.sleep(0.5)
    return redirect('/')


def store_videos(request):

    # Getting the number of videos to be generated
    if request.method == 'POST':
        number = request.POST['number']
        number = int(number)
    # Setting the POlicy so that no runtimes error occurs
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(get_names_async(number))
    return redirect('/')

# Returns the List of All videos that have stored in the database
def get_list(request):
    entries = Video.objects.all().order_by('-date')
    print(type(entries))
    videos = []
    for entry in entries:
        # Appending the Video is to youtube url
        url = 'https://www.youtube.com/watch?v='
        url = url + entry.id
        context = {
                'title': entry.title,
                'description': entry.description,
                'thumbnail':entry.thumbnail,
                'url': url,
                'width' : entry.width,
                'height' : entry.height,
                'date' : entry.date,
                'category' : entry.category
            }
        videos.append(context)
    
    # Redirects to Error page if there are no videos in the database
    if(len(videos) == 0):
        return render(request, 'error.html')
        
    context = {
        'videos' : videos
    }
    return render(request, 'list.html', context)

# View to Display the search page
def search(request):
    return render(request, 'search.html')


# return the video details that matches either title or description
def get_by_title_description(request):
    title_name = request.POST.get('title')
    description = request.POST.get('description')

    # If title and description are not provided, redirects to error page
    if title_name == "" and description == "":
        return render(request, 'error.html')

    # Checks for video that matches title
    for v in Video.objects.all():
        if v.title == title_name:
            url = 'https://www.youtube.com/watch?v='
            url = url + v.id
            context = {
                'title': v.title,
                'description': v.description,
                'thumbnail': v.thumbnail,
                'url': url,
                'width' : v.width,
                'height' : v.height,
                'date' : v.date,
                'category' : v.category
            }
            return render(request, 'title.html', context)

    # checks for video that matches description
    for v in Video.objects.all():
        if v.description == description:
            url = 'https://www.youtube.com/watch?v='
            url = url + v.id
            context = {
                'title': v.title,
                'description': v.description,
                'thumbnail': v.thumbnail,
                'url': url,
                'width' : v.width,
                'height' : v.height,
                'date' : v.date
            }
            return render(request, 'title.html', context)
    return render(request, 'error.html')