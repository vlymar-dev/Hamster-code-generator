def load_proxies_from_file(file_path):
    proxies = []
    with open(file_path, 'r') as file:
        for line in file:
            proxy = line.strip()
            if proxy:
                proxies.append(proxy)
    return proxies


proxies = load_proxies_from_file('proxies.txt')

# Basic configuration of games and proxies
game_configs = [
    {
        'name': 'Chain Cube 2048',
        'app_token': 'd1690a07-3780-4068-810f-9b5bbf2931b2',
        'promo_id': 'b4170868-cef0-424f-8eb9-be0622e8e8e3',
        'base_delay': 20,
        'attempts': 20,
        'copies': 0,
    },
    {
        'name': 'Train Miner',
        'app_token': '82647f43-3f87-402d-88dd-09a90025313f',
        'promo_id': 'c4480ac7-e178-4973-8061-9ed5b2e17954',
        'base_delay': 20,
        'attempts': 15,
        'copies': 0,
    },
    {
        'name': 'Merge Away',
        'app_token': '8d1cc2ad-e097-4b86-90ef-7a27e19fb833',
        'promo_id': 'dc128d28-c45b-411c-98ff-ac7726fbaea4',
        'base_delay': 20,
        'attempts': 30,
        'copies': 0,
    },
    {
        'name': 'Twerk Race 3D',
        'app_token': '61308365-9d16-4040-8bb0-2f4a4c69074c',
        'promo_id': '61308365-9d16-4040-8bb0-2f4a4c69074c',
        'base_delay': 20,
        'attempts': 45,
        'copies': 15,
    },
    {
        'name': 'Polysphere',
        'app_token': '2aaf5aee-2cbc-47ec-8a3f-0962cc14bc71',
        'promo_id': '2aaf5aee-2cbc-47ec-8a3f-0962cc14bc71',
        'base_delay': 15,
        'attempts': 50,
        'copies': 0,
    },
    {
        'name': 'Mow and Trim',
        'app_token': 'ef319a80-949a-492e-8ee0-424fb5fc20a6',
        'promo_id': 'ef319a80-949a-492e-8ee0-424fb5fc20a6',
        'base_delay': 20,
        'attempts': 20,
        'copies': 0,
    },
    {
        'name': 'Zoopolis',
        'app_token': 'b2436c89-e0aa-4aed-8046-9b0515e1c46b',
        'promo_id': 'b2436c89-e0aa-4aed-8046-9b0515e1c46b',
        'base_delay': 20,
        'attempts': 35,
        'copies': 0,
    },
    {
        'name': 'Fluff Crusade',
        'app_token': '112887b0-a8af-4eb2-ac63-d82df78283d9',
        'promo_id': '112887b0-a8af-4eb2-ac63-d82df78283d9',
        'base_delay': 30,
        'attempts': 35,
        'copies': 0,
    },
    {
        'name': 'Tile Trio',
        'app_token': 'e68b39d2-4880-4a31-b3aa-0393e7df10c7',
        'promo_id': 'e68b39d2-4880-4a31-b3aa-0393e7df10c7',
        'base_delay': 20,
        'attempts': 35,
        'copies': 0,
    },
    {
        'name': 'Stone Age',
        'app_token': '04ebd6de-69b7-43d1-9c4b-04a6ca3305af',
        'promo_id': '04ebd6de-69b7-43d1-9c4b-04a6ca3305af',
        'base_delay': 20,
        'attempts': 40,
        'copies': 0,
    },
    {
        'name': 'Bouncemasters',
        'app_token': 'bc72d3b9-8e91-4884-9c33-f72482f0db37',
        'promo_id': 'bc72d3b9-8e91-4884-9c33-f72482f0db37',
        'base_delay': 20,
        'attempts': 35,
        'copies': 0,
    },
    {
        'name': 'Hide Ball',
        'app_token': '4bf4966c-4d22-439b-8ff2-dc5ebca1a600',
        'promo_id': '4bf4966c-4d22-439b-8ff2-dc5ebca1a600',
        'base_delay': 40,
        'attempts': 35,
        'copies': 0,
    },
    {
        'name': 'Pin Out Master',
        'app_token': 'd2378baf-d617-417a-9d99-d685824335f0',
        'promo_id': 'd2378baf-d617-417a-9d99-d685824335f0',
        'base_delay': 20,
        'attempts': 35,
        'copies': 0,
    },
    {
        'name': 'Count Masters',
        'app_token': '4bdc17da-2601-449b-948e-f8c7bd376553',
        'promo_id': '4bdc17da-2601-449b-948e-f8c7bd376553',
        'base_delay': 20,
        'attempts': 45,
        'copies': 15,
    },
    {
        'name': 'Infected Frontier',
        'app_token': 'eb518c4b-e448-4065-9d33-06f3039f0fcb',
        'promo_id': 'eb518c4b-e448-4065-9d33-06f3039f0fcb',
        'base_delay': 20,
        'attempts': 40,
        'copies': 0,
    },
    {
        'name': 'Among Waterr',
        'app_token': 'daab8f83-8ea2-4ad0-8dd5-d33363129640',
        'promo_id': 'daab8f83-8ea2-4ad0-8dd5-d33363129640',
        'base_delay': 20,
        'attempts': 45,
        'copies': 0,
    },
    {
        'name': 'Factory World',
        'app_token': 'd02fc404-8985-4305-87d8-32bd4e66bb16',
        'promo_id': 'd02fc404-8985-4305-87d8-32bd4e66bb16',
        'base_delay': 20,
        'attempts': 45,
        'copies': 0,
    },
]

# Convert the list of proxies to a list
proxy_keys = list(proxies)

# Check if there are enough proxies
total_proxies_needed = sum(config['copies'] for config in game_configs)
if len(proxy_keys) < total_proxies_needed:
    raise ValueError(f'Not enough proxies: {len(proxy_keys)} provided, but {total_proxies_needed} needed.')

# Variable to track the current proxy index
proxy_index = 0

# Generate a list of games based on the number of copies and proxies
games = []

for config in game_configs:
    for i in range(config['copies']):
        if proxy_index >= len(proxies):
            raise ValueError(
                f'Not enough proxies for game copies: {config["name"]} needs {config["copies"]} copies, '
                f'but only {len(proxies)} proxies are available.'
            )

        game_copy = {
            'name': config['name'],
            'app_token': config['app_token'],
            'promo_id': config['promo_id'],
            'proxy': proxies[proxy_index],
            'base_delay': config['base_delay'],
            'attempts': config['attempts'],
        }
        games.append(game_copy)
        proxy_index += 1
