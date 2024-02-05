import os

import yaml

__all__ = ["i18n"]


class YAMLParser:
    def __init__(self):
        self.directory_path = os.path.dirname(os.path.realpath(__file__))
        self.yaml_data = self._load_all_yaml()

    def _load_all_yaml(self):
        yaml_data = {}
        for filename in os.listdir(self.directory_path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                file_path = os.path.join(self.directory_path, filename)
                with open(file_path) as file:
                    yaml_data[filename.split(".")[0]] = yaml.safe_load(file)
        return yaml_data

    def get_text(self, language_code):
        if language_code in self.yaml_data:
            return self.yaml_data[language_code]
        else:
            raise ValueError(
                f"Language code {language_code} not found in available YAML files."
            )


i18n = YAMLParser().get_text
