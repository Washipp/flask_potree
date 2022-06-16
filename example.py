from src.App.app import Tarasp

app = Tarasp(5000)
# app.add_point_cloud('./data/fragment.ply')
app.load_example_elements()
app.run()
