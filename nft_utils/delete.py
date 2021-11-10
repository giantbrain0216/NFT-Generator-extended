import easygui
import os
import json


def open_window():
    read = easygui.fileopenbox(multiple=True, filetypes=["*.png"])
    return read

# delete file function


def delete_file():
    del_img = open_window()
    token_ids = []
    if(del_img):
        for i in del_img:
            del_meta = i.replace(
                "\\results\\", "\\metadata\\").replace(".png", "")
            token_ids.append(
                i.split("\\")[len(i.split("\\")) - 1].replace('.png', ''))
            if os.path.exists(i):
                os.remove(i)
                print('delete successful', i)
            else:
                print('Warning!', "File not found !")
            if os.path.exists(del_meta):
                os.remove(del_meta)
                print('delete successful', del_meta)
            else:
                print('Warning!', "File not found !")

        json_path = del_img[0].split(
            "results")[0] + 'metadata\\all-traits.json'
        
        new_json = []
        with open(json_path, 'r') as json_file:
            
            json_data = json.load(json_file)
            
            for tk in list(token_ids):
                for element in list(json_data):
                    if(element['tokenId'] == tk):
                        json_data.remove(element)
            new_json = json_data 

        with open(json_path, 'w') as f:
            json.dump(new_json, f)

delete_file()
