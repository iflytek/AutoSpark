import unittest

from artifacts_docker_tool import DockerImageListTool, ListImageTagsInput


class DockerImageListToolTestCase(unittest.TestCase):
    def setUp(self):
        self.tool = DockerImageListTool()

    def test_tool_name(self):
        self.assertEqual(self.tool.name, "Greetings Tool")

    def test_tool_args_schema(self):
        self.assertEqual(self.tool.args_schema, ListImageTagsInput)

    def test_tool_description(self):
        self.assertEqual(self.tool.description, "Sends List Image Input")

    def test_execute_method(self):
        list_input = ListImageTagsInput(repo_path="docker-private/atp")
        output = self.tool._execute(repo_path=list_input.repo_path)
        print(output)
        #self.assertEqual(output, expected_output)
