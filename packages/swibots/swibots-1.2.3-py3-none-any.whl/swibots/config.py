import os


APP_CONFIG = {
    "CHAT_SERVICE": {
        "BASE_URL": os.getenv("CHAT_SERVICE_BASE_URL") or "https://api-gateway.switch.pe/chat-service",
        "WS_URL": os.getenv("CHAT_SERVICE_WS_URL")
        or "wss://api-gateway.switch.pe/chat-service/v1/websocket/message/ws",
    },
    "BOT_SERVICE": {
        "BASE_URL": os.getenv("BOT_SERVICE_BASE_URL") or "https://api-gateway.switch.pe/chat-service",
    },
    "AUTH_SERVICE": {
        "BASE_URL": os.getenv("AUTH_SERVICE_BASE_URL") or "https://api-gateway.switch.pe/user-service/api",
    },
    "COMMUNITY_SERVICE": {
        "BASE_URL": os.getenv("COMMUNITY_SERVICE_BASE_URL") or "https://api-gateway.switch.pe/community-service",
        "WS_URL": os.getenv("COMMUNITY_SERVICE_WS_URL")
        or "wss://api-gateway.switch.pe/community-service/v1/websocket/community/ws",
    },
}


def get_config():
    return APP_CONFIG


def reload_config():
    APP_CONFIG["CHAT_SERVICE"]['BASE_URL'] = os.getenv(
        "CHAT_SERVICE_BASE_URL") or "https://api-gateway.switch.pe/chat-service"
    APP_CONFIG["CHAT_SERVICE"]['WS_URL'] = os.getenv(
        "CHAT_SERVICE_WS_URL") or "wss://api-gateway.switch.pe/chat-service/v1/websocket/message/ws"
    APP_CONFIG["BOT_SERVICE"]['BASE_URL'] = os.getenv(
        "BOT_SERVICE_BASE_URL") or "https://api-gateway.switch.pe/chat-service"
    APP_CONFIG["AUTH_SERVICE"]['BASE_URL'] = os.getenv(
        "AUTH_SERVICE_BASE_URL") or "https://api-gateway.switch.pe/user-service/api"
    APP_CONFIG["COMMUNITY_SERVICE"]['BASE_URL'] = os.getenv(
        "COMMUNITY_SERVICE_BASE_URL") or "https://api-gateway.switch.pe/community-service"
    APP_CONFIG["COMMUNITY_SERVICE"]['WS_URL'] = os.getenv(
        "COMMUNITY_SERVICE_WS_URL") or "wss://api-gateway.switch.pe/community-service/v1/websocket/community/ws"


reload_config()
