import json
import os
from argparse import Namespace


class CfgDict(dict):
    """
    A subclass of `dict` with some useful changes, most notably 
    storing a path to save, including saving methods
    """

    def __init__(self, cfg_path, config: dict = {},
                 autofill: bool = False,
                 save_on_change: bool = False, sort_on_save: bool = False, start_empty=False):
        super().__init__()
        self.cfg_path = cfg_path
        self.save_on_change = False
        self.update(config)
        self.save_on_change = save_on_change
        self.sort_on_save = sort_on_save
        if not os.path.exists(self.cfg_path) and autofill:
            self.save(config)
        if not start_empty:
            self.load()

    def set_path(self, path):
        self.cfg_path = path
        return self

    def save(self, out_dict=None, indent=4):
        if not isinstance(out_dict, dict):
            out_dict = self
        if self.sort_on_save:
            out_dict = dict(sorted(out_dict.items()))
        with open(self.cfg_path, 'w+') as f:
            f.write(json.dumps(out_dict, indent=indent))
        return self

    def _save_on_change(self):
        if self.save_on_change:
            self.save()
            return True
        return False

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._save_on_change()
        return self

    def pop(self, *args, **kwargs):
        super().pop(*args, **kwargs)
        self._save_on_change()
        return self

    def clear(self):
        super().clear()
        return self

    def load(self):
        if os.path.exists(self.cfg_path):
            with open(self.cfg_path, 'r', encoding='utf-8') as config_file:
                data = config_file.read()
                try:
                    self.update(json.loads(data))
                except (json.decoder.JSONDecodeError, TypeError):
                    print(f'[!] failed to load config from {self.cfg_path}')
        else:
            self.save({})
        return self

    def get_namespace(self) -> Namespace:
        return Namespace(self)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if self.save_on_change:
            self.save()

    def __delitem__(self, key):
        super().__delitem__(key)
        if self.save_on_change:
            self.save()
