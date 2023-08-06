from ..keycloak import get_default_master_keycloak_admin


def create_realm_by_owner(realm_model):
    keycloak_admin = get_default_master_keycloak_admin()
    payload = dict(realm_model.base_config)
    payload['id'] = str(realm_model.id)
    payload['realm'] = realm_model.realm
    if realm_model.email_realm_config:
        payload['smtpServer'] = {
            "replyToDisplayName": realm_model.email_realm_config.replyToDisplayName,
            "starttls": realm_model.email_realm_config.starttls,
            "auth": realm_model.email_realm_config.auth,
            "envelopeFrom": realm_model.email_realm_config.envelopeFrom,
            "ssl": realm_model.email_realm_config.ssl,
            "password": realm_model.email_realm_config.password,
            "port": realm_model.email_realm_config.port,
            "replyTo": realm_model.email_realm_config.replyTo,
            "host": realm_model.email_realm_config.host,
            "from": realm_model.email_realm_config.from_email,
            "fromDisplayName": realm_model.email_realm_config.fromDisplayName,
            "user": realm_model.email_realm_config.user
        }
    else:
        payload.pop('smtpServer')

    keycloak_admin.create_realm(payload=payload)


def update_realm_by_owner(realm_model):
    keycloak_admin = get_default_master_keycloak_admin()
    payload = dict(realm_model.base_config)
    payload.pop('id')
    payload.pop('realm')
    payload['smtpServer'] = {}
    keycloak_admin.update_realm(realm_name=realm_model.realm, payload=payload)
    if realm_model.email_realm_config:
        payload['smtpServer'] = {
            "replyToDisplayName": realm_model.email_realm_config.replyToDisplayName,
            "starttls": realm_model.email_realm_config.starttls,
            "auth": realm_model.email_realm_config.auth,
            "envelopeFrom": realm_model.email_realm_config.envelopeFrom,
            "ssl": realm_model.email_realm_config.ssl,
            "password": realm_model.email_realm_config.password,
            "port": realm_model.email_realm_config.port,
            "replyTo": realm_model.email_realm_config.replyTo,
            "host": realm_model.email_realm_config.host,
            "from": realm_model.email_realm_config.from_email,
            "fromDisplayName": realm_model.email_realm_config.fromDisplayName,
            "user": realm_model.email_realm_config.user
        }
        keycloak_admin.update_realm(realm_name=realm_model.realm, payload=payload)


def delete_realm_by_owner(realm_model):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.delete_realm(realm_name=realm_model.realm)


def get_apps_login_by_owner(user):
    keycloak_admin = get_default_master_keycloak_admin()
    keycloak_admin.set_realm_name(realm_name=user.realm_name)
    logins = set([group.name for group in user.groups if group.name.startswith(
        f'login_{user.realm_name}')])
    clients = keycloak_admin.get_clients()
    clients = [
        client for client in clients if f"login_{user.realm_name}_{client['client_id']}" in logins]
    return clients