import os
from unittest import TestCase
from src.thoth_doc.parsers import env_var_parser


class EnvVarParserTestCase(TestCase):
    def setUp(self):
        os.environ['ENV_VAR_NAME'] = 'env_var_value'

    def test_env_var_parser(self):
        line = '[$env.ENV_VAR_NAME]'
        parsed = env_var_parser(line)
        self.assertEqual(parsed, 'env_var_value')

    def test_env_var_parser_multiple_on_same_line(self):
        line = '[$env.ENV_VAR_NAME] [$env.ENV_VAR_NAME]'
        parsed = env_var_parser(line)
        self.assertEqual(parsed, 'env_var_value env_var_value')

    def test_env_var_parser_with_other_text(self):
        line = 'some text [$env.ENV_VAR_NAME] some text'
        parsed = env_var_parser(line)
        self.assertEqual(parsed, 'some text env_var_value some text')

    def test_env_var_parser_embedded_in_codeline(self):
        line = 'some text `ENV_VAR_NAME=[$env.ENV_VAR_NAME]` some text'
        parsed = env_var_parser(line)
        self.assertEqual(parsed, 'some text `ENV_VAR_NAME=env_var_value` some text')
