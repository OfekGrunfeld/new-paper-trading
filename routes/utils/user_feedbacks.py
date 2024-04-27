from enum import Enum
class UserFeedbacks(Enum):
    internal_error = "Internal Server Error"
    something_wrong = "Something Wrong Happend. Please Try Again Later"
    success = "Success"
    password_not_match = "Passwords Do Not Match"