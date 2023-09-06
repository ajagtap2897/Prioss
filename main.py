# This is a sample Python script.
import json

import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def load_json():
    file_list = ["Userdata.json", "StreamingHistory.json", "Inferences.json"]
    json_content = []
    for file in file_list:
        with open(file, encoding="utf-8") as f:
            json_content.append(json.load(f))
    return json_content


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    json_data = load_json()
    streamingData = {}

    for item in json_data[1]:
        if item['artistName'] in streamingData.keys():
            if item['trackName'] in streamingData[item['artistName']].keys():
                streamingData[item['artistName']][item['trackName']]['freq'] += 1
                streamingData[item['artistName']][item['trackName']]['msPlayed'] += item['msPlayed']
            else:
                streamingData[item['artistName']][item['trackName']] = {"freq": 1, "msPlayed": item['msPlayed']}
        else:
            streamingData[item['artistName']] = {item['trackName']: {"freq": 1, "msPlayed": item['msPlayed']}}

    artistListByFreq = {}
    songListByFreq = {}
    artistListByTime = {}
    songListByTime = {}

    for artist, artistData in streamingData.items():
        artistTotalPlayFreq = 0
        artistTotalPlayTime = 0

        for song, song_data in artistData.items():
            artistTotalPlayFreq += song_data['freq']
            artistTotalPlayTime += song_data['msPlayed']
            songListByFreq[song] = song_data['freq']
            songListByTime[song] = song_data['msPlayed']

        artistListByFreq[artist] = artistTotalPlayFreq
        artistListByTime[artist] = artistTotalPlayTime

    artistListByFreq = sorted(artistListByFreq.items(), key=lambda x: x[1], reverse=True)[:5]
    artistListByTime = sorted(artistListByTime.items(), key=lambda x: x[1], reverse=True)[:5]
    songListByFreq = sorted(songListByFreq.items(), key=lambda x: x[1], reverse=True)[:5]
    songListByTime = sorted(songListByTime.items(), key=lambda x: x[1], reverse=True)[:5]

    monthlyViewData = {}

    for item in json_data[1]:
        date = datetime.strptime(item['endTime'], "%Y-%m-%d %H:%M").date()
        dataKey = str(date.year) + "-" + str(date.month)
        if dataKey in monthlyViewData.keys():
            monthlyViewData[dataKey]['freq'] += 1
            monthlyViewData[dataKey]['msPlayed'] += item['msPlayed']
        else:
            monthlyViewData[dataKey] = {'freq': 1, 'msPlayed': item['msPlayed']}

    inferPartyNo = []
    inferPartyName = []
    inferPartyValue = []

    for item in json_data[2]['inferences']:
        inferenceData = item.split('P_')
        inferPartyNo.append(inferenceData[0] + "P")
        inferPartyName.append(inferenceData[1])
        inferPartyValue.append(1)

    # df = pd.DataFrame({
    #     "partyNo": inferPartyNo,
    #     "partyName": inferPartyName,
    #     "partyValue": inferPartyValue
    # })
    # sunburstFig = px.sunburst(df, path=["partyNo", "partyName"], values="partyValue")

    fig = make_subplots(5, 2,
                        specs=[[{"type": "Table", "colspan": 2}, None], [{"type": "Bar"}, {"type": "Bar"}],
                               [{"type": "Bar"}, {"type": "Bar"}],
                               [{"type": "Bar"}, {"type": "Bar"}], [{"type": "Bar", "colspan": 2}, None]],
                        subplot_titles=("User Data", "Top 5 Artists by Frequency", "Top 5 Artists by listening time",
                                        "Top 5 Song by Frequency", "Top 5 Songs by listening time",
                                        "Monthly View Frequency", "Monthly Viewing Time", "Inference Data")
                        )

    fig.add_trace(go.Table(
        header=dict(values=["Field", "Data"]),
        cells=dict(
            values=[list(json_data[0].keys()), [("" if value is None else value) for value in json_data[0].values()]])),
        row=1, col=1)

    fig.add_trace(
        go.Bar(x=[item[0] for item in artistListByFreq], y=[item[1] for item in artistListByFreq],
               showlegend=False),
            row=2, col=1)
    fig.add_trace(go.Bar(x=[item[0] for item in artistListByTime], y=[item[1] / 60000 for item in artistListByTime],
                         showlegend=False),
                  row=2, col=2)

    fig.add_trace(
        go.Bar(x=[item[0] for item in songListByFreq], y=[item[1] for item in songListByFreq], showlegend=False), row=3,
        col=1)
    fig.add_trace(go.Bar(x=[item[0] for item in songListByTime], y=[item[1] / 60000 for item in songListByTime],
                         showlegend=False), row=3,
                  col=2)

    fig.add_trace(
        go.Bar(x=list(monthlyViewData.keys()), y=[item['freq'] for item in monthlyViewData.values()], showlegend=False),
        row=4,
        col=1)
    fig.add_trace(
        go.Bar(x=list(monthlyViewData.keys()), y=[item['msPlayed'] / 60000 for item in monthlyViewData.values()],
               showlegend=False),
        row=4, col=2)

    fig.add_trace(
        go.Bar(x=inferPartyNo, y=inferPartyValue, hovertext=inferPartyName, showlegend=False),
        row=5, col=1
    )

    fig.update_xaxes(title_text="Artist", row=2, col=1)
    fig.update_xaxes(title_text="Artist", row=2, col=2)
    fig.update_xaxes(title_text="Song", row=3, col=1)
    fig.update_xaxes(title_text="Song", row=3, col=2)
    fig.update_xaxes(title_text="Month", row=4, col=1)
    fig.update_xaxes(title_text="Month", row=4, col=2)
    fig.update_xaxes(title_text="Party Type", row=5, col=1)

    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    fig.update_yaxes(title_text="Time (in mins)", row=2, col=2)
    fig.update_yaxes(title_text="Frequency", row=3, col=1)
    fig.update_yaxes(title_text="Time (in mins)", row=3, col=2)
    fig.update_yaxes(title_text="Frequency", row=4, col=1)
    fig.update_yaxes(title_text="Time (in mins)", row=4, col=2)
    fig.update_yaxes(title_text="No. of Parties", row=5, col=1)

    fig.update_layout(height=1600)
    fig.show()
