from mock import patch

from PyQt4.QtGui import QApplication

from ..glue_application import GlueApplication


def tab_count(app):
    return app.tab_bar.count()


def setup_module(module):
    module.app = QApplication([''])


def teardown_module(module):
    del module.app


class TestGlueApplication(object):

    def setup_method(self, method):
        self.app = GlueApplication()

    def teardown_method(self, method):
        self.app.close()
        del self.app

    def test_new_tabs(self):
        t0 = tab_count(self.app)
        self.app._new_tab()
        assert tab_count(self.app) == t0 + 1

    def test_save_session_pickle_error(self):
        from pickle import PicklingError
        with patch('glue.core.glue_pickle.dumps') as dumps:
            with patch('glue.qt.glue_application.QMessageBox') as mb:
                dumps.side_effect = PicklingError
                self.app._save_session()
                assert mb.critical.call_count == 1

    def test_save_session_no_file(self):
        """shouldnt try to save file if no file name provided"""
        with patch('glue.core.glue_pickle.dumps') as dumps:
            dumps.return_value = ''
            with patch('glue.qt.glue_application.QFileDialog') as fd:
                fd.getSaveFileName.return_value = ''
                # crashes if open called on null string
                self.app._save_session()

    def test_save_session_ioerror(self):
        """should show box on ioerror"""
        with patch('glue.qt.glue_application.QFileDialog') as fd:
            # can't write, raises IOError. Dangerous hack!
            fd.getSaveFileName.return_value = '/_junk'
            with patch('glue.qt.glue_application.QMessageBox') as mb:
                self.app._save_session()
                assert mb.critical.call_count == 1