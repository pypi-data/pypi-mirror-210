import json

def parse_json(file_path, encoding):
    with open(file_path, 'r', encoding=encoding) as json_file:
        json_data = json.load(json_file)
    assert type(json_data['categories'])==dict
    assert type(json_data['tags'])==list

    category_list = list(json_data['categories'].keys())
    tag_list = json_data['tags']
    assert len(category_list)>=2

    def category_json2list(json_category, current_index_lists, prefix):
        if type(json_category)==str:
            current_index_lists += [prefix+[json_category]]
        elif type(json_category)==list:
            for item in json_category:
                current_index_lists = category_json2list(item, current_index_lists, prefix)
        elif type(json_category)==dict:
            for key, values in json_category.items():
                current_index_lists = category_json2list(values, current_index_lists, prefix+[key])
        return current_index_lists
    category_dict = {}
    for category in list(json_data['categories'].keys()):
        category_dict[category] = category_json2list(json_data['categories'][category], [], [category,])

    contents = json_data['contents']
    for content in contents:
        assert 'name' in content.keys()
        assert 'categories' in content.keys()
        assert set(content['categories'].keys())==set((category_dict.keys()))

    return category_list, tag_list, category_dict, contents

if __name__=="__main__":
    file_path = "../examples/dinner.json"
    category_list, tag_list, category_dict, contents = parse_json(file_path, encoding='utf-8')
