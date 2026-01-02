# # web.py
# import flet as ft
# from gui import flet_creb

# def main(page: ft.Page):
#     page.title = "CREB Chemical Suite"  # App name
#     page.route_strategy = "hash"
    
#     # Your app code here...

# if __name__ == "__main__":

#     # app(target=flet_creb.main)
#     ft.app(
#         target=flet_creb.main,
#         view=None,
#         route_url_strategy="hash",
#         assets_dir="assets",
#         # You can also set theme here
#         theme_mode=ft.ThemeMode.LIGHT
#     )

from flet import app
from gui import flet_creb
app(target=flet_creb.main)