# import unittest
# import os
# from cube_list_printer.pdf_generator import generate_pdf


# class TestPDFGenerator(unittest.TestCase):
#     def test_generate_pdf(self):
#         boosters = {
#             "Booster1": {
#                 "cards": [
#                     {
#                         "name": "Card A",
#                         "mana_cost": "{W}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card B",
#                         "mana_cost": "{U}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card C",
#                         "mana_cost": "{B}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card D",
#                         "mana_cost": "{G}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card E",
#                         "mana_cost": "{R}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card F",
#                         "mana_cost": "{W}{W}",
#                         "value": 5.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card G",
#                         "mana_cost": "{W}{B}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card H",
#                         "mana_cost": "{W}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card I",
#                         "mana_cost": "{W}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card J",
#                         "mana_cost": "{W}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card K",
#                         "mana_cost": "{W}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card L",
#                         "mana_cost": "{W}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card M",
#                         "mana_cost": "{W}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card N",
#                         "mana_cost": "{W}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                     {
#                         "name": "Card O",
#                         "mana_cost": "{W}",
#                         "value": 1.0,
#                         "image_local_path": "data/images/fake_id_placeholder.png",
#                     },
#                 ]
#             }
#         }
#         icon_map = {}
#         output_path = "test_output.pdf"
#         generate_pdf(output_path, boosters, icon_map, 63, 88)
#         self.assertTrue(os.path.exists(output_path))
#         os.remove(output_path)


# if __name__ == "__main__":
#     unittest.main()
