import connexion


def create_app():
    connexion_app = connexion.App(__name__, specification_dir='swagger/')
    connexion_app.add_api('api.yaml')
    return connexion_app.app
