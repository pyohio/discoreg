from pathlib import Path

import arrow
from ruamel.yaml import YAML

yaml = YAML()

TALKS_DIR = "~/checkouts/pyohio/static-website/data/talks"


def load_talks():
    talks_path = Path.expanduser(Path(TALKS_DIR))
    talk_data = []
    for talk_file in talks_path.glob("**/*.yaml"):
        with open(talk_file) as talk_fh:
            talk_data.append(yaml.load(talk_fh))
    return talk_data


def create_notifications(model, talks):
    for talk in talks:
        if talk["stream_timestamp"] != "":
            print(talk["title"])
            time_str = f"2021-07-31 {(talk['stream_timestamp'])}-0400"
            print(time_str)
            talk_timestamp = arrow.get(time_str)
        else:
            print(f"No timestamp for {talk['title']}!")
            continue

        new_notification = model(
            title=talk["title"],
            url=f"https://www.pyohio.org/2021/program/talks/{talk['slug']}",
            description="",
            color_hex_string="502962",
            author_name="Up next:",
            send_by=talk_timestamp.isoformat()
        )

        if talk["type"].endswith("Talk"):
            new_notification.description = (
                f"{talk['type']} by {talk['speakers'][0]['name']}"
            )
        if talk.get("youtube_url"):
            new_notification.field_1_name = "YouTube Video:"
            new_notification.field_1_value = f"[{talk['youtube_url']}]({talk['youtube_url']})"
        
        if talk["type"].endswith("Talk"):
            new_notification.field_2_name = "Q&A Channel:"
            if talk["qna"]:
                new_notification.field_2_value = f"<#{talk['discord_channel_id']}>"
            else:
                new_notification.field_2_value = "No speaker Q&A for this talk"

        if talk.get("content_warnings"):
            new_notification.field_3_name = "⚠️ Content Warning:"
            new_notification.field_3_value = talk["content_warnings"]

        new_notification.save()
