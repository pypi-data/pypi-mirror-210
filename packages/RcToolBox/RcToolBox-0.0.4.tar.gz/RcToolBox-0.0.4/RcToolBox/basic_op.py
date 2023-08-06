# some functions copy from nnUnet
import pickle
import os
import yaml
import json
import time
import glob
import shutil
import sys
"""load and save file"""


def add_parent_path(level=2):

    if level == 2:
        sys.path.append(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    elif level == 3:
        sys.path.append(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    elif level == 4:
        sys.path.append(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(
                        os.path.abspath(__file__))))))


def load_yaml(file):
    """

    :param file: yaml
    :return:
    """
    return yaml.load(open(file), Loader=yaml.FullLoader)


def load_json(file):
    with open(file, 'r') as f:
        tmp = json.load(f)
    return tmp


def save_json(obj, file, indent=4, sort_keys=False):
    with open(file, 'w') as f:
        json.dump(obj, f, sort_keys=sort_keys, indent=indent)


def load_pkl(path):
    pickle_file = open(path, 'rb')
    obj = pickle.load(pickle_file)
    pickle_file.close()
    return obj


def save_pkl(path, obj):
    pickle_file = open(path, 'wb')
    pickle.dump(obj, pickle_file)
    pickle_file.close()


def load_txt(file):
    filestream = []
    with open(file, 'r') as f:
        for line in f.readlines():
            line = line.rstrip('\n')
            filestream.append(line)
    return filestream


"""print with highlight"""


def sprint(content, placeholder=40):
    if isinstance(content, str):
        placeholder -= len(content)
        left_placeholder = int(placeholder / 2)
        right_placeholder = int(placeholder - left_placeholder)
        print('\n' + '-' * left_placeholder + content +
              '-' * right_placeholder)
    else:
        print('content should be str')


"""Timer"""


def programStart(program_name='it'):
    return time.time(), program_name


def programEnd(inputs):
    start, program_name = inputs
    end = time.time()
    time_slot = end - start
    if time_slot > 3600:
        print('{} cost: {} hour {} min {}s'.format(program_name,
                                                   time_slot // 3600,
                                                   time_slot % 3600 // 60,
                                                   time_slot % 60))
    elif time_slot > 60:
        print('{} cost: {} min {} s'.format(program_name, int(time_slot // 60),
                                            int(time_slot % 60)))
    else:
        print('{} cost: {:.1f} s'.format(program_name, time_slot))


"""Date"""


def get_date(detail=False):
    if detail:
        return time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
    else:
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def set_project_result_folder(project_name, add_date=True, overwrite=False):
    """ create project result folder, join(result_folder, project_name, get_date())


    Returns:
        _type_: _description_
    """

    if "Server_Result" in os.environ:
        result_folder = join(os.environ["Server_Result"], project_name)

        os.makedirs(result_folder, exist_ok=False)

        if add_date:
            result_folder = join(result_folder, get_date())

        sprint('Create Project Result folder')
        print('\n' + result_folder + '\n')
        
        if overwrite:
            print("be careful! we will delete {0}".format(result_folder))
            shutil.rmtree(result_folder, ignore_errors=True)
        
        os.makedirs(result_folder, exist_ok=False)

    else:
        raise RuntimeError("Server_Result not set in environment variables!")

    return result_folder


# shortcut
join = os.path.join

dir_path = os.path.dirname
abs_path = os.path.abspath
exists = os.path.exists

isdir = os.path.isdir
isfile = os.path.isfile

if __name__ == '__main__':

    print(get_date(detail=False))

    _ = programStart('Testing')
    for i in range(10000000):
        pass
    programEnd(_)