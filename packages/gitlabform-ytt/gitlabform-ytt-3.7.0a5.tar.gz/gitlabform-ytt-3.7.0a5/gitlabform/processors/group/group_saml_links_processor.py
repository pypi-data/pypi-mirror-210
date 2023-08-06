from gitlabform.gitlab import GitLab
from gitlabform.processors.defining_keys import Key
from gitlabform.processors.multiple_entities_processor import MultipleEntitiesProcessor


class GroupSAMLLinksProcessor(MultipleEntitiesProcessor):
    def __init__(self, gitlab: GitLab):
        super().__init__(
            "group_saml_links",
            gitlab,
            list_method_name="get_saml_group_links",
            add_method_name="add_saml_group_link",
            delete_method_name="delete_saml_group_link",
            defining=Key("saml_group_name"),
            required_to_create_or_update=Key("saml_group_name"),
        )
