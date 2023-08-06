class ResultAccess:
    def __init__(self):
        self.allow_access = False
        self.display_config = []
        self.filter_config = []
        self.log_statement_deny = []
        self.log_statement_allow = []

    def get_allow_access(self):
        if self.allow_access:
            print("statement_allow: {}".format(self.log_statement_allow))
        else:
            print("statement_deny: {}".format(self.log_statement_deny))

        return self.allow_access

    def set_allow_access(self, value: bool):
        self.allow_access = value

    def get_filter_config(self):
        """

        filter: [{'effect': 'allow', 'condition': [{'operator': 'StringEquals', 'field': 'deal:block',
        'values': ['KHDN'], 'qualifier': 'ForAnyValue', 'if_exists': False, 'ignore_case': False},
        {'operator': 'StringStartsWith', 'field': 'deal:scope_code', 'values': ['MB##HN'],
        'qualifier': 'ForAnyValue', 'if_exists': False, 'ignore_case': False}]}]
        :return:
        """
        # print(self.filter_config)
        dict_field = {}
        dict_exists = {}
        list_filter_config = []
        index_statement = 0
        for statement in self.filter_config:
            item_condition = []
            index_condition = 0
            effect = statement.get("effect")
            for condition in statement.get("condition"):
                operator = condition.get("operator")
                field = condition.get("field")
                qualifier = condition.get("qualifier")
                key_filter = self.build_key_filter_config(effect, operator, field, qualifier)
                if key_filter not in dict_field:
                    dict_field[key_filter] = [index_statement, index_condition]
                    item_condition.append(condition)
                else:
                    dict_exists[key_filter] = condition
                index_condition += 1
            if item_condition:
                list_filter_config.append({
                    'effect': effect,
                    'condition': item_condition
                })
            index_statement += 1
        for k, v in dict_exists.items():
            if k in dict_field:
                list_filter_config[dict_field.get(k)[0]].get("condition")[dict_field.get(k)[1]].get("values").extend(v.get("values"))

        return list_filter_config

    def add_filter_config(self, value):
        self.filter_config.append(value)

    def get_display_config(self):
        return self.display_config

    def add_display_config(self, value):
        self.display_config.append(value)

    @classmethod
    def build_key_filter_config(cls, effect, operator, field, qualifier):
        return effect + "#" + operator + "#" + field + "#" + qualifier

    @classmethod
    def extract_key_filter_config(cls, key_filter):
        items = key_filter.split("#")
        return {
            "effect": items[0],
            "operator": items[1],
            "field": items[2],
            "qualifier": items[3],
        }
    @classmethod
    def convert_data_save_log(cls, value):
        return {
            'merchant_id': value.get('merchant_id'),
            'policy_code': value.get('policy_code'),
            'statement_id': value.get('statement_id'),
            'effect': value.get('effect'),
            'action': value.get('action'),
            'resource': value.get('resource'),
        }

    def add_log_deny(self, value):
        self.log_statement_deny.append(self.convert_data_save_log(value))

    def add_log_allow(self, value):
        self.log_statement_allow.append(self.convert_data_save_log(value))
