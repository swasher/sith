# coding: utf-8
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminFileWidget
import cloudinary


class AdminCloudinaryWidget(AdminFileWidget):

    #template_with_initial = ('%(initial_text)s: <a href="%(initial_url)s">%(initial)s</a> %(clear_template)s<br />%(input_text)s: %(input)s')
    # override:
    template_with_initial = ''

    #template_with_clear = '%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'
    # override:
    template_with_clear = ''

    def render(self, name, value, attrs=None):
        output = []

        if value and getattr(value, "url", None):

            try:
                caption = cloudinary.api.resource(value.public_id)['context']['custom']['caption']
            except (cloudinary.api.NotFound, KeyError):
                caption = '<br>'

            try:
                alt = cloudinary.api.resource(value.public_id)['context']['custom']['alt']
            except cloudinary.api.NotFound:
                alt = ''

            picture_preview = cloudinary.CloudinaryImage(value.public_id).image(format='JPG', width = 150, height = 150, crop = 'fill', alt = "Sample Image")
            picture_full = cloudinary.CloudinaryImage(value.public_id).build_url()
            picture = '<a href={}  target="_blank" alt="{}">{}</a>'.format(picture_full, alt, picture_preview)
            cloudinary_link = '<a href="https://cloudinary.com/console/media_library#/dialog/image/upload/{}" target="_blank">Cloudinary Link</a>'.format(value.public_id)

            output.append('<div>{}</div> <div class="cloudinary-image">{}</div><div>{}</div>'.format(caption, picture, cloudinary_link))

        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))