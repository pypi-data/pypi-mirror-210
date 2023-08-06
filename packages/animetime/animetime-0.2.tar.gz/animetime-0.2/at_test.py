from random import randint
import warnings
import animetime as at

# Test : Import/Export
def test_import_export():
    test_delete_anime()
    import_dict = at.ad.get_ad_lib_content(True)
    at.import_database(import_dict)
    at.ad.save_json(at.export_database())
    export_dict = at.ad.get_ad_lib_content(False)
    del import_dict["ANIMEDATA-METADATA"]
    del export_dict["ANIMEDATA-METADATA"]
    if import_dict != export_dict:
        warnings.warn("FAILED : Import/Export processes")
    else:
        print("IMPORT/EXPORT : OK")
        
def test_add_anime():
    at.Anime.add_anime("TEST_ANIME")
    anime_object = at.Anime.animes_index["TEST_ANIME"]
    anime_object.add_season(1)
    season_object = anime_object.seasons_index[1]
    for episode in range(1,30):
        season_object.add_episode(episode)
        season_object.episodes_index[episode].duration = 24
        season_object.episodes_index[episode].release_date = [12,7,2022]
        season_object.episodes_index[episode].name = f"Episode {episode}"
    random_test = randint(1,29)
    if season_object.episodes_index[random_test].name != f"Episode {random_test}":
        warnings.warn("FAILED: Addition process")
    else:
        print("ADDITION : OK")

def test_delete_anime():
    at.Anime.delete_animes()
    if len(at.Anime.animes_index) != 0:
        warnings.warn("FAILED : Deletion process")
    else:
        print("DELETION : OK")
    
def test_all():
    test_import_export()
    test_add_anime()
    test_delete_anime()