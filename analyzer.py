#!/usr/bin/env python3

import os
import sys
import logging
import datetime
from typing import List

import exif


def get_exif_ts(img: exif.Image) -> datetime.datetime:
    return datetime.datetime.strptime(img.datetime, r"%Y:%m:%d %H:%M:%S")


class WildlifeEvent:
    def __init__(self, images: List[exif.Image]):
        assert images
        self.images = images

    @property
    def first_ts(self) -> datetime.datetime:
        return get_exif_ts(self.images[0])

    @property
    def last_ts(self) -> datetime.datetime:
        return get_exif_ts(self.images[-1])

    @property
    def duration(self) -> datetime.timedelta:
        return self.last_ts - self.first_ts

    @property
    def first_ts_rounded(self) -> datetime.datetime:
        """
        First timestamp, rounded to nearest minute
        """
        timestamp = self.first_ts.timestamp()
        timestamp = round(timestamp / 60) * 60
        return datetime.datetime.fromtimestamp(timestamp)

    def get_report_row(self) -> List[str]:
        """
        initials
        initials
        camera id
        date
        time
        duration
        species
        n individuals
        certainty
        n photos
        activity
        B&W/Color
        direction
        good?
        comments
        """
        columns = []

        # Skip: 2 initials + camera id
        for _ in range(3):
            columns.append("")

        ts = self.first_ts_rounded
        # Date in MM/DD/YYYY
        columns.append(ts.strftime(r"%m/%d/%Y"))

        # Time in HH/MM
        columns.append(ts.strftime(r"%H:%M"))

        # Duration in minutes (rounded to nearest)
        if self.duration.seconds <= 60:
            columns.append("")
        else:
            mins = round(self.duration.seconds / 60)
            columns.append(f"{mins}")

        # Skip: species, n individuals, certainty
        for _ in range(3):
            columns.append("")

        # N Photos. Add parentheses to indicate user review
        columns.append(f"({len(self.images)})")

        # Skip: activity
        columns.append("")

        # B&W or Color
        if self.images[0].scene_capture_type == exif.SceneCaptureType.NIGHT_SCENE:
            columns.append("B&W")
        else:
            columns.append("Color")

        # Skip: direction, is good, comments
        for _ in range(3):
            columns.append("")

        # Bonus! Image range
        columns.append(
            os.path.basename(self.images[0].path)
            + " - "
            + os.path.basename(self.images[-1].path)
        )

        return columns

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    GROUP_TS_THRESHOLD = datetime.timedelta(minutes=30)

    img_folder = sys.argv[1]

    if not os.path.isdir(img_folder):
        logging.error("Target path is not a directory: %s", img_folder)
        sys.exit(1)

    # Load all images first
    images = [] # type: List[exif.Image]
    for path in os.listdir(img_folder):
        path = os.path.join(img_folder, path)
        if not os.path.isfile(path):
            logging.warning("Skipping path: %s", path)
            continue

        with open(path, 'rb') as f:
            img = exif.Image(f)
            # monkey-patch the path into the image object for convenience
            img.path = path
            if not img.has_exif:
                logging.warning("File is missing exif. Skipping: %s", path)
                continue
            images.append(img)

    # Sort images by timestamp
    images.sort(key=lambda x: x.datetime)

    # Create image groups
    current_group_images = [] # type: List[exif.Image]
    prev_ts = datetime.datetime(1,1,1)
    wildlife_events = [] # type: List[WildlifeEvent]

    for img in images:
        ts = get_exif_ts(img)

        if (prev_ts + GROUP_TS_THRESHOLD) < ts:
            # this photo's timestamp is sufficiently in the future to start a new group
            if current_group_images:
                wildlife_events.append(WildlifeEvent(current_group_images))
                current_group_images = []
        current_group_images.append(img)
        prev_ts = ts

    # collect last event
    if current_group_images:
        wildlife_events.append(WildlifeEvent(current_group_images))

    # report events:
    for event in wildlife_events:
        print("\t".join(event.get_report_row()))
