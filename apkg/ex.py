"""
apkg exceptions

when apkg CLI run results in exception being raised
its returncode is returned as process return code
"""


class ApkgException(Exception):
    msg_fmt = "An unknown error occurred"
    returncode = 1

    def __init__(self, msg=None, returncode=None, **kwargs):
        self.kwargs = kwargs
        if not msg:
            try:
                msg = self.msg_fmt.format(**kwargs)
            except Exception:
                # kwargs doesn't match those in message.
                # Returning this is still better than nothing.
                msg = self.msg_fmt
        if returncode is not None:
            self.returncode = returncode
        super().__init__(msg)


class QuietExit(ApkgException):
    msg_fmt = ""


# 10-29: Invalid
class InvalidUsage(ApkgException):
    msg_fmt = "Invalid usage: {fail}"
    returncode = 10


class InvalidInput(ApkgException):
    msg_fmt = "Invalid input: {fail}"
    returncode = 11


class InvalidType(ApkgException):
    msg_fmt = "Invalid type: $(var) must be {desired} but is {type}"
    returncode = 12


class InvalidChoice(ApkgException):
    msg_fmt = "Invalid choice: {var} must be one of: {opts} (is: {val})"
    returncode = 13


class InvalidVersion(ApkgException):
    msg_fmt = "Invalid version: {ver}"
    returncode = 14


class InvalidFormat(ApkgException):
    msg_fmt = "Invalid format: {fmt}"
    returncode = 16


class InvalidArchiveFormat(InvalidFormat):
    msg_fmt = "Invalid archive format: {fmt}"
    returncode = 17


class InvalidSourcePackageFormat(InvalidFormat):
    msg_fmt = "Invalid source package format: {fmt}"
    returncode = 18


class InvalidCompatLevel(ApkgException):
    msg_fmt = (
        "Project compat level {proj} is newer than current"
        " apkg compat level {apkg}.\n\n"
        "Run `apkg compat` for more information.\n\n"
        "Please upgrade apkg to work with this project."
    )
    returncode = 20


class InvalidVariablesSource(ApkgException):
    msg_fmt = "Invalid variables source: {src}"
    returncode = 26


# 30-39: Missing and NotFound
class MissingRequiredArgument(ApkgException):
    msg_fmt = "Missing required argument: {arg}"
    returncode = 30


class MissingRequiredConfigOption(ApkgException):
    msg_fmt = "Missing required config option: {opt}"
    returncode = 31


class MissingPackagingTemplate(ApkgException):
    msg_fmt = "Missing package template: {temp}"
    returncode = 32


class ArchiveNotFound(ApkgException):
    msg_fmt = "{type} archive not found: {ar}"
    returncode = 36


class SourcePackageNotFound(ApkgException):
    msg_fmt = "{type} source package not found: {srcpkg}"
    returncode = 37


# 40-49: Parsing
class ParsingFailed(ApkgException):
    msg_fmt = "Unable to parse: {fail}"
    returncode = 42


# 50-59: remote failures
class FileDownloadFailed(ApkgException):
    msg_fmt = "Failed to download file with code {code}:\n\n{url}"
    returncode = 52


# 60-69: Command
class CommandNotFound(ApkgException):
    msg_fmt = "Command not found: {cmd}"
    returncode = 60


class CommandFailed(ApkgException):
    msg_fmt = (
        "Command failed: {cmdout.args_str} "
        "(return code: {cmdout.returncode})"
    )
    returncode = 62


class UnexpectedCommandOutput(ApkgException):
    msg_fmt = "Unexpected command output: {out}"
    returncode = 64


# 70-79: Distro
class DistroNotSupported(ApkgException):
    msg_fmt = "Distro not supported: {distro}"
    returncode = 70


# 80-89: auto-magic
class UnableToDetectUpstreamVersion(ApkgException):
    msg_fmt = (
        "Unable to detect upstream version.\n\n"
        "Please consider one of following:\n\n"
        "1) set upstream.archive_url\n"
        "2) set upstream.version_script to custom script\n"
        "3) manually supply version using -v/--version option")
    returncode = 84


# 100-110: package tests
class PkgTestFail(ApkgException):
    msg_fmt = "Packaging tests failed."
    returncode = 100
