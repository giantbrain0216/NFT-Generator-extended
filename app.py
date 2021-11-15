import eel
import wx
import os
import json
from PIL import Image, ImageDraw, ImageFont
import random
import shutil
import base64
import pandas as pd
from mandelbrot import Mandelbrot
import joblib
from joblib import Parallel, delayed
from colorthief import ColorThief
from scipy.spatial import KDTree
from webcolors import (
    CSS3_HEX_TO_NAMES,
    hex_to_rgb,
)

number_of_cpu = joblib.cpu_count()

eel.init('web')

excel = None
bg = None

# system1


@eel.expose
def browse(option):
    app = wx.App(None)
    defaultPath = os.getcwd()

    if option == 'system1_folder':
        path = ''
        dlg1 = wx.DirDialog(
            None,
            message='Choose folder',
            defaultPath=defaultPath,
            style=wx.STAY_ON_TOP)
        # Show the dialog and retrieve the user response.
        if dlg1.ShowModal() == wx.ID_OK:
            # load directory
            path = dlg1.GetPath()
        else:
            path = ''
        # Destroy the dialog.
        dlg1.Destroy()
        if path != '':
            return loadResource(path)
        return "path_error!"
    elif option == 'system2_excel':
        path = ''
        dlg2 = wx.FileDialog(
            None,
            'Choose excel file',
            defaultDir=defaultPath,
            wildcard="Excel File |*.xls;*.xlsx;",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.STAY_ON_TOP
        )
        try:
            if dlg2.ShowModal() == wx.ID_CANCEL:
                return None
            path = dlg2.GetPath()
            if path != '':
                return loadExcelFile(path)
            return 'path_error'
        finally:
            dlg2.Destroy()
    elif option == 'system2_bg':
        path = ''
        dlg2 = wx.FileDialog(
            None,
            'Choose image file',
            defaultDir=defaultPath,
            wildcard="PNG File |*.png",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.STAY_ON_TOP
        )
        try:
            if dlg2.ShowModal() == wx.ID_CANCEL:
                return None
            path = dlg2.GetPath()
            if path != '':
                return loadBgFile(path)
            return 'path_error'
        finally:
            dlg2.Destroy()


def loadResource(path):
    resList = []
    entries = os.scandir(path)
    i: int = 0
    for entry in entries:
        if(entry.is_dir()):
            resList += [{'id': entry.name, 'parent': "#",
                         'text': entry.name, 'icon': "jstree-folder"}]
            entry2 = os.scandir(entry.path)
            for entry3 in entry2:
                i = int(i) + 1
                index = entry3.name.find('.png')
                resList += [{'id': entry3.name[:index] + str(
                    i) + entry3.name[index:], 'parent': entry.name, 'text': entry3.name, 'icon': "jstree-file", 'path': entry3.path}]
    return json.dumps(resList)


@eel.expose
def combineImages(data):
    d = json.loads(data)
    result = generateImages(d)
    return result


def generateImages(d):
    all_images = []
    number = int(d['number'])
    projectName = d['projectName']
    uploadURL = d['uploadURL']

    if(os.path.isdir('results') != True):
        os.makedirs('results')
    else:
        shutil.rmtree('results')
        os.makedirs('results')

    if(os.path.isdir('metadata') != True):
        os.makedirs('metadata')
    else:
        shutil.rmtree('metadata')
        os.makedirs('metadata')

    for it in range(number):
        new_image = {}
        preparedData = prepareData(d)
        img = 'EMPTY'

        for i in range(len(preparedData)):
            if(i == 0):
                img = Image.alpha_composite(Image.open(preparedData[i]['path']).convert(
                    'RGBA'), Image.open(preparedData[i+1]['path']).convert('RGBA'))
            else:
                if(i < (len(preparedData)-1)):
                    img = Image.alpha_composite(img, Image.open(
                        preparedData[i+1]['path']).convert('RGBA'))

            new_image[preparedData[i]['parent'].replace(preparedData[i]['parent'].split('_')[0] + '_', '')] = preparedData[i]['path'].split(
                '\\')[-1].replace('.png', '').replace(preparedData[i]['path'], '')

        new_image['tokenId'] = str(it)
        rgbImg = img.convert('RGB')
        all_images.append(new_image)

        rgbImg.save("./results/" + new_image['tokenId'] + ".png")

    METADATA_FILE_NAME = 'all-traits.json'
    with open('./metadata/' + METADATA_FILE_NAME, 'w') as outfile:
        json.dump(all_images, outfile, indent=4)

    f = open('./metadata/all-traits.json')
    allTraits = json.load(f)
    for i in allTraits:
        tokenId = i['tokenId']
        token = {
            "image": uploadURL + '/' + tokenId + ".png",
            "tokenId": tokenId,
            "name": projectName + ' ' + str(tokenId),
            "attributes": []
        }
        for key in i.keys():
            token['attributes'].append(getAttribute(key, i[key]))

        with open('./metadata/' + tokenId, 'w') as outfile:
            json.dump(token, outfile, indent=4)

    return 'success'


def getAttribute(key, value):
    return {
        "trait_type": key,
        "value": value
    }


def prepareData(data):
    datums = []
    for i in data["unwantImages"]:
        if(i["group"] != '#'):
            stop = len(i["children"]) - 1
            start = 0
            randIndex = random.randint(start, stop)
            datums.append({'parent': i["children"][randIndex]["original"]
                          ["parent"], 'path': i["children"][randIndex]["original"]["path"]})

    for i in data["importantImages"]:
        if(i["group"] != '#'):
            datums.append({'parent': i["children"][0]["original"]
                          ["parent"], 'path': i["children"][0]["original"]["path"]})
    unique = {each['parent']: each for each in datums}.values()
    result = json.loads(json.dumps(list(unique)))
    result.sort(key=lambda x: x["parent"])
    return result


@eel.expose
def getImgSrc(path):
    f = open(path, 'rb')
    data = f.read()
    data = base64.b64encode(data).decode("utf-8")
    return data


# system2


def loadExcelFile(path):
    global excel
    excel = {
        'superPowers': {
            'SUPERPOWERS': [],
            'RARITY': []
        },
        'gifts': {
            'GIFTS': [],
            'RARITY': []
        },
        'skills': {
            'SKILLS': [],
            'RARITY': []
        }
    }

    data1 = pd.read_excel(path, header=1, usecols="A,C", na_filter=False)
    data2 = pd.read_excel(path, header=1, usecols="E,G", na_filter=False)
    data3 = pd.read_excel(path, header=1, usecols="I,K", na_filter=False)

    for i in data1['SUPERPOWERS']:
        if i != '':
            excel['superPowers']['SUPERPOWERS'].append(i)
    for j in data1['RARITY']:
        if j != '':
            excel['superPowers']['RARITY'].append(j)

    for k in data2['GIFTS']:
        if k != '':
            excel['gifts']['GIFTS'].append(k)
    for l in data2['RARITY.1']:
        if l != '':
            excel['gifts']['RARITY'].append(l)

    for m in data3['SKILLS']:
        if m != '':
            excel['skills']['SKILLS'].append(m)
    for n in data3['RARITY.2']:
        if n != '':
            excel['skills']['RARITY'].append(n)

    return 'success'


def loadBgFile(path):
    global bg
    bg = Image.open(path)
    return 'success'

# superpowers -> [20,139], [20, 186], gifts -> [20, 351], [20, 402], [20, 452], skills -> [20, 585], [20, 635], [20, 685], [20, 735], [20, 785]
# superpowers -> [20,140], [20, 190], gifts -> [20, 350], [20, 400], [20, 450], skills -> [20, 590], [20, 640], [20, 690], [20, 740], [20, 790]
# superpowers -> [20,117], [20, 167], gifts -> [20, 327], [20, 377], [20, 427], skills -> [20, 567], [20, 617], [20, 667], [20, 717], [20, 767]


@eel.expose
def combineImages2(amount):
    if(os.path.isdir('results') != True):
        os.makedirs('results')
    else:
        shutil.rmtree('results')
        os.makedirs('results')

    if(os.path.isdir('txts') != True):
        os.makedirs('txts')
    else:
        shutil.rmtree('txts')
        os.makedirs('txts')

    font = ImageFont.truetype(r'C:\Windows\Fonts\javatext.ttf', 42)
    color = 'black'
    txtPosition = [(20, 117), (20, 167), (20, 327), (20, 377), (20, 427),
                   (20, 567), (20, 617), (20, 667), (20, 717), (20, 767)]

    for j in range(int(amount)):
        txt = open('./txts/' + str(j) + ".txt", "x")
        txt.write('Rarity\n')
        img = bg.copy()
        d = ImageDraw.Draw(img)
        totalRarity = 0
        for i in range(len(txtPosition)):
            if i < 2:
                randIndex = random.randint(
                    0, len(excel['superPowers']['SUPERPOWERS']) - 1)
                word = excel['superPowers']['SUPERPOWERS'][randIndex]
                d.text(xy=txtPosition[i], text=word, fill=color, font=font)
                if i == 0:
                    txt.write('\nSuperpowers\n')
                txt.write('-' + word + ' = ' +
                          str(excel['superPowers']['RARITY'][randIndex]))
                txt.write('\n')
                totalRarity += excel['superPowers']['RARITY'][randIndex]
            if 1 < i < 5:
                randIndex = random.randint(0, len(excel['gifts']['GIFTS']) - 1)
                word = excel['gifts']['GIFTS'][randIndex]
                d.text(xy=txtPosition[i], text=word, fill=color, font=font)
                if i == 2:
                    txt.write('\nGifts\n')
                txt.write('-' + word + ' = ' +
                          str(excel['gifts']['RARITY'][randIndex]))
                txt.write('\n')
                totalRarity += excel['gifts']['RARITY'][randIndex]
            if i > 4:
                randIndex = random.randint(0, len(excel['gifts']['GIFTS']) - 1)
                word = excel['skills']['SKILLS'][randIndex]
                d.text(xy=txtPosition[i], text=word, fill=color, font=font)
                if i == 5:
                    txt.write('\nSkills\n')
                txt.write('-' + word + ' = ' +
                          str(excel['skills']['RARITY'][randIndex]))
                txt.write('\n')
                totalRarity += excel['skills']['RARITY'][randIndex]
        img.save('./results/' + str(j) + '.png')
        txt.write('\n\n')
        txt.write('Total rarity = ' + str(totalRarity/10))
    return 'success'


# system 3

@eel.expose
def generateFractal(data):

    all_traits = []

    if(os.path.isdir('results') != True):
        os.makedirs('results')
    else:
        shutil.rmtree('results')
        os.makedirs('results')

    if(os.path.isdir('metadata') != True):
        os.makedirs('metadata')
    else:
        shutil.rmtree('metadata')
        os.makedirs('metadata')

    datums = json.loads(data)
    Parallel(n_jobs=number_of_cpu)(delayed(drawFractal)(i, datums)
                                   for i in range(int(datums['repeatNum'])))

    for filename in os.listdir("metadata"):
        with open(os.path.join("metadata", filename), 'r') as f:
            text = f.read()
            all_traits.append(json.loads(text))
    METADATA_FILE_NAME = 'all-traits.json'
    with open('./metadata/' + METADATA_FILE_NAME, 'w') as outfile:
        json.dump(all_traits, outfile, indent=4)
    # for i in range(int(datums['repeatNum'])):
    #     drawFractal(i, datums)
    return 'success'


def drawFractal(value, datums):
    xmin = -2
    xmax = 1
    ymin = -1
    ymax = 1

    pointNames = [
        {'name': "Poseidon", 'value': (0.25, 9)},
        {'name': "Hera", 'value': (0.04, 0.25)},
        {'name': "Zeus", 'value': (-0.3, 0.04)},
        {'name': "Demeter", 'value': (-0.453, -0.3)},
        {'name': "Athena", 'value': (-0.637, -0.453)},
        {'name': "Apollo", 'value': (-0.735, -0.637)},
        {'name': "Aphrodite", 'value': (-0.8, -0.735)},
        {'name': "Ares", 'value': (-0.97, -0.8)},
        {'name': "Artemis", 'value': (-1.226, -0.97)},
        {'name': "Hephaestus", 'value': (-1.29, -1.226)},
        {'name': "Hermes", 'value': (-1.43, -1.29)},
        {'name': "Hestia", 'value': (-9, -1.43)}
    ]
    locationNames = [
        {'name': "Surface", 'value': (-1, 200)},
        {'name': "Shallow", 'value': (200, 2000)},
        {'name': "Profound", 'value': (2000, 20000)},
        {'name': "Deep", 'value': (20000, float('inf'))},
    ]

    if(datums['mode'] == 'auto'):
        x1 = random.uniform(xmin, xmax)
        x2 = random.uniform(xmin, xmax)
        y1 = random.uniform(ymin, ymax)
        y2 = (1 / 1) * (x2 - x1) + y1
        r = round(random.uniform(0, 1), 2)
        g = round(random.uniform(0, 1), 2)
        b = round(random.uniform(0, 1), 2)
        maxiter = int(datums['maxiter'])
        stripe_s = random.randint(0, 10)
        ncycle = random.randint(1, 64)
        step_s = random.randint(0, 10)
        xpixels = 1280 if datums['imgResolution'] == '' else int(
            datums['imgResolution'])
        mand = Mandelbrot(maxiter=maxiter, coord=[x1, x2, y1, y2], rgb_thetas=[
                          r, g, b], stripe_s=stripe_s, ncycle=ncycle, step_s=step_s, xpixels=xpixels)
        mand.draw('./results/' + str(value) + '.png')
        
        color_thief = ColorThief('./results/' + str(value) + '.png')
        dominant_color = color_thief.get_color(quality=1)
        dominant_color_name = convert_rgb_to_names(dominant_color).capitalize()

        centerPointX = (x2 + x1) / 2
        pointName = ''
        for point in pointNames:
            if point['value'][0] <= centerPointX and point['value'][1] >= centerPointX:
                pointName = point['name']

        locationName = ''
        zoom = int(round((xmax - xmin) * (ymax - ymin)) /
                   ((x2 - x1) * (y2 - y1)))
        for location in locationNames:
            if location['value'][0] <= zoom and location['value'][1] >= zoom:
                locationName = location['name']

        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        token = {
            "image": datums['uploadURL'] + '/' + str(value) + '.png',
            "tokenId": str(value),
            "name": "#" + str(value) + " " + locationName + " " + dominant_color_name + " " + pointName,
            "description": dominant_color_name + " " + pointName + " in a neighbourhood of the point (" + str(x) + ", " + str(y) + "), on the "+ locationName +" of the Mandelbrot set",
            "attributes": [
                {
                    "trait_type": "Stripe",
                    "value": stripe_s,
                },
                {
                    "trait_type": "Cycle",
                    "value": ncycle,
                },
                {
                    "trait_type": "Step",
                    "value": step_s,
                },
                {
                    "trait_type": "Zoom",
                    "value": zoom,
                },
                {
                    "trait_type": "Color",
                    "value": dominant_color_name,
                },
                {
                    "trait_type": "Point",
                    "value": pointName,
                },
                {
                    "trait_type": "Location",
                    "value": locationName,
                },
                {
                    "trait_type": "x",
                    "value": x,
                },
                {
                    "trait_type": "y",
                    "value": y,
                },
            ]
        }
        with open('./metadata/' + str(value), 'w') as outfile:
            json.dump(token, outfile, indent=4)

    if(datums['mode'] == 'semi'):
        x1 = float(datums['coord']['x1'])
        x2 = float(datums['coord']['x2'])
        y1 = float(datums['coord']['y1'])
        y2 = float(datums['coord']['y2'])
        x1 = random.uniform(x1, x2)
        x2 = random.uniform(x1, x2)
        y1 = random.uniform(y1, y2)
        y2 = (1 / 1) * (x2 - x1) + y1
        xpixels = 1280 if datums['imgResolution'] == '' else int(
            datums['imgResolution'])
        r = round(random.uniform(0, 1), 2) if datums['color']['r'] == '' else float(
            datums['color']['r'])
        g = round(random.uniform(0, 1), 2) if datums['color']['g'] == '' else float(
            datums['color']['g'])
        b = round(random.uniform(0, 1), 2) if datums['color']['b'] == '' else float(
            datums['color']['b'])
        stripe_s = random.randint(
            0, 10) if datums['stripeS'] == '' else int(datums['stripeS'])
        ncycle = random.randint(
            1, 64) if datums['ncycle'] == '' else int(datums['ncycle'])
        step_s = random.randint(
            0, 10) if datums['stepS'] == '' else int(datums['stepS'])

        mand = Mandelbrot(maxiter=int(datums['maxiter']), coord=[x1, x2, y1, y2], rgb_thetas=[
                          r, g, b], stripe_s=step_s, ncycle=ncycle, step_s=step_s, xpixels=xpixels)
        mand.draw('./results/' + str(value) + '.png')

        color_thief = ColorThief('./results/' + str(value) + '.png')
        dominant_color = color_thief.get_color(quality=1)
        dominant_color_name = convert_rgb_to_names(dominant_color).capitalize()

        centerPointX = (x2 + x1) / 2
        pointName = ''
        for point in pointNames:
            if point['value'][0] <= centerPointX and point['value'][1] >= centerPointX:
                pointName = point['name']

        locationName = ''
        zoom = int(round((xmax - xmin) * (ymax - ymin)) /
                   ((x2 - x1) * (y2 - y1)))
        for location in locationNames:
            if location['value'][0] <= zoom and location['value'][1] >= zoom:
                locationName = location['name']

        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        token = {
            "image": datums['uploadURL'] + '/' + str(value) + '.png',
            "tokenId": str(value),
            "name": "#" + str(value) + " " + locationName + " " + dominant_color_name + " " + pointName,
            "description": dominant_color_name + " " + pointName + " in a neighbourhood of the point (" + str(x) + ", " + str(y) + "), on the "+ locationName +" of the Mandelbrot set",
            "attributes": [
                {
                    "trait_type": "Stripe",
                    "value": stripe_s,
                },
                {
                    "trait_type": "Cycle",
                    "value": ncycle,
                },
                {
                    "trait_type": "Step",
                    "value": step_s,
                },
                {
                    "trait_type": "Zoom",
                    "value": zoom,
                },
                {
                    "trait_type": "Color",
                    "value": dominant_color_name,
                },
                {
                    "trait_type": "Point",
                    "value": pointName,
                },
                {
                    "trait_type": "Location",
                    "value": locationName,
                },
                {
                    "trait_type": "x",
                    "value": x,
                },
                {
                    "trait_type": "y",
                    "value": y,
                },
            ]
        }
        with open('./metadata/' + str(value), 'w') as outfile:
            json.dump(token, outfile, indent=4)

    if(datums['mode'] == 'range'):
        x1 = float(datums['coord']['x1'])
        x2 = float(datums['coord']['x2'])
        y1 = float(datums['coord']['y1'])
        y2 = float(datums['coord']['y2'])
        x1 = random.uniform(x1, x2)
        x2 = random.uniform(x1, x2)
        y1 = random.uniform(y1, y2)
        y2 = (1 / 1) * (x2 - x1) + y1

        r = round(random.uniform(0, 1), 2) if datums['color']['r'] == '' else float(
            datums['color']['r'])
        g = round(random.uniform(0, 1), 2) if datums['color']['g'] == '' else float(
            datums['color']['g'])
        b = round(random.uniform(0, 1), 2) if datums['color']['b'] == '' else float(
            datums['color']['b'])
        stripe_s = random.randint(
            0, 10) if datums['stripeS'] == '' else int(datums['stripeS'])
        ncycle = random.randint(
            1, 64) if datums['ncycle'] == '' else int(datums['ncycle'])
        step_s = random.randint(
            0, 10) if datums['stepS'] == '' else int(datums['stepS'])
        xpixels = 1280 if datums['imgResolution'] == '' else int(
            datums['imgResolution'])

        mand = Mandelbrot(maxiter=int(datums['maxiter']), coord=[x1, x2, y1, y2], rgb_thetas=[
                          r, g, b], stripe_s=step_s, ncycle=ncycle, step_s=step_s, xpixels=xpixels)
        mand.draw('./results/' + str(value) + '.png')

        color_thief = ColorThief('./results/' + str(value) + '.png')
        dominant_color = color_thief.get_color(quality=1)
        dominant_color_name = convert_rgb_to_names(dominant_color).capitalize()

        centerPointX = (x2 + x1) / 2
        pointName = ''
        for point in pointNames:
            if point['value'][0] <= centerPointX and point['value'][1] >= centerPointX:
                pointName = point['name']

        locationName = ''
        zoom = int(round((xmax - xmin) * (ymax - ymin)) /
                   ((x2 - x1) * (y2 - y1)))
        for location in locationNames:
            if location['value'][0] <= zoom and location['value'][1] >= zoom:
                locationName = location['name']

        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        token = {
            "image": datums['uploadURL'] + '/' + str(value) + '.png',
            "tokenId": str(value),
            "name": "#" + str(value) + " " + locationName + " " + dominant_color_name + " " + pointName,
            "description": dominant_color_name + " " + pointName + " in a neighbourhood of the point (" + str(x) + ", " + str(y) + "), on the "+ locationName +" of the Mandelbrot set",
            "attributes": [
                {
                    "trait_type": "Stripe",
                    "value": stripe_s,
                },
                {
                    "trait_type": "Cycle",
                    "value": ncycle,
                },
                {
                    "trait_type": "Step",
                    "value": step_s,
                },
                {
                    "trait_type": "Zoom",
                    "value": zoom,
                },
                {
                    "trait_type": "Color",
                    "value": dominant_color_name,
                },
                {
                    "trait_type": "Point",
                    "value": pointName,
                },
                {
                    "trait_type": "Location",
                    "value": locationName,
                },
                {
                    "trait_type": "x",
                    "value": x,
                },
                {
                    "trait_type": "y",
                    "value": y,
                },
            ]
        }
        with open('./metadata/' + str(value), 'w') as outfile:
            json.dump(token, outfile, indent=4)


@eel.expose
def getRange():
    mand = Mandelbrot()
    mand.explore()
    return json.dumps(mand.range)


def convert_rgb_to_names(rgb_tuple):
    css3_db = CSS3_HEX_TO_NAMES
    names = []
    rgb_values = []

    for color_hex, color_name in css3_db.items():
        names.append(color_name)
        rgb_values.append(hex_to_rgb(color_hex))

    kdt_db = KDTree(rgb_values)

    distance, index = kdt_db.query(rgb_tuple)
    return names[index]

eel.start('index.html', port=0)
