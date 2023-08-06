"""A class to encapsulate the ComicBookInfo data"""

# Copyright 2012-2014 Anthony Beville

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
from collections import defaultdict
from datetime import datetime

from comicapi import utils
from comicapi.genericmetadata import GenericMetadata

logger = logging.getLogger(__name__)


class ComicBookInfo:
    def metadata_from_string(self, string):

        cbi_container = json.loads(str(string, "utf-8"))

        metadata = GenericMetadata()

        cbi = defaultdict(lambda: None, cbi_container["ComicBookInfo/1.0"])

        metadata.series = utils.xlate(cbi["series"])
        metadata.title = utils.xlate(cbi["title"])
        metadata.issue = utils.xlate(cbi["issue"])
        metadata.publisher = utils.xlate(cbi["publisher"])
        metadata.month = utils.xlate(cbi["publicationMonth"], True)
        metadata.year = utils.xlate(cbi["publicationYear"], True)
        metadata.issue_count = utils.xlate(cbi["numberOfIssues"], True)
        metadata.comments = utils.xlate(cbi["comments"])
        metadata.genre = utils.xlate(cbi["genre"])
        metadata.volume = utils.xlate(cbi["volume"], True)
        metadata.volume_count = utils.xlate(cbi["numberOfVolumes"], True)
        metadata.language = utils.xlate(cbi["language"])
        metadata.country = utils.xlate(cbi["country"])
        metadata.critical_rating = utils.xlate(cbi["rating"])

        metadata.credits = cbi["credits"]
        metadata.tags = cbi["tags"]

        # make sure credits and tags are at least empty lists and not None
        if metadata.credits is None:
            metadata.credits = []
        if metadata.tags is None:
            metadata.tags = []

        # need the language string to be ISO
        if metadata.language is not None:
            metadata.language = utils.get_language(metadata.language)

        metadata.is_empty = False

        return metadata

    def string_from_metadata(self, metadata):

        cbi_container = self.create_json_dictionary(metadata)
        return json.dumps(cbi_container)

    def validate_string(self, string):
        """Verify that the string actually contains CBI data in JSON format"""

        try:
            cbi_container = json.loads(string)
        except:
            return False

        return "ComicBookInfo/1.0" in cbi_container

    def create_json_dictionary(self, metadata):
        """Create the dictionary that we will convert to JSON text"""

        cbi = {}
        cbi_container = {
            "appID": "ComicTagger/" + "1.0.0",
            "lastModified": str(datetime.now()),
            "ComicBookInfo/1.0": cbi,
        }  # TODO: ctversion.version,

        # helper func
        def assign(cbi_entry, md_entry):
            if md_entry is not None or isinstance(md_entry, str) and md_entry != "":
                cbi[cbi_entry] = md_entry

        assign("series", utils.xlate(metadata.series))
        assign("title", utils.xlate(metadata.title))
        assign("issue", utils.xlate(metadata.issue))
        assign("publisher", utils.xlate(metadata.publisher))
        assign("publicationMonth", utils.xlate(metadata.month, True))
        assign("publicationYear", utils.xlate(metadata.year, True))
        assign("numberOfIssues", utils.xlate(metadata.issue_count, True))
        assign("comments", utils.xlate(metadata.comments))
        assign("genre", utils.xlate(metadata.genre))
        assign("volume", utils.xlate(metadata.volume, True))
        assign("numberOfVolumes", utils.xlate(metadata.volume_count, True))
        assign("language", utils.xlate(utils.get_language_from_iso(metadata.language)))
        assign("country", utils.xlate(metadata.country))
        assign("rating", utils.xlate(metadata.critical_rating))
        assign("credits", metadata.credits)
        assign("tags", metadata.tags)

        return cbi_container

    def write_to_external_file(self, filename, metadata):

        cbi_container = self.create_json_dictionary(metadata)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(json.dumps(cbi_container, indent=4))
