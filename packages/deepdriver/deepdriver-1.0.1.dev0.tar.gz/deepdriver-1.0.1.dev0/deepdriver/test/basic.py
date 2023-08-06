import random
import PIL
import pandas as pd
import shutil
import unittest
from deepdriver.test.setting import Setting
import json
from deepdriver import *

# Lower the log level for the debugging purpose
logger.setLevel(logging.DEBUG)

class TestBasic(unittest.TestCase):

    @classmethod
    def setUpClass(cl):
        setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
        succeeded = login(Setting.LOGIN_KEY)

    @classmethod
    def tearDownClass(cls):
        pass

    # def test_1(self):
    #     # 1 로그인
    #     setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
    #     succeeded = login(Setting.LOGIN_KEY)
    #     self.assertTrue(succeeded)

    def test_2(self):
        # 2.2 실험환경 생성
        run = init()
        self.assertEqual("uncategorized", run.exp_name)
        self.assertEqual("molamola.bokchi", run.team_name)

        exp_name = "exp1"
        run = init(exp_name)
        self.assertEqual(exp_name, run.exp_name)

        # team_name = "team1"
        # run = init(exp_name, team_name)
        # self.assertEqual(exp_name, run.exp_name)
        # self.assertEqual(team_name, run.team_name)

        run_name = "run1"
        run = init(exp_name,  run.team_name, run_name)
        self.assertEqual(exp_name, run.exp_name)
        self.assertEqual( run.team_name, run.team_name)
        self.assertEqual(run_name, run.run_name)

    def test_3(self):
        # 3.1.1.1 DataFrame
        df1 = DataFrame(columns=["a", "b", "c"], data=[[1, 2, 3]])
        pd_df = pd.DataFrame(columns=["a", "b", "c"], data=[[1, 2, 3]])
        df2 = DataFrame(dataframe=pd_df)
        self.assertEqual(df1.data, df2.data)
        self.assertEqual(df1.columns, df2.columns)
        self.assertTrue(df1.dataframe.equals(df2.dataframe))

        # 3.1.1.2 Table
        tbl = Table(data=df1)
        key_name = "test"
        data = {
            "data": {
                "columns": ["a","b","c"],
                "data" :[[1, 2, 3]]
            },
            "log_type":"table",
            "path": key_name+".TABLE.json",
            "cols":3,
            "rows":1
        }
        json_data = json.dumps(data)

        #self.assertEqual(tbl.to_json(key_name), f"{{\"log_type\": \"table\", \"path\": \"{key_name}.Table.json\", \"cols\": 3, \"rows\": 1}}")
        self.assertEqual(tbl.to_json(key_name), json_data)



        # 3.1.1.3 Image
        random.seed(0)
        pil_img = PIL.Image.open(os.path.join("deepdriver", "test", "cat_dog", "cat", "cat.png"))
        deep_img = Image(pil_img)
        self.assertEqual(deep_img.height, 100)
        self.assertEqual(deep_img.width, 100)
        self.assertEqual(deep_img.format, "PNG")
        os.remove(deep_img.local_path)

        # 3.1.2 Chart
        chart = Chart(df1, "Chart", {"x": "step", "y" :"height"}, {"title" :"what a great Chart plot"})
        data = {"data": {"columns": ["a", "b", "c"], "data": [[1, 2, 3]]}, "log_type": "chart", "chart_type": "Chart", "data_fields": {"x": "step", "y": "height"}, "label_fields": {"title": "what a great Chart plot"}, "path": key_name+".CHART.json"}
        json_data = json.dumps(data)

        self.assertEqual(chart.to_json(key_name),json_data)

        histogram_chart = histogram(df1, x="step", y="height", title= "what a great histogram plot")
        data = {"data": {"columns": ["a", "b", "c"], "data": [[1, 2, 3]]}, "log_type": "chart", "chart_type": "histogram", "data_fields": {"x": "step", "y": "height"}, "label_fields": {"title": "what a great histogram plot"}, "path": key_name+".CHART.json"}
        json_data = json.dumps(data)

        self.assertEqual(histogram_chart.to_json(key_name), json_data)

        line_chart = line(df1, x="step", y="height", title= "what a great line plot")
        data = {"data": {"columns": ["a", "b", "c"], "data": [[1, 2, 3]]}, "log_type": "chart", "chart_type": "line", "data_fields": {"x": "step", "y": "height"}, "label_fields": {"title": "what a great line plot"}, "path": key_name+".CHART.json"}
        json_data = json.dumps(data)

        self.assertEqual(line_chart.to_json(key_name), json_data)

        scatter_chart = scatter(df1, x="step", y="height", title= "what a great scatter plot")
        data = {"data": {"columns": ["a", "b", "c"], "data": [[1, 2, 3]]}, "log_type": "chart", "chart_type": "scatter", "data_fields": {"x": "step", "y": "height"}, "label_fields": {"title": "what a great scatter plot"}, "path": key_name+".CHART.json"}
        json_data = json.dumps(data)

        self.assertEqual(scatter_chart.to_json(key_name), json_data)
    def test_4(self):
        # Move test data to the temp test directory
        test_dir_name = "cat_dog"
        test_org_path = os.path.join("deepdriver", "test", test_dir_name)
        test_temp_path = os.path.join(".", test_dir_name)
        shutil.move(test_org_path, test_temp_path)

        try:
            # 4.1 Artifact

            # add() without a name parameter
            exp_paths = '''[{'path': 'cat/cat.png', 'local_path': './cat_dog/cat/cat.png', 'size': 7695, 'digest': '837018be54b49e5592e114b82497dd1d', 'status': 'ADD', 'lfs_yn': '', 'repo_tag': '', 'type': 'FILE', 'metadata': '', 'key': ''},{'path': 'dog/dog.png', 'local_path': './cat_dog/dog/dog.png', 'size': 7507, 'digest': '806ed4db95b39278a992d36f2e08b549', 'status': 'ADD', 'lfs_yn': '', 'repo_tag': '', 'type': 'FILE', 'metadata': '', 'key': ''}]'''
            #exp_paths = f"[{{path:{os.path.join('cat', 'cat.png')},local_path:{os.path.join(test_temp_path, 'cat', 'cat.png')},size:7507,digest:806ed4db95b39278a992d36f2e08b549,status:ADD,lfs_yn:,repo_tag:,type:FILE,metadata:,key:}},{{path:{os.path.join('dog', 'dog.png')},local_path:{os.path.join(test_temp_path, 'dog', 'dog.png')}}}]"
            arti1 = Artifacts("animal", "dataset")
            arti1.add(test_temp_path)
            print(str(arti1))
            print(exp_paths)
            self.assertEqual(str(arti1), exp_paths)

            arti2 = Artifacts("animal", "dataset")
            arti2.add(os.path.relpath(test_temp_path))
            self.assertEqual(str(arti2), exp_paths)

            arti3 = Artifacts("animal", "dataset")
            arti3.add(os.path.join(os.getcwd(), test_dir_name))
            self.assertEqual(str(arti3), exp_paths)

            arti4 = Artifacts("animal", "dataset")
            arti4.add(os.path.join(test_dir_name, "cat"))
            self.assertEqual(str(arti4), f"[{{path:cat.png,local_path:{os.path.join(test_temp_path, 'cat', 'cat.png')}}}]")

            # add() with a name parameter
            exp_paths = f"[{{path:{os.path.join('cat_dog', 'cat', 'cat.png')},local_path:{os.path.join(test_temp_path, 'cat', 'cat.png')}}},{{path:{os.path.join('cat_dog', 'dog', 'dog.png')},local_path:{os.path.join(test_temp_path, 'dog', 'dog.png')}}}]"
            arti1 = Artifacts("animal", "dataset")
            arti1.add(test_temp_path, test_dir_name)
            self.assertEqual(str(arti1), exp_paths)

            arti2 = Artifacts("animal", "dataset")
            arti2.add(os.path.relpath(test_temp_path), test_dir_name)
            self.assertEqual(str(arti2), exp_paths)

            arti3 = Artifacts("animal", "dataset")
            arti3.add(os.path.join(os.getcwd(), test_dir_name), test_dir_name)
            self.assertEqual(str(arti3), exp_paths)

            # 4.5 아티팩트 업로드
            succeeded = arti3.upload()
            self.assertTrue(succeeded)

        finally:
            # Move test data back to the original test directory
            shutil.move(test_temp_path, test_org_path)

        # 4.6 아티팩트 다운로드
        name = "animal"
        type = "dataset"
        arti3 = get_artifact(name, type)
        path = arti3.download()
        self.assertEqual(os.path.join(".", "deepdriver", "artifact", "5678"), path)
        shutil.rmtree(path)

    def test_5(self):
        # 5.2 로그 전송
        succeeded = log({"key-test": "value-test"})
        self.assertTrue(succeeded)

        # 5.3 아티팩트 전송

        # Move test data to the temp test directory
        test_dir_name = "cat_dog"
        test_org_path = os.path.join("deepdriver", "test", test_dir_name)
        test_temp_path = os.path.join(test_dir_name)
        shutil.move(test_org_path, test_temp_path)

        try:
            arti = Artifacts("animal", "dataset")
            arti.add(test_temp_path, test_dir_name)
            succeeded = upload_artifact(arti)
            self.assertTrue(succeeded)

        finally:
            # Move test data back to the original test directory
            shutil.move(test_temp_path, test_org_path)

        # 5.5 실행 종료
        succeeded = finish()
        self.assertTrue(succeeded)
