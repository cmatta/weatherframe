import inky
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import requests
from scipy.signal import argrelextrema
import numpy as np
import io
from PIL import Image, ImageDraw
import matplotlib.dates as mdates
import time

def get_tide_data(station_id):
    # Define a start and end time for tide data
    start_time = datetime.datetime.now() - datetime.timedelta(hours=12)
    end_time = datetime.datetime.now() + datetime.timedelta(hours=12)

    # Format start_time and end_time for the API request
    start_time_str = start_time.strftime("%Y%m%d %H:%M")
    end_time_str = end_time.strftime("%Y%m%d %H:%M")

    # determine if it's daylight savings
    current_time = time.time()
    local_time = time.localtime(current_time)
    dst_in_effect = local_time.tm_isdst > 0 or time.daylight > 0
    if dst_in_effect:
        tz = "lst_ldt"
    else:
        tz = "lst"
    # Specify the URL for the NOAA API
    noaa_api_url = f"https://tidesandcurrents.noaa.gov/api/datagetter?begin_date={start_time_str}&end_date={end_time_str}&station={station_id}&product=predictions&datum=MLLW&units=english&time_zone={tz}&interval=h&format=json"
 
    # Send a request to the NOAA API and parse the response
    response = requests.get(noaa_api_url)
    tide_data = response.json()

    # Convert the tide data into a Pandas DataFrame
    tide_df = pd.DataFrame(tide_data['predictions'])
    tide_df['t'] = pd.to_datetime(tide_df['t'], format="%Y-%m-%d %H:%M")
    tide_df['v'] = pd.to_numeric(tide_df['v'])

    return tide_df


def plot_tide_data(tide_data):
    # Set the desired image size and DPI
    img_width, img_height = 800, 240
    dpi = 100



    tide_times = tide_data['t']
    tide_heights = tide_data['v']

  
    # Create a new figure and axis for the plot
    fig, ax = plt.subplots(figsize=(img_width / dpi, img_height / dpi), dpi=dpi)

    # Plot the tide heights vs. time
    ax.plot(tide_times, tide_heights)

    # Add a vertical red line for the current time
    current_time = datetime.datetime.now()
    ax.axvline(current_time, color='red', linestyle='--', label='Now')

    # Fill the area below the line graph with a blue color
    ax.fill_between(tide_times, tide_heights, color="blue", alpha=0.2)

    # Customize the plot
    ax.set_ylabel("Tide height (ft)")
    ax.set_title("Tides")
    ax.legend()
    ax.grid(True)
    ax.tick_params(axis='x', which='both', labelbottom=False)

    # Annotate the peaks and valleys of the tide graph with the 12-hour am/pm time
    for i in range(1, len(tide_heights)-1):
        # peaks
        if tide_heights[i-1] < tide_heights[i] and tide_heights[i] > tide_heights[i+1]:
            tide_time = tide_times[i].strftime('%-I:%M %p')
            ax.annotate(tide_time, (tide_times[i], tide_heights[i]), xytext=(-8, 8), textcoords='offset points', ha='left', va='bottom', fontsize=8, color='blue')
        # valleys
        elif tide_heights[i-1] > tide_heights[i] and tide_heights[i] < tide_heights[i+1]:
            tide_time = tide_times[i].strftime('%-I:%M %p')
            ax.annotate(tide_time, (tide_times[i], tide_heights[i]), xytext=(-8, -8), textcoords='offset points', ha='left', va='top', fontsize=8, color='blue')


    plt.tight_layout()

    # Save the plot as a PNG in a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Create a PIL Image object from the buffer
    image = Image.open(buf)

    return image

if __name__ == "__main__":
    WIDTH = 800
    HEIGHT = 480
    PADDING = 5
    REFRESH = 5*60

    while True:
        tide_data = get_tide_data(8465705)
        tide_img = plot_tide_data(tide_data)
            
        image = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        image.paste(tide_img, (0,240))

        inky.inky_display = inky.auto()
        inky.inky_display.set_image(image)
        inky.inky_display.set_border(inky.BLACK)
        inky.inky_display.show()
        time.sleep(REFRESH)