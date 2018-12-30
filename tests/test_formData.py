from unittest import TestCase
from formdata import FormData
import json


class TestFormData(TestCase):
    def test_form_data_string_widget(self):

        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{"单行文本":"单行文本"},"op":"create","query_fields":["单行文本"]}'
        raw_widgets = '{"widgets":[{"name":"_widget_text","label":"单行文本","type":"text"}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        payload = json.loads(raw_payload)
        form_data = FormData.create_form_data(widgets, payload)

        self.assertEqual(form_data.app_id, 'app_id')
        self.assertEqual(form_data.entry_id, 'entry_id')
        self.assertListEqual(form_data.query_fields, ['单行文本', ])
        self.assertDictEqual(form_data.schema.data['_widget_text'], {'value': '单行文本'})

    def test_form_data_number_widget(self):
        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{"数字1":123,"数字2":123.1},"op":"create","query_fields":["数字1"]}'
        raw_widgets = '{"widgets":[{"name":"_widget_number_1","label":"数字1","type":"number"},{"name":"_widget_number_2","label":"数字2","type":"number"}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        payload = json.loads(raw_payload)
        form_data = FormData.create_form_data(widgets, payload)
        self.assertDictEqual(form_data.schema.data['_widget_number_1'], {'value': 123})
        self.assertDictEqual(form_data.schema.data['_widget_number_2'], {'value': 123.1})

    def test_form_data_subform_widget(self):
        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{"数字":123,"子表单":[{"子表单单行文本":"子表单单行文本1","子表单数字":123.01},{"子表单单行文本":"子表单单行文本2","子表单数字":123.02}]},"op":"create","query_fields":["数字"]}'
        raw_widgets = '{"widgets":[{"name":"_widget_number","label":"数字","type":"number"},{"name":"_widget_subform","label":"子表单","type":"subform","items":[{"name":"_widget_subfrom_text","label":"子表单单行文本","type":"text"},{"name":"_widget_subform_number","label":"子表单数字","type":"number"}]}]}'

        widgets = json.loads(raw_widgets).get('widgets')
        payload = json.loads(raw_payload)
        form_data = FormData.create_form_data(widgets, payload)
        self.assertDictEqual(
            form_data.schema.data['_widget_subform'],
            {'value': [
                {'_widget_subform_number': {'value': 123.01}, '_widget_subfrom_text': {'value': '子表单单行文本1'}},
                {'_widget_subform_number': {'value': 123.02}, '_widget_subfrom_text': {'value': '子表单单行文本2'}}
            ]}
        )

    def test_form_data_multi_subform_widget(self):
        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{"数字":123,"子表单1":[{"子表单1单行文本":"子表单1单行文本1","子表单1数字":123.01},{"子表单1单行文本":"子表单1单行文本2","子表单1数字":123.02}],"子表单2":[{"子表单2单行文本":"子表单2单行文本1","子表单2数字":123.01},{"子表单2单行文本":"子表单2单行文本2","子表单2数字":123.02}]},"op":"create","query_fields":["数字"]}'
        raw_widgets = '{"widgets":[{"name":"_widget_number","label":"数字","type":"number"},{"name":"_widget_subform_1","label":"子表单1","type":"subform","items":[{"name":"_widget_subfrom_1_text","label":"子表单1单行文本","type":"text"},{"name":"_widget_subform_1_number","label":"子表单1数字","type":"number"}]},{"name":"_widget_subform_2","label":"子表单2","type":"subform","items":[{"name":"_widget_subfrom_2_text","label":"子表单2单行文本","type":"text"},{"name":"_widget_subform_2_number","label":"子表单2数字","type":"number"}]}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        payload = json.loads(raw_payload)
        form_data = FormData.create_form_data(widgets, payload)
        self.assertDictEqual(
            form_data.schema.data['_widget_subform_1'],
            {'value': [
                {'_widget_subform_1_number': {'value': 123.01}, '_widget_subfrom_1_text': {'value': '子表单1单行文本1'}},
                {'_widget_subform_1_number': {'value': 123.02}, '_widget_subfrom_1_text': {'value': '子表单1单行文本2'}}
            ]}
        )
        self.assertDictEqual(
            form_data.schema.data['_widget_subform_2'],
            {'value': [
                {'_widget_subform_2_number': {'value': 123.01}, '_widget_subfrom_2_text': {'value': '子表单2单行文本1'}},
                {'_widget_subform_2_number': {'value': 123.02}, '_widget_subfrom_2_text': {'value': '子表单2单行文本2'}}
            ]}
        )

    def test_form_data_user_widget(self):

        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{"成员单选":"user_id"},"op":"create","query_fields":["成员单选"]}'
        raw_widgets = '{"widgets":[{"name":"_widget_user","label":"成员单选","type":"user"}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        payload = json.loads(raw_payload)
        form_data = FormData.create_form_data(widgets, payload)
        self.assertDictEqual(form_data.schema.data['_widget_user'], {'value': 'user_id'})

    def test_form_data_usergroup_widget(self):
        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{"成员多选":["user_id_1","user_id_2"]},"op":"create","query_fields":["成员多选"]}'
        raw_widgets = '{"widgets":[{"name":"_widget_usergroup","label":"成员多选","type":"usergroup"}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        payload = json.loads(raw_payload)
        form_data = FormData.create_form_data(widgets, payload)
        self.assertDictEqual(form_data.schema.data['_widget_usergroup'], {'value': ['user_id_1', 'user_id_2']})

    def test_form_data_dept_widget(self):
        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{"部门单选":"dept_id"},"op":"create","query_fields":["部门单选"]}'
        raw_widgets = '{"widgets":[{"name":"_widget_dept","label":"部门单选","type":"dept"}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        payload = json.loads(raw_payload)
        form_data = FormData.create_form_data(widgets, payload)
        self.assertDictEqual(form_data.schema.data['_widget_dept'], {'value': 'dept_id'})

    def test_form_data_deptgroup_widget(self):
        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{"部门多选":["dept_id_1","dept_id_2"]},"op":"create","query_fields":["部门多选"]}'
        raw_widgets = '{"widgets":[{"name":"_widget_deptgroup","label":"部门多选","type":"deptgroup"}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        payload = json.loads(raw_payload)
        form_data = FormData.create_form_data(widgets, payload)
        self.assertDictEqual(form_data.schema.data['_widget_deptgroup'], {'value': ['dept_id_1', 'dept_id_2']})

    def test_create_form_data(self):
        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{"单行文本":"单行文本测试数据","数字":123.12,"日期时间":"2018-06-28","子表单":[{"单行文本":"子表单单行文本1","数字":123.12},{"单行文本":"子表单单行文本2","数字":123.12}]},"op":"create","query_fields":["单行文本"]}'
        raw_widgets = '{"widgets":[{"name":"_widget_1534402957633","label":"单行文本","type":"text"},{"name":"_widget_1534410141534","label":"数字","type":"number"},{"name":"_widget_1534486898848","label":"日期时间","type":"datetime"},{"name":"_widget_1534927008217","label":"下拉复选框","type":"combocheck"},{"name":"_widget_1534927008179","label":"复选框组","type":"checkboxgroup"},{"name":"_widget_1534732137668","label":"单选按钮组","type":"radiogroup"},{"name":"_widget_1534732137742","label":"下拉框","type":"combo"},{"name":"_widget_1534927008108","label":"部门多选","type":"deptgroup"},{"name":"_widget_1534732137803","label":"成员单选","type":"user"},{"name":"_widget_1534732137822","label":"部门单选","type":"dept"},{"name":"_widget_1534732138005","label":"子表单","type":"subform","items":[{"name":"_widget_1534732138017","label":"单行文本","type":"text"},{"name":"_widget_1534732138020","label":"数字","type":"number"},{"name":"_widget_1534732138024","label":"日期时间","type":"datetime"}]}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        payload = json.loads(raw_payload)
        form_data = FormData.create_form_data(widgets, payload)
        self.assertEqual(form_data.operate, 'create')
        self.assertEqual(form_data.identifier, 'app_id-entry_id')

    def test_create_from_data_payload_without_op_key(self):
        raw_widgets = '{"widgets":[{"name":"_widget_1534402957633","label":"单行文本","type":"text"},{"name":"_widget_1534410141534","label":"数字","type":"number"},{"name":"_widget_1534486898848","label":"日期时间","type":"datetime"},{"name":"_widget_1534927008217","label":"下拉复选框","type":"combocheck"},{"name":"_widget_1534927008179","label":"复选框组","type":"checkboxgroup"},{"name":"_widget_1534732137668","label":"单选按钮组","type":"radiogroup"},{"name":"_widget_1534732137742","label":"下拉框","type":"combo"},{"name":"_widget_1534927008108","label":"部门多选","type":"deptgroup"},{"name":"_widget_1534732137803","label":"成员单选","type":"user"},{"name":"_widget_1534732137822","label":"部门单选","type":"dept"},{"name":"_widget_1534732138005","label":"子表单","type":"subform","items":[{"name":"_widget_1534732138017","label":"单行文本","type":"text"},{"name":"_widget_1534732138020","label":"数字","type":"number"},{"name":"_widget_1534732138024","label":"日期时间","type":"datetime"}]}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{},"query_fields":["单行文本"]}'
        payload = json.loads(raw_payload)
        try:
            form_data = FormData.create_form_data(widgets, payload)
        except Exception:
            self.assertRaises(KeyError)

    def test_create_from_data_payload_without_query_fields_key(self):
        raw_widgets = '{"widgets":[{"name":"_widget_1534402957633","label":"单行文本","type":"text"},{"name":"_widget_1534410141534","label":"数字","type":"number"},{"name":"_widget_1534486898848","label":"日期时间","type":"datetime"},{"name":"_widget_1534927008217","label":"下拉复选框","type":"combocheck"},{"name":"_widget_1534927008179","label":"复选框组","type":"checkboxgroup"},{"name":"_widget_1534732137668","label":"单选按钮组","type":"radiogroup"},{"name":"_widget_1534732137742","label":"下拉框","type":"combo"},{"name":"_widget_1534927008108","label":"部门多选","type":"deptgroup"},{"name":"_widget_1534732137803","label":"成员单选","type":"user"},{"name":"_widget_1534732137822","label":"部门单选","type":"dept"},{"name":"_widget_1534732138005","label":"子表单","type":"subform","items":[{"name":"_widget_1534732138017","label":"单行文本","type":"text"},{"name":"_widget_1534732138020","label":"数字","type":"number"},{"name":"_widget_1534732138024","label":"日期时间","type":"datetime"}]}]}'
        widgets = json.loads(raw_widgets).get('widgets')
        raw_payload = '{"app_id":"app_id","entry_id":"entry_id","data":{},"op":"create"}'
        payload = json.loads(raw_payload)
        try:
            form_data = FormData.create_form_data(widgets, payload)
        except Exception:
            self.assertRaises(KeyError)
