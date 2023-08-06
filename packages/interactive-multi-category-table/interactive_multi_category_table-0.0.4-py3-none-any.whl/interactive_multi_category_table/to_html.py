import os
from .utils import parse_json

def json_to_html(json_file_path, encoding='utf-8'):
    category_list, tag_list, category_dict, contents = parse_json(json_file_path, encoding)
    title = os.path.split(json_file_path)[-1][:-5]

    with open(os.path.join(os.path.split(__file__)[0], "template.html"), "r") as f:
        html = f.read()

    html = html.replace("__title__", title)
    html = html.replace("__category_list__", str(category_list))
    html = html.replace("__tag_list__", str(tag_list))
    html = html.replace("__category_dict__", str(category_dict))
    html = html.replace("__contents__", str(contents))

    with open(json_file_path+".html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__=="__main__":
    json_file_path = "../examples/dinner.json"
    json_to_html(json_file_path)
