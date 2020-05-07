import sys
import os
import json
from PIL import Image


def check_image(file_path, height, width):
    if not os.path.isfile(file_path):
        print('Image file does not exit: {}'.format(file_path))
        return False

    image = Image.open(file_path)
    if image.size != (width, height):
        print('Image size does not match'.format(file_path))
        return False
    return True


def main(argv):
    root_path = argv[1]
    vott_path = os.path.join(root_path, 'train')

    if not os.path.exists(root_path):
        print('input path does not exit.')
        return

    output_dict = {}
    images = []
    annotations = []
    category_dict = {'home': 1, 'back': 2, 'hamburgermenu': 3, 'clickable': 4, 'more': 5, 'spinner': 6, 'search': 7,
                     'swipe': 8, 'edittext': 9, 'checkbox': 10, 'radio': 11, 'switch': 12, 'keyboard': 13}
    categories = [{"supercategory": "change_page", "id": 1, "name": "home"},
                  {"supercategory": "change_page", "id": 2, "name": "back"},
                  {"supercategory": "change_page", "id": 3, "name": "hamburgermenu"},
                  {"supercategory": "change_page", "id": 4, "name": "clickable"},
                  {"supercategory": "not_change_page", "id": 5, "name": "more"},
                  {"supercategory": "not_change_page", "id": 6, "name": "spinner"},
                  {"supercategory": "not_change_page", "id": 7, "name": "search"},
                  {"supercategory": "not_change_page", "id": 8, "name": "swipe"},
                  {"supercategory": "not_change_page", "id": 9, "name": "edittext"},
                  {"supercategory": "not_change_page", "id": 10, "name": "checkbox"},
                  {"supercategory": "not_change_page", "id": 11, "name": "radio"},
                  {"supercategory": "not_change_page", "id": 12, "name": "switch"},
                  {"supercategory": "not_change_page", "id": 13, "name": "keyboard"}]

    annotation_index = 0
    for image_id, json_file in enumerate(os.listdir(vott_path)):
        with open(os.path.join(vott_path, json_file), "r+") as fp:
            modified = False
            data = json.load(fp)
            height = data['asset']['size']['height']
            width = data['asset']['size']['width']
            file_name = data['asset']['name']
            image_path = os.path.join(os.path.join(root_path, 'Object_Detection'), file_name)
            if not check_image(image_path, height, width):
                continue
            image_data = {
                'height': height,
                'width': width,
                'id': image_id,
                'file_name': file_name

            }
            images.append(image_data)
            box_list = data['regions']
            for box in box_list:
                tag = box['tags']
                if len(tag) != 1:
                    a = 1
                tag = tag[0].lower()
                match = True
                if tag not in category_dict:
                    match = False

                if not match:
                    if tag == 'hambergermenu':
                        modified_tag = 'HamburgerMenu'
                        box['tags'][0] = modified_tag
                        tag = modified_tag.lower()
                        modified = True
                    # ignore the tag 'ad'
                    elif tag == 'ad':
                        continue

                box_dict = {
                    'image_id': image_id,
                    'area': box['boundingBox']['height'] * box['boundingBox']['width'],
                    "iscrowd": 0,
                    'bbox': [
                        box['boundingBox']['height'],
                        box['boundingBox']['width'],
                        box['boundingBox']['left'],
                        box['boundingBox']['top']
                    ],
                    'category_id': category_dict[tag],
                    'id': annotation_index
                }
                annotations.append(box_dict)
                annotation_index += 1
            if modified:
                fp.seek(0)
                json.dump(data, fp)
                fp.truncate()
    output_dict['images'] = images
    output_dict['categories'] = categories
    output_dict['annotations'] = annotations
    with open('/home/kimberly/projects/instances_train2017.json', 'w') as fp:
        json.dump(output_dict, fp)


if __name__ == '__main__':
    main(sys.argv)
