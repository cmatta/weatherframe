import inky
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import requests
import io
from PIL import Image
import matplotlib.dates as mdates

def get_tide_data(station_id):
    # Define a start and end time for tide data
    start_time = datetime.datetime.now() - datetime.timedelta(hours=12)
    end_time = datetime.datetime.now() + datetime.timedelta(hours=12)

    # Format start_time and end_time for the API request
    start_time_str = start_time.strftime("%Y%m%d %H:%M")
    end_time_str = end_time.strftime("%Y%m%d %H:%M")

    # Specify the URL for the NOAA API
    noaa_api_url = f"https://tidesandcurrents.noaa.gov/api/datagetter?begin_date={start_time_str}&end_date={end_time_str}&station={station_id}&product=predictions&datum=MLLW&units=english&time_zone=gmt&interval=h&format=json"

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
    img_width, img_height = 800, 480
    dpi = 100

    # Plot the tide data
    fig, ax = plt.subplots(figsize=(img_width / dpi, img_height / dpi), dpi=dpi)
    ax.plot(tide_data['t'], tide_data['v'])
    ax.fill_between(tide_data['t'], tide_data['v'], color='skyblue', alpha=0.4)

    # Add a vertical red line for the current time
    current_time = datetime.datetime.now()
    ax.axvline(current_time, color='red', linestyle='--', label='Current time')

    # Customize the plot
    ax.set_xlabel("Time")
    ax.set_ylabel("Tide height (ft)")
    ax.set_title("Tide - Madison, CT")
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=30)
    last_updated = f"Updated: {current_time.strftime('%Y-%m-%d %H:%M')}"
    fig.text(0.5, 0.95, last_updated, fontsize=10, ha='right', va='center',
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))    plt.tight_layout()

    # Save the plot as a PNG in a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Create a PIL Image object from the buffer
    image = Image.open(buf)

    return image

if __name__ == "__main__":
    tide_data = get_tide_data(8465705)
    img = plot_tide_data(tide_data)
    inky.inky_display = inky.auto()
    inky.inky_display.set_image(img)
    inky.inky_display.set_border(inky.BLACK)
    inky.inky_display.show()