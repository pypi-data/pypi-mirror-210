import sys
from time import sleep


def run(practicus_app=None):
    """
    Starts Practicus AI GUI Application.
    :return: None
    """
    run_(practicus_app)
    try:
        # doing this since QT apps don't quit properly in IPython/Jupyter notebooks
        exec("import IPython; app = IPython.Application.instance(); app.kernel.do_shutdown(True); "
             "debug_pid('Re-starting Jupyter kernel..')")
    except:
        pass


def run_(practicus_app=None):
    """
    Starts Practicus AI GUI Application.
    :return: True if successful, otherwise False
    """
    if practicus_app is None:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QEvent

        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView  # needs to be imported before creating app, if web browsing is enabled
        except:
            print("Embedded web browser not available, will use external browser")

        try:
            import practicus.resources_rc
        except:
            print("Could not import resources, icons will not be visible", file=sys.stderr)

        class PRTApp(QApplication):
            def __init__(self, terminal_args):
                # THIS CLASS IS REPLICATED
                # We had to create a QT app *before* most of our code kicks-in since pyinstaller frozen app start errors cause
                # macOS .app to crash (without proper explanation). We want to create the QT app as early as possible
                super().__init__(terminal_args)
                self.open_file_event_list = []

            def event(self, a0: QEvent) -> bool:
                # macOS does not pass right click + open with as argv. pyinstaller argv_emulation did not work
                # Qt successfully catches these and fires the event handler
                try:
                    if a0.type() == QEvent.Type.FileOpen:
                        # from PyQt6.QtGui import QFileOpenEvent
                        # a0 = cast(QFileOpenEvent, a0)
                        # noinspection PyUnresolvedReferences
                        self.open_file_event_list.append(a0.file())
                except Exception as ex2:
                    print("Could not process QT event. ", ex2)
                return super().event(a0)

        practicus_app = PRTApp(terminal_args=sys.argv)

    log_manager_glbl = None
    try:
        from practicus.app_starter import AppStarter

        from practicuscore.core_conf import log_manager_glbl
        from practicus.app_conf import app_conf_glbl
        from practicus.shared import AppDef

        if AppStarter.is_frozen():
            pkg_or_lib = "packaged app"
        else:
            pkg_or_lib = "practicus library"

        _ = app_conf_glbl  # this needs to be imported to make sure logging config is also loaded
        logger = log_manager_glbl.get_logger()
        logger.info("Starting Practicus AI GUI App v%s (Python %s.%s.%s, running from %s)"
                    % (AppDef.APP_VERSION, sys.version_info.major, sys.version_info.minor, sys.version_info.micro,
                       pkg_or_lib))

        AppStarter.verify_create_folders()

        app_starter = AppStarter(practicus_app)
        app_starter.start()

        logger.debug("Running clean-up tasks to shutdown Practicus AI GUI App..")
        # app_starter.main_window.destroy()  # this started causing issues after Qt6 + web page tab opened. removing
        app_starter.main_window.run_shutdown_cleanup_tasks()
        logger.info("Shutting down..\n\n")
        sleep(1)
        app_starter.app.quit()
        sys.exit(0)
    except Exception as ex:
        try:
            import traceback
            trace = str(traceback.format_exc())
        except:
            trace = ""

        err_msg = "An error occurred while starting Practicus AI App. " \
                  "Please consider the below if you the issue persists.\n" \
                  "1) Reinstall the application\n" \
                  "2) If you are using your own Python deployment, create a new virtual environment.\n" \
                  "3) Backup and then delete the hidden .practicus folder in your home directory.\n\n" \
                  "%s: %s" % (ex.__class__.__name__, ex)

        try:
            print(err_msg, file=sys.stderr)
            if trace:
                print(trace, file=sys.stderr)
        except:
            print(err_msg)

        try:
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox()
            msg_box.setText(err_msg)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            if trace:
                msg_box.setDetailedText(trace)
            msg_box.exec()
        except:
            try:
                from PyQt6.QtWidgets import QMessageBox
                msg_box = QMessageBox()
                msg_box.setText(err_msg)
                msg_box.setIcon(QMessageBox.Icon.Critical)
                if trace:
                    msg_box.setDetailedText(trace)
                msg_box.exec()
            except:
                pass

        try:
            if log_manager_glbl is not None:
                logger = log_manager_glbl.get_logger()
                logger.error(err_msg, exc_info=True)
        except:
            pass

    finally:
        try:
            del app_starter
        except:
            pass


try:
    from practicus.shared import AppDef
    __version__ = AppDef.APP_VERSION
except:
    __version__ = "0.0.0"


if __name__ == '__main__':
    run_()
