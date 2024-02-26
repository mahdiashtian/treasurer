from rest_framework.exceptions import APIException


class PasswordDoesNotMatch(APIException):
    status_code = 400
    default_detail = 'پسورد ها با یک دیگر تطابق ندارند.'
    default_code = 'password_does_not_match'


class OldPasswordDoesNotMatch(APIException):
    status_code = 400
    default_detail = 'پسورد قبلی صحیح نمی باشد.'
    default_code = 'old_password_does_not_match'
