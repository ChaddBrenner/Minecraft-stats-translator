# Chadd Brenner
# May 19, 2022
# Python Script to change all .json files in a minecraft stats folder to one CSV file with all data
import os
import requests
import json
import csv
from tkinter import Tk, messagebox
from tkinter.filedialog import askdirectory, asksaveasfilename


# Given the file path of the stats folder for the minecraft world
# Return a list of names and all the data in those files
def read_files(stats_file_path: str):
    # List of player names
    player_name_list: list[str] = []
    # List of data for each player
    # Structure of data for each individual player is a dictionary where the key is the category (used, mined, etc.)
    # and the value is a inner dictionary. In this inner dictionary, the key is the thing that was used, mined, etc. and the value
    # is the number of times each thing was used, mined, etc.
    player_data_list: list[dict[str, dict[str, int]]] = []

    # Navigate to the folder
    os.chdir(stats_file_path)
    # Iterate through all files that end in .json in that folder
    for file in os.listdir():
        if file.endswith(".json"):
            # Remove .json to just get UUID of the player
            # Use that UUID to get the player's name
            name = get_player_name(file[:-5])
            player_name_list.append(name)
            # Create full file path to read the data in the file
            file_path = f"{stats_file_path}/{file}"
            data = read_text_file(file_path)
            # Convert the data from json to python dictionaries 
            readable = json.loads(data)
            # Add the data to the list of data, only adding the part of the data that contains the statistics
            player_data_list.append(readable['stats'])

    return player_data_list, player_name_list


# Given the UUID of a player, use Mojang API to get the player's current name
def get_player_name(uuid: str):
    try:
        # Hit the Mojang API to get the player's name
        website_url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        website = requests.get(website_url)
        website_data = json.loads(website.text)
        # Return the name of the player
        return website_data["name"]
    except:
        # Throw an error if the player's name cannot be found, most likely because there is a internet issue
        messagebox.showerror("Error", "Make sure you are connected to the internet.\n This script requires access to the internet to convert UUID's to player names using Mojang's API", )
        raise Exception('Not connected to internet')


# Given a file path, return that file's contents
def read_text_file(file_path: str):
    with open(file_path, 'r') as file:
        return file.read()


# Given a list of all data from all players return a list of all unique statistics
# This is used to create the first left column of the csv file
def read_all_stats(data_list: list[dict[str, dict[str, int]]]):
    stat_list: list[str] = []
    # For the stats from every player
    for i in range(len(data_list)):
        # For every category for every player
        for category in data_list[i]:
            # For every stat in every category for every player
            for stat_name in data_list[i][category]:
                # Using the category:stat format which is easily edited in Excel
                full_stat_name = category + ":" + stat_name
                if full_stat_name not in stat_list:
                    stat_list.append(full_stat_name)

    return stat_list


# Given the list of names, the list of all data, and the list of unique stats, return a 2d array
# where x, or the separate lists are the different statistics and y is the statistic for that particular player
def create_stat_list(name_list: list[str], data_list: list[dict[str, dict[str, int]]], stat_list: list[str]):
    # This list will contain all the data for all players
    all_player_data: list[list[int]] = []

    # Create a list of zeros for every stat where each list is the length of how many players there are
    # This means in the final product, if a player does not have a stat, it will be 0
    for _ in stat_list:
        all_player_data.append([0] * len(name_list))

    # x axis (values inside of list) is the player we are at
    # y axis (different lists) is the stat we are at
    # So list[player][stat] is the value for that player and that stat

    # For every player
    for current_player_index in range(len(data_list)):
        # For every category for every player
        for category_name in data_list[current_player_index]:
            # For every stat in every category for every player
            for stat_name in data_list[current_player_index][category_name]:
                # The get value of the stat for that player
                stat_value = data_list[current_player_index][category_name][stat_name]
                # Recreate full stat name
                full_stat_name = category_name + ":" + stat_name
                # Stat index is the index where the name of that stat is
                stat_index = stat_list.index(full_stat_name)
                # Replace the placeholder 0 with the value of that stat when it is found
                all_player_data[stat_index][current_player_index] = stat_value

    return all_player_data


# Go through the complete process of getting a file location
# reading the files, and returning the data from those files
def get_user_data():
    # Infinite loop until the user selects a valid folder or they cancel
    while True:
        # Get the folder location of the minecraft world
        file_path = get_file_location()
        # If the user cancels, exit the program
        if file_path == None:
            raise Exception("User cancelled")
        
        # Create the full path to the stats folder
        input_path = file_path + "/stats"
        try:
            # Try to read the files in the stats folder, if it fails, it is not a valid folder
            os.chdir(input_path)
        except:
            messagebox.showerror("Error", "Make sure you are selecting the correct folder for your Minecraft world.\n Also, make sure that the your minecraft world has a stats folder with contents")
            continue

        data_list, name_list = read_files(input_path)
        break
            
    return data_list, name_list


# Go through the process of getting the data from the files, creating the csv file, and saving it
def create_data():
    # Get the data from the files that the user selected
    data_list, name_list = get_user_data()

    # Create a list of all the stats that appear in the list
    stat_list = read_all_stats(data_list)

    # Sort the list in alphabetical order, it's important we do this before we create the stat list
    # because order and index matters
    stat_list.sort()

    # Create the final data list that will be used to create the csv file
    final_data_list = create_stat_list(name_list, data_list, stat_list)

    # Put a blank at the very top left of the csv file so everything lines up correctly
    # Create a final list which we will use to write the csv file, meaning we need to put the names at the top
    writing_list = [' ', name_list]

    # After the names, put every row of real data in each consecutive row
    for i, row in enumerate(final_data_list):
        # insert the name of the stat at the start of the row
        row.insert(0, stat_list[i])
        # Then add the row that contains the stat for each player, in the same order as the names so they line up
        writing_list.append(row)

    return writing_list


# Given a list of lists, write that list to a csv file
def write_csv(data: list[list[str]], output_path: str):
    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


# Prompt the user to select a folder, return the path to that folder, or None if the user cancels
def get_file_location():
    file_path = askdirectory(initialdir=os.path.expanduser("~/Downloads"), title='Select Save Folder', mustexist=True)
    # Cancel if the user presses cancel
    if not file_path:
        return None
            
    return file_path


# Prompt the user to select a save location, return the path to that location, or None if the user cancels
def get_save_location():
    output_path = asksaveasfilename(defaultextension='.csv', initialdir=os.path.expanduser("~/Desktop"), title='Select Save Location')
    # Cancel if the user presses cancel
    if not output_path:
        return None
    
    return output_path


def main():
    # Get a basic gui to select the folder
    Tk().withdraw()
    
    to_write = create_data()

    save_location = get_save_location()
    if save_location == None:
        raise Exception('User cancelled')
        
    write_csv(to_write, save_location)


if __name__ == "__main__":
    main()
