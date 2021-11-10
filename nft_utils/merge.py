from tkinter import filedialog
import os
import shutil
import json


def merge_folder():
    first_dir = filedialog.askdirectory(
        initialdir="/", title="Select directory to merge")
    second_dir = filedialog.askdirectory(
        initialdir="/", title="Select directory to be merged")
    first_entries = os.scandir(first_dir)

    first_array = []

    for first_entry in first_entries:
        if(first_entry.is_file()):
            first_array.append(
                {'path': first_entry.path, 'name': first_entry.name})

    for i in first_array:
        existed = False

        second_array = []
        second_entries = os.scandir(second_dir)
        for second_entry in second_entries:
            if(second_entry.is_file()):
                second_array.append(
                    {'path': second_entry.path, 'name': second_entry.name})

        for j in second_array:
            if(i['name'] == j['name']):
                existed = True

        if(existed == False):
            first_meta_path = i['path'].split(
                'results')[0] + 'metadata/' + i['name'].replace('.png', '')
            second_meta_dir = second_dir.replace('results', '') + 'metadata/'
            shutil.copy(i['path'], second_dir)
            shutil.copy(first_meta_path, second_meta_dir)

            my_trait = {}
            all_traits2 = []

            with open(i['path'].split('results')[0] + 'metadata/all-traits.json', 'r') as f1:
                all_traits1 = json.load(f1)
                id = i['name'].replace('.png', '')

                for trait in all_traits1:
                    if(trait['tokenId'] == id):
                        my_trait = trait

            with open(second_dir.replace('results', '') + 'metadata/all-traits.json', 'r') as f2:
                all_traits2 = json.load(f2)

            all_traits2.append(my_trait)
            # print(my_trait)

            with open(second_dir.replace('results', '') + 'metadata/all-traits.json', 'w') as f3:
                json.dump(all_traits2, f3)

        else:
            new_name = ''

            for k in range(50000):
                for l in second_array:
                    if(str(k) == l['name'].replace('.png', '')):
                        new_name = ''
                        break
                    else:
                        new_name = str(k)
                if(new_name != ''):
                    break

            os.rename(i['path'], second_dir + '/' + new_name + '.png')

            first_meta_path = i['path'].split(
                'results')[0] + 'metadata/' + i['name'].replace('.png', '')
            second_meta_path = second_dir.replace(
                'results', '') + 'metadata/' + new_name
            meta = {}
            with open(first_meta_path, 'r') as f4:
                meta = json.load(f4)
                meta['image'] = meta['image'].replace(
                    i['name'], new_name + '.png')
                meta['tokenId'] = new_name
                meta['name'] = meta['name'].replace(
                    '#' + i['name'].replace('.png', ''), '#' + new_name)
            with open(second_meta_path, 'w') as f5:
                json.dump(meta, f5)

            # new_meta_path = first_meta_path.split('metadata')[0] + new_name
            # os.rename(first_meta_path, new_meta_path)

            # all_traits3 = {}
            # with open(i['path'].split('results')[0] + 'metadata/all-traits.json', 'r') as f6:
            #     all_traits3 = json.load(f6)
            #     id1 = i['name'].replace('.png', '')

            #     for t in range(len(all_traits3)):
            #         if(all_traits3[t]['tokenId'] == id1):
            #             all_traits3[t] = meta
            # with open(i['path'].split('results')[0] + 'metadata/all-traits.json', 'w') as f7:
            #     json.dump(all_traits3, f7)

            all_traits4 = {}
            with open(second_dir.replace('results', '') + 'metadata/all-traits.json', 'r') as f8:
                all_traits4 = json.load(f8)
            all_traits4.append(meta)
            with open(second_dir.replace('results', '') + 'metadata/all-traits.json', 'w') as f9:
                json.dump(all_traits4, f9)

            # shutil.copy(i['path'].replace(i['name'], new_name + '.png'), second_dir)
            # shutil.copy(new_meta_path, second_meta_dir)
# for first_entry in first_entries:
#     if(first_entry.is_file()):
#         existed = False
#         for second_entry in second_entries:
#             if(second_entry.is_file()):
#                 if(first_entry.name == second_entry.name):
#                     existed == True
#             print('s')

#         if(existed == False):
#             first_meta_path = first_entry.path.split('results')[0] + 'metadata/' + first_entry.name.replace('.png', '')
#             second_meta_dir = second_dir.replace('results', '') + 'metadata/'
# shutil.copy(first_entry.path, second_dir)
# shutil.copy(first_meta_path, second_meta_dir)


merge_folder()
