# Override the name of the HTML output file

from plasTeX import Base


def file_name_from_label(node):
    label_descendants = node.getElementsByTagName('label')

    if not label_descendants:
        return id(node)

    label_node = label_descendants[0]
    label_value = label_node.attributes['label']

    if not label_value:
        return id(node)

    bad_characters = ': #$%^&*!~`"\'=?/{}[]()|<>;\\,.'
    replacement = '-'

    for character in bad_characters:
        label_value = label_value.replace(character, replacement)

    return label_value


Base.section.filenameoverride = property(file_name_from_label)

# End of file
