def define_prefixed_exports(
        options,
        document,
        *,
        exports_from_package,
        classes_in_package,
        prefix_in_package,
        default_prefix_in_document
):
    prefix_in_document = options.get(
        'prefix', default_prefix_in_document
    )
    for name in exports_from_package:
        name_in_package = prefix_in_package + name
        class_in_package = classes_in_package.get(name_in_package)
        name_in_document = prefix_in_document + name
        class_in_document = type(
            name_in_document,
            (class_in_package,),
            {'templateName': name_in_package}
        )
        document.context.addGlobal(
            name_in_document, class_in_document
        )
