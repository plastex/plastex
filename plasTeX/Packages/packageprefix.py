import importlib
from plasTeX import Command
from plasTeX.Logging import getLogger

log = getLogger()


class PackagePrefixAdder(Command):
    macroName = 'addpackageprefix'
    args = 'prefix:str package:str'

    def invoke(self, tex):
        super().invoke(tex)
        attributes = self.attributes
        prefix = attributes['prefix']
        package = attributes['package']
        packages = self.ownerDocument.context.packages

        if package in packages:
            module = importlib.import_module(package)
            exports = getattr(module, 'package_prefix_exports', None)
            if exports is not None:
                for export in exports:
                    copy_name = prefix + export
                    main_name = '%s_%s' % (package, export)
                    main_class = getattr(module, main_name, None)
                    if main_class is not None:
                        copy_class = type(
                            copy_name,
                            (main_class,),
                            {'templateName': main_name}
                        )
                        self.ownerDocument.context.addGlobal(
                            copy_name, copy_class
                        )
                    else:
                        log.info(
                            'The export %s does not have a'
                            ' definition %s' % (export, main_name)
                        )
            else:
                log.info(
                    'The package %s does not define any exports'
                    ' to be prefixed' % package
                )
        else:
            log.info(
                'The package %s has not been loaded;'
                ' nothing to be prefixed' % package
            )
