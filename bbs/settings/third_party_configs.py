""" # Project Third Party Configurations # """

"""
----------------------- * Django Allauth Configuration * -----------------------
"""
LOGIN_REDIRECT_URL = '/'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # mandatory, optional, none
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_FORMS = {
    'login': 'users.forms.CustomLoginForm'
}


"""
----------------------- * Django CK Editor Configuration * -----------------------
"""
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_JQUERY_URL = "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.min.js"
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = False
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_BROWSE_SHOW_DIRS = True

CKEDITOR_CONFIGS = {
    'default': {
        'uiColor': '#cdc9ff',
        'height': '100%',
        'width': '100%',
        # 'skin': 'moono',
        # 'skin': 'office2013',
        # 'toolbar_Basic': [
        #     ['Source', '-', 'Bold', 'Italic']
        # ],
        'toolbar_NMNckCustomToolbarConfig': [
            {'name': 'document', 'items': [
                'Print', '-', 'Templates', '-', 'Maximize', 'ShowBlocks', 'Preview']},
            {'name': 'clipboard', 'items': [
                'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo', 'Find', 'Replace', '-', 'SelectAll']},
            '/',
            {'name': 'basicstyles',
             'items': ['TextColor', 'BGColor', '-', 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       ]},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak']},
            '/',
            {'name': 'styles', 'items': [
                'Styles', 'Format', 'FontSize']},
        ],
        # 'toolbar': 'NMNckCustomToolbarConfig',  # put selected toolbar config here
        'toolbar': 'Basic',  # put selected toolbar config here
        'toolbar': 'full',  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        'height': 500,
        'width': '100%',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
        "removePlugins": "exportpdf",
    }
}


"""
----------------------- * File Configuration * -----------------------
"""
ALLOWED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.svg']
MAX_UPLOAD_SIZE = 2621440

# File Validation Staffs
ALLOWED_DOCUMENT_FILE_TYPES = ['.doc', '.docx', '.pdf']


"""
----------------------- * Django Crispy Forms Configurations * -----------------------
"""

# CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"
CRISPY_CLASS_CONVERTERS = {
    "textinput": "textinput focus:border-app-theme-400 dark:focus:border-app-theme dark:focus:border-app-theme focus:outline-none focus:shadow-outline-app-theme dark:focus:shadow-outline-app-theme-200 dark:text-gray-800 dark:focus:shadow-outline-app-theme form-input",
    "passwordinput": "passwordinput focus:border-app-theme-400 dark:focus:border-app-theme dark:focus:border-app-theme focus:outline-none focus:shadow-outline-app-theme dark:focus:shadow-outline-app-theme-200 dark:text-gray-800 dark:focus:shadow-outline-app-theme form-input",
}
