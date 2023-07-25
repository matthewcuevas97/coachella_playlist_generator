CLIENT_ID = "e36288ab18cf49429e1557dde04554a6"
CLIENT_SECRET = "563acf13011c43cab8d4ce23922d0aa8"

#TODO: use access and refresh tokens temporarily to test
a = 'BQAsXqj6N3QmZVww5VnTINiu7U2M01LQkMIGOTxgN_bkA_zmGPTaZJDVFj_DYpCmPhHSD1cm76z6rt3EH8wwp-DTwZDcpuiOrK5v_4tdUcAJb7TOlQeN8rQwHWMWzgoYnGqEKt--T1ocZ7ZnCsRG0LCZfHj6YWmgUVlPuE-a7dY0VrbTL5ixvTeO6wGDJe-iTGU_G-erTJh18eE'
r = 'AQAHcqJ1jm73z3OIpmlrTbjzmPLyhu1bRK01CxC9aKUXsPm5_6XVxaobRWH_xCiGSkBYAR6B_DWOfJkOD8wByiHA0UGcA7f1h0WnNu3msQ1RzU1hCB0giaeAyu2yQCNQQE8'

import utils

def generate_playlist(access_token, refresh_token, lineup):
    top_artists = utils.get_my_top(access_token, item="artists")
    top_tracks = utils.get_my_top(access_token, item="tracks")


    return 5

def follow_playlist_copy(access_token, refresh_token):

    return 5




if __name__ == '__main__':
    generate_playlist(a, r)