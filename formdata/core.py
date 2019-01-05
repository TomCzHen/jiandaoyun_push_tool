from marshmallow import Schema, fields, pre_load


class Widget(Schema):

    @pre_load
    def process_data(self, in_value):
        return {'value': in_value}


class StringWidget(Widget):
    value = fields.Str()


class NumberWidget(Widget):
    value = fields.Number()


class TextAreaWidget(Widget):
    value = fields.Str()


class DateTimeWidget(Widget):
    value = fields.Str()


class ComboWidget(Widget):
    value = fields.Str()


class UserWidget(Widget):
    value = fields.Str()


class UserGroupWidget(Widget):
    value = fields.List(fields.Str())


class DeptWidget(Widget):
    value = fields.Str()


class DeptGroupWidget(Widget):
    value = fields.List(fields.Str())


class CheckBoxGroupWidget(Widget):
    value = fields.List(fields.Str())


class ComboCheckWidget(Widget):
    value = fields.List(fields.Str())


class RadioGroupWidget(Widget):
    value = fields.Str()


FIELD_WIDGETS = {
    'text': StringWidget,  # 单行文本
    'textarea': TextAreaWidget,  # 多行文本
    'number': NumberWidget,  # 数字
    'datetime': DateTimeWidget,  # 日期时间
    'radiogroup': RadioGroupWidget,  # 单选按钮组
    'checkboxgroup': CheckBoxGroupWidget,  # 复选框组
    'combo': ComboWidget,  # 下拉框
    'combocheck': ComboCheckWidget,  # 下拉复选框
    'user': UserWidget,  # 成员单选
    'usergroup': UserGroupWidget,  # 成员多选
    'dept': DeptWidget,  # 部门单选
    'deptgroup': DeptGroupWidget  # 部门多选
}


class FormData:
    _data_filter = None

    def __init__(self, widgets: list, payload: dict):
        self._widgets = widgets
        self._payload = payload
        self._exists_data = []
        self._initialize()

    @property
    def payload(self):
        return self._payload

    @property
    def exists_data(self):
        return self._exists_data

    @exists_data.setter
    def exists_data(self, value):
        self._exists_data = value

    @property
    def widgets(self):
        return self._widgets

    @property
    def app_id(self) -> str:
        return self.payload['app_id']

    @property
    def entry_id(self) -> str:
        return self.payload['entry_id']

    @property
    def identifier(self) -> str:
        return f'{self.app_id}-{self.entry_id}'

    @property
    def operate(self) -> str:
        return self.payload['op']

    @property
    def data(self) -> dict:
        return self.payload['data']

    @property
    def query_fields(self):
        return self.payload['query_fields']

    @property
    def data_filter(self):
        return self._data_filter

    @property
    def schema(self):
        return self._schema

    @property
    def is_start_workflow(self):
        return self.payload.get('is_start_workflow', False)

    def _initialize(self):

        self._schema = self._init_schema()
        self._data_filter = self._init_data_filter()

    def _init_data_filter(self):

        filter_fields = []
        filter_cond = []
        filter_limit = 11

        for widget in self.widgets:
            if widget['label'] in self.query_fields:
                filter_fields.append(widget['name'])
                filter_cond.append({
                    "field": widget['name'],
                    "type": widget['type'],
                    "method": "eq",
                    "value": [self.data[widget['label']]]
                })

        data_filter = {
            "limit": filter_limit,
            "fields": filter_fields,
            "filter": {
                "rel": "and",
                "cond": filter_cond
            }
        }

        return data_filter

    def _init_schema(self):
        schema_fields = {
            widget.get('name'): self._build_widget(widget=widget) for widget in self.widgets
        }
        schema_class = type(
            self.identifier,
            (Schema,),
            schema_fields
        )
        schema = schema_class()
        form_data_schema = schema.load(self.data)
        return form_data_schema

    def _build_widget(self, widget: dict):
        field_widget = FIELD_WIDGETS.get(widget['type'], None)
        if field_widget:
            return fields.Nested(field_widget, load_from=widget['label'])
        elif widget.get('type') == 'subform':
            return self._build_subform_widget(widget)

    def _build_subform_widget(self, widget: dict):
        schema_widgets = {
            widget.get('name'): self._build_widget(widget) for widget in widget['items']
        }

        schema_class = type(
            '{}-{}'.format(self.identifier, widget['name']),
            (Schema,),
            schema_widgets
        )

        sub_form_widget = fields.Nested(
            type(
                '{}-{}-subform'.format(self.identifier, widget['name']),
                (Widget,),
                {'value': fields.Nested(schema_class, many=True)}
            ),
            load_from=widget['label']
        )

        return sub_form_widget
