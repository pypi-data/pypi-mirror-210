"""Module that provides tools to manage its anime or tv series."""

import animedata as ad
import tomllib
import os.path
import warnings


dir_path = os.path.dirname(__file__)


with open(os.path.join(dir_path, ".\\pyproject.toml"), mode="rb") as pypr:
    at_version = tomllib.load(pypr)["project"]["version"]
print("AnimeTime script version : ", at_version)


class Episode():
    """A class to create episodes.

    Attributes:
        anime_object (object): anime object related to the episode
        season_object (object): season object related to the episode
        episode_number (int): episode number
        episode_name (str): episode name
        episode_duration (int): episode duration (in seconds)
        release_date (dict): dictionnary contaning episode's release date
    """

    def __init__(self,
                 anime_object: object,
                 season_object: object,
                 episode_number: int,
                 episode_name: str = None,
                 episode_duration: int = None,
                 episode_release_date: list = None) -> None:
        """Initialize an Episode instance and add it to its season's index.

        Args:
            anime_object (object): anime object related to the episode.
            season_object (object): season object related to the episode.
            episode_number (int): episode number.
            episode_name (str, optional): episode name. Defaults to None.
            episode_duration (int, optional): episode duration in minutes.
                Defaults to None
            episode_release_date (list): episode release date in format
                [DD,MM,YYYY]. Default to None
        """
        instance_exist(episode_number,
                       season_object.episodes_index,
                       True,
                       "presence")
        self.anime_object = anime_object
        self.season_object = season_object
        self.number = episode_number
        self.duration = episode_duration
        self.release_date = episode_release_date
        self.name = episode_name
        season_object.episodes_index[episode_number] = self

    def export_episode(self) -> dict:
        """Export the episode and its data into a AnimeData friendly dict.

        Returns:
            dict: contains episode data
        """
        episode_dict = {}
        episode_dict[ad.ad_table["episode_name"]] = self.name
        episode_dict[ad.ad_table["episode_duration"]] = self.duration
        episode_dict[ad.ad_table["episode_release_date"]] = self.release_date
        return episode_dict

    def import_episode(self, episode_dict: dict) -> None:
        """Import and replace the data of an episode with the dict data.

        Args:
            episode_dict (dict): contains episode data.
        """
        self.duration = episode_dict[ad.ad_table["episode_duration"]]
        self.name = episode_dict[ad.ad_table["episode_name"]]
        self.release_date = episode_dict[ad.ad_table["episode_release_date"]]


class Season():
    """A class to create seasons.

    Attributes:
        anime_object (object): anime object related to the season
        number_of_episodes (int): number of episodes in the season
        number (int): season number
        episodes_index (dict): index of every episode instance of the season,
            binding episode number and its object
    """

    def __init__(self,
                 anime_object: object,
                 season_number: int) -> None:
        """Initialize an Season instance and add itself to its anime's index.

        Args:
            anime_object (object): anime object related to the season
            season_number (int): season number
        """
        instance_exist(season_number,
                       anime_object.seasons_index,
                       True,
                       "presence")
        self.anime_object = anime_object
        self.number = season_number
        self.episodes_index = {}
        anime_object.seasons_index[season_number] = self
        
    def __del__(self):
        delete_instance(self.episodes_index)

    def add_episode(self, episode_number: int) -> None:
        """Add an episode to the season.

        Args:
            episode_number (int): number of the episode
        """
        globals()[f"episode_{self.anime_object.local_id}_ \
            {self.number}_{episode_number}"] = \
            Episode(self.anime_object, self, episode_number)

    def delete_episodes(self, episodes_list: list = None) -> None:
        """Delete an episode.

        Args:
            episodes_list (int): list of the episodes to delete
        """
        delete_instance(self.episodes_index, episodes_list)

    def edit_episode_data(self,
                          episode_number: int,
                          modified_attribute: str,
                          new_value) -> None:
        """Edit a specific attribute of an episode.

        Args:
            episode_number (int): number of the episode to be modified
            modified_attribute (str): attribute to be modified
            new_value (any): new value of the modified attribute
        """
        if modified_attribute == "episode_name":
            self.episodes_index[episode_number].episode_name = new_value
        elif modified_attribute == "episode_duration":
            self.episodes_index[episode_number].episode_duration = new_value
        elif modified_attribute == "release_date":
            self.episodes_index[episode_number].release_date = new_value

    def export_season(self) -> dict:
        """Export a season and its data.

        Returns:
            dict: episode's data
        """
        season_dict = {}
        for episode in self.episodes_index.keys():
            season_dict[episode] = \
                self.episodes_index[episode].export_episode()
        return season_dict

    def import_season(self, season_dict: dict) -> None:
        """Import the episodes of the season from an AD dictionnary.

        Args:
            season_dict (dict): _description_
        """
        if len(self.episodes_index) > 0:
            warnings.warn("The season already contains episode, \
they will be replaced.")
            self.delete_episodes()
        for episode in season_dict.keys():
            self.add_episode(episode)
            self.episodes_index[episode].import_episode(season_dict[episode])


class Anime():
    """A class to create animes.

    Attributes:
        animes_index (dict, class attribute): index of every Anime instance
            binding anime name and its object
        animes_id_counter (int, class attribute):animes indentifiers counter,
            used to create unique anime instances
        name(str) : anime name
        seasons_index (dict) : index of every Season instance of the anime,
            binding season number and its object
        local_id (int): anime identifier, depending of animes_id_counter when
            instanced and only used for instance name
    """

    animes_index = {}
    animes_id_counter = 0

    def __init__(self, anime_name: str) -> None:
        """Initialize an Anime instance and increase by one animes_id_counter.

        Args:
            anime_name (str): anime name
        """
        instance_exist(anime_name, Anime.animes_index, True, "presence")
        self.name = anime_name
        self.seasons_index = {}
        self.local_id = Anime.animes_id_counter
        Anime.animes_index[anime_name] = self
        Anime.animes_id_counter += 1

    def __del__(self):
        delete_instance(self.seasons_index)
    
    @classmethod
    def add_anime(cls, anime_name: str) -> None:
        """Add an anime by creating an Anime instance.

        Args:
            anime_name (str): anime name
        """
        globals()[f"anime_{Anime.animes_id_counter-1}"] = Anime(anime_name)

    @classmethod
    def delete_animes(cls, animes_list: list = None) -> None:
        """Delete the selected animes.

        Args:
            animes_list (list, optional): list of the animes to delete.
            Defaults to None.
        """
        delete_instance(cls.animes_index, animes_list)

    @classmethod
    def export_anime_list(cls) -> list:
        """Return a list containing every anime in the Anime index.

        Returns:
            list: contains the animes of the Anime index
        """
        return list(cls.animes_index.keys())

    def add_season(self, season_number: int) -> None:
        """Add a season to an anime.

        Args:
            season_number (int): the number of the season to be added.
        """
        globals()[f"season_{self.local_id}_{season_number}"] = \
            Season(self, season_number)

    def delete_seasons(self, seasons_list: list = None) -> None:
        """Delete a season and its episodes of the season anime index.

        Args:
            seasons_list (list): list of the season to be deleted
        """
        delete_instance(self.seasons_index, seasons_list)

    def export_anime(self) -> dict:
        """Export a dictionnary containing all the data of the anime.

        Returns:
            dict: contains anime data
        """
        dict_seasons = {}
        for season in self.seasons_index.keys():
            dict_seasons[season] = self.seasons_index[season].export_season()
        anime_dict = {"type": "anime",
                      ad.ad_table["anime_name"]: self.name,
                      ad.ad_table["seasons"]: dict_seasons}
        return anime_dict

    def import_anime(self, anime_dict: dict) -> None:
        """Import anime's data from a dict.

        Args:
            anime_dict (dict): dict containing anime's data.
        """
        if len(self.seasons_index) > 0:
            warnings.warn("The anime already contains seasons,\
they will be replaced.")
            self.delete_seasons()
        for season in anime_dict[ad.ad_table["seasons"]].keys():
            self.add_season(season)
            self.seasons_index[season].import_season(
                anime_dict[ad.ad_table["seasons"]][season])


def import_database(animes_list: list = None, ad_online: bool = True) -> None:
    """Import one or several animes from AnimeData.

    Args:
        animes_list (list, optional): List of animes to load. Defaults to None.
        ad_online (bool, optional): _description_. Defaults to True.
    """
    if ad_online:
        ad.get_ad_lib()
    dict_ad = ad.get_ad_lib_content(ad_online)
    if animes_list == None:
        animes_list = []
    for element in dict_ad.values():
        if element["type"] == "anime":
            anime_name = element[ad.ad_table["anime_name"]]
            if anime_name in animes_list or len(animes_list)==0:
                if instance_exist(anime_name, Anime.animes_index, True, "presence"):
                    Anime.animes_index[anime_name].delete_seasons()
                else:
                    Anime.add_anime(anime_name)
                Anime.animes_index[anime_name].import_anime(element)

def export_database(animes_list: list = None) -> dict:
    """Merge several anime dict in a dict in order to be used by AnimeData.

    Args:
        animes_list (list, optional): contains the list of animes to export.
        Default to None.

    Returns:
        dict: contains the dictionnaries of the animes.
    """
    ad_dict = {}
    animes_list = select_all_instances(Anime.animes_index, animes_list)
    animes_ignored = []
    for anime_to_export in animes_list:
        if not instance_exist(anime_to_export,
                          Anime.animes_index,
                          True,
                          "missing"):
            animes_ignored.append(anime_to_export)
        else:
            ad_dict[anime_to_export] = \
                Anime.animes_index[anime_to_export].export_anime()
    return ad_dict


def instance_exist(instance_name_id,
                   instances_index: dict,
                   warn_user: bool,
                   warn_mode: str) -> bool:
    """Check if an instance identified by a name or a number in a class index.

    Args:
        instance_name_id (Any): instance's identifier
        instances_index (dict): class index
        warn_user (bool): send a warning to the user.
        warn_mode (str): warn either when the anime is missing or if it\
            exists : "missing" or "presence" respectively.

    Returns:
        bool: if the instance exists or not.
    """
    if instance_name_id in instances_index.keys():
        if warn_user and warn_mode == "presence":
            warnings.warn("An instance with the same id already exist, \
ignoring it.")
        return True
    else:
        if warn_user and warn_mode == "missing":
            warnings.warn("Not any instance with this id exists in \
AnimeTime database, ignoring it.")
        return False


def delete_instance(instances_index: dict, instances_list: list = None) -> None:
    """Delete instances from their identifier and the linked index.

    Args:
        instances_index (dict): index related to the instances.
        instances_list (list, optional): list of the instances to delete.
        Defaults to None.
    """
    instances_list = select_all_instances(instances_index, instances_list)
    for instance_to_delete in instances_list:
        if instance_exist(instance_to_delete,
                          instances_index,
                          True,
                          "missing"):
            del instances_index[instance_to_delete]


def select_all_instances(instances_index: dict,
                         instances_list: list = None) -> list:
    """Return all the instances of their index if instances_list == None.

    Args:
        instances_index (dict): index of the instances
        instances_list (list, optional): list of the instances.
        Defaults to None.

    Returns:
        list: instances list
    """
    if instances_list is None:
        return list(instances_index.keys())
    return instances_list