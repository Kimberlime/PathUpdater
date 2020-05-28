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


def vott2coco(vott_path, input_image_folder, json_path):
    data_dict = {}
    images = []
    annotations = []
    count = 0
    category_dict = {'home': 1, 'back': 2, 'hamburgermenu': 3, 'clickable': 4, 'more': 5, 'spinner': 6, 'search': 7,
                     'swipe': 8, 'edittext': 9, 'checkbox': 10, 'radio': 11, 'switch': 12, 'keyboard': 13}
    category_count = []
    for _ in category_dict:
        category_count.append(0)
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

    annotation_index = 1
    path = os.listdir(vott_path)
    for image_id, json_file in enumerate(path):
        with open(os.path.join(vott_path, json_file), "r+") as fp:
            modified = False
            data = json.load(fp)
            height = data['asset']['size']['height']
            width = data['asset']['size']['width']
            file_name = data['asset']['name']
            image_path = os.path.join(input_image_folder, file_name)
            if not check_image(image_path, height, width):
                continue
            image_data = {
                'height': height,
                'width': width,
                'id': image_id,
                'file_name': file_name
            }
            box_dict_per_image = []
            box_list = data['regions']
            for box in box_list:
                tag = box['tags']
                if len(tag) != 1:
                    a = 1
                tag = tag[0].lower()
                # if tag != 'clickable':
                #     continue
                match = True
                if tag not in category_dict:
                    match = False

                if not match:
                    if tag != 'clickable':
                        continue
                    if tag == 'hambergermenu':
                        modified_tag = 'HamburgerMenu'
                        box['tags'][0] = modified_tag
                        tag = modified_tag.lower()
                        modified = True
                    # ignore the tag 'ad'
                    elif tag == 'ad':
                        continue
                    else:
                        raise Exception()
                category_id = category_dict[tag]
                category_count[category_id - 1] += 1
                count += 1
                box_dict = {
                    'image_id': image_id,
                    'area': box['boundingBox']['height'] * box['boundingBox']['width'],
                    "iscrowd": 0,
                    'bbox': [
                        box['boundingBox']['left'],
                        box['boundingBox']['top'],
                        box['boundingBox']['width'],
                        box['boundingBox']['height']
                    ],
                    'category_id': category_id,
                    'id': annotation_index
                }
                annotation_index += 1
                annotations.append(box_dict)
            if modified:
                fp.seek(0)
                json.dump(data, fp)
                fp.truncate()

            images.append(image_data)
            count += 1

    data_dict['images'] = images
    data_dict['categories'] = categories
    data_dict['annotations'] = annotations
    with open(json_path, 'w') as fp:
        json.dump(data_dict, fp, indent=4)
    print('total count: ' + str(count))
    print(category_dict)
    print('category count: ' + str(category_count))


def main(argv):
    root_path = argv[1]
    vott_path = os.path.join(root_path, 'test_vott')
    json_path = os.path.join(root_path, 'test.json')
    input_image_folder = os.path.join(root_path, 'test')

    if not os.path.exists(root_path):
        print('input path does not exit.')
        return

    vott2coco(vott_path, input_image_folder, json_path)


if __name__ == '__main__':
    main(sys.argv)
