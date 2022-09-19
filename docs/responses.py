SUCCESS_GENERATE_SHORT_URL = {
    "success": True,
    "message": "Url generated successfully.",
    "data": {"short_url": "ml/0580d228441a6dc9b69e729db5b8334f"}
}
FAILED_GENERATE_SHORT_URL = {
    "error_code": 500,
    "success": False,
    "message": "Server failed to generate the short URL.",
    "data": {}
}

SUCCESS_DELETE_SHORT_URL = {
    "success": True,
    "message": "The Short URL is inactivated successfully.",
    "data": {}
}
FAILED_DELETE_SHORT_URL = {
    "error_code": -1,
    "success": False,
    "message": "Server failed to delete the requested URL.",
    "data": {}
}
NOT_FOUND_URL = {
    "error_code": -2,
    "success": False,
    "message": "Requested URL does not found or has deleted before.",
    "data": {}
}

SUCCESS_GET_URL_INFO = {
    "success": True,
    "message": "The URL info retrieved successfully.",
    "data": {
        "url_info": {
            "original": "http://www.google.com",
            "hashed": "ml/a2e419c8ef4e2d3d7f774e724a3a9308",
            "is_active": True,
            "created_at": "2022-09-19 15:29:36.552644+04:30",
            "statistics": []
        }
    }
}

FAILED_GET_URL_INFO = {
    "error_code": -1,
    "success": False,
    "message": "Server failed to retrieve the requested URL's info.",
    "data": {}
}

FAILED_REDIRECT_URL = {
    "error_code": -1,
    "success": False,
    "message": "Server failed to redirect the visitor.",
    "data": {}
}
