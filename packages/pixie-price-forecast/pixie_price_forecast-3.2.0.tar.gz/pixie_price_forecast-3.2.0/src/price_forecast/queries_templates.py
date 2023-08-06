class QueryHandler:
    WHERE_DICT = {'leads_only': {'include': False, 'value': 'leads > 0'},
                  'is_professional': {'include': False, 'value': 'lister_name = 3'},
                  'flat': {'include': False, 'value': "property_type= 'flat'"},
                  'house': {'include': False, 'value': "property_type= 'house'"},
                  'all_properties': {'include': False, 'value': "property_type in ('house', 'flat')"},
                  'is_rent': {'include': False, 'value': "operation='rent' and price_m2 <100 and price_m2 >5"},
                  'is_sell': {'include': False, 'value': "operation='buy' and price_m2 <10000 and price_m2 >200"}}
    VALID_PROPERTY_TYPES = ['flat', 'house', 'all_properties']
    VALID_OPERATIONS = ['is_rent', 'is_buy']

    def __init__(self,
                 leads_only: bool = False,
                 is_professional: bool = False,
                 prop_type: str = 'flat',
                 operation_type: str = 'is_sell'):
        self.WHERE_DICT['leads_only']['include'] = leads_only
        self.WHERE_DICT['is_professional']['include'] = is_professional
        self.set_cat_values(prop_type, self.VALID_PROPERTY_TYPES)
        self.set_cat_values(operation_type, self.VALID_OPERATIONS)

    def set_cat_values(self, name_category: str, list_valid_values: list):
        """
        Determine whether flat-house or rent-sell
        :param name_category: Either flat, house, rent or sell
        :param list_valid_values: VALID_PROPERTY_TYPES or VALID_OPERATIONS.
        :return: Updates WHERE_DICT
        """
        try:
            self.WHERE_DICT[name_category]['include'] = True
        except KeyError:
            raise KeyError(f'{name_category} is not a valid property type. Please select among the following options:'
                           f' {", ".join(list_valid_values)}')

    def create_query(self, table_name: str, var_list: list):
        """
        Join all pieces.
        :param table_name: Name of the table.
        :param var_list: Group by var_list.
        :return: String containing query.
        """
        select_clause = self.get_base_select_clause(table_name=table_name)
        where_clause = self.get_where_clause()
        group_clause = self.get_group_clause(var_list=var_list)
        return select_clause+where_clause+'\n'+group_clause

    @staticmethod
    def get_base_select_clause(table_name: str) -> str:
        """
        Select clause.
        :param table_name: Name of the table in question
        :return: Select clause.
        """
        str_query = f"""
                select 
                    avg(price_m2) as mean_unitary_price, 
                    percentile_cont(0.50) within group (order by price_m2 asc) as median_unitary_price, 
                    avg(price) as mean_price, 
                    percentile_cont(0.50) within group (order by price asc) as median_price, 
                    count(*) as number_properties, 
                    max(price_m2) as max_price,
                    percentile_cont(0.99) within group (order by price_m2 asc) as perc_price_99,
                    percentile_cont(0.95) within group (order by price_m2 asc) as perc_price_95,
                    percentile_cont(0.90) within group (order by price_m2 asc) as perc_price_90,
                    percentile_cont(0.10) within group (order by price_m2 asc) as perc_price_10,
                    percentile_cont(0.05) within group (order by price_m2 asc) as perc_price_05,
                    percentile_cont(0.01) within group (order by price_m2 asc) as perc_price_01,
                    sum(visits) as visits,
                    sum(leads) as leads,
                    province as province
                from "{table_name}"
                """
        return str_query

    def get_where_clause(self):
        additional_conditions = []
        for key, sub_dict in self.WHERE_DICT.items():
            if sub_dict['include']:
                additional_conditions.append(sub_dict['value'])
        additional_conditions.insert(0, self.base_where_clause)
        return ' and '.join(additional_conditions)

    @staticmethod
    def get_group_clause(var_list: list):
        var_str = ', '.join(var_list)
        return f"group by {var_str}"

    @property
    def base_where_clause(self):
        return "where 1=1"


def query_read_data(mode: str, table_name: str = 'price_raw_data', use_tag: bool = False):
    q = f"""
        SELECT *
        FROM {table_name}
        WHERE extraction_type='{mode}'
    """
    if use_tag:
        q = q + ' and tag_use=TRUE'
    return q


def reset_use_tag(table_name: str):
    q = f"""
        UPDATE {table_name}
        SET tag_use=FALSE
        WHERE 1=1
    """
    return q
