from dataclasses import dataclass
from typing import List
from core.bp_metadata_utils.policy import Policy, Validation


@dataclass
class BlueprintMetaData:
    """
    Class to represent blueprint metadata
    """
    # name: str
    # desc: str
    # author: str
    validations: List[Validation]
    
    def __json__(self):
        validations_json_list = []
        if self.validations:
          for validation in self.validations:
            if validation:
              validations_json_list.append(validation.__json__())

        return {
            # 'name': self.name,
            # 'desc': self.desc,
            # 'author': self.author,
            'validations': validations_json_list,
        }
