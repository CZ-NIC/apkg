"""
apkg exceptions

when apkg CLI run results in exception being raised
its exit_code is returned as process exit code
"""


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


# 10-29: Invalid
class InvalidUsage(ApkgException):
    msg_fmt = "Invalid usage: %(fail)s"
    exit_code = 10


class InvalidInput(ApkgException):
    msg_fmt = "Invalid input: %(fail)s"
    exit_code = 11


class InvalidType(ApkgException):
    msg_fmt = "Invalid type: $(var) must be %(desired)s but is %(type)s"
    exit_code = 12


class InvalidChoice(ApkgException):
    msg_fmt = "Invalid choice: %(var)s must be one of: %(opts)s (is: %(val)s)"
    exit_code = 13


class InvalidVersion(ApkgException):
    msg_fmt = "Invalid version: %(ver)s"
    exit_code = 14


class InvalidFormat(ApkgException):
    msg_fmt = "Invalid format: %(fmt)s"
    exit_code = 16


class InvalidArchiveFormat(InvalidFormat):
    msg_fmt = "Invalid archive format: %(fmt)s"
    exit_code = 17


class InvalidSourcePackageFormat(InvalidFormat):
    msg_fmt = "Invalid source package format: %(fmt)s"
    exit_code = 18


class InvalidCompatLevel(ApkgException):
    msg_fmt = (
        "Project compat level %(proj)s is newer than current"
        " apkg compat level %(apkg)s.\n\n"
        "Run `apkg compat` for more information.\n\n"
        "Please upgrade apkg to work with this project."
    )
    exit_code = 20


# 30-39: Missing and NotFound
class MissingRequiredArgument(ApkgException):
    msg_fmt = "Missing required argument: %(arg)s"
    exit_code = 30


class MissingRequiredConfigOption(ApkgException):
    msg_fmt = "Missing required config option: %(opt)s"
    exit_code = 31


class MissingPackagingTemplate(ApkgException):
    msg_fmt = "Missing package template: %(temp)s"
    exit_code = 32


class ArchiveNotFound(ApkgException):
    msg_fmt = "%(type)s archive not found: %(ar)s"
    exit_code = 36


class SourcePackageNotFound(ApkgException):
    msg_fmt = "%(type)s source package not found: %(srcpkg)s"
    exit_code = 37


# 40-49: Parsing
class ParsingFailed(ApkgException):
    msg_fmt = "Unable to parse: %(fail)s"
    exit_code = 42


# 50-59: remote failures
class FileDownloadFailed(ApkgException):
    msg_fmt = "Failed to download file with code %(code)s:\n\n%(url)s"
    exit_code = 52


# 60-69: Command
class CommandNotFound(ApkgException):
    msg_fmt = "Command not found: %(cmd)s"
    exit_code = 60


class CommandFailed(ApkgException):
    msg_fmt = "Command failed: %(cmd)s"
    exit_code = 62


class UnexpectedCommandOutput(ApkgException):
    msg_fmt = "Unexpected command output: %(out)s"
    exit_code = 64


# 70-79: Distro
class DistroNotSupported(ApkgException):
    msg_fmt = "Distro not supported: %(distro)s"
    exit_code = 70


# 80-89: auto-magic
class UnableToDetectUpstreamVersion(ApkgException):
    msg_fmt = (
        "Unable to detect upstream version.\n\n"
        "Please consider one of following:\n\n"
        "1) set upstream.archive_url\n"
        "2) set upstream.version_script to custom script\n"
        "3) manually supply version using -v/--version option")
    exit_code = 84
