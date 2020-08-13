import os
import json
from shutil import copyfile


def get_coordinates(bounding_box_xywh):
    x1 = bounding_box_xywh['left']
    y1 = bounding_box_xywh['top']
    x2 = x1 + bounding_box_xywh['width']
    y2 = y1 + bounding_box_xywh['height']
    return x1, y1, x2, y2


def calculate_iou(box1, box2):
    # intersection
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)

    box1_area = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    box2_area = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)

    iou = inter_area / float(box1_area + box2_area - inter_area)

    return iou


def main():
    asset_path = 'c:/Users/kk316/Documents/ui_data_v10/ui/train_vott'
    folder_path = 'c:/Users/kk316/Documents/ui_data_v10/ui/train'

    # The data with overlapped bounding boxes will be saved in paths below
    output_path = 'c:/Users/kk316/Documents/ui_data_v10/ui/changed/train'
    output_vott_path = 'c:/Users/kk316/Documents/ui_data_v10/ui/changed/train_vott'

    # Made a new project in Vott, changed .vott to json, and used it to make a new .vott file.
    with open('./overlapped.json', 'r') as f:
        output_dict = json.load(f)
    asset_dict = {}
    for path in os.listdir(asset_path):
        if not path.endswith('.vott'):
            with open(os.path.join(asset_path, path), 'r') as f:
                vott_dict = json.load(f)
            asset = vott_dict['asset']
            id = vott_dict['asset']['id']
            bbox_list = []
            for r in vott_dict['regions']:
                bounding_box = r['boundingBox']
                x1, y1, x2, y2 = get_coordinates(bounding_box)
                bbox_list.append([x1, y1, x2, y2])

            for i in range(len(bbox_list) - 1):
                for j in range(i + 1, len(bbox_list)):
                    iou = calculate_iou(bbox_list[i], bbox_list[j])
                    if iou > 0.6:
                        file_name = asset['name']
                        json_file_name = id + '-asset.json'
                        copyfile(folder_path + '/' + file_name, output_path + '/' + file_name)
                        copyfile(asset_path + '/' + json_file_name, output_vott_path + '/' + json_file_name)
                        asset['path'] = 'file:' + output_path + '/' + file_name
                        asset_dict[id] = asset
                        continue

    with open('output.vott', 'w') as f:
        output_dict['assets'] = asset_dict
        json.dump(output_dict, f, indent=4)
