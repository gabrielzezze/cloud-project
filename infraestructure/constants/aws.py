DEFAULT_UBUNTU_IMAGE_ID = 'ami-0a91cd140a1fc148a'

# Frontend Names
FRONTEND_IMAGE_ID = "ami-047056bb387ad7173"
def get_frontend_image_id() -> str:
    return 'ami-0885b1f6bd170450c'

FRONTEND_SECURITY_GROUP_NAME = "zezze-frontend_security_group"
def get_frontend_security_group_name() -> str:
    return FRONTEND_SECURITY_GROUP_NAME


FRONTEND_LOAD_BALANCER_NAME = "zezze-frontend-load-balancer"
def get_frontend_load_balancer_name() -> str:
    return FRONTEND_LOAD_BALANCER_NAME


FRONTEND_TARGET_GROUP_NAME = "zezze-frontend-lb-target-group"
def get_frontend_lb_target_group_name() -> str:
    return FRONTEND_TARGET_GROUP_NAME

FRONTEND_LAUNCH_CONFIG_NAME = "zezze-frontend-launch-config"
def get_frontend_launch_config_name() -> str:
    return FRONTEND_LAUNCH_CONFIG_NAME

FRONTEND_AUTO_SCALING_GROUP_NAME = "zezze-frontend-as-group"
def get_frontend_auto_scaling_group_name() -> str:
    return FRONTEND_AUTO_SCALING_GROUP_NAME


# Backend names
BACKEND_SECURITY_GROUP_NAME = "zezze-backend-security-group"
def get_backend_security_group_name():
    return BACKEND_SECURITY_GROUP_NAME

BACKEND_IMAGE_ID = "ami-027d711a2459d7406"
def get_backend_image_id():
    return DEFAULT_UBUNTU_IMAGE_ID

BACKEND_ELASTIC_IP_NAME = "zezze-backend-elastic-ip"
def get_backend_elastic_ip_name():
    return BACKEND_ELASTIC_IP_NAME

BACKEND_ELASTIC_IP_ALLOC_ID = "eipalloc-0383a09bbaf5d3687"
def get_elastic_ip_alloc_id():
    return BACKEND_ELASTIC_IP_ALLOC_ID


# Database Names
DATABASE_SECURITY_GROUP_NAME = "zezze-database-security-group"
def get_database_security_group_name():
    return DATABASE_SECURITY_GROUP_NAME

DATABASE_IMAGE_ID = "ami-07fcffe449d86a37a"
def get_database_image_id():
    return DEFAULT_UBUNTU_IMAGE_ID

DATABASE_ELASTIC_IP_NAME = 'zezze-database-elastic-ip'
def get_database_elastic_ip_name():
    return DATABASE_ELASTIC_IP_NAME

# Backend VPN
BACKEND_VPN_GATEWAY_ELASTIC_IP_NAME = 'zezze-backend-vpn-gateway-elastic-ip'
def get_backend_vpn_gateway_elastic_ip_name():
    return BACKEND_VPN_GATEWAY_ELASTIC_IP_NAME

BACKEND_VPN_GATEWAY_NAME = 'zezze-backend-vpn-gateway'
def get_backend_vpn_gateway_name():
    return BACKEND_VPN_GATEWAY_NAME

BACKEND_VPN_GATEWAY_SECURITY_GROUP_NAME = 'zezze-backend-vpn-security-group'
def get_backend_vpn_gateway_security_group_name():
    return BACKEND_VPN_GATEWAY_SECURITY_GROUP_NAME

BACKEND_VPN_GATEWAY_IMAGE_ID = DEFAULT_UBUNTU_IMAGE_ID
def get_backend_vpn_gateway_image_id():
    return BACKEND_VPN_GATEWAY_IMAGE_ID


#Frontend Outway
FRONTEND_OUTWAY_NAME = 'zezze-frontend-outway'
def get_frontend_outway_name():
    return FRONTEND_OUTWAY_NAME

FRONTEND_OUTWAY_SECURITY_GROUP_NAME = 'zezze-frontend-outway-security-group'
def get_frontend_outway_security_group_name():
    return FRONTEND_OUTWAY_SECURITY_GROUP_NAME

FRONTEND_OUTWAY_IMAGE_ID = 'ami-0885b1f6bd170450c'
def get_frontend_outway_image_id():
    return FRONTEND_OUTWAY_IMAGE_ID

FRONTEND_OUTWAY_ELASTIC_IP_NAME = 'zezze-frontend-outway-elastic-ip'
def get_frontend_outway_elastic_ip_name():
    return FRONTEND_OUTWAY_ELASTIC_IP_NAME


