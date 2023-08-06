#!/usr/bin/env python3
"""
TestSandbox class.
"""

import os
import re
import sys
import base64
import traceback
import signal
import atexit
import time
import xml.etree.ElementTree as ET
from time import sleep
from subprocess import Popen
from mimetypes import MimeTypes
from typing import Union
import behave
import pkg_resources
from dogtail.utils import (  # pylint: disable=import-error
    config,
    isA11yEnabled,
    enableA11y,
)
from dogtail.rawinput import keyCombo  # pylint: disable=import-error

from qecore.utility import run, run_verbose, overview_action
from qecore.logger import Logging
from qecore.application import Application
from qecore.flatpak import Flatpak
from qecore.icons import qecore_icons, QECoreIcon

# First check: dogtail utility for accessibility check and enabling.
if not isA11yEnabled():
    print("Accessibility not detected running. Enabling via dogtail...")
    enableA11y()
    sleep(2)

# Second check: gsettings command to get the state and enable if set to false.
GET_ACCESSIBILITY = "gsettings get org.gnome.desktop.interface toolkit-accessibility"
SET_ACCESSIBILITY = (
    "gsettings set org.gnome.desktop.interface toolkit-accessibility true"
)
if "true" not in run(GET_ACCESSIBILITY):
    print("Accessibility not detected running. Enabling via gsettings command...")
    run(SET_ACCESSIBILITY)


logging_class = Logging()
log = logging_class.logger


NO_VALUES = ["", "n", "no", "f", "false", "0"]


class TestSandbox:
    """
    TestSandbox class.
    """

    def __init__(self, component, context=None, kiosk=False) -> None:
        """
        :type component: str
        :param component: Name of the component that is being tested.

        :type context: <behave.runner.Context>
        :param context: Behave context

        .. note::

            You are able to use logging via debug variable:
            QECORE_DEBUG=yes behave -kt <test_name>

            You are able to use general logging via variable:
            LOGGING=yes behave -kt <test_name>

            You can enforce embedding for testing purposes via debug variable:
            QECORE_EMBED_ALL=yes
        """

        if context is not None:
            assert isinstance(context, behave.runner.Context), "".join(
                "Unexpected argument, context should be <behave.runner.Context>"
            )

        self._embed_all = os.environ.get("QECORE_EMBED_ALL", "").lower() not in NO_VALUES
        self._no_cache = os.environ.get("QECORE_NO_CACHE", "").lower() not in NO_VALUES
        self._logging_to_console = os.environ.get("LOGGING", "").lower() not in NO_VALUES

        # Once user sets TestSandbox with logging, we assume they want console logs.
        if self._logging_to_console:
            log.info("Setting qecore to log in console.")
            logging_class.qecore_debug_to_console()

        if context is not None:
            for formatter in context._runner.formatters:
                if (
                    "pretty" in formatter.name
                    and getattr(formatter, "monochrome", None) is not None
                ):
                    formatter.monochrome = self._logging_to_console

        log.debug(
            "".join(
                (
                    f"__init__(self, component={component}, ",
                    f"context={repr(context)})",
                )
            )
        )

        # This might actually be required - we can fix the issue while running.
        self.do_not_let_dogtail_abort_on_bugged_a11y()

        log.debug("Accessibility is somehow turning off, making another check.")
        # First check: dogtail utility for accessibility check and enabling.
        if not isA11yEnabled():
            print("Accessibility not detected running. Enabling via dogtail.")
            enableA11y()
            sleep(2)

        # Second check: gsettings command to get the state and enable if set to false.
        if "true" not in run(GET_ACCESSIBILITY):
            print("Accessibility not detected running. Enabling via gsettings command...")
            run(SET_ACCESSIBILITY)

        self.context = context
        self.shell = None

        if self.context:
            self.context.failed_setup = None

        self.kiosk = kiosk
        self.component = component
        self.current_scenario = None
        self.background_color = None
        self.background_image_revert = False
        self.background_image_location = ""

        self.disable_welcome_tour = True

        self.enable_animations = None

        self.enable_close_yelp = True

        self.logging_start = None
        self.screenshot_run_result = None
        self.screenshot_portal_run_result = None

        self.record_video = True
        self.record_video_pid = None

        self.attach_video = True
        self.attach_video_on_pass = False

        self.attach_journal = True
        self.attach_journal_on_pass = False

        self.attach_coredump = False
        self.attach_coredump_on_pass = True
        self.attach_coredump_file_check = False

        self.attach_screenshot = True
        self.failed_test = False

        self.attach_faf = True
        self.attach_faf_on_pass = True

        self.status_report = True

        self.logging_cursor = None
        self.test_execution_start = None

        self.workspace_return = False

        self.set_keyring = True
        self.keyring_process_pid = None

        self.wait_for_stable_video = True

        self.production = True

        self.timeout_handling = True

        self._after_scenario_hooks = []
        self.reverse_after_scenario_hooks = False

        self.html_report_links = True

        self.embed_separate = False
        self.change_title = True
        self.session_icon_to_title = True
        self.default_application_icon_to_title = False

        self.applications = []
        self.package_list = {"gnome-shell", "mutter"}
        self.default_application = None

        self._new_log_indicator = True
        self._scenario_skipped = False

        self._project_git_url = None
        self._project_git_commit = None

        self._attach_qecore_debug = True
        self._attach_qecore_debug_on_pass = False
        self._qecore_debug_log_file = "/tmp/qecore_logger.log"

        self._set_up_scenario_skip_check()
        self._retrieve_session_data()
        self._check_for_coredump_fetching()
        self._set_g_debug_environment_variable()

    def before_scenario(self, context, scenario) -> None:
        """
        Actions that are to be executed before every scenario.

        :type context: <behave.runner.Context>
        :param context: Pass this object from environment file.

        :type scenario: <Scenario>
        :param scenario: Pass this object from environment file.

        .. note::

            You can enforce embedding for testing purposes via debug variable:
            QECORE_EMBED_ALL=yes
        """

        log.debug(f"before_scenario(self, context, scenario) test: {scenario.tags[-1]}")

        if hasattr(context, "failed_setup") and context.failed_setup:
            # Upon failed setup we care only about embedding setup.
            self._set_up_embedding(context)
            # Load the data from failed setup variable.
            data = context.failed_setup
            # Embed the data to the log.
            context.embed("text", data, "Failed setup in Before All")
            sys.exit(1)

        self._wait_until_shell_becomes_responsive()

        self._scenario_skipped = False

        self.failed_test = False

        # If QECORE_EMBED_ALL is set, set production to True.
        self.production = self.production or self._embed_all

        self._set_welcome_tour()

        self._set_animations()

        self.current_scenario = scenario.tags[-1]
        self._set_journal_log_start_time()
        self._set_coredump_log_start_time()

        if not self.kiosk:
            overview_action(action="hide")

        self.set_typing_delay(0.2)

        self.set_debug_to_stdout_as(False)
        self._close_yelp()
        self._close_initial_setup()
        self._copy_data_folder()
        self.set_blank_screen_to_never()

        self._set_up_embedding(context)

        if self.change_title:
            self._set_title(context)

        if self.timeout_handling:
            self._set_timeout_handling()

        if self.record_video and self.production:
            self._start_recording()

        self._detect_keyring()
        self._return_to_home_workspace()

        # Separater of testing suite and setup logs.
        log.debug(" ======== Start of the test suite section ======== ")

    def after_scenario(self, context, scenario) -> None:
        """
        Actions that are to be executed after every scenario.

        :type context: <behave.runner.Context>
        :param context: Pass this object from environment file.

        :type scenario: <Scenario>
        :param scenario: Pass this object from environment file.
        """

        # Separater of testing suite and setup logs.
        log.debug(" ======== End of the test suite section ======== ")

        log.debug(f"after_scenario(self, context, scenario) test: {scenario.tags[-1]}")

        if scenario.status == "failed":
            self.failed_test = True

        self._capture_image()

        if self.background_image_revert:
            self._revert_background_image()

        if self.record_video:
            self._stop_recording()

        if not self.kiosk:
            overview_action(action="hide")

        for application in self.applications:
            application.kill_application()

        self._attach_screenshot_to_report(context)

        self._attach_journal_to_report(context)

        self._attach_coredump_log_to_report(context)

        self._attach_video_to_report(context)

        self._attach_abrt_link_to_report(context)

        self._attach_version_status_to_report(context)

        self._process_after_scenario_hooks(context)

        self._process_embeds(context)

        self._attach_qecore_debug_log(context)

        if self.html_report_links:
            self._html_report_links(context)

        self._new_log_indicator = False

    def _after_all(self, context) -> None:  # pylint: disable=unused-argument
        """
        This is executed as behave after_all hook,
        if context is proved in :func:`__init__`.

        :type context: <behave.runner.Context>
        :param context: Object is passed from the function that is calling it.

        .. note::
            Do **NOT** call this, if you provided context to :func:`__init__`.
        """

        log.debug("_after_all(self, context)")

        self._scenario_skip_check_cb(do_assert=True)

    def _scenario_skip_check_cb(self, do_assert=False) -> None:
        """
        Callback function. Checks if any scenario was executed.

        .. note::

            Do **NOT** call this by yourself. This method is called when test ends.
        """

        log.debug(f"_scenario_skip_check_cb(self, do_assert={do_assert})")

        if do_assert:
            assert not self._scenario_skipped, "No scenario matched tags"
        else:
            if self._scenario_skipped:
                print("No scenario matched tags, exiting with error code 1.")
                # sys.exit, raise, assert do not work in an atexit hook.
                os._exit(1)  # pylint: disable=protected-access

    def _set_up_scenario_skip_check(self) -> None:
        """
        Remember in sandbox if any scenario (:func:`before_scenario`) was executed.

        If context provided, set after_all behave hook, otherwise set atexit hook.

        .. note::

            Do **NOT** call this by yourself. This method is called at :func:`__init__`.
        """

        log.debug("_set_up_scenario_skip_check(self)")

        self._scenario_skipped = True

        if self.context is not None:
            log.debug(" context is set, setting after_all behave hook")

            def get_hook(old_hook):
                def hook_runner(*args, **kwargs) -> None:
                    if old_hook is not None:
                        log.debug("execute environment after_all HOOK")
                        old_hook(*args, **kwargs)
                    else:
                        log.debug("after_all not defined in environment")
                    log.debug("execute QECore after_all HOOK")
                    self._after_all(*args, **kwargs)

                return hook_runner

            hooks = self.context._runner.hooks  # pylint: disable=protected-access
            hooks["after_all"] = get_hook(hooks.get("after_all", None))
            self.context._runner.hooks = hooks  # pylint: disable=protected-access
        else:
            log.debug(" context is None, setting atexit hook")
            atexit.register(self._scenario_skip_check_cb)

    def _gracefull_exit(self, signum, frame) -> None:  # pylint: disable=unused-argument
        """
        If killed externally, run user defined hooks not to break tests that will be
        executed next.

        .. note::

            Do **NOT** call this by yourself. This method is called when killed
            externally (timeout).
        """

        log.debug(f"_graceful_exit(self, signum={signum}, frame)")

        assert False, f"Timeout: received signal: '{signum}'"

    def _start_recording(self) -> None:
        """
        Start recording the video.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_start_recording(self)")

        self.display_clock_seconds()
        self.set_max_video_length_to(600)

        active_script_recordings = run("pgrep -fla qecore_start_recording").strip("\n")
        log.debug(f"_start_recording: removing active recordings: '{active_script_recordings}'")

        leftover_recording_processes_pids = run("pgrep -f qecore_start_recording").strip("\n")
        if leftover_recording_processes_pids:
            leftover_recording_process_pid_list = (leftover_recording_processes_pids.split("\n"))
            for script_pid in leftover_recording_process_pid_list:
                run(f"sudo kill -9 {script_pid}")

        active_screen_casts = run("pgrep -fla Screencast").strip("\n")
        log.debug(f"_start_recording: removing active Screencasts: '{active_screen_casts}'")

        leftover_screencast_processes_pids = run("pgrep -f Screencast").strip("\n")
        if leftover_screencast_processes_pids:
            leftover_screencast_process_pid_list = (leftover_screencast_processes_pids.split("\n"))
            for screen_cast_pid in leftover_screencast_process_pid_list:
                run(f"sudo kill -9 {screen_cast_pid}")

        absolute_path_to_video = os.path.expanduser("~/Videos")
        run(f"sudo rm -rf {absolute_path_to_video}/Screencast*")

        record_video_process = Popen("qecore_start_recording", shell=True)
        self.record_video_pid = record_video_process.pid

    def _stop_recording(self) -> None:
        """
        Stop recording the video.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        log.debug("_stop_recording(self)")

        # Stop screencasting started by qecore.
        if self.record_video_pid is not None:
            run(f"sudo kill -9 {self.record_video_pid} > /dev/null")

        # Giving the org.gnome.Shell.Screencast chance to end
        # on its own - before killing it.
        for timer in range(30):
            screencast_process = run("pgrep -f Screencast").strip("\n")
            if screencast_process:
                sleep(0.1)
            else:
                log.debug(
                    "".join(
                        (
                            "_stop_recording: ",
                            f"Screencast process ended on its own in '{str(timer/10)}' seconds.",
                        )
                    )
                )
                break

        # Failsafe.
        leftover_recording_processes_pids = run(
            "pgrep -f 'qecore_start_recording|Screencast'"
        ).strip("\n")
        if leftover_recording_processes_pids:
            # Purely for logging purposes.
            leftover_recording_processes = run("pgrep -fla 'qecore_start_recording|Screencast'").strip("\n")
            log.debug(f"_stop_recording: leftover processes: '{leftover_recording_processes}'")

            # Kill any leftover process.
            leftover_recording_processes_pid_list = (leftover_recording_processes_pids.split("\n"))
            for leftover_process_pid in leftover_recording_processes_pid_list:
                log.debug(
                    "".join(
                        (
                            "_stop_recording: failsafe needed, ",
                            f"killing active recording '{leftover_process_pid}'",
                        )
                    )
                )
                run(f"sudo kill -9 {leftover_process_pid}")

            sleep(1)

        self.record_video_pid = None

    def get_application(
        self,
        name,
        a11y_app_name=None,
        desktop_file_exists=True,
        desktop_file_name="",
        desktop_file_path="",
        app_process_name="",
    ) -> Application:
        """
        Return application to be used in test.

        :type name: str
        :param name: Name of the package that provides the application.

        :type a11y_app_name: str
        :param a11y_app_name: Application's name as it appears in the a11y tree.

        :type desktop_file_exists: bool
        :param desktop_file_exists: Does desktop file of the application exist?

        :type desktop_file_name: str
        :param desktop_file_name: Application's desktop file name.

        :type app_process_name: str
        :param app_process_name: Application's name as it appears in a running process.

        :return: Application class instance
        :rtype: <qecore.application.Application>

        This function is wrapped by :func:`get_app`.
        """

        log.debug(
            " ".join(
                (
                    f"get_application(self, name={name},",
                    f"a11y_app_name={a11y_app_name},",
                    f"desktop_file_exists={desktop_file_exists},",
                    f"desktop_file_name={desktop_file_name},",
                    f"desktop_file_path={desktop_file_path},",
                    f"app_process_name={app_process_name})",
                )
            )
        )

        new_application = Application(
            name,
            a11y_app_name=a11y_app_name,
            desktop_file_exists=desktop_file_exists,
            desktop_file_name=desktop_file_name,
            desktop_file_path=desktop_file_path,
            app_process_name=app_process_name,
            session_type=self.session_type,
            session_desktop=self.session_desktop,
            kiosk=self.kiosk,
        )

        self.package_list.add(name)
        self.applications.append(new_application)
        self.default_application = (
            new_application
            if self.default_application is None
            else self.default_application
        )

        return new_application

    def get_flatpak(self, flatpak_id, **kwargs) -> Flatpak:
        """
        Return flatpak to be used in test.

        :type flatpak_id: str
        :param flatpak_id: Unique name of flatpak, mandatory format: org.flathub.app

        :return: Flatpak class instance
        :rtype: <qecore.flatpak.Flatpak>
        """

        log.debug(f"get_flatpak(self, flatpak_id={flatpak_id}")

        flatpak = Flatpak(flatpak_id=flatpak_id, **kwargs)
        self.applications.append(flatpak)
        self.default_application = self.default_application or flatpak
        return flatpak

    def add_package(self, package_input) -> None:
        """
        Add package for a Status embed to the html log.

        :type package_input: str or list
        :param package_input: Package string or Package list .
        """

        log.debug(f"add_package(self, package_input='{package_input}')")

        if isinstance(package_input, str):
            self.package_list.add(package_input)

        elif isinstance(package_input, list):
            self.package_list = self.package_list.union(package_input)

        else:
            self.package_list.add("You did not provide a string or a list.")

    def _wait_until_shell_becomes_responsive(self) -> None:
        """
        Give some time if shell is not yet loaded fully.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`sandbox.TestSandbox.__init__`.
        """

        log.debug(f"_wait_until_shell_becomes_responsive: waiting for '{self.session_type}'.")

        if self.kiosk:
            self.shell = None
            return

        error_message = ""
        for _ in range(60):
            try:
                from dogtail.tree import (  # pylint: disable=import-error,import-outside-toplevel
                    root,
                )

                if "gnome-shell" not in [x.name for x in root.applications()]:
                    log.debug(
                        "".join((
                            "_wait_until_shell_becomes_responsive: ",
                            "gnome-shell not detected in a11y root yet.",
                        ))
                    )
                    sleep(0.5)
                else:
                    self.shell = root.application("gnome-shell")

                    # Once we have shell set the attribute in applications also.
                    for application in self.applications:
                        application.shell = self.shell

                    return

            except Exception as error:  # pylint: disable=broad-except
                error_message = error
                log.debug(f"_wait_until_shell_becomes_responsive: session is not usable yet: '{error}'.")

        raise RuntimeError(f"A11y root not found: unable to continue: '{error_message}'")

    def _retrieve_session_data(self) -> None:
        """
        Get session/system data.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`__init__`.
        """

        log.debug("_retrieve_session_data(self)")

        self.architecture = run("uname -m").strip("\n")
        log.debug(f"_retrieve_session_data: architecture detected: '{self.architecture}'")

        # Distributions expected for now: self.distribution = ["Red Hat Enterprise Linux", "Fedora"]
        self.distribution = run("cat /etc/os-release | grep ^NAME=")
        self.distribution = self.distribution.split("=")[-1].strip("\n").strip('"')
        log.debug(f"_retrieve_session_data: distribution detected: '{self.distribution}'")

        self.session_display = run("echo $DISPLAY").strip("\n")
        if not self.session_display:
            log.debug(
                "".join((
                    "_retrieve_session_data: session display is not set - retrieve from ",
                    "qecore_get_active_display",
                ))

            )

            self.session_display = run("qecore_get_active_display").strip("\n")
            os.environ["DISPLAY"] = self.session_display

        log.debug(f"_retrieve_session_data: session_display detected: '{self.session_display}'")

        try:
            self.resolution = [
                int(x)
                for x in re.findall(r"\d+x\d+", run("xrandr | grep '*'"))[0].split("x")
            ]
        except Exception as error:  # pylint: disable=broad-except
            self.resolution = f"The resolution retrieval failed for: {error}"

        log.debug(f"_retrieve_session_data: resolution detected: '{self.resolution}'")

        self.session_desktop = run("echo $XDG_SESSION_DESKTOP").strip("\n")
        log.debug(f"_retrieve_session_data: session_desktop detected: '{self.session_desktop}'")

        self.session_type = "x11"
        if (
            "XDG_SESSION_TYPE" in os.environ
            and "wayland" in os.environ["XDG_SESSION_TYPE"]
        ):
            self.session_type = "wayland"
        log.debug(f"_retrieve_session_data: session_type detected: '{self.session_type}'")

    def _set_up_embedding(self, context) -> None:
        """
        Set up embeding to the behave html formatter.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_set_up_embedding(self)")

        def embed_data(
            mime_type, data, caption, html_el=None, fail_only=False, separate=None
        ) -> None:
            log.debug(
                " ".join(
                    (
                        f"embed(mime_type={mime_type},",
                        f"data=..., caption={caption},",
                        f"html_el={repr(html_el)},",
                        f"fail_only={fail_only},",
                        f"separate={separate})",
                    )
                )
            )

            if context.html_formatter is None:
                log.debug("  skipping embed as no html formatter detected")
                return

            formatter = context.html_formatter

            if separate is None:
                separate = self.embed_separate

            # If data is empty we want to finish html tag by at least one character
            non_empty_data = " " if not data else data

            if html_el is None:
                html_el = formatter.actual["act_step_embed_span"]

            if mime_type == "call" or fail_only:
                context._to_embed.append(  # pylint: disable=protected-access
                    {
                        "html_el": html_el,
                        "mime_type": mime_type,
                        "data": non_empty_data,
                        "caption": caption,
                        "fail_only": fail_only,
                        "separate": separate,
                    }
                )
            else:
                formatter._doEmbed(  # pylint: disable=protected-access
                    html_el, mime_type, non_empty_data, caption
                )
                if separate:
                    ET.SubElement(html_el, "br")

        def set_title(title, append=False, tag="span", **kwargs) -> None:
            for (
                formatter
            ) in context._runner.formatters:  # pylint: disable=protected-access
                if (
                    formatter.name == "html"
                    and getattr(formatter, "set_title", None) is not None
                ):
                    formatter.set_title(title=title, append=append, tag=tag, **kwargs)

                elif (
                    formatter.name == "html-pretty"
                    and getattr(formatter, "set_title", None) is not None
                ):
                    formatter.set_title(title=title)

        # Set up a variable that we can check against if there is a formatter in use.
        context.html_formatter = None

        # Main reason for this is backwards compatibility.
        # There always used to be context.embed defined and was ignored if called.
        # We define the same to not break the legacy usage while checking
        # html_formatter to save time.
        def _dummy_embed(*args, **kwargs) -> None:  # pylint: disable=unused-argument
            pass

        context.embed = _dummy_embed

        for formatter in context._runner.formatters:  # pylint: disable=protected-access

            # Formatter setup for html.
            if formatter.name == "html":
                formatter.embedding = embed_data
                context.html_formatter = formatter
                context.embed = embed_data
                break

            # Formatter setup for html-pretty.
            if formatter.name == "html-pretty":
                context.html_formatter = formatter
                context.embed = formatter.embed
                break

        context._to_embed = []  # pylint: disable=protected-access
        context.set_title = set_title

    def add_after_scenario_hook(self, callback, *args, **kwargs) -> None:
        """
        Creates hook from callback function and its arguments.
        Hook will be called during :func:`sandbox.after_scenario`.

        :type callback: <function>
        :param callback: function to be called

        .. note::
            Hooks are called in :func:`sandbox.after_scenario` in the order they were
            added. To reverse the order of execution set
            `sandbox.reverse_after_scenario_hooks` (default `False`).

        **Examples**::

            # already defined function
            def something():
                ...

            sandbox.add_after_scenario_hook(something)

            # generic function call
            sandbox.add_after_scenario_hook(function_name, arg1, arg2, kwarg1=val1, ...)

            # call command
            sandbox.add_after_scenario_hook(subprocess.call, "command to be called", shell=True)

            # embed data - if you want them embeded in the last step
            sandbox.add_after_scenario_hook(context.embed, "text/plain", data, caption="DATA")

            # embed data computed later (read log file)
            sandbox.add_after_scenario_hook(lambda context:
                context.embed("text/plain", open(log_file).read(), caption="LOG"), context)
        """

        log.debug("add_after_scenario_hook()")

        self._after_scenario_hooks += [(callback, args, kwargs)]

    def _set_timeout_handling(self) -> None:
        """
        Set up signal handling.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_set_timeout_handling(self)")

        signal.signal(signal.SIGTERM, self._gracefull_exit)
        run("touch /tmp/qecore_timeout_handler")

    def _set_welcome_tour(self) -> None:
        """
        Disable gnome-welcome-tour via gsettings command if allowed.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_set_welcome_tour(self)")

        if self.disable_welcome_tour:
            run(
                " ".join(
                    (
                        "gsettings",
                        "set",
                        "org.gnome.shell",
                        "welcome-dialog-last-shown-version",
                        "100.0",  # larger number than the current 40
                    )
                )
            )

    def _set_animations(self) -> None:
        """
        Set animations via gsettings command.
        Default value is None so the settings is not set unless user specifies otherwise.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_set_animations(self)")

        if self.enable_animations is not None:
            run(
                " ".join(
                    (
                        "gsettings",
                        "set",
                        "org.gnome.desktop.interface",
                        "enable-animations",
                        "true" if self.enable_animations else "false",
                    )
                )
            )

    def _set_journal_log_start_time(self) -> None:
        """
        Save time.
        Will be used to retrieve logs from journal.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_set_journal_log_start_time(self)")

        initial_cursor_output = run("sudo journalctl --lines=0 --show-cursor").strip()
        cursor_target = initial_cursor_output.split("cursor: ", 1)[-1]
        self.logging_cursor = f'"--after-cursor={cursor_target}"'

    def _set_coredump_log_start_time(self) -> None:
        """
        Save time.
        Will be used to retrieve coredumpctl list.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_set_coredump_log_start_time(self)")

        self.test_execution_start = run("date +%s").strip("\n")

    def _close_yelp(self) -> None:
        """
        Close yelp application that is opened after fresh system installation.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_close_yelp(self)")

        # Attribute switch to allow not closing yelp in before_scenario.
        # Corner case was found in which we test yelp and do not close between scenarios.
        if not self.enable_close_yelp:
            return

        help_process_id = run("pgrep yelp").strip("\n")
        if help_process_id.isdigit():
            run(f"kill -9 {help_process_id}")

    def _close_initial_setup(self) -> None:
        """
        Close initial setup window that is opened after the first login to the system.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_close_initial_setup(self)")

        run("echo yes > ~/.config/gnome-initial-setup-done")

    def set_blank_screen_to_never(self) -> None:
        """
        Set blank screen to never. For longer tests it is undesirable for screen to lock.

        .. note::

            This method is called by :func:`before_scenario`.
            There was never need to have other options,
            we do not want the system to sleep during the test.
        """

        log.debug("set_blank_screen_to_never(self)")

        run("gsettings set org.gnome.desktop.session idle-delay 0")

    def set_max_video_length_to(self, number=600) -> None:
        """
        Set maximum allowed video length. With default value for 10 minutes.

        :type number: int
        :param number: Maximum video length.

        .. note::

            This method is called by :func:`before_scenario`.
            You can overwrite the setting.
        """

        log.debug(f"set_max_video_length_to(self, number={number})")

        run(
            " ".join(
                (
                    "gsettings set",
                    "org.gnome.settings-daemon.plugins.media-keys",
                    f"max-screencast-length {number}",
                )
            )
        )

    def display_clock_seconds(self) -> None:
        """
        Display clock seconds for better tracking test in video.

        .. note::

            This method is called by :func:`before_scenario`.
            There was never need to have other options,
            as we want to see the seconds ticking during the test.
        """

        log.debug("display_clock_seconds(self)")

        run("gsettings set org.gnome.desktop.interface clock-show-seconds true")

    def _return_to_home_workspace(self) -> None:
        """
        Return to home workspace.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_return_to_home_workspace(self)")

        if not self.workspace_return:
            return

        keyCombo("<Super><Home>")

    def set_typing_delay(self, number) -> None:
        """
        Set typing delay so slower machines will not lose characters on type.

        :type number: int
        :param number: Time in between accepted key strokes.

        .. note::

            This method is called by :func:`before_scenario`.
            You can overwrite the setting.
        """

        log.debug(f"set_typing_delay(self, number={number})")

        config.typingDelay = number

    def do_not_let_dogtail_abort_on_bugged_a11y(self) -> None:
        """
        Do not let dogtail abort when we can fix the issue while running.

        .. note::

            This method is called by :func:`before_scenario`.
            You can overwrite the setting.
        """

        log.debug("Do_not_let_dogtail_abort_on_bugged_a11y(self)")

        config.checkForA11y = False

    def set_debug_to_stdout_as(self, true_or_false=False) -> None:
        """
        Set debugging to stdout.

        :type true_or_false: bool
        :param true_or_false: Decision if debug to stdout or not.

        .. note::

            This method is called by :func:`before_scenario`.
            You can overwrite the setting.
        """

        log.debug(f"set_debug_to_stdout_as(self, true_or_false={true_or_false})")

        config.logDebugToStdOut = true_or_false

    def _copy_data_folder(self) -> None:
        """
        Copy data/ directory content to the /tmp/ directory.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_copy_data_folder(self)")

        if os.path.isdir("data/"):
            run("rsync -r data/ /tmp/")

    def _detect_keyring(self) -> None:
        """
        Detect if keyring was setup. If not, setup the keyring with empty password.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
        """

        log.debug("_detect_keyring(self)")

        if not self.set_keyring:
            return

        if self.kiosk:
            return

        current_user = os.path.expanduser("~")

        is_keyring_set = os.path.isfile("/tmp/keyring_set")
        log.debug(f"_detect_keyring: keyring set by qecore: '{is_keyring_set}'")

        is_keyring_in_place = os.path.isfile(f"{current_user}/.local/share/keyrings/default")
        log.debug(f"_detect_keyring: default keyring exists: '{is_keyring_in_place}'")

        if not is_keyring_set or not is_keyring_in_place or self._no_cache:
            log.debug(f"_detect_keyring: removing all keyrings from '{current_user}/.local/share/keyrings/'.")
            run(f"sudo rm -rf {current_user}/.local/share/keyrings/*")

            # This should always succeed.
            # If not, do not fail here, let behave handle it and generate html log.
            try:
                log.debug("_detect_keyring: creating keyring process.")

                create_keyring_process = Popen("qecore_create_keyring", shell=True)
                self.keyring_process_pid = create_keyring_process.pid
                sleep(1)

                log.debug("_detect_keyring: confirming choosing empty password for keyring in session.")
                self.shell.child("Continue").click()
                sleep(0.2)

                log.debug("_detect_keyring: confirming to store password unencrypted in session.")
                self.shell.child("Continue").click()
                sleep(0.2)
            except Exception as error:  # pylint: disable=broad-except
                print(f"_detect_keyring error with keyring creation/confirmation: '{error}'")
                traceback.print_exc(file=sys.stdout)

                log.debug("_detect_keyring: failed to create, end the session prompt.")
                create_keyring_process.kill()

            run("touch /tmp/keyring_set")

    def _capture_image(self) -> None:
        """
        Capture screenshot after failed step.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        if not self.production:
            return

        if not (self.attach_screenshot or self._embed_all):
            return

        if not (self.failed_test or self._embed_all):
            return

        log.debug("_capture_image(self)")

        self.screenshot_run_result = run_verbose(
            "gnome-screenshot -f /tmp/screenshot.png"
        )

        # Lets assume once there is an error the portal should be used.
        if self.screenshot_run_result[1] != 0:
            self.screenshot_portal_run_result = run_verbose(
                "qecore_capture_screenshot", timeout=5
            )

    def _check_for_coredump_fetching(self) -> None:
        """
        Set attach_coredump variable if set in Jenkins - tested via file existance.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`__init__`.
        """

        log.debug("_check_for_coredump_fetching(self)")

        self.attach_coredump_file_check = os.path.exists("/tmp/qecore_coredump_fetch")

    def _set_g_debug_environment_variable(self) -> None:
        """
        Setup environment variable G_DEBUG as 'fatal-criticals'.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`__init__`.
        """

        log.debug("_set_g_debug_environment_variable(self)")

        # Environment value set upon checked field in Jenkins.
        if os.path.isfile("/tmp/headless_enable_fatal_critical"):
            log.debug("_set_g_debug_environment_variable: set G_DEBUG=fatal-criticals.")
            os.environ["G_DEBUG"] = "fatal-criticals"

        # Fatal_wanings has bigger priority than criticals.
        # Should both options be set in Jenkins the warning will overwrite the variable.
        if os.path.isfile("/tmp/headless_enable_fatal_warnings"):
            log.debug("_set_g_debug_environment_variable: set G_DEBUG=fatal-warnings.")
            os.environ["G_DEBUG"] = "fatal-warnings"

    def _set_title(self, context) -> None:
        """
        Append component name and session type to HTML title.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`before_scenario`.
            Use :func:`context.set_title` to set HTML title.
        """

        log.debug("_set_title(self, context)")

        formatter_instance = getattr(context, "html_formatter", None)
        if formatter_instance is None:
            return

        if formatter_instance.name == "html":
            context.set_title("", tag="br", append=True)

            if self.default_application_icon_to_title:
                icon = self.get_default_application_icon()
                if icon is not None:
                    context.set_title(
                        "",
                        append=True,
                        tag="img",
                        alt=self.session_type[1],
                        src=icon.to_src(),
                        style="height:1.8rem; vertical-align:text-bottom;",
                    )

                context.set_title(f"{self.component} - ", append=True, tag="small")

            if self.session_icon_to_title:
                context.set_title(
                    "",
                    append=True,
                    tag="img",
                    alt=self.session_type[1],
                    src=qecore_icons[self.session_type].to_src(),
                    style="height:1.8rem; vertical-align:text-bottom;",
                )

                context.set_title(
                    self.session_type[1:],
                    append=True,
                    tag="small",
                    style="margin-left:-0.4em;",
                )

            self.change_title = False

        elif formatter_instance.name == "html-pretty":
            formatter_instance.set_icon(icon=qecore_icons[self.session_type].to_src())

    def get_default_application_icon(self) -> Union[QECoreIcon, None]:
        """
        Get icon for default application.

        :return: icon or None
        :rtype: <icons.QECoreIcon>
        """

        log.debug("get_default_application_icon(self)")

        # Importing here because of sphinx documentation generating issues.
        import gi  # pylint: disable=import-outside-toplevel

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk  # pylint: disable=import-outside-toplevel

        if self.default_application and self.default_application.icon:
            icon_theme = Gtk.IconTheme.get_default()
            icon = icon_theme.lookup_icon(self.default_application.icon, 48, 0)
            if icon:
                icon_path = icon.get_filename()
                if icon_path:
                    mime = MimeTypes()
                    mime_type = mime.guess_type(icon_path)[0]
                    data_base64 = base64.b64encode(open(icon_path, "rb").read())
                    data_encoded = data_base64.decode("utf-8").replace("\n", "")
                    return QECoreIcon(mime_type, "base64", data_encoded)
        return None

    def _attach_screenshot_to_report(self, context) -> None:
        """
        Attach screenshot to the html report upon failed test.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`after_scenario`.
        """

        log.debug("_attach_screenshot_to_report(self, context)")

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            log.debug("No formatter defined.")
            return

        if not self.production:
            log.debug(f"Attribute self.production='{str(self.production)}'.")
            return

        if not (self.attach_screenshot or self._embed_all):
            log.debug(f"Attribute self.attach_screenshot='{str(self.attach_screenshot)}'.")
            return

        if not (self.failed_test or self._embed_all):
            log.debug(f"Attribute self.failed_test='{str(self.failed_test)}'.")
            return

        if self.screenshot_run_result[1] != 0:
            log.debug("_attach_screenshot_to_report: Screenshot capture failed.")
            context.embed(
                mime_type="text/plain",
                data=f"Screenshot capture failed: \n{self.screenshot_run_result}\n",
                caption="ScreenshotFailed",
                fail_only=not self._embed_all,
            )

            # Attempt to embed screenshot via portal on failed gnome-screenshot command.
            if self.screenshot_portal_run_result and self.screenshot_portal_run_result[1] != 0:
                log.debug("_attach_screenshot_to_report: Screenshot Portal capture failed.")
                context.embed(
                    mime_type="text/plain",
                    data=f"Screenshot Portal capture failed: \n{self.screenshot_portal_run_result}\n",
                    caption="ScreenshotPortalFailed",
                    fail_only=not self._embed_all,
                )

            else:
                log.debug("_attach_screenshot_to_report: Attempting to attach Portal Screenshot to report.")

                image_path_stripped = self.screenshot_portal_run_result[0].lstrip("file:/").rstrip("\n")
                image_path = "/" + image_path_stripped
                self.attach_image_to_report(
                    context, image_path,
                    "ScreenshotPortal",
                    fail_only=not self._embed_all,
                )
        else:
            log.debug("_attach_screenshot_to_report: Attempting to attach screenshot to report.")
            self.attach_image_to_report(context, "/tmp/screenshot.png", "Screenshot", fail_only=True)

    def attach_image_to_report(
        self, context, image="", caption="DefaultCaption", fail_only=False
    ) -> None:
        """
        Attach image to the html report upon user request.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        :type image: str
        :param image: Location of the image/png file.

        :type caption: str
        :param caption: Caption that is to be displayed in test html report.

        :type fail_only: bool
        :param fail_only: attach only if scenario fails

        .. note::

            Use this to attach any image to report at any time.
        """

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            log.debug("No formatter defined.")
            return

        if not self.production:
            log.debug(f"Attribute self.production='{str(self.production)}'.")
            return

        log.debug(f"Path to the image to be embedded: '{image}'")

        log.debug(
            " ".join(
                (
                    "attach_image_to_report(self, context,",
                    f"image={image},",
                    f"caption={caption},",
                    f"fail_only={fail_only})",
                )
            )
        )

        if os.path.isfile(image):
            data_base64 = base64.b64encode(open(image, "rb").read())
            data_encoded = data_base64.decode("utf-8").replace("\n", "")
            context.embed(
                mime_type="image/png",
                data=data_encoded,
                caption=caption,
                fail_only=fail_only,
            )

    def _attach_video_to_report(self, context) -> None:
        """
        Attach video to the html report upon failed test.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        log.debug("_attach_video_to_report(self, context)")

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            log.debug("No formatter defined.")
            return

        if not (self.production and self.record_video):
            log.debug(f"Attribute self.production='{str(self.production)}'.")
            log.debug(f"Attribute self.record_video='{str(self.record_video)}'.")
            return

        if not (self.attach_video or self._embed_all):
            log.debug(f"Attribute self.attach_video='{str(self.attach_video)}'.")
            return

        if not (self.attach_video_on_pass or self.failed_test or self._embed_all):
            log.debug(f"Attribute self.failed_test='{str(self.failed_test)}'.")
            log.debug(f"Attribute self.attach_video_on_pass='{str(self.attach_video_on_pass)}'.")
            return

        absolute_path_to_video = os.path.expanduser("~/Videos")
        screencast_list = [
            f"{absolute_path_to_video}/{file_name}"
            for file_name in os.listdir(absolute_path_to_video)
            if "Screencast" in file_name
        ]
        log.debug(f"_attach_video_to_report: screencast list '{screencast_list}'")

        video_name = f"{self.component}_{self.current_scenario}"
        absolute_path_to_new_video = f"{absolute_path_to_video}/{video_name}.webm"
        log.debug(f"_attach_video_to_report: absolute path to new video '{absolute_path_to_new_video}'")

        if screencast_list == []:
            log.debug("_attach_video_to_report: No video file found.")
            context.embed(
                mime_type="text/plain",
                data="No video file found.",
                caption="Video",
                fail_only=not (self.attach_video_on_pass or self._embed_all),
            )
        else:
            if self.wait_for_stable_video:
                self._wait_for_video_encoding(screencast_list[0])

            data_base64 = base64.b64encode(open(screencast_list[0], "rb").read())
            data_encoded = data_base64.decode("utf-8").replace("\n", "")
            context.embed(
                mime_type="video/webm",
                data=data_encoded,
                caption="Video",
                fail_only=not (self.attach_video_on_pass or self._embed_all),
            )

            log.debug("_attach_video_to_report: renaming screencast.")
            run(f"mv {screencast_list[0]} {absolute_path_to_new_video}")
            log.debug("_attach_video_to_report: erasing unsaved videos.")
            run(f"sudo rm -rf {absolute_path_to_video}/Screencast*")

    def _attach_journal_to_report(self, context) -> None:
        """
        Attach journal to the html report upon failed test.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        log.debug("_attach_journal_to_report(self, context)")

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            log.debug("No formatter defined.")
            return

        if not self.production:
            log.debug(f"Attribute self.production='{str(self.production)}'.")
            return

        if not (self.attach_journal or self._embed_all):
            log.debug(f"Attribute self.attach_journal='{str(self.attach_journal)}'.")
            return

        if not (self.attach_journal_on_pass or self.failed_test or self._embed_all):
            log.debug(f"Attribute self.failed_test='{str(self.failed_test)}'.")
            log.debug(f"Attribute self.attach_journal_on_pass='{str(self.attach_journal_on_pass)}'.")
            return

        journal_run = run_verbose(
            " ".join(
                (
                    "sudo journalctl --all",
                    f"--output=short-precise {self.logging_cursor}",
                    "> /tmp/journalctl_short.log",
                )
            )
        )

        if journal_run[1] != 0:
            log.debug("_attach_journal_to_report: creation of journalctl log failed.")
            context.embed(
                mime_type="text/plain",
                data=f"Creation of journalctl file failed: \n{journal_run}\n",
                caption="journalctl",
                fail_only=not (self.attach_journal_on_pass or self._embed_all),
            )
        else:
            log.debug("_attach_journal_to_report: creation of journalctl log succeeded.")
            journal_data = self.file_loader("/tmp/journalctl_short.log")

            context.embed(
                mime_type="text/plain",
                data=journal_data,
                caption="journalctl",
                fail_only=not (self.attach_journal_on_pass or self._embed_all),
            )

        log.debug("_attach_journal_to_report: erase the journalctl log.")
        run("rm /tmp/journalctl_short.log")

    def _attach_coredump_log_to_report(self, context) -> None:
        """
        Attach coredump log to the html report upon failed test.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`after_scenario`.
        """

        log.debug("_attach_coredump_log_to_report(self, context)")

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            log.debug("No formatter defined.")
            return

        if not self.production:
            log.debug(f"Attribute self.production='{str(self.production)}'.")
            return

        if not (self.attach_coredump or self.attach_coredump_file_check or self._embed_all):
            log.debug(f"Attribute self.attach_coredump='{str(self.attach_coredump)}'.")
            short_crdmp_check = str(self.attach_coredump_file_check)
            log.debug(f"Attribute self.attach_coredump_file_check='{short_crdmp_check}'.")
            return

        if not (self.attach_coredump_on_pass or self.failed_test or self._embed_all):
            log.debug(f"Attribute self.failed_test='{str(self.failed_test)}'.")
            log.debug(f"Attribute self.attach_coredump_on_pass='{str(self.attach_coredump_on_pass)}'.")
            return

        # Get coredump list results only from duration of the test.
        coredump_list = run(f"sudo coredumpctl list --since=@{self.test_execution_start}")

        # If there are no coredumps end right here.
        if "No coredumps found." in coredump_list:
            log.debug("_attach_coredump_log_to_report: No coredumps found.")
            return

        coredump_log = "/tmp/qecore_coredump.log"
        debuginfo_install_log = "/tmp/qecore_debuginfo_install.log"

        # Empty the coredump file logs.
        if os.path.isfile(coredump_log):
            log.debug("_attach_coredump_log_to_report: emptying the coredump log.")
            run(f">{coredump_log}")

        # Do not empty debuginfo log - the content is desired in all possible tests.
        if not os.path.isfile(debuginfo_install_log):
            log.debug("_attach_coredump_log_to_report: creating debuginfo log file.")
            run(f"touch {debuginfo_install_log}")

        # Get packages to be installed from gdb.
        def get_packages_from_coredump(pid) -> Union[str, None]:
            # Get first gdb output and load it to file to parse over.
            run(f"echo 'q' | sudo coredumpctl gdb {pid} 2&> {coredump_log}")

            # Set the base variable to return with all data.
            desired_data = ""

            # Open the file and iterate over its lines.
            with open(coredump_log, "r", encoding="utf-8") as coredump_file:
                # Loading one line at a time.
                next_line = coredump_file.readline()

                # Loop until there is no next line.
                while next_line:
                    # Parse correct lines to fetch debuginfo packages.
                    if "debug" in next_line and "install" in next_line:
                        _, target = next_line.split("install ", 1)
                        desired_data += target.strip("\n") + " "

                    # If there is no coredump file present there si nothing to fetch.
                    elif "Coredump entry has no core attached." in next_line:
                        log.debug("_attach_coredump_log_to_report: coredump entry has no core attached.")
                        return None

                    # Load the next line.
                    next_line = coredump_file.readline()

            return desired_data

        # Install all packages that gdb desires.
        def install_debuginfo_packages(pid) -> None:
            # We need gdb to be installed.
            if "not installed" in run("rpm -q gdb"):
                log.debug("_attach_coredump_log_to_report: installing gdb.")
                run(f"sudo dnf install -y gdb >> {debuginfo_install_log}")

            # Iterate a few times over the gdb to get packages and install them.
            packages_installed_in_last_attempt = ""
            for _ in range(20):
                packages_to_install = get_packages_from_coredump(pid)

                # Install required packages but break if packages were already
                # attempted to be installed.
                if packages_to_install and (
                    packages_to_install != packages_installed_in_last_attempt
                ):
                    packages_installed_in_last_attempt = packages_to_install
                    run(
                        "".join(
                            (
                                "sudo dnf debuginfo-install -y ",
                                f"{packages_to_install} >> {debuginfo_install_log}",
                            )
                        )
                    )
                else:
                    break

        # Load coredump lines as provided.
        list_of_results = coredump_list.rstrip("\n").split("\n")[1:]
        valid_coredump_counter = 0

        for coredump_line in list_of_results:
            starting_time = time.time()

            coredump_line_split = coredump_line.split(" ")
            coredump_line_filtered = [x for x in coredump_line_split if x]
            coredump_pid_to_investigate = coredump_line_filtered[4]

            # Check if coredump file does not exist.
            if coredump_line_filtered[8] == "none":
                # Attach data to html report.
                context.embed(
                    mime_type="text/plain",
                    data=f"Coredump entry '{coredump_pid_to_investigate}' has no core attached.",
                    caption=f"coredump_log_{coredump_pid_to_investigate}_no_core",
                )
                continue

            # Install all debuginfos given by coredump file with found pid.
            install_debuginfo_packages(coredump_pid_to_investigate)

            # All debuginfo packages should be installed now - get the backtrace and
            # attach it to report.
            gdb_command = "thread apply all bt full"
            run(
                "".join(
                    (
                        f"echo '{gdb_command}' | sudo coredumpctl ",
                        f"gdb {coredump_pid_to_investigate} 2&> {coredump_log}",
                    )
                )
            )

            # Calculate the total execution time of coredump fetch.
            coredump_fetch_time = time.time() - starting_time

            valid_coredump_counter += 1
            context.embed(
                mime_type="text/plain",
                data=self.file_loader(coredump_log),
                caption=f"coredump_log_{coredump_pid_to_investigate}+{coredump_fetch_time:.1f}s",
            )

        if valid_coredump_counter != 0:
            context.embed(
                mime_type="text/plain",
                data=self.file_loader(debuginfo_install_log),
                caption="debug_info_install_log",
            )

    def _attach_abrt_link_to_report(self, context) -> None:
        """
        Attach abrt link to the html report upon detected abrt FAF report.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`after_scenario`.
        """

        log.debug("_attach_abrt_link_to_report(self, context)")

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            log.debug("No formatter defined.")
            return

        if not self.production:
            log.debug(f"Attribute self.production='{str(self.production)}'.")
            return

        if not (self.attach_faf or self._embed_all):
            log.debug(f"Attribute self.attach_faf='{str(self.attach_faf)}'.")
            return

        if not (self.attach_faf_on_pass or self.failed_test or self._embed_all):
            log.debug(f"Attribute self.failed_test='{str(self.failed_test)}'.")
            log.debug(f"Attribute self.attach_faf_on_pass='{str(self.attach_faf_on_pass)}'.")
            return

        faf_reports = set()
        faf_reports_data = []

        # There are a few known prefixes for directories.
        abrt_known_directories_identifiers = [
            "oops", "vmcore", "ccpp", "Python", "Java"
        ]

        abrt_directories = run_verbose("sudo ls /var/spool/abrt/")
        log.debug(f" abrt_directories result: '{abrt_directories}'")
        log.debug(f" abrt_directories known prefixes: '{abrt_known_directories_identifiers}'")

        if abrt_directories[1] != 0:
            log.debug(f" abrt_directories return code was non-zero: '{abrt_directories[1]}'")
            return

        # List of direcotries is empty - there is no faf to be processed.
        if abrt_directories[0] == "":
            log.debug(" abrt_directories the directory was empty: no data to be processed.")
            return

        # Utility function to get data from abrt files.
        def _abrt_directory_data_fetch(data_id, file_to_read) -> str:
            # Set default value to use on error.
            abrt_faf_file_data = ""

            # Log what file is getting parsed.
            # Have to check like this since the files will not load with non-root user.
            if run_verbose(f"sudo ls {file_to_read}")[1] != 0:
                log.debug(f"_abrt_directory_data_fetch: no such file '{file_to_read}'")
                return abrt_faf_file_data

            log.debug(f"_abrt_directory_data_fetch: reading file '{file_to_read}'")

            # Cat the file to prevent IO issues.
            abrt_faf_file_run = run_verbose(f"sudo cat '{file_to_read}'")
            if abrt_faf_file_run[1] == 0:
                # Get the data without the end line character.
                abrt_faf_file_data = abrt_faf_file_run[0].strip("\n")
                # Log the data that will be returned.
                log.debug(f" abrt_directories: {data_id} '{abrt_faf_file_data}'.")
            else:
                log.debug(f" abrt_directories: non-zero return code '{abrt_faf_file_run}'")

            # Return the data from file.
            return abrt_faf_file_data

        # Check just the directories that are unique.
        unique_reasons = set()
        unique_faf_directories_to_check = set()

        # Go over all abrt directories and get FAF links with reason.
        log.debug(" abrt_directories: parsing links")
        abrt_directories_as_list = abrt_directories[0].strip("\n").split("\n")
        for abrt_directory in abrt_directories_as_list:

            reason_file = f"/var/spool/abrt/{abrt_directory}/reason"
            reported_to_file = f"/var/spool/abrt/{abrt_directory}/reported_to"

            try:
                abrt_faf_reason = _abrt_directory_data_fetch("reason", reason_file)

                # If the reason is unique mark the directory to pull data from it later.
                if abrt_faf_reason and (abrt_faf_reason not in unique_reasons):
                    unique_faf_directories_to_check.add(abrt_directory)
                    # Keeping the list of unique reasons.
                    unique_reasons.add(abrt_faf_reason)

                abrt_faf_reported_to = _abrt_directory_data_fetch("reported_to", reported_to_file)

                # Hyperlink needs a little bit of extra parsing.
                abrt_faf_lines = abrt_faf_reported_to.split("ABRT Server: URL=")[-1]
                abrt_faf_hyperlink = abrt_faf_lines.split("\n")[0]

                # Success condition for link is a reason it failed and hyperlink present.
                if abrt_faf_reason and abrt_faf_hyperlink:
                    data_to_insert = (abrt_faf_hyperlink, f"Reason: {abrt_faf_reason}")
                    faf_reports.add(data_to_insert)

            except Exception as error:  # pylint: disable=broad-except
                log.debug(f" abrt_directories: Exception caught: {error}'")

        # Embed the links.
        log.debug("_attach_abrt_link_to_report: Attempting to embed FAF links.")
        if faf_reports:
            context.embed(
                "link",
                faf_reports,
                caption="FAF reports",
                fail_only=not (self.attach_faf_on_pass or self._embed_all),
            )

        # Pull all the data only from unique directories.
        log.debug(f" abrt_directories: parsing data in {unique_faf_directories_to_check}")
        for unique_faf_directory in unique_faf_directories_to_check:
            # Main data to pull.
            cmdline_file = f"/var/spool/abrt/{unique_faf_directory}/cmdline"
            backtrace_file = f"/var/spool/abrt/{unique_faf_directory}/backtrace"
            component_file = f"/var/spool/abrt/{unique_faf_directory}/component"
            # Pull the reason and reported again to have the proper logs on fail.
            reason_file = f"/var/spool/abrt/{unique_faf_directory}/reason"
            reported_to_file = f"/var/spool/abrt/{unique_faf_directory}/reported_to"

            # Handle parts one by one to make sure any error is shown in logs.
            try:
                abrt_faf_cmdline = _abrt_directory_data_fetch("cmdline", cmdline_file)
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_cmdline = error

            try:
                abrt_faf_backtrace = _abrt_directory_data_fetch("backtrace", backtrace_file)
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_backtrace = error

            try:
                abrt_faf_component = _abrt_directory_data_fetch("component", component_file)
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_component = error

            try:
                abrt_faf_reason = _abrt_directory_data_fetch("reason", reason_file)
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_reason = error

            try:
                abrt_faf_reported_to = _abrt_directory_data_fetch("reported_to", reported_to_file)

                # Hyperlink needs a little bit of extra parsing.
                abrt_faf_lines = abrt_faf_reported_to.split("ABRT Server: URL=")[-1]
                abrt_faf_hyperlink = abrt_faf_lines.split("\n")[0]
            except Exception as error:  # pylint: disable=broad-except
                abrt_faf_hyperlink = error

            # Adding visual spacer only after the first entry.
            if len(faf_reports_data) == 0:
                visual_spacer = ""
            else:
                visual_spacer = "=" * 80 + "\n"

            faf_reports_data.append(
                (
                    visual_spacer,
                    f"<h4>ABRT component:</h4> {abrt_faf_component}\n",
                    f"<h4>ABRT reason:</h4> {abrt_faf_reason}\n",
                    f"<h4>ABRT reported_to:</h4> {abrt_faf_hyperlink}\n",
                    f"<h4>ABRT cmdline:</h4> {abrt_faf_cmdline}\n",
                    f"<h4>ABRT backtrace:</h4> {abrt_faf_backtrace}\n",
                )
            )

        # Embed the data
        log.debug("_attach_abrt_link_to_report: Attempting to embed FAF data.")

        # Formatting data to respect html tags and local string format.
        formatted_data = ""
        for data_entry in faf_reports_data:
            formatted_data += "".join(data_entry)

        if faf_reports_data:
            context.embed(
                "text/html",
                formatted_data,
                "FAF reports data",
            )

    def _attach_version_status_to_report(self, context) -> None:
        """
        Process status report - this will attach version of many components needed for
        correct function.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`after_scenario`.
        """

        log.debug("_attach_version_status_to_report(self, context)")

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            log.debug("No formatter defined.")
            return

        cached_versions_file = "/tmp/qecore_version_status.txt"

        if self.status_report and self._new_log_indicator:
            # If there are no cache to be kept, delete the file with data and create new.
            if self._no_cache:
                run(f"sudo rm -rf {cached_versions_file}")
                # Just in case to prevent race conditions.
                sleep(0.1)

            # If the cached file exists attach it.
            if os.path.isfile(cached_versions_file):
                context.embed(
                    "text/plain",
                    data=self.file_loader(cached_versions_file),
                    caption="Status",
                    fail_only=False,
                )
                return

            status_data = "Versions used in testing:\n"

            # Iterate over components and get package version.
            for component in self.package_list:

                # Handling gnome-shell differently to prevent flooding the Status log
                # with extensions.
                if component == "gnome-shell":
                    component_rpm = run(f"rpm -q '{component}'")

                # Get a name for rpm version check, we want other components to list
                # all parts.
                else:
                    component_rpm = run(f"rpm -qa | grep '{component}'")

                status_data += "\n".join(
                    (
                        f"\nComponent: '{component}'",
                        f"{component_rpm}",
                    )
                )

            # Import version from module.
            try:
                qecore_version = pkg_resources.require("qecore")[0].version
            except ImportError as error:
                qecore_version = f"__qecore_version_unavailable__: '{error}'"

            # Import version from module.
            try:
                behave_version = pkg_resources.require("behave")[0].version
            except ImportError as error:
                behave_version = f"__behave_version_unavailable__: '{error}'"

            # Import version from module.
            try:
                behave_html_formatter_version = pkg_resources.require(
                    "behave_html_formatter"
                )[0].version
            except ImportError as error:
                behave_html_formatter_version = f"__formatter_version_unavailable__: '{error}'"

            # Import version from module.
            try:
                behave_html_pretty_formatter_version = pkg_resources.require(
                    "behave_html_pretty_formatter"
                )[0].version
            except ImportError as error:
                behave_html_pretty_formatter_version = f"__formatter_version_unavailable__: '{error}'"

            # Get dogtial rpm version.
            dogtail_rpm = run("rpm -qa | grep dogtail")

            # Join the data from modules and dogtail rpm.
            status_data += "\n".join(
                (
                    "\nVersions from modules:",
                    f"qecore: '{qecore_version}'",
                    f"behave: '{behave_version}'",
                    f"behave_html_formatter: '{behave_html_formatter_version}'",
                    f"behave_html_pretty_formatter: '{behave_html_pretty_formatter_version}'",
                    f"dogtail: \n{dogtail_rpm}",
                )
            )

            # Embed the data to the report.
            with open(cached_versions_file, "w+", encoding="utf-8") as _cache_file:
                _cache_file.write(status_data)

            context.embed("text/plain", status_data, caption="Status", fail_only=False)

    def _process_after_scenario_hooks(self, context) -> None:
        """
        Process attached after_scenario_hooks.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`after_scenario`.
        """

        log.debug("_process_after_scenario_hooks(self, context)")

        hook_errors = ""

        if self.reverse_after_scenario_hooks:
            log.debug(" reversing _after_scenario_hooks")
            self._after_scenario_hooks.reverse()

        log.debug(f" processing {len(self._after_scenario_hooks)} hooks")

        for callback, args, kwargs in self._after_scenario_hooks:
            try:
                callback(*args, **kwargs)
            except Exception as error:  # pylint: disable=broad-except
                error_trace = traceback.format_exc()
                hook_errors += "\n\n" + error_trace
                context.embed(
                    "text/plain",
                    f"Hook Error: {error}\n{error_trace}",
                    caption="Hook Error",
                )

        self._after_scenario_hooks = []

        assert not hook_errors, "".join(
            f"Exceptions during after_scenario hook:{hook_errors}"
        )

    def _process_embeds(self, context) -> None:
        """
        Process posponed embeds (with myme_type="call" or fail_only=True).

        :type context: <behave.runner.Context>
        :param context: Passed object.

        :type scenario: <behave.model.Scenario>
        :param scenario: Passed object.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`after_scenario`.
        """

        log.debug("_process_embeds(self, context)")

        scenario_fail = self.failed_test or self._embed_all

        embeds = getattr(context, "_to_embed", [])
        log.debug(f" process {len(embeds)} embeds")

        for kwargs in embeds:
            # Execute postponed "call"s.
            if kwargs["mime_type"] == "call":
                # "data" is function, "caption" is args, function returns triple.
                mime_type, data, caption = kwargs["data"](*kwargs["caption"])
                kwargs["mime_type"], kwargs["data"], kwargs["caption"] = (
                    mime_type,
                    data,
                    caption,
                )
            # skip "fail_only" when scenario passed
            if not scenario_fail and kwargs["fail_only"]:
                continue
            # Reset "fail_only" to prevent loop.
            kwargs["fail_only"] = False
            context.embed(**kwargs)
        context._to_embed = []  # pylint: disable=protected-access

    def _html_report_links(self, context) -> None:
        """
        Fetch a tag link to the git repository in current commit.

        :type context: <behave.runner.Context>
        :param context: Passed object.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`after_scenario`.
        """

        log.debug("_html_report_links(self, context)")

        # Running this function makes sense only when formatter is defined.
        if context.html_formatter is None:
            log.debug("No formatter defined.")
            return

        git_url = self.project_git_url
        git_commit = self.project_git_commit
        if not git_url or not git_commit:
            log.debug("The git_url or git_commit is not valid.")
            return

        project_url_base = f"{git_url}/-/tree/{git_commit}/"
        qecore_url_base = "/".join(
            ("https://gitlab.com", "dogtail/qecore/-/tree/master/qecore/")
        )
        nmci_url_base = "/".join(
            (
                "https://gitlab.freedesktop.org",
                "NetworkManager/NetworkManager-ci/-/tree/master/",
            )
        )

        # This will return an instance of PrettyHTMLFormatter.
        formatter_instance = getattr(context, "html_formatter", None)

        # If no instance was given end the handling.
        if formatter_instance is None:
            log.debug("No instance of formatter found.")
            return

        # Formatter html handling.
        if formatter_instance.name == "html":
            log.debug("Handling 'html' formatter.")

            # Search for links in scenario HTML element.
            scenario_el = getattr(formatter_instance, "scenario_el", None)
            if scenario_el is None:
                log.debug("Formatter instance has no scenario_el attribute.")
                return

            scenario_file = scenario_el.find(".//span[@class='scenario_file']")
            step_files = scenario_el.findall(".//div[@class='step_file']/span")
            tags_el = scenario_el.find(".//span[@class='tag']")

            # Link tags to scenario (.feature file).
            if tags_el is not None:
                tags = tags_el.text.split()
                tags.reverse()
                tags_el.text = ""
                scenario_name = True

                for tag in tags:
                    if tag.startswith("@rhbz"):
                        bug_id = tag.replace("@rhbz", "").rstrip(",")
                        link_el = ET.Element(
                            "a",
                            {
                                "href": "https://bugzilla.redhat.com/" + bug_id,
                                "target": "_blank",
                                "style": "color:inherit",
                            },
                        )
                        link_el.text = tag
                        tags_el.insert(0, link_el)

                    elif scenario_name:
                        scenario_name = False
                        if scenario_file is not None:
                            file_name, line = scenario_file.text.split(":", 2)
                            link_el = ET.Element(
                                "a",
                                {
                                    "href": project_url_base + file_name + "#L" + line,
                                    "target": "_blank",
                                    "style": "color:inherit",
                                },
                            )
                            link_el.text = tag
                            tags_el.insert(0, link_el)

                    else:
                        span_el = ET.Element("span")
                        span_el.text = tag
                        tags_el.insert(0, span_el)

            # Link files.
            for file_el in [scenario_file] + step_files:
                if file_el is not None and ":" in file_el.text:
                    file_name, line = file_el.text.split(":", 2)
                    if file_name.startswith("NMci"):
                        url = nmci_url_base + file_name.replace("NMci/", "", 1)

                    elif "/site-packages/qecore/" in file_name:
                        url = (
                            qecore_url_base
                            + file_name.split("/site-packages/qecore/")[-1]
                        )

                    else:
                        url = project_url_base + file_name

                    link = ET.SubElement(
                        file_el,
                        "a",
                        {
                            "href": url + "#L" + line,
                            "target": "_blank",
                            "style": "color:inherit",
                        },
                    )
                    link.text = file_el.text
                    file_el.text = ""

        # Formatter html-pretty handling.
        if formatter_instance.name == "html-pretty":
            log.debug("Handling 'html-pretty' formatter.")

            # Iterate over the data we have and change links where necessary.
            for feature in formatter_instance.features:
                for scenario in feature.scenarios:
                    # Iterate over all tags.
                    for tag in scenario.tags:
                        # Tag class has attributes behave_tag and link
                        # The tag becomes link only after this setup, the default on
                        # formatters' side is <span>.

                        # If the tag.link is not None, it was modified already,
                        # skip another attempt to modify it to link.
                        if tag.has_link():
                            break

                        # Either it becomes a link to bugzilla or link to git.
                        if tag.behave_tag.startswith("rhbz"):
                            # Exctract just the number from th @rhbz tag so we can link
                            # it to bugzilla.
                            bug_id = tag.behave_tag.replace("rhbz", "").rstrip(",")
                            bug_link = "https://bugzilla.redhat.com/" + bug_id

                            # Tag becomes link to bugzilla.
                            tag.set_link(bug_link)

                        # No reason to not attempt to do link every single
                        # time, everything should be on git.
                        else:
                            # Tag becomes link to git project.
                            # If the tag was normalized for Outline as a string, use
                            # the scenario location line.
                            if isinstance(tag.behave_tag, str):
                                tag.set_link(
                                    project_url_base
                                    + scenario.location.filename
                                    + "#L"
                                    + str(scenario.location.line)
                                )
                            else:
                                tag.set_link(
                                    project_url_base
                                    + scenario.location.filename
                                    + "#L"
                                    + str(tag.behave_tag.line)
                                )

                    # Iterate once over all steps to make links to its location.
                    for step in scenario.steps:
                        # Iterate over it only in case it was not set yet and
                        # the location exists.
                        if not step.location_link and step.location:
                            # Split the location to file_name and line number
                            # so we can shape it.
                            file_name, line = step.location.split(":", 2)
                            # Handling for NMci project.
                            if file_name.startswith("NMci"):
                                url = nmci_url_base + file_name.replace("NMci/", "", 1)
                            # Handling for qecore project.
                            elif "/site-packages/qecore/" in file_name:
                                url = (
                                    qecore_url_base
                                    + file_name.split("/site-packages/qecore/")[-1]
                                )
                            # Handling for all other projects.
                            else:
                                url = project_url_base + file_name

                            # Set the actual link so formatter can use it.
                            step.location_link = url + "#L" + line

    @property
    def project_git_url(self) -> str:
        """
        Property that returns git url of the project.

        :return: String with the git url.
        :rtype: str
        """

        remote = getattr(self, "_project_git_url", None)
        if remote is None:
            remote, return_code, _ = run_verbose("sudo git config --get remote.origin.url")
            remote = remote.strip("\n")[:-4]

            if return_code != 0:
                remote = ""

            elif remote.startswith("git@"):
                remote = remote.replace(":", "/").replace("git@", "https://")

            self._project_git_url = remote

        log.debug(f"The project_git_url property is returning '{str(remote)}'")
        return remote

    @property
    def project_git_commit(self) -> str:
        """
        Property that returns git commit of the project.

        :return: String with the git url.
        :rtype: str
        """

        commit = getattr(self, "_project_git_commit", None)
        if commit is None:
            commit, return_code, _ = run_verbose("sudo git rev-parse HEAD")
            commit = commit.strip("\n")

            if return_code != 0:
                commit = ""

            self._project_git_commit = commit

        log.debug(f"The project_git_commit property is returning '{str(commit)}'")
        return commit

    def _wait_for_video_encoding(self, file_name) -> None:
        """
        Wait until the video is fully encoded.
        This is verified by video's changing size.
        Once the file is encoded the size will not change anymore.

        :type file_name: str
        :param file_name: Video location for size verification.

        .. note::

            Do **NOT** call this by yourself.
            This method is called by :func:`attach_video_to_report`.

        This fixes some issues with the video and most of the time the video will
        get passed with all data, in the testing this took between 2-5 seconds.
        But there still are situations when the encoding is not made in the trivial amount of time
        mostly on slower machines. Currently the hard cutoff is 60 seconds after that the wait will
        terminate and the video will get passed as is to the html report.

        This time loss is no issue with few failing tests and has huge advantage of
        having an entire video with all controling elements (sometimes the video cannot be moved
        to the middle, or does not have data abouts its length). With many failing tests this might
        add significant time to the testing time. To prevent waiting for the encoded video
        and therefore not waiting at all use::

            <qecore.sandbox.TestSandbox>.wait_for_stable_video = False
        """

        log.debug(f"_wait_for_video_encoding(self, file_name={file_name})")

        current_size = 0
        current_stability = 0

        iteration_cutoff = 0

        while current_stability < 30:
            new_size = os.path.getsize(file_name)
            if current_size == new_size:
                current_stability += 1
            else:
                current_stability = 0

            current_size = new_size
            sleep(0.1)

            iteration_cutoff += 1
            if iteration_cutoff > 600:
                break

        log.debug(f"The stability counter: '{current_stability}")
        log.debug(f"The iteration cutoff: '{iteration_cutoff}'")

    def set_background(
        self, color="", background_image=None, background_image_revert=False
    ) -> None:
        """
        Change background to a single color or an image.

        :type color: str
        :param color: String black/white to set as background color.

        :type background_image: str
        :param background_image: Image location to be set as background.

        :type background_image_revert: bool
        :param background_image_revert: Upon settings this attribute to True,
            the :func:`after_scenario` will return the background to the original state,
            after the test.

        To get the wanted color you can pass strings as follows::

            color="black"
            color="white"
            color="#FFFFFF" # or any other color represented by hexadecimal
        """

        log.debug(
            "".join(
                (
                    f"set_background(self, color={color}, ",
                    f"background_image={background_image}).",
                )
            )
        )

        self.background_image_revert = background_image_revert

        if self.background_image_revert:
            self.background_image_location = run(
                "gsettings get org.gnome.desktop.background picture-uri"
            ).strip("\n")

        if background_image:
            if "file://" in background_image:
                run(f"gsettings set org.gnome.desktop.background picture-uri {background_image}")
            else:
                run(
                    "".join(
                        (
                            "gsettings set org.gnome.desktop.background ",
                            f"picture-uri file://{background_image}",
                        )
                    )
                )
        elif color == "white":
            run("gsettings set org.gnome.desktop.background picture-uri file://")
            run('gsettings set org.gnome.desktop.background primary-color "#FFFFFF"')
            run('gsettings set org.gnome.desktop.background secondary-color "#FFFFFF"')
            run('gsettings set org.gnome.desktop.background color-shading-type "solid"')
        elif color == "black":
            run("gsettings set org.gnome.desktop.background picture-uri file://")
            run('gsettings set org.gnome.desktop.background primary-color "#000000"')
            run('gsettings set org.gnome.desktop.background secondary-color "#000000"')
            run('gsettings set org.gnome.desktop.background color-shading-type "solid"')
        elif "#" in color:
            run("gsettings set org.gnome.desktop.background picture-uri file://")
            run(f"gsettings set org.gnome.desktop.background primary-color '{color}'")
            run(f"gsettings set org.gnome.desktop.background secondary-color '{color}'")
            run('gsettings set org.gnome.desktop.background color-shading-type "solid"')
        else:
            log.debug(
                " ".join(
                    (
                        f"Color '{color}' is not defined.",
                        "You can define one yourself and submit merge request.",
                    )
                )
            )

    def _revert_background_image(self) -> None:
        """
        Revert background image to the before-test state.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`after_scenario`.
        """

        log.debug("_revert_background_image(self)")

        run(
            " ".join(
                (
                    "gsettings",
                    "set",
                    "org.gnome.desktop.background",
                    "picture-uri",
                    self.background_image_location,
                )
            )
        )

    def file_loader(self, file_name) -> str:
        """
        Load content from file or upon UnicodeDecodeError debug the location
        of the error and return replaced data.

        :type file_name: str
        :param file_name: String representation of file location.

        :rtype: str
        :return: File data or some debug data and file content replaced in places that
            were not readable.
        """

        log.debug(f"file_loader(self, file_name={file_name})")

        _file_data = ""
        if not os.path.isfile(file_name):
            log.debug("file_loader: File does not exist.")

            return "File does not exist."

        log.debug("file_loader: File exists, continuing to read.")

        try:
            _file_data = open(file_name, "r", encoding="utf-8").read()
            log.debug("file_loader: File read is successful.")

        except UnicodeDecodeError as error:
            log.debug("file_loader: File read is NOT successful.")

            # Gather all lines that contain non-ASCII characters.
            _file = open(file_name, "rb")
            non_ascii_lines = [
                line for line in _file if any(_byte > 127 for _byte in line)
            ]
            _file.close()

            # Attempt to load the file and replace all error data.
            file_content = open(
                file_name, "r", encoding="utf-8", errors="replace"
            ).read()

            _file_data = f"\nException detected:\n{error}"
            _file_data += (
                f"\nDetected non-ASCII lines:\n{non_ascii_lines}"
                if any(non_ascii_lines)
                else "None"
            )
            _file_data += f"\nReplaced file content:\n{file_content}"

        log.debug("file_loader: return _file_data.")

        return _file_data

    def _attach_qecore_debug_log(self, context) -> None:
        log.debug("_attach_qecore_debug_log: Attaching debug log to the html report.")

        if not (self._attach_qecore_debug or self._embed_all):
            log.debug(f"Attribute self._attach_qecore_debug={self._attach_qecore_debug}.",)
            return

        if not (
            self._attach_qecore_debug_on_pass or self.failed_test or self._embed_all
        ):
            log.debug(
                "".join(
                    (
                        f"Attribute self.failed_test={self._attach_qecore_debug}.",
                        "Attribute self._attach_qecore_debug_on_pass=",
                        f"'{str(self._attach_qecore_debug_on_pass)}'.",
                    )
                )
            )
            return

        # Attach this log only once.
        if self._new_log_indicator:
            # If the file is not there, the content will be name of the file.
            # In such case do not embed at all.
            if os.path.isfile(self._qecore_debug_log_file):
                context.embed("text", self._qecore_debug_log_file, "qecore_debug_log")
            else:
                log.debug("_attach_qecore_debug_log: no file to attach.")

    def enable_logging_to_console(self) -> None:
        """
        Enable logging to console after sandbox is initiated.
        """

        log.info("enable_logging_to_console: Setting qecore to log in console.")
        logging_class.qecore_debug_to_console()
