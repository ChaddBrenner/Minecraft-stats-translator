# Chadd Brenner
# May 19, 2022
# Python Script to change all .json files in a minecraft stats folder to one CSV file with all data
import os
import requests
import json
import csv


# given the file path of the stats folder for the minecraft server
# return a list of names and all the data in those files
def read_files(stats_file_path):
    player_name_list = []
    player_data_list = []
    os.chdir(stats_file_path)
    # iterate through all files that in in .json in that folder
    for file in os.listdir():
        if file.endswith(".json"):
            # remove .json to just get UUID
            name = get_player_name(file[:-5])
            player_name_list.append(name)
            # create full file path to read the data in the file
            file_path = f"{stats_file_path}/{file}"
            data = read_text_file(file_path)
            player_data_list.append(json.loads(data))
    return player_data_list, player_name_list


# given the UUID of a player, use Mojang API to get player name
def get_player_name(uuid):
    website_url = f"https://api.mojang.com/user/profiles/{uuid}/names"
    website = requests.get(website_url)
    # convert json speak into Python speak
    website_data = json.loads(website.text)
    # return the name of the player
    return website_data[0]["name"]


# given a file path, return that file's contents
def read_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


# given a list of all data from all players return a list of all unique statistics
def read_all_stats(data_list):
    stat_list = []
    # for the stats from every player
    for i, player_data in enumerate(data_list):
        # for every category
        for category in data_list[i]["stats"]:
            # for every stat in every category for every player
            for stat_name in data_list[i]["stats"][category]:
                # using the category:stat format
                full_stat_name = category + ":" + stat_name
                if full_stat_name not in stat_list:
                    stat_list.append(full_stat_name)

    return stat_list


# given the list of names, the list of all data, and the list of unique stats, return a 2d array
# where x, or the separate lists are the different statistics and y is the statistic for that particular player
def create_stat_list(name_list, data_list, stat_list):
    new_list = []
    # create a list of zeros for every stat where each list is the length of how many players there are
    for _ in stat_list:
        new_list.append([0] * len(name_list))

    # x axis (values inside of list) is the player we are at
    # y axis (different lists) is the stat we are at
    for i, player_data in enumerate(data_list):
        for category in data_list[i]["stats"]:
            for stat in data_list[i]["stats"][category]:
                stat_name = stat
                stat_value = data_list[i]["stats"][category][stat]
                # recreate full stat name
                full_stat_name = category + ":" + stat_name
                # current player index is how far along we are in the list of data
                current_player_index = i
                # stat index is the index where the name of that stat is
                stat_index = stat_list.index(full_stat_name)
                # replace the placeholder 0 with the value of that stat
                new_list[stat_index][current_player_index] = stat_value

    return new_list


# create a CSV file
def create_csv():
    # change the file path here to the file path of your particular stats folder of your particular minecraft world
    file_path = "/Users/chaddbrenner/Downloads/hermitcraft8/stats"
    # get list of data and list of names from all the files in that file path that end in .json
    data_list, name_list = read_files(file_path)
    # create a list of all the stats that appear in the list
    stat_list = read_all_stats(data_list)
    # sort the list in alphabetical order, it's important we do this before we create the stat list
    # because order and index matters
    stat_list.sort()
    # create the final data list
    final_data_list = create_stat_list(name_list, data_list, stat_list)
    # put a blank at the very top left of the csv file so everything lines up correctly
    name_list.insert(0, " ")
    # create a final list which we will use to write the csv file, meaning we need to put the names at the top
    writing_list = [name_list]
    # after the names, put every row of real data in each consecutive row
    for i, row in enumerate(final_data_list):
        # insert the name of the stat at the start of the row
        row.insert(0, stat_list[i])
        writing_list.append(row)

    # create and write the csv file
    # change where you want to save the csv file and what the name if it should be to your particular file path
    with open("/Users/chaddbrenner/Desktop/csvfile.csv", 'w', newline='') as file:
        writer = csv.writer(file, dialect='excel')
        # write all rows at one time
        writer.writerows(writing_list)


create_csv()
