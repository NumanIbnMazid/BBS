from django import template
from utils.models import DashboardSetting, BBStranslation
from deep_translator import GoogleTranslator
from posts.models import Thread


register = template.Library()



@register.simple_tag(name='get_dashboard_setting')
def get_dashboard_setting():
    dashboard_setting_qs = DashboardSetting.objects.all()
    if not dashboard_setting_qs.exists():
        dashboard_setting_instance = DashboardSetting.objects.create(title="Dashboard")
        return dashboard_setting_instance
    else:
        dashboard_setting_instance = dashboard_setting_qs.last()
        return dashboard_setting_instance
    return None


@register.simple_tag(name='get_thread_list')
def get_thread_list():
    return Thread.objects.all()


@register.filter
def truncate_word(value, numWords):
    if value:
        return value[:numWords] + " ..."
    else:
        return "--"

@register.filter
def truncate_fifty_percent_word(value):
    if value:
        return value[:int(len(value)/2)] + " ..."
    else:
        return "--"

@register.filter
def remove_html_tags(text):
    """
    remove_html_tags() => Removes HTML Markup Tags
    """
    tag = False
    quote = False
    out = ""

    for c in text:
        if c == '<' and not quote:
            tag = True
        elif c == '>' and not quote:
            tag = False
        elif (c == '"' or c == "'") and tag:
            quote = not quote
        elif not tag:
            out = out + c

    return out


@register.filter
def get_file_type(value):
    if type(value) == str:
        values = value.split(".")
        file_extension = values[-1]
        image_file_extensions = ["jpg", "jpeg", "png", "gif"]
        doc_file_extensions = ["doc", "docx"]
        pdf_file_extensions = ["pdf"]
        if file_extension.lower() in image_file_extensions:
            return "image"
        elif file_extension.lower() in doc_file_extensions:
            return "document"
        elif file_extension.lower() in pdf_file_extensions:
            return "pdf"
        else:
            return "unknown"


@register.filter
def remove_id(value):
    if "_id" in value:
        return value.replace("_id", "")
    else:
        return value.replace(" id", "")


@register.simple_tag(takes_context=True)
def user_has_perm(context, permission):
    request = context['request']
    if request.user.has_perm(permission) == True:
        return True
    return False


@register.filter
def to_title(value):
    result = value.replace("_", " ").title()
    return result


@register.filter
def translate_to_jp(value):
    # def dashboard_setting():
    #     dashboard_setting_qs = DashboardSetting.objects.all()
    #     if not dashboard_setting_qs.exists():
    #         dashboard_setting_instance = DashboardSetting.objects.create(title="Dashboard")
    #         return dashboard_setting_instance
    #     else:
    #         dashboard_setting_instance = dashboard_setting_qs.last()
    #         return dashboard_setting_instance
    #
    # dashboard_setting = dashboard_setting()
    #
    # try:
    #     if dashboard_setting.allow_translation:
    #         bbs_translation_qs = BBStranslation.objects.filter(
    #             english_version__iexact=value
    #         )
    #         if bbs_translation_qs.exists():
    #             return bbs_translation_qs.last().japanese_version
    #         elif dashboard_setting.allow_auto_translation:
    #             return GoogleTranslator(source='auto', target='ja').translate(value)
    #         else:
    #             return value
    # except Exception as e:
    #     print(f"Exception: {str(e)}")
    #     return value

    return value


