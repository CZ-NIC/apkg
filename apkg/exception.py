class ApkgException(Exception):
    msg_fmt = "An unknown error occurred"
    exit_code = 1

    def __init__(self, msg=None, exit_code=None, **kwargs):
        self.kwargs = kwargs
        if not msg:
            try:
                msg = self.msg_fmt % kwargs
            except Exception:
                # kwargs doesn't match those in message.
                # Returning this is still better than nothing.
                msg = self.msg_fmt
        if exit_code is not None:
            self.exit_code = exit_code
        super().__init__(msg)


class InvalidApkgCommand(ApkgException):
    msg_fmt = (
        "Invalid apkg command: %(command)s\n\n"
        "Run `apkg -h` to list supported commands."
    )
    exit_code = 10


class InvalidInput(ApkgException):
    msg_fmt = "Invalid input: %(fail)s"
    exit_code = 12


class InvalidType(ApkgException):
    msg_fmt = "Invalid type: $(var) must be %(desired)s but is %(type)s"
    exit_code = 14


class InvalidChoice(ApkgException):
    msg_fmt = "Invalid choice: %(var)s must be one of: %(opts)s (is: %(val)s)"
    exit_code = 16


class InvalidFormat(ApkgException):
    msg_fmt = "Invalid format: %(fmt)s"
    exit_code = 17


class InvalidArchiveFormat(InvalidFormat):
    msg_fmt = "Invalid archive format: %(fmt)s"
    exit_code = 18


class InvalidSourcePackageFormat(InvalidFormat):
    msg_fmt = "Invalid source package format: %(fmt)s"
    exit_code = 19


class MissingRequiredArgument(ApkgException):
    msg_fmt = "Missing required argument: %(arg)s"
    exit_code = 20


class MissingRequiredConfigOption(ApkgException):
    msg_fmt = "Missing required config option: %(opt)s"
    exit_code = 22


class MissingPackagingTemplate(ApkgException):
    msg_fmt = "Missing package template: %(temp)s"
    exit_code = 24


class ParsingFailed(ApkgException):
    msg_fmt = "Unable to parse: %(fail)s"
    exit_code = 30


class InvalidVersion(ApkgException):
    msg_fmt = "Invalid version: %(ver)s"
    exit_code = 40


class DistroNotSupported(ApkgException):
    msg_fmt = "Distro not supported: %(distro)s"
    exit_code = 44


class FileDownloadFailed(ApkgException):
    msg_fmt = "Failed to download file with code %(code)s:\n\n%(url)s"
    exit_code = 56


class CommandNotFound(ApkgException):
    msg_fmt = "Command not found: %(cmd)s"
    exit_code = 60


class CommandFailed(ApkgException):
    msg_fmt = "Command failed: %(cmd)s"
    exit_code = 62


class UnexpectedCommandOutput(ApkgException):
    msg_fmt = "Unexpected command output: %(out)s"
    exit_code = 66


class ArchiveNotFound(ApkgException):
    msg_fmt = "%(type)s archive not found: %(ar)s"
    exit_code = 80


class SourcePackageNotFound(ApkgException):
    msg_fmt = "%(type)s source package not found: %(srcpkg)s"
    exit_code = 82


class UnableToDetectUpstreamVersion(ApkgException):
    msg_fmt = (
        "Unable to detect upstream version.\n\n"
        "Please consider one of following:\n\n"
        "1) set upstream.archive_url "
        "(requires htmllistparse module)\n"
        "2) set upstream.version_script to custom script\n"
        "3) manually supply version using -v/--version option")
    exit_code = 90
