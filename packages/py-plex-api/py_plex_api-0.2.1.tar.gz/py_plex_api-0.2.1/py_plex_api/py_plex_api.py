from xml.etree import ElementTree
import requests
from loguru import logger
from typing import List, Dict
from tqdm import tqdm

logger.remove(0)
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True,)

class PyPlexAPI:
    def __init__(self, ip_address: str, port: str, plex_api_token: str):
        """

        :param ip_address:
        :type ip_address: str
        :param port:
        :type port: str
        :param plex_api_token:
        :type plex_api_token: str
        """
        self.class_name = type(self).__name__
        logger.info(f"{self.class_name} initialised")

        # created like this so it can be passed as params
        self.token = {"X-Plex-Token": plex_api_token}
        
        self.server_url = f"http://{ip_address}:{port}"
        # No return types on the below, throws conn error if unsuccessful
        self._test_library_exists()

    def _test_library_exists(self) -> None:
        """
        
        :return: None
        """
        logger.info("Testing server connection")
        url = self.server_url
        response = requests.get(url=url, params=self.token)
        if response.status_code == 200:
            logger.info("Server found")
        else:
            raise ConnectionError("Could not find server")
    
    @staticmethod
    def extract_keys_from_xml(response_content: bytes) -> List[Dict]:
        """
        
        :param response_content:
        :return:
        """
        all_contents = []
        response_xml_root = ElementTree.fromstring(response_content)
        for child in response_xml_root:
            content_details = {
                    "key": child.attrib.get("key"),
                    "title": child.attrib.get("title"),
                    "type": child.attrib.get("type")
            }
            all_contents.append(content_details)
        return all_contents
    
    def get_keys_from_plex_api(self, plex_endpoint: str) -> List[Dict]:
        """
            Only returns key + name
        :param plex_endpoint:
        :type plex_endpoint:
        :return:
        :rtype:
        """
        api_url = self.server_url + plex_endpoint
        response = requests.get(url=api_url, params=self.token)
        plex_keys = self.extract_keys_from_xml(response_content=response.content)
        return plex_keys
    
    def get_movie_details(self, plex_endpoint: str) -> Dict:
        """
        :param plex_endpoint:
        :return:
        """
        api_url = self.server_url + plex_endpoint
        response = requests.get(url=api_url, params=self.token)
        
        response_xml_root = ElementTree.fromstring(response.content)
        
        media_details = {}
        for child in response_xml_root:
            media_details["title"] = child.attrib.get("title")
            media_details["rating"] = child.attrib.get("rating")
            media_details["type"] = child.attrib.get("type")
            media_details["studio"] = child.attrib.get("studio")
            media_details["audience_rating"] = child.attrib.get("audienceRating")
            media_details["year"] = child.attrib.get("year")
        
        genres = []
        for child in response_xml_root.iter("Genre"):
            genres.append(child.attrib.get("tag"))
        media_details["genres"] = genres
        
        files = []
        for child in response_xml_root.iter("Part"):
            files.append(child.attrib.get("file"))
        media_details["files"] = files
        
        return media_details
    
    def update_all_library_sections(self) -> bool:
        """
        
        :return:
        """
        # Sections
        logger.info("Getting library sections")
        library_sections = self.get_keys_from_plex_api(plex_endpoint="/library/sections")
        for section in library_sections:
            section_endpoint = f"/library/sections/{section['key']}/refresh"
            api_uri = self.server_url + section_endpoint
            response = requests.get(api_uri, params=self.token)
            if response.status_code == 200:
                logger.success(f"Successfully started refresh for {section['title']}")
            else:
                raise ConnectionError(f"Refresh failed for {section['title']}")
        return True
    
    def get_all_episode_details(self, endpoint: str) -> List[Dict]:
        """
        
        :param endpoint:
        :return:
        """
        api_url = self.server_url + endpoint
        response = requests.get(url=api_url, params=self.token)
        
        response_xml_root = ElementTree.fromstring(response.content)
        
        all_episodes = []
        for child in response_xml_root:
            if child.tag == "Video":
                episode_details = {
                        "studio": child.attrib.get("studio"),
                        "type": child.attrib.get("type"),
                        "title": child.attrib.get("title"),
                        "grandparentTitle": child.attrib.get("grandparentTitle"),
                        "parentTitle": child.attrib.get("parentTitle"),
                        "contentRating": child.attrib.get("contentRating"),
                        "summary": child.attrib.get("summary"),
                        "year": child.attrib.get("year"),
                        "index": child.attrib.get("index"),
                        "lastViewedAt": child.attrib.get("lastViewedAt"),
                        "duration": child.attrib.get("duration"),
                        "originallyAvailableAt": child.attrib.get("originallyAvailableAt"),
                        "addedAt": child.attrib.get("addedAt"),
                        "updatedAt": child.attrib.get("updatedAt"),
                        "key": child.attrib.get("key")
                }
                all_episodes.append(episode_details)
        return all_episodes
    
    def get_all_show_details(self, show_endpoint: str) -> Dict:
        """

        :param show_endpoint:
        :return: show_summary
                 all_season_details
                 all_episode_details
        """
        api_url = self.server_url + show_endpoint
        response = requests.get(url=api_url, params=self.token)

        response_xml_root = ElementTree.fromstring(response.content)
        show_details = {
            "show_summary": response_xml_root.attrib.get("summary"),
            "show_title1" : response_xml_root.attrib.get("title2"),
            "show_title2" : response_xml_root.attrib.get("title1"),
            "year"        : response_xml_root.attrib.get("parentYear"),
            "key"         : show_endpoint
        }
        all_season_details = []
        all_episode_details = []
        for child in response_xml_root:
            if child.attrib.get("type") == "season":

                season_details = {
                    "title"    : child.attrib.get("title"),
                    "type"     : child.attrib.get("type"),
                    "updatedAt": child.attrib.get("updatedAt"),
                    "addedAt"  : child.attrib.get("addedAt"),
                    "key"      : child.attrib.get("key")
                }

                all_season_details.append(season_details)

                episodes_endpoint = child.attrib.get("key")
                all_episode_details.append(self.get_all_episode_details(endpoint=episodes_endpoint))

        show_details["season_details"] = all_season_details
        show_details["episode_details"] = all_episode_details
        return show_details

    def get_section_contents(self, content: Dict) -> Dict:
        """

        :param content:
        :type content:
        :return:
        :rtype:
        """
        content_key = content.get("key")
        content_type = content.get("type")
        if content_type == "movie":
            return self.get_movie_details(content_key)
        elif content_type == "show":
            return self.get_all_show_details(content_key)

    def get_plex_section_content(self, library_section_name: str):
        """

        """
        library_section = [section for section in self.get_keys_from_plex_api(plex_endpoint="/library/sections") if
                           section['title'] == library_section_name]

        if len(library_section) > 0:
            section_details = library_section[0]
        else:
            logger.error(f"No results found for section {library_section_name}")
            return

        section_endpoint = f"/library/sections/{section_details['key']}/all"
        section_contents = self.get_keys_from_plex_api(section_endpoint)

        return [self.get_section_contents(section_contents[i]) for i in tqdm(range(len(section_contents)))]

    def get_movie_info(self):
        logger.info("Getting movie info")
        return self.get_plex_section_content("Movies")

    def get_show_info(self):
        logger.info("Getting show info")
        return self.get_plex_section_content("TV Shows")

    def get_all_plex_info(self) -> (Dict):
        """
        
        :return:
        """
        
        # Sections
        
        logger.info("Getting library sections")

        all_data = {}

        all_data["movies"] = self.get_movie_info()
        all_data["shows"] = self.get_show_info()

        return all_data


