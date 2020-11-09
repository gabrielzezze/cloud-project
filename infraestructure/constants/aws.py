# Frontend Names
FRONTEND_IMAGE_ID = "ami-047056bb387ad7173"
def get_frontend_image_id() -> str:
    return FRONTEND_IMAGE_ID

FRONTEND_SECURITY_GROUP_NAME = "zezze-frontend_security_group"
def get_frontend_security_group_name() -> str:
    return FRONTEND_SECURITY_GROUP_NAME


FRONTEND_LOAD_BALANCER_NAME = "zezze-frontend-load-balancer"
def get_frontend_load_balancer_name() -> str:
    return FRONTEND_LOAD_BALANCER_NAME


FRONTEND_TARGET_GROUP_NAME = "zezze-frontend-lb-target-group"
def get_frontend_lb_target_group_name() -> str:
    return FRONTEND_TARGET_GROUP_NAME


# Backend names
BACKEND_SECURITY_GROUP_NAME = "zezze-backend-security-group"
def get_backend_security_group_name():
    return BACKEND_SECURITY_GROUP_NAME

BACKEND_IMAGE_ID = "ami-027d711a2459d7406"
def get_backend_image_id():
    return BACKEND_IMAGE_ID
