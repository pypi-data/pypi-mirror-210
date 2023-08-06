"""Base support for creating commands."""

import argparse
import inspect
import io
import json
import logging
import platform
import os
import subprocess
import sys
from urllib.parse import urlparse

import colorama
import pkg_resources

from rbtools import get_version_string
from rbtools.api.capabilities import Capabilities
from rbtools.api.client import RBClient
from rbtools.api.errors import APIError, ServerInterfaceError
from rbtools.api.resource import RootResource
from rbtools.api.transport.sync import SyncTransport
from rbtools.clients import scan_usable_client
from rbtools.clients.errors import OptionsCheckError
from rbtools.deprecation import RemovedInRBTools40Warning
from rbtools.diffs.tools.errors import MissingDiffToolError
from rbtools.utils.console import get_input, get_pass
from rbtools.utils.filesystem import (cleanup_tempfiles, get_home_path,
                                      is_exe_in_path, load_config)
from rbtools.utils.repository import get_repository_resource


RB_MAIN = 'rbt'


class CommandExit(Exception):
    def __init__(self, exit_code=0):
        super(CommandExit, self).__init__('Exit with code %s' % exit_code)
        self.exit_code = exit_code


class CommandError(Exception):
    pass


class ParseError(CommandError):
    pass


class JSONOutput(object):
    """Output wrapper for JSON output.

    JSON outputter class that stores Command outputs in python dictionary
    and outputs as JSON object to output stream object. Commands should add any
    structured output to this object. JSON output is then enabled with the
    --json argument.

    Version Added:
        3.0
    """
    def __init__(self, output_stream):
        """Initialize JSONOutput class.

        Args:
            output_stream (Object):
                Object to output JSON object to.
        """
        self._output = {}
        self._output_stream = output_stream

    def add(self, key, value):
        """Add a new key value pair.

        Args:
            key (unicode):
                The key associated with the value to be added to dictionary.

            value (object):
                The value to attach to the key in the dictionary.
        """
        self._output[key] = value

    def append(self, key, value):
        """Add new value to an existing list associated with key.

        Args:
            key (unicode):
                The key associated with the list to append to.

            value (object):
                The value to append to the list associated with key.

        Raises:
            KeyError:
                The key was not found in the state.

            AttributeError:
                The existing value was not a list.
        """
        self._output[key].append(value)

    def add_error(self, error):
        """Add new error to 'errors' key.

        Append a new error to the ``errors`` key, creating one if needed.

        Args:
            error (unicode):
                The error that will be added to ``errors``.
        """
        self._output.setdefault('errors', []).append(error)

    def add_warning(self, warning):
        """Add new warning to 'warnings' key.

        Append a new warning to the ``warnings`` key, creating one if needed.

        Args:
            warning (unicode):
                The warning that will be added to ``warnings``.
        """
        self._output.setdefault('warnings', []).append(warning)

    def print_to_stream(self):
        """Output JSON string representation to output stream."""
        self._output_stream.write(json.dumps(self._output,
                                             indent=4,
                                             sort_keys=True))
        self._output_stream.write('\n')


class SmartHelpFormatter(argparse.HelpFormatter):
    """Smartly formats help text, preserving paragraphs."""

    def _split_lines(self, text, width):
        # NOTE: This function depends on overriding _split_lines's behavior.
        #       It is clearly documented that this function should not be
        #       considered public API. However, given that the width we need
        #       is calculated by HelpFormatter, and HelpFormatter has no
        #       blessed public API, we have no other choice but to override
        #       it here.
        lines = []

        for line in text.splitlines():
            lines += super(SmartHelpFormatter, self)._split_lines(line, width)
            lines.append('')

        return lines[:-1]


class OutputWrapper(object):
    """Wrapper for output of a command.

    Wrapper around some output object that handles outputting messages.
    Child classes specify the default object. The wrapper can handle
    messages in either unicode or bytes.

    Version Added:
        3.0
    """

    def __init__(self, output_stream):
        """Initialize with an output object to stream to.

        Args:
            output_stream (object):
                The output stream to send command output to.
        """
        self.output_stream = output_stream

    def write(self, msg, end='\n'):
        """Write a message to the output stream.

        Write a string to output stream object if defined, otherwise
        do nothing. end specifies a string that should be appended to
        the end of msg before being given to the output stream.

        Args:
            msg (unicode):
                String to write to output stream.

            end (unicode, optional):
                String to append to end of msg. This defaults to ``\\n```.
        """
        if self.output_stream:
            if end:
                if (isinstance(msg, bytes) and
                    isinstance(end, str)):
                    msg += end.encode('utf-8')
                else:
                    msg += end

            self.output_stream.write(msg)

    def new_line(self):
        """Pass a new line character to output stream object."""
        if self.output_stream:
            self.output_stream.write('\n')


class Option(object):
    """Represents an option for a command.

    The arguments to the constructor should be treated like those
    to argparse's add_argument, with the exception that the keyword
    argument 'config_key' is also valid. If config_key is provided
    it will be used to retrieve the config value as a default if the
    option is not specified. This will take precedence over the
    default argument.

    Serves as a wrapper around the ArgumentParser options, allowing us
    to specify defaults which will be grabbed from the configuration
    after it is loaded.
    """

    def __init__(self, *opts, **attrs):
        self.opts = opts
        self.attrs = attrs

    def add_to(self, parent, config={}, argv=[]):
        """Adds the option to the parent parser or group.

        If the option maps to a configuration key, this will handle figuring
        out the correct default.

        Once we've determined the right set of flags, the option will be
        added to the parser.
        """
        attrs = self.attrs.copy()

        if 'config_key' in attrs:
            config_key = attrs.pop('config_key')

            if config_key in config:
                attrs['default'] = config[config_key]

        if 'deprecated_in' in attrs:
            attrs['help'] += '\n[Deprecated since %s]' % attrs['deprecated_in']

        # These are used for other purposes, and are not supported by
        # argparse.
        for attr in ('added_in', 'deprecated_in', 'extended_help',
                     'versions_changed'):
            attrs.pop(attr, None)

        parent.add_argument(*self.opts, **attrs)


class OptionGroup(object):
    """Represents a named group of options.

    Each group has a name, an optional description, and a list of options.
    It serves as a way to organize related options, making it easier for
    users to scan for the options they want.

    This works like argparse's argument groups, but is designed to work with
    our special Option class.
    """

    def __init__(self, name=None, description=None, option_list=[]):
        self.name = name
        self.description = description
        self.option_list = option_list

    def add_to(self, parser, config={}, argv=[]):
        """Add the group and all its contained options to the parser.

        Args:
            parser (argparse.ArgumentParser):
                The command-line parser.

            config (dict):
                The loaded RBTools configuration.

            argv (list, deprecated):
                Unused legacy argument.
        """
        # First look for an existing group with the same name. This allows
        # a BaseSubCommand to merge option groups with its parent
        # BaseMultiCommand.
        for group in parser._action_groups:
            if group.title == self.name:
                break
        else:
            group = parser.add_argument_group(self.name, self.description)

        for option in self.option_list:
            option.add_to(group, config, argv)


class LogLevelFilter(logging.Filter):
    """Filters log messages of a given level.

    Only log messages that have the specified level will be allowed by
    this filter. This prevents propagation of higher level types to lower
    log handlers.
    """

    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


class Command(object):
    """Base class for rb commands.

    This class will handle retrieving the configuration, and parsing
    command line options.

    ``usage`` is a list of usage strings each showing a use case. These
    should not include the main rbt command or the command name; they
    will be added automatically.

    Attributes:
        api_client (rbtools.api.client.RBClient):
            The API client. This will be ``None`` if :py:attr:`needs_api` is
            ``False``.

        api_root (rbtools.api.resource.RootResource):
            The API root resource. This will be ``None`` if
            :py:attr:`needs_api` is ``False``.

        capabilities (rbtools.api.capabilities.Capabilities):
            The API capabilities object. This will be ``None`` if
            :py:attr:`needs_api` is ``False``.

        repository (rbtools.api.resource.ItemResource):
            The API resource corresponding to the repository.

        repository_info (rbtools.clients.base.repository.RepositoryInfo):
            The repository info object. This will be ``None`` if
            :py:attr:`needs_scm_client` is ``False``.

        server_url (unicode):
            The URL to the Review Board server.

        stdout (OutputWrapper):
            Standard unicode output wrapper that subclasses must write to.

        stdout_is_atty (bool):
            Whether :py:attr:`stdout` is connected to a TTY or similar device.

            Version Added:
                3.1

        stderr (OutputWrapper):
            Standard unicode error output wrapper that subclasses must write
            to.

        stderr_is_atty (bool):
            Whether :py:attr:`stderr` is connected to a TTY or similar device.

            Version Added:
                3.1

        stdin (io.TextIOWrapper):
            Standard input.

            Version Added:
                3.1

        stdin_is_atty (bool):
            Whether :py:attr:`stdin` is connected to a TTY or similar device.

            Version Added:
                3.1

        stdout_bytes (OutputWrapper):
            Standard byte output wrapper that subclasses must write to.

        stderr_bytes (OutputWrapper):
            Standard byte error output wrapper that subclasses must write to.

        tool (rbtools.clients.base.BaseSCMClient):
            The SCM client. This will be ``None`` if
            :py:attr:`needs_scm_client` is ``False``.
    """

    #: The name of the command.
    #:
    #: Type:
    #:     unicode
    name = ''

    #: The author of the command.
    #:
    #: Type:
    #:     unicode
    author = ''

    #: A short description of the command, suitable for display in usage text.
    #:
    #: Type:
    #:     unicode
    description = ''

    #: Whether the command needs the API client.
    #:
    #: If this is set, the initialization of the command will set
    #: :py:attr:`api_client` and :py:attr:`api_root`.
    #:
    #: Version Added:
    #:     3.0
    #:
    #: Type:
    #:     bool
    needs_api = False

    #: Whether the command needs to generate diffs.
    #:
    #: If this is set, the initialization of the command will check for the
    #: presence of a diff tool compatible with the chosen type of repository.
    #:
    #: This depends on :py:attr:`needs_repository` and
    #: :py:attr:`needs_scm_client` both being set to ``True``.
    #:
    #: Version Added:
    #:     4.0
    #:
    #: Type:
    #:     bool
    needs_diffs = False

    #: Whether the command needs the SCM client.
    #:
    #: If this is set, the initialization of the command will set
    #: :py:attr:`repository_info` and :py:attr:`tool`.
    #:
    #: Version Added:
    #:     3.0
    #:
    #: Type:
    #:     bool
    needs_scm_client = False

    #: Whether the command needs the remote repository object.
    #:
    #: If this is set, the initialization of the command will set
    #: :py:attr:`repository`.
    #:
    #: Version Added:
    #:     3.0
    #:
    #: Type:
    #:     bool
    needs_repository = False

    #: Usage text for what arguments the command takes.
    #:
    #: Arguments for the command are anything passed in other than defined
    #: options (for example, revisions passed to :command:`rbt post`).
    #:
    #: Type:
    #:     unicode
    args = ''

    #: Command-line options for this command.
    #:
    #: Type:
    #:     list of Option or OptionGroup
    option_list = []

    _global_options = [
        Option('-d', '--debug',
               action='store_true',
               dest='debug',
               config_key='DEBUG',
               default=False,
               help='Displays debug output.',
               extended_help='This information can be valuable when debugging '
                             'problems running the command.'),
        Option('--json',
               action='store_true',
               dest='json_output',
               config_key='JSON_OUTPUT',
               default=False,
               added_in='3.0',
               help='Output results as JSON data instead of text.')
    ]

    server_options = OptionGroup(
        name='Review Board Server Options',
        description='Options necessary to communicate and authenticate '
                    'with a Review Board server.',
        option_list=[
            Option('--server',
                   dest='server',
                   metavar='URL',
                   config_key='REVIEWBOARD_URL',
                   default=None,
                   help='Specifies the Review Board server to use.'),
            Option('--username',
                   dest='username',
                   metavar='USERNAME',
                   config_key='USERNAME',
                   default=None,
                   help='The user name to be supplied to the Review Board '
                        'server.'),
            Option('--password',
                   dest='password',
                   metavar='PASSWORD',
                   config_key='PASSWORD',
                   default=None,
                   help='The password to be supplied to the Review Board '
                        'server.'),
            Option('--ext-auth-cookies',
                   dest='ext_auth_cookies',
                   metavar='EXT_AUTH_COOKIES',
                   config_key='EXT_AUTH_COOKIES',
                   default=None,
                   help='Use an external cookie store with pre-fetched '
                        'authentication data. This is useful with servers '
                        'that require extra web authentication to access '
                        'Review Board, e.g. on single sign-on enabled sites.',
                   added_in='0.7.5'),
            Option('--api-token',
                   dest='api_token',
                   metavar='TOKEN',
                   config_key='API_TOKEN',
                   default=None,
                   help='The API token to use for authentication, instead of '
                        'using a username and password.',
                   added_in='0.7'),
            Option('--disable-proxy',
                   action='store_false',
                   dest='enable_proxy',
                   config_key='ENABLE_PROXY',
                   default=True,
                   help='Prevents requests from going through a proxy '
                        'server.'),
            Option('--disable-ssl-verification',
                   action='store_true',
                   dest='disable_ssl_verification',
                   config_key='DISABLE_SSL_VERIFICATION',
                   default=False,
                   help='Disable SSL certificate verification. This is useful '
                        'with servers that have self-signed certificates.',
                   added_in='0.7.3'),
            Option('--disable-cookie-storage',
                   config_key='SAVE_COOKIES',
                   dest='save_cookies',
                   action='store_false',
                   default=True,
                   help='Use an in-memory cookie store instead of writing '
                        'them to a file. No credentials will be saved or '
                        'loaded.',
                   added_in='0.7.3'),
            Option('--disable-cache',
                   dest='disable_cache',
                   config_key='DISABLE_CACHE',
                   action='store_true',
                   default=False,
                   help='Disable the HTTP cache completely. This will '
                        'result in slower requests.',
                   added_in='0.7.3'),
            Option('--disable-cache-storage',
                   dest='in_memory_cache',
                   config_key='IN_MEMORY_CACHE',
                   action='store_true',
                   default=False,
                   help='Disable storing the API cache on the filesystem, '
                        'instead keeping it in memory temporarily.',
                   added_in='0.7.3'),
            Option('--cache-location',
                   dest='cache_location',
                   metavar='FILE',
                   config_key='CACHE_LOCATION',
                   default=None,
                   help='The file to use for the API cache database.',
                   added_in='0.7.3'),
            Option('--ca-certs',
                   dest='ca_certs',
                   metavar='FILE',
                   config_key='CA_CERTS',
                   default=None,
                   help='Additional TLS CA bundle.'),
            Option('--client-key',
                   dest='client_key',
                   metavar='FILE',
                   config_key='CLIENT_KEY',
                   default=None,
                   help='Key for TLS client authentication.'),
            Option('--client-cert',
                   dest='client_cert',
                   metavar='FILE',
                   config_key='CLIENT_CERT',
                   default=None,
                   help='Certificate for TLS client authentication.'),
            Option('--proxy-authorization',
                   dest='proxy_authorization',
                   metavar='PROXY_AUTHORIZATION',
                   config_key='PROXY_AUTHORIZATION',
                   default=None,
                   help='Value of the Proxy-Authorization header to send with '
                        'HTTP requests.'),
        ]
    )

    repository_options = OptionGroup(
        name='Repository Options',
        option_list=[
            Option('--repository',
                   dest='repository_name',
                   metavar='NAME',
                   config_key='REPOSITORY',
                   default=None,
                   help='The name of the repository configured on '
                        'Review Board that matches the local repository.'),
            Option('--repository-url',
                   dest='repository_url',
                   metavar='URL',
                   config_key='REPOSITORY_URL',
                   default=None,
                   help='The URL for a repository.'
                        '\n'
                        'When generating diffs, this can be used for '
                        'creating a diff outside of a working copy '
                        '(currently only supported by Subversion with '
                        'specific revisions or --diff-filename, and by '
                        'ClearCase with relative paths outside the view).'
                        '\n'
                        'For Git, this specifies the origin URL of the '
                        'current repository, overriding the origin URL '
                        'supplied by the client.',
                   versions_changed={
                       '0.6': 'Prior versions used the `REPOSITORY` setting '
                              'in .reviewboardrc, and allowed a '
                              'repository name to be passed to '
                              '--repository-url. This is no '
                              'longer supported in 0.6 and higher. You '
                              'may need to update your configuration and '
                              'scripts appropriately.',
                   }),
            Option('--repository-type',
                   dest='repository_type',
                   metavar='TYPE',
                   config_key='REPOSITORY_TYPE',
                   default=None,
                   help='The type of repository in the current directory. '
                        'In most cases this should be detected '
                        'automatically, but some directory structures '
                        'containing multiple repositories require this '
                        'option to select the proper type. The '
                        '`rbt list-repo-types` command can be used to '
                        'list the supported values.'),
        ]
    )

    diff_options = OptionGroup(
        name='Diff Generation Options',
        description='Options for choosing what gets included in a diff, '
                    'and how the diff is generated.',
        option_list=[
            Option('--no-renames',
                   dest='no_renames',
                   action='store_true',
                   help='Add the --no-renames option to the git when '
                        'generating diff.'
                        '\n'
                        'Supported by: Git',
                   added_in='0.7.11'),
            Option('--revision-range',
                   dest='revision_range',
                   metavar='REV1:REV2',
                   default=None,
                   help='Generates a diff for the given revision range.',
                   deprecated_in='0.6'),
            Option('-I', '--include',
                   metavar='FILENAME',
                   dest='include_files',
                   action='append',
                   help='Includes only the specified file in the diff. '
                        'This can be used multiple times to specify '
                        'multiple files.'
                        '\n'
                        'Supported by: Bazaar, CVS, Git, Mercurial, '
                        'Perforce, SOS, and Subversion.',
                   added_in='0.6'),
            Option('-X', '--exclude',
                   metavar='PATTERN',
                   dest='exclude_patterns',
                   action='append',
                   config_key='EXCLUDE_PATTERNS',
                   help='Excludes all files that match the given pattern '
                        'from the diff. This can be used multiple times to '
                        'specify multiple patterns. UNIX glob syntax is used '
                        'for pattern matching.'
                        '\n'
                        'Supported by: Bazaar, CVS, Git, Mercurial, '
                        'Perforce, SOS, and Subversion.',
                   extended_help=(
                       'Patterns that begin with a path separator (/ on Mac '
                       'OS and Linux, \\ on Windows) will be treated as being '
                       'relative to the root of the repository. All other '
                       'patterns are treated as being relative to the current '
                       'working directory.'
                       '\n'
                       'For example, to exclude all ".txt" files from the '
                       'resulting diff, you would use "-X /\'*.txt\'".'
                       '\n'
                       'When working with Mercurial, the patterns are '
                       'provided directly to "hg" and are not limited to '
                       'globs. For more information on advanced pattern '
                       'syntax in Mercurial, run "hg help patterns"'
                       '\n'
                       'When working with CVS all diffs are generated '
                       'relative to the current working directory so '
                       'patterns beginning with a path separator are treated '
                       'as relative to the current working directory.'
                       '\n'
                       'When working with Perforce, an exclude pattern '
                       'beginning with `//` will be matched against depot '
                       'paths; all other patterns will be matched against '
                       'local paths.'),
                   added_in='0.7'),
            Option('--parent',
                   dest='parent_branch',
                   metavar='BRANCH',
                   config_key='PARENT_BRANCH',
                   default=None,
                   help='The parent branch this diff should be generated '
                        'against (Bazaar/Git/Mercurial only).'),
            Option('--diff-filename',
                   dest='diff_filename',
                   default=None,
                   metavar='FILENAME',
                   help='Uploads an existing diff file, instead of '
                        'generating a new diff.'),
        ]
    )

    branch_options = OptionGroup(
        name='Branch Options',
        description='Options for selecting branches.',
        option_list=[
            Option('--tracking-branch',
                   dest='tracking',
                   metavar='BRANCH',
                   config_key='TRACKING_BRANCH',
                   default=None,
                   help='The remote tracking branch from which your local '
                        'branch is derived (Git/Mercurial only).'
                        '\n'
                        'For Git, the default is to use the remote branch '
                        'that the local branch is tracking, if any, falling '
                        'back on `origin/master`.'
                        '\n'
                        'For Mercurial, the default is one of: '
                        '`reviewboard`, `origin`, `parent`, or `default`.'),
        ]
    )

    git_options = OptionGroup(
        name='Git Options',
        description='Git-specific options for diff generation.',
        option_list=[
            Option('--git-find-renames-threshold',
                   dest='git_find_renames_threshold',
                   metavar='THRESHOLD',
                   default=None,
                   help='The threshold to pass to `--find-renames` when '
                        'generating a git diff.'
                        '\n'
                        'For more information, see `git help diff`.'),
        ])

    perforce_options = OptionGroup(
        name='Perforce Options',
        description='Perforce-specific options for selecting the '
                    'Perforce client and communicating with the '
                    'repository.',
        option_list=[
            Option('--p4-client',
                   dest='p4_client',
                   config_key='P4_CLIENT',
                   default=None,
                   metavar='CLIENT_NAME',
                   help='The Perforce client name for the repository.'),
            Option('--p4-port',
                   dest='p4_port',
                   config_key='P4_PORT',
                   default=None,
                   metavar='PORT',
                   help='The IP address for the Perforce server.'),
            Option('--p4-passwd',
                   dest='p4_passwd',
                   config_key='P4_PASSWD',
                   default=None,
                   metavar='PASSWORD',
                   help='The Perforce password or ticket of the user '
                        'in the P4USER environment variable.'),
        ]
    )

    subversion_options = OptionGroup(
        name='Subversion Options',
        description='Subversion-specific options for controlling diff '
                    'generation.',
        option_list=[
            Option('--basedir',
                   dest='basedir',
                   config_key='BASEDIR',
                   default=None,
                   metavar='PATH',
                   help='The path within the repository where the diff '
                        'was generated. This overrides the detected path. '
                        'Often used when passing --diff-filename.'),
            Option('--svn-username',
                   dest='svn_username',
                   default=None,
                   metavar='USERNAME',
                   help='The username for the SVN repository.'),
            Option('--svn-password',
                   dest='svn_password',
                   default=None,
                   metavar='PASSWORD',
                   help='The password for the SVN repository.'),
            Option('--svn-prompt-password',
                   dest='svn_prompt_password',
                   config_key='SVN_PROMPT_PASSWORD',
                   default=False,
                   action='store_true',
                   help="Prompt for the user's svn password. This option "
                        "overrides the password provided by the "
                        "--svn-password option.",
                   added_in='0.7.3'),
            Option('--svn-show-copies-as-adds',
                   dest='svn_show_copies_as_adds',
                   metavar='y|n',
                   default=None,
                   help='Treat copied or moved files as new files.'
                        '\n'
                        'This is only supported in Subversion 1.7+.',
                   added_in='0.5.2'),
            Option('--svn-changelist',
                   dest='svn_changelist',
                   default=None,
                   metavar='ID',
                   help='Generates the diff for review based on a '
                        'local changelist.',
                   deprecated_in='0.6'),
        ]
    )

    tfs_options = OptionGroup(
        name='TFS Options',
        description='Team Foundation Server specific options for '
                    'communicating with the TFS server.',
        option_list=[
            Option('--tfs-login',
                   dest='tfs_login',
                   default=None,
                   metavar='TFS_LOGIN',
                   help='Logs in to TFS as a specific user (ie.'
                        'user@domain,password). Visit https://msdn.microsoft.'
                        'com/en-us/library/hh190725.aspx to learn about '
                        'saving credentials for reuse.'),
            Option('--tf-cmd',
                   dest='tf_cmd',
                   default=None,
                   metavar='TF_CMD',
                   config_key='TF_CMD',
                   help='The full path of where to find the tf command. This '
                        'overrides any detected path.'),
            Option('--tfs-shelveset-owner',
                   dest='tfs_shelveset_owner',
                   default=None,
                   metavar='TFS_SHELVESET_OWNER',
                   help='When posting a shelveset name created by another '
                        'user (other than the one who owns the current '
                        'workdir), look for that shelveset using this '
                        'username.'),
        ]
    )

    default_transport_cls = SyncTransport

    def __init__(self,
                 transport_cls=SyncTransport,
                 stdout=sys.stdout,
                 stderr=sys.stderr,
                 stdin=sys.stdin):
        """Initialize the base functionality for the command.

        Args:
            transport_cls (rbtools.api.transport.Transport, optional):
                The transport class used for all API communication. By default,
                this uses the transport defined in
                :py:attr:`default_transport_cls`.

            stdout (io.TextIOWrapper, optional):
                The standard output stream. This can be used to capture output
                programmatically.

                Version Added:
                    3.1

            stderr (io.TextIOWrapper, optional):
                The standard error stream. This can be used to capture errors
                programmatically.

                Version Added:
                    3.1

            stdin (io.TextIOWrapper, optional):
                The standard input stream. This can be used to provide input
                programmatically.

                Version Added:
                    3.1
        """
        self.log = logging.getLogger('rb.%s' % self.name)
        self.transport_cls = transport_cls or self.default_transport_cls
        self.api_client = None
        self.api_root = None
        self.capabilities = None
        self.repository = None
        self.repository_info = None
        self.server_url = None
        self.tool = None

        self.stdout = OutputWrapper(stdout)
        self.stderr = OutputWrapper(stderr)
        self.stdin = stdin

        self.stdout_is_atty = hasattr(stdout, 'isatty') and stdout.isatty()
        self.stderr_is_atty = hasattr(stderr, 'isatty') and stderr.isatty()
        self.stdin_is_atty = hasattr(stdin, 'isatty') and stdin.isatty()

        if isinstance(stdout, io.TextIOWrapper):
            self.stderr_bytes = OutputWrapper(stderr.buffer)
            self.stdout_bytes = OutputWrapper(stdout.buffer)
        else:
            # Python 2.x, or while we're running unit tests (where stdout and
            # stderr are actually io.StringIO)
            self.stderr_bytes = OutputWrapper(stderr)
            self.stdout_bytes = OutputWrapper(stdout)

        self.json = JSONOutput(stdout)

    def create_parser(self, config, argv=[]):
        """Create and return the argument parser for this command."""
        parser = argparse.ArgumentParser(
            prog=RB_MAIN,
            usage=self.usage(),
            formatter_class=SmartHelpFormatter)

        for option in self.option_list:
            option.add_to(parser, config, argv)

        for option in self._global_options:
            option.add_to(parser, config, argv)

        return parser

    def post_process_options(self):
        if self.options.disable_ssl_verification:
            try:
                import ssl
                ssl._create_unverified_context()
            except Exception:
                raise CommandError('The --disable-ssl-verification flag is '
                                   'only available with Python 2.7.9+')

    def usage(self):
        """Return a usage string for the command."""
        usage = '%%(prog)s %s [options] %s' % (self.name, self.args)

        if self.description:
            return '%s\n\n%s' % (usage, self.description)
        else:
            return usage

    def _create_formatter(self, level, fmt):
        """Create a logging formatter for the appropriate logging level.

        When writing to a TTY, the format will be colorized by the colors
        specified in the ``COLORS`` configuration in :file:`.reviewboardrc`.
        Otherwise, the format will not be altered.

        Args:
            level (unicode):
                The logging level name.

            fmt (unicode):
                The logging format.

        Returns:
            logging.Formatter:
            The created formatter.
        """
        color = ''
        reset = ''

        if self.stdout_is_atty:
            color_name = self.config['COLOR'].get(level.upper())

            if color_name:
                color = getattr(colorama.Fore, color_name.upper(), '')

                if color:
                    reset = colorama.Fore.RESET

        return logging.Formatter(fmt.format(color=color, reset=reset))

    def initialize(self):
        """Initialize the command.

        This will set up various prerequisites for commands. Individual command
        subclasses can control what gets done by setting the various
        ``needs_*`` attributes (as documented in this class).
        """
        if self.needs_repository:
            # If we need the repository, we implicitly need the API and SCM
            # client as well.
            self.needs_api = True
            self.needs_scm_client = True

        if self.needs_api:
            self.server_url = self._init_server_url()
            self.api_client, self.api_root = self.get_api(self.server_url)
            self.capabilities = self.get_capabilities(self.api_root)

        if self.needs_scm_client:
            # _init_server_url might have already done this, in the case that
            # it needed to use the SCM client to detect the server name. Only
            # repeat if necessary.
            if self.repository_info is None and self.tool is None:
                self.repository_info, self.tool = self.initialize_scm_tool(
                    client_name=self.options.repository_type)

            # Some SCMs allow configuring the repository name in the SCM
            # metadata. This is a legacy configuration, and is only used as a
            # fallback for when the repository name is not specified through
            # the config or command line.
            if self.options.repository_name is None:
                self.options.repository_name = \
                    self.tool.get_repository_name()

            self.tool.capabilities = self.capabilities

        if self.needs_repository:
            self.repository, info = get_repository_resource(
                api_root=self.api_root,
                tool=self.tool,
                repository_name=self.options.repository_name,
                repository_paths=self.repository_info.path)

            if self.repository:
                self.repository_info.update_from_remote(self.repository, info)

        if self.options.json_output:
            self.stdout.output_stream = None
            self.stderr.output_stream = None
            self.stderr_bytes.output_stream = None
            self.stdout_bytes.output_stream = None

    def create_arg_parser(self, argv):
        """Create and return the argument parser.

        Args:
            argv (list of unicode):
                A list of command line arguments

        Returns:
            argparse.ArgumentParser:
            Argument parser for commandline arguments
        """
        self.config = load_config()
        parser = self.create_parser(self.config, argv)
        parser.add_argument('args', nargs=argparse.REMAINDER)

        return parser

    def run_from_argv(self, argv):
        """Execute the command using the provided arguments.

        The options and commandline arguments will be parsed
        from ``argv`` and the commands ``main`` method will
        be called.
        """
        parser = self.create_arg_parser(argv)
        self.options = parser.parse_args(argv[2:])

        args = self.options.args

        # Check that the proper number of arguments have been provided.
        if hasattr(inspect, 'getfullargspec'):
            # Python 3
            argspec = inspect.getfullargspec(self.main)
        else:
            # Python 2
            argspec = inspect.getargspec(self.main)

        minargs = len(argspec.args) - 1
        maxargs = minargs

        # Arguments that have a default value are considered optional.
        if argspec.defaults is not None:
            minargs -= len(argspec.defaults)

        if argspec.varargs is not None:
            maxargs = None

        if len(args) < minargs or (maxargs is not None and
                                   len(args) > maxargs):
            parser.error('Invalid number of arguments provided')
            sys.exit(1)

        try:
            self._init_logging()
            logging.debug('Command line: %s', subprocess.list2cmdline(argv))

            self.initialize()

            exit_code = self.main(*args) or 0
        except CommandError as e:
            if isinstance(e, ParseError):
                parser.error(e)
            elif self.options.debug:
                raise

            logging.error(e)
            self.json.add_error(str(e))
            exit_code = 1
        except CommandExit as e:
            exit_code = e.exit_code
        except Exception as e:
            # If debugging is on, we'll let python spit out the
            # stack trace and report the exception, otherwise
            # we'll suppress the trace and print the exception
            # manually.
            if self.options.debug:
                raise

            self.json.add_error('Internal error: %s: %s'
                                % (type(e).__name__, e))
            logging.critical(e)
            exit_code = 1

        cleanup_tempfiles()

        if self.options.json_output:
            if 'errors' in self.json._output:
                self.json.add('status', 'failed')
            else:
                self.json.add('status', 'success')

            self.json.print_to_stream()

        sys.exit(exit_code)

    def initialize_scm_tool(self, client_name=None,
                            require_repository_info=True):
        """Initialize the SCM tool for the current working directory.

        Args:
            client_name (unicode, optional):
                A specific client name, which can come from the configuration.
                This can be used to disambiguate if there are nested
                repositories, or to speed up detection.

            require_repository_info (bool, optional):
                Whether information on a repository is required. This is the
                default. If disabled, this will return ``None`` for the
                repository information if a matching repository could not be
                found.

        Returns:
            tuple:
            A 2-tuple, containing the repository info structure and the tool
            instance.
        """
        if not require_repository_info:
            RemovedInRBTools40Warning.warn(
                'The require_repository_info parameter to '
                'Command.initialize_scm_tool is deprecated and will be '
                'removed in RBTools 4.0. Commands which need to use only the '
                'API should set the needs_api attribute.')

        repository_info, tool = scan_usable_client(
            self.config,
            self.options,
            client_name=client_name)

        try:
            tool.check_options()
        except OptionsCheckError as e:
            raise CommandError(str(e))

        if self.needs_diffs:
            try:
                tool.get_diff_tool()
            except MissingDiffToolError as e:
                raise CommandError(str(e))

        return repository_info, tool

    def setup_tool(self, tool, api_root=None):
        """Performs extra initialization on the tool.

        If api_root is not provided we'll assume we want to
        initialize the tool using only local information
        """
        RemovedInRBTools40Warning.warn(
            'The Command.setup_tool method is deprecated and will be removed '
            'in RBTools 4.0. Commands which need to use both the API and SCM '
            'client should instead set the needs_api and needs_scm_client '
            'attributes.')
        tool.capabilities = self.get_capabilities(api_root)

    def get_server_url(self, repository_info, tool):
        """Return the Review Board server url.

        Args:
            repository_info (rbtools.clients.base.repository.RepositoryInfo,
                             optional):
                Information about the current repository

            tool (rbtools.clients.base.BaseSCMClient, optional):
                The repository client.

        Returns:
            unicode:
            The server URL.
        """
        RemovedInRBTools40Warning.warn(
            'The Command.get_server_url method is deprecated and will be '
            'removed in RBTools 4.0. Commands which need the API client '
            'should instead set the needs_api attribute.')

        if self.server_url is None:
            self.server_url = self._init_server_url()

        return self.server_url

    def credentials_prompt(self, realm, uri, username=None, password=None,
                           *args, **kwargs):
        """Prompt the user for credentials using the command line.

        This will prompt the user, and then return the provided
        username and password. This is used as a callback in the
        API when the user requires authorization.
        """
        # TODO: Consolidate the logic in this function with
        #       get_authenticated_session() in rbtools/utils/users.py.

        if username is None or password is None:
            if getattr(self.options, 'diff_filename', None) == '-':
                raise CommandError('HTTP authentication is required, but '
                                   'cannot be used with --diff-filename=-')

            # Interactive prompts don't work correctly when input doesn't come
            # from a terminal. This could seem to be a rare case not worth
            # worrying about, but this is what happens when using native
            # Python in Cygwin terminal emulator under Windows and it's very
            # puzzling to the users, especially because stderr is also _not_
            # flushed automatically in this case, so the program just appears
            # to hang.
            if not self.stdin_is_atty:
                message_parts = [
                    'Authentication is required but RBTools cannot prompt for '
                    'it.'
                ]

                if sys.platform == 'win32':
                    message_parts.append(
                        'This can occur if you are piping input into the '
                        'command, or if you are running in a Cygwin terminal '
                        'emulator and not using Cygwin Python.'
                    )
                else:
                    message_parts.append(
                        'This can occur if you are piping input into the '
                        'command.'
                    )

                message_parts.append(
                    'You may need to explicitly provide API credentials when '
                    'invoking the command, or try logging in separately.'
                )

                raise CommandError(' '.join(message_parts))

            self.stdout.new_line()
            self.stdout.write('Please log in to the Review Board server at '
                              '%s.'
                              % urlparse(uri)[1])

            if username is None:
                username = get_input('Username: ')

            if password is None:
                password = get_pass('Password: ')

        return username, password

    def otp_token_prompt(self, uri, token_method, *args, **kwargs):
        """Prompt the user for a one-time password token.

        Their account is configured with two-factor authentication. The
        server will have sent a token to their configured mobile device
        or application. The user will be prompted for this token.
        """
        if getattr(self.options, 'diff_filename', None) == '-':
            raise CommandError('A two-factor authentication token is '
                               'required, but cannot be used with '
                               '--diff-filename=-')

        self.stdout.new_line()
        self.stdout.write('Please enter your two-factor authentication '
                          'token for Review Board.')

        if token_method == 'sms':
            self.stdout.write('You should be getting a text message with '
                              'an authentication token.')
            self.stdout.write('Enter the token below.')
        elif token_method == 'call':
            self.stdout.write('You should be getting an automated phone '
                              'call with an authentication token.')
            self.stdout.write('Enter the token below.')
        elif token_method == 'generator':
            self.stdout.write('Enter the token shown on your token '
                              'generator app below.')

        self.stdout.new_line()

        return get_pass('Token: ', require=True)

    def _make_api_client(self, server_url):
        """Return an RBClient object for the server.

        The RBClient will be instantiated with the proper arguments
        for talking to the provided Review Board server url.
        """
        return RBClient(
            server_url,
            username=self.options.username,
            password=self.options.password,
            api_token=self.options.api_token,
            auth_callback=self.credentials_prompt,
            otp_token_callback=self.otp_token_prompt,
            disable_proxy=not self.options.enable_proxy,
            verify_ssl=not self.options.disable_ssl_verification,
            allow_caching=not self.options.disable_cache,
            cache_location=self.options.cache_location,
            in_memory_cache=self.options.in_memory_cache,
            save_cookies=self.options.save_cookies,
            ext_auth_cookies=self.options.ext_auth_cookies,
            ca_certs=self.options.ca_certs,
            client_key=self.options.client_key,
            client_cert=self.options.client_cert,
            proxy_authorization=self.options.proxy_authorization,
            transport_cls=self.transport_cls)

    def get_api(self, server_url):
        """Returns an RBClient instance and the associated root resource.

        Commands should use this method to gain access to the API,
        instead of instantianting their own client.
        """
        if not urlparse(server_url).scheme:
            server_url = '%s%s' % ('http://', server_url)

        api_client = self._make_api_client(server_url)
        api_root = None

        try:
            api_root = api_client.get_root()
        except ServerInterfaceError as e:
            raise CommandError('Could not reach the Review Board '
                               'server at %s: %s' % (server_url, e))
        except APIError as e:
            if e.http_status != 404:
                raise CommandError('Unexpected API Error: %s' % e)

        # If we either couldn't find an API endpoint or its contents don't
        # appear to be from Review Board, we should provide helpful
        # instructions to the user.
        if api_root is None or not hasattr(api_root, 'get_review_requests'):
            if server_url.rstrip('/') == 'https://rbcommons.com':
                raise CommandError(
                    'RBTools must be configured to point to your RBCommons '
                    'team account. For example: '
                    'https://rbcommons.com/s/<myteam>/')
            elif server_url.startswith('https://rbcommons.com/s/'):
                raise CommandError(
                    'Your configured RBCommons team account could not be '
                    'found. Make sure the team name is correct and the team '
                    'is still active.')
            else:
                raise CommandError(
                    'The configured Review Board server URL (%s) does not '
                    'appear to be correct.'
                    % server_url)

        return api_client, api_root

    def get_capabilities(
        self,
        api_root: RootResource,
    ) -> Capabilities:
        """Retrieve capabilities from the server and return them.

        Args:
            api_root (rbtools.api.resource.RootResource):
                The root resource

        Returns:
            rbtools.api.capabilities.Capabilities:
            The server capabilities.
        """
        if 'capabilities' in api_root:
            # Review Board 2.0+ provides capabilities in the root resource.
            return Capabilities(api_root.capabilities)

        info = api_root.get_info()

        if 'capabilities' in info:
            return Capabilities(info.capabilities)
        else:
            return Capabilities({})

    def main(self, *args):
        """The main logic of the command.

        This method should be overridden to implement the commands
        functionality.
        """
        raise NotImplementedError()

    def _init_logging(self):
        """Initializes logging for the command.

        This will set up different log handlers based on the formatting we want
        for the given levels.

        The INFO log handler will just show the text, like a print statement.

        WARNING and higher will show the level name as a prefix, in the form of
        "LEVEL: message".

        If debugging is enabled, a debug log handler will be set up showing
        debug messages in the form of ">>> message", making it easier to
        distinguish between debugging and other messages.
        """
        if self.stderr_is_atty:
            # We only use colorized logging when writing to TTYs, so we don't
            # bother initializing it then.
            colorama.init()

        # We use the stderr interface to be compliant with the default
        # behavior of StreamHandler (which will use sys.stderr if not
        # specified).
        log_stream = self.stderr.output_stream

        root = logging.getLogger()

        if self.options.debug:
            handler = logging.StreamHandler(log_stream)
            handler.setFormatter(self._create_formatter(
                'DEBUG', '{color}>>>{reset} %(message)s'))
            handler.setLevel(logging.DEBUG)
            handler.addFilter(LogLevelFilter(logging.DEBUG))
            root.addHandler(handler)

            root.setLevel(logging.DEBUG)
        else:
            root.setLevel(logging.INFO)

        # Handler for info messages. We'll treat these like prints.
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(self._create_formatter(
            'INFO', '{color}%(message)s{reset}'))

        handler.setLevel(logging.INFO)
        handler.addFilter(LogLevelFilter(logging.INFO))
        root.addHandler(handler)

        # Handlers for warnings, errors, and criticals. They'll show the
        # level prefix and the message.
        levels = (
            ('WARNING', logging.WARNING),
            ('ERROR', logging.ERROR),
            ('CRITICAL', logging.CRITICAL),
        )

        for level_name, level in levels:
            handler = logging.StreamHandler(log_stream)
            handler.setFormatter(self._create_formatter(
                level_name, '{color}%(levelname)s:{reset} %(message)s'))
            handler.addFilter(LogLevelFilter(level))
            handler.setLevel(level)
            root.addHandler(handler)

        logging.debug('RBTools %s', get_version_string())
        logging.debug('Python %s', sys.version)
        logging.debug('Running on %s', platform.platform())
        logging.debug('Home = %s', get_home_path())
        logging.debug('Current directory = %s', os.getcwd())

    def _init_server_url(self):
        """Initialize the server URL.

        This will discover the URL to the Review Board server (if possible),
        and store it in :py:attr:`server_url`.

        Returns:
            unicode:
            The Review Board server URL.

        Raises:
            CommandError:
                The Review Board server could not be detected.
        """
        # First use anything directly provided on the command line or in the
        # config file. This may be None or empty.
        server_url = self.options.server

        # Now try to use the SCM to discover the server name. Several SCMs have
        # ways for the administrator to configure the Review Board server in
        # the SCM metadata.
        if not server_url:
            self.repository_info, self.tool = self.initialize_scm_tool(
                client_name=self.options.repository_type)

            if self.repository_info is not None and self.tool is not None:
                server_url = self.tool.scan_for_server(self.repository_info)

        # Finally, fall back on the TREES config. Once upon a time, we
        # suggested that users create a TREES dict in their config
        # file that specified the REVIEWBOARD_URL for multiple repository
        # paths. This was never properly documented, and has long outlived its
        # usefulness. We're continuing to support it for now but emit a
        # deprecation warning.
        if not server_url:
            if 'TREES' in self.config:
                trees = self.config['TREES']
                path = None

                # Some repositories will return a list of paths.
                if isinstance(self.repository_info.path, list):
                    for path in self.repository_info.path:
                        if path in trees:
                            break
                    else:
                        path = None
                elif self.repository_info.path in trees:
                    path = self.repository_info.path

                if path and 'REVIEWBOARD_URL' in trees[path]:
                    RemovedInRBTools40Warning.warn(
                        'The TREES configuration for specifying the '
                        'REVIEWBOARD_URL is no longer supported and will be '
                        'removed in RBTools 4.0. If you have multiple Review '
                        'Board servers for different repositories, create '
                        'individual .reviewboardrc files in each repository '
                        'to define REVIEWBOARD_URL.')
                    server_url = trees[path]['REVIEWBOARD_URL']

        if not server_url:
            raise CommandError('Unable to find a Review Board server for this '
                               'source code tree.')

        return server_url

    def _get_text_type(self, markdown):
        """Return the appropriate text type for a field.

        Args:
            markdown (bool):
                Whether the field should be interpreted as Markdown-formatted
                text.

        Returns:
            unicode:
            The text type value to set for the field.
        """
        if markdown and self.capabilities.has_capability('text', 'markdown'):
            return 'markdown'
        else:
            return 'plain'


class BaseSubCommand(Command):
    """Abstract base class for a subcommand."""

    #: The subcommand's help text.
    #:
    #: Type:
    #:     unicode
    help_text = ''

    def __init__(self, options, config, *args, **kwargs):
        """Initialize the subcommand.

        Args:
            options (argparse.Namespace):
                The parsed options.

            config (dict):
                The loaded RBTools configuration.

            *args (list):
                Positional arguments to pass to the Command class.

            **kwargs (dict):
                Keyword arguments to pass to the Command class.
        """
        super(BaseSubCommand, self).__init__(*args, **kwargs)
        self.options = options
        self.config = config


class BaseMultiCommand(Command):
    """Abstract base class for commands which offer subcommands.

    Some commands (such as :command:`rbt review`) want to offer many
    subcommands.

    Version Added:
        3.0
    """

    #: The available subcommands.
    #:
    #: This is a list of BaseSubCommand sub classes.
    #:
    #: Type:
    #:     list
    subcommands = {}

    #: Options common to all subcommands.
    #:
    #: Type:
    #:     list
    common_subcommand_option_list = []

    def usage(self, command_cls=None):
        """Return a usage string for the command.

        Args:
            command_cls (type, optional):
                The subcommand class to generate usage information for.

        Returns:
            unicode:
            The usage string.
        """
        if command_cls is None:
            subcommand = ' <subcommand>'
            description = self.description
        else:
            subcommand = ''
            description = command_cls.description

        usage = '%%(prog)s%s [options] %s' % (subcommand, self.args)

        if description:
            return '%s\n\n%s' % (usage, description)
        else:
            return usage

    def create_parser(self, config, argv=[]):
        """Create and return the argument parser for this command.

        Args:
            config (dict):
                The loaded RBTools config.

            argv (list, optional):
                The argument list.

        Returns:
            argparse.ArgumentParser:
            The argument parser.
        """
        subcommand_parsers = {}

        prog = '%s %s' % (RB_MAIN, self.name)

        # Set up a parent parser containing the options that will be shared.
        #
        # Ideally the globals would also be available to the main command,
        # but it ends up leading to arguments on the main command overruling
        # those on the subcommand, which is a problem for --json. For now,
        # we are only sharing on the subcommands.
        common_parser = argparse.ArgumentParser(add_help=False)

        for option in self.common_subcommand_option_list:
            option.add_to(common_parser, config, argv)

        for option in self._global_options:
            option.add_to(common_parser, config, argv)

        # Set up the parser for the main command.
        parser = argparse.ArgumentParser(
            prog=prog,
            usage=self.usage(),
            formatter_class=SmartHelpFormatter)

        for option in self.option_list:
            option.add_to(parser, config, argv)

        # Set up the parsers for each subcommand.
        subparsers = parser.add_subparsers(
            description=(
                'To get additional help for these commands, run: '
                '%s <subcommand> --help' % prog))

        for command_cls in self.subcommands:
            subcommand_name = command_cls.name

            subparser = subparsers.add_parser(
                subcommand_name,
                usage=self.usage(command_cls),
                formatter_class=SmartHelpFormatter,
                prog='%s %s' % (parser.prog, subcommand_name),
                description=command_cls.description,
                help=command_cls.help_text,
                parents=[common_parser])

            for option in command_cls.option_list:
                option.add_to(subparser, config, argv)

            subparser.set_defaults(command_cls=command_cls)
            subcommand_parsers[subcommand_name] = subparser

        self.subcommand_parsers = subcommand_parsers

        return parser

    def initialize(self):
        """Initialize the command."""
        super(BaseMultiCommand, self).initialize()

        command = self.options.command_cls(options=self.options,
                                           config=self.config,
                                           transport_cls=self.transport_cls)
        command.stdout = self.stdout
        command.stderr = self.stderr
        command.json = self.json
        command.initialize()
        self.subcommand = command

    def main(self):
        """Run the command."""
        self.subcommand.main()


def find_entry_point_for_command(command_name):
    """Return an entry point for the given rbtools command.

    If no entry point is found, None is returned.
    """
    # Attempt to retrieve the command class from the entry points. We
    # first look in rbtools for the commands, and failing that, we look
    # for third-party commands.
    entry_point = pkg_resources.get_entry_info('rbtools', 'rbtools_commands',
                                               command_name)

    if not entry_point:
        try:
            entry_point = next(pkg_resources.iter_entry_points(
                'rbtools_commands', command_name))
        except StopIteration:
            # There aren't any custom entry points defined.
            pass

    return entry_point


def command_exists(cmd_name):
    """Determine if the given command exists.

    This function checks for the existence of an RBTools command entry point
    with the given name and an executable named rbt-"cmd_name" on the path.
    Aliases are not considered.
    """
    return (find_entry_point_for_command(cmd_name) or
            is_exe_in_path('rbt-%s' % cmd_name))
