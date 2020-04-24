import xml.etree.ElementTree as elemTree
import shutil
import csv
import sys
import os
import json
import hashlib
from PIL import Image


def list_only_dir_sorted(input_path):
    input_folders = []
    for folder in os.listdir(input_path):
        if os.path.isdir(os.path.join(input_path, folder)):
            input_folders.append(folder)
    input_folders.sort()
    return input_folders


def get_package_name(xml_file_list):
    tree = elemTree.parse(xml_file_list[0])
    package_name = tree.getroot().getchildren()[0].attrib['package']
    return package_name


def process_xml(input_path, output_path):
    xml_file_list = []
    for file in os.listdir(input_path):
        if file.endswith('.xml'):
            xml_file_list.append(os.path.join(input_path, file))
    xml_file_list.sort()

    package_name = get_package_name(xml_file_list)
    for xml in xml_file_list:
        xml_modified = os.path.join(output_path, '{}_{}'.format(package_name, os.path.basename(xml)))
        shutil.copy(xml, xml_modified)
    return package_name


def convert_image_and_get_list(path):
    file_list = []
    for file in os.listdir(path):
        if file.endswith('.png'):
            image_path = os.path.join(path, file)
            image = Image.open(image_path)
            image_name, ext = os.path.splitext(image_path)
            converted_image_path = image_name + '.jpg'
            image.save(converted_image_path)
            assert os.path.exists(converted_image_path)
            file_list.append(converted_image_path)
            os.remove(image_path)
        elif file.endswith('.jpg'):
            file_list.append(os.path.join(path, file))
        else:
            print('not an image file: {}'.format(file))
    return file_list


def process_image(input_path, output_path, package_name):
    image_file_list = convert_image_and_get_list(input_path)
    for image in image_file_list:
        image_modified = os.path.join(output_path, '{}_{}'.format(package_name, os.path.basename(image)))
        shutil.copy(image, image_modified)


def process_action(input_path, output_path, package_name):
    input_txt = os.path.join(input_path, 'action tag.txt')
    action_data = []
    action_list = ['clickable', 'back', 'more', 'search', 'hamburgermenu', 'spinner', 'switch', 'checkbox', 'radio', 'home', 'swipe', 'scroll', 'edittext']
    with open(input_txt, newline='') as cvs:
        reader = csv.reader(cvs, delimiter='\t')
        for row in reader:
            if row[0] == 'restart':
                action_data.append(['restart'])
                continue
            files = row[1].split('->')
            start = '{}_{}.jpg'.format(package_name, files[0])
            end = '{}_{}.jpg'.format(package_name, files[1])
            action = row[2].lower()
            label = ''
            if len(row) > 3:
                label = row[3]
            if action not in action_list:
                print('action {} is not in action_list {}'.format(action, action_list))
            elif action == action_list[0] or action == action_list[1] or action == action_list[2] or \
                    action == action_list[3] or action == action_list[4] or action == action_list[9] or \
                    action == action_list[5] or action == action_list[6] or action == action_list[7] or \
                    action == action_list[8]:
                label = '{}-{}'.format(action, label)
                action = 'click'

            new_row = [start, end, action, label]
            action_data.append(new_row)
    with open(os.path.join(output_path, '{}.txt'.format(package_name)), 'w', newline='')as f:
        writer = csv.writer(f)
        writer.writerows(action_data)


def process_group(input_path, output_path, package_name):
    g_list = list_only_dir_sorted(input_path)
    package_path = os.path.join(output_path, package_name)
    if not os.path.exists(package_path):
        os.mkdir(package_path)

    group_list = []
    for i, g in enumerate(g_list):
        g_path = os.path.join(input_path, g)

        g_image_list = convert_image_and_get_list(g_path)
        if not g_image_list:
            print('a group folder is empty: {}'.format(os.path.join(input_path, g)))
            continue

        output_g_path = os.path.join(package_path, 'g' + "%03d" % i)
        os.makedirs(output_g_path, exist_ok=True)

        image_list = []
        for g_i in g_image_list:
            g_i_modified = '{}_{}'.format(package_name, os.path.basename(g_i))
            shutil.copy(os.path.join(g_path, g_i), os.path.join(output_g_path, g_i_modified))
            image_list.append(g_i_modified)
        group_list.append(image_list)

    with open(os.path.join(output_path, '{}.txt'.format(package_name)), 'w', newline='')as f:
        writer = csv.writer(f)
        writer.writerows(group_list)


def process_vott(input_path, output_path, package_name, new_source_directory):
    name_set = set()
    for asset in os.listdir(input_path):
        if asset.endswith('.json'):
            old_path = os.path.join(input_path, asset)

            with open(os.path.join(old_path)) as f:
                vott_dict = json.load(f)

            vott_dict['asset']['format'] = 'jpg'

            old_file_name = vott_dict['asset']['name']
            if old_file_name in name_set:
                raise Exception()
            name_set.add(old_file_name)
            new_file_name = '{}_{}'.format(package_name, old_file_name)
            vott_dict['asset']['name'] = new_file_name

            new_id_source = 'file:'+os.path.join(new_source_directory, new_file_name)
            vott_dict['asset']['path'] = new_id_source

            new_id = hashlib.md5(new_id_source.encode('utf-8')).hexdigest()
            vott_dict['asset']['id'] = new_id

            new_path = os.path.join(output_path, new_id+'-asset.json')

            with open(new_path, 'w') as f:
                json.dump(vott_dict, f, indent=4)


def main(argv):
    input_path = argv[1]
    output_path = argv[2]

    if not os.path.exists(input_path):
        print('input path does not exit.')
        return

    if not os.path.exists(output_path):
        print('output path does not exit.')
        return

    input_folder_list = ['action tag', 'grouping', 'images', 'vott', 'xml']
    output_folder_list = ['Action', 'Group', 'Object_Detection', 'VOTT', 'XML']
    index_action = 0
    index_group = 1
    index_od = 2
    index_vott = 3
    index_xml = 4

    for i in list_only_dir_sorted(input_path):
        app_folder_path = os.path.join(input_path, i)
        print('start processing: {}'.format(app_folder_path))

        input_folders = list_only_dir_sorted(app_folder_path)
        if not input_folders == input_folder_list:
            print('input path does not have appropriate folder structure')
            print(input_folders)
            print(input_folder_list)
            return

        for j in range(len(output_folder_list)):
            output_folder_path = os.path.join(output_path, output_folder_list[j])
            os.makedirs(output_folder_path, exist_ok=True)
            output_folder_list[j] = output_folder_path

        for k, input_folder in enumerate(input_folder_list):
            input_folder_path = os.path.join(app_folder_path, input_folder)
            input_folder_list[k] = input_folder_path


        # xml should pe processed first to get a package name.
        package_name = process_xml(input_folder_list[index_xml], output_folder_list[index_xml])
        process_image(input_folder_list[index_od], output_folder_list[index_od], package_name)
        process_action(input_folder_list[index_action], output_folder_list[index_action], package_name)
        process_group(input_folder_list[index_group], output_folder_list[index_group], package_name)

        new_source_directory = '/home/embian/dataset/MAUI/images'
        process_vott(input_folder_list[index_vott], output_folder_list[index_vott], package_name, new_source_directory)

        print('Done!')


if __name__ == '__main__':
    main(sys.argv)
