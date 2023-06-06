import datetime
import os
import tkinter as tk

import unittest

from src.application import Application
from src.utils import get_init_dir

import pycodestyle


class PEP8TestCase(unittest.TestCase):
    def test_pep8_compliance(self):
        files = [
            'main.py',
            './src/application.py',
            './src/constants.py',
            './src/utils.py',
            './src/windows/cookies.py',
            './src/windows/debug.py',
            './src/windows/proxy.py',
            './tests_package/run_tests.py'
        ]
        style_guide = pycodestyle.StyleGuide()
        result = style_guide.check_files(files)
        self.assertEqual(
            result.total_errors,
            0,
            f"PEP 8 violations found: {result.total_errors}"
        )


class EntryApplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def tearDown(self):
        self.app.destroy()

    def test_start_text_input_download(self):
        state = self.app.input_download.cget('state')
        self.assertEqual("normal", str(state))
        self.assertEqual("http://", self.app.text_input_download.get())

    def test_start_path_download(self):
        state = self.app.input_path.cget('state')
        self.assertEqual("normal", str(state))
        self.assertEqual(get_init_dir(), self.app.path_download.get())

    def test_start_path_upload(self):
        state = self.app.input_upload.cget('state')
        self.assertEqual('normal', str(state))
        self.assertEqual(get_init_dir(), self.app.path_upload.get())

    def test_start_speedlimit(self):
        state = self.app.input_speedlimit.cget('state')
        self.assertEqual('normal', str(state))
        self.assertEqual('', self.app.input_speedlimit.get())

    def test_start_username(self):
        state = self.app.input_username.cget('state')
        self.assertEqual('normal', str(state))
        self.assertEqual('', self.app.input_username.get())

    def test_start_password(self):
        state = self.app.input_password.cget('state')
        self.assertEqual('normal', str(state))
        self.assertEqual('', self.app.input_password.get())

    def test_start_customuseragent(self):
        state = self.app.input_customuseragent.cget('state')
        self.assertEqual("disabled", str(state))
        self.assertEqual("", self.app.input_customuseragent.get())


class EntryDebugTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def tearDown(self):
        self.app.destroy()

    def test_start_text_cookies(self):
        text_state = self.app.window_debug.text_logs.cget('state')
        self.assertEqual("disabled", text_state)

        self.assertEqual(
            self.app.window_debug.text_logs.get("1.0", tk.END),
            "\n"
        )


class EntryCookiesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def tearDown(self):
        self.app.destroy()

    def test_start_text_cookies(self):
        state = self.app.window_cookies.text_cookies.cget('state')
        self.assertEqual('normal', state)

        self.assertEqual(
            self.app.window_cookies.text_cookies.get("1.0", tk.END),
            "\n"
        )


class EntryProxyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def tearDown(self):
        self.app.destroy()

    def test_start_hostname(self):
        state = self.app.window_proxy.input_hostname.cget('state')
        self.assertEqual('normal', str(state))
        self.assertEqual('', self.app.window_proxy.input_hostname.get())

    def test_start_port(self):
        state = self.app.window_proxy.input_port.cget('state')
        self.assertEqual('normal', str(state))
        self.assertEqual('', self.app.window_proxy.input_port.get())

    def test_start_username(self):
        state = self.app.window_proxy.input_username.cget('state')
        self.assertEqual('normal', str(state))
        self.assertEqual('', self.app.window_proxy.input_username.get())

    def test_start_password(self):
        state = self.app.window_proxy.input_password.cget('state')
        self.assertEqual('normal', str(state))
        self.assertEqual(self.app.window_proxy.input_password.get(), "")


class ButtonApplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def tearDown(self):
        self.app.destroy()

    def test_button_debugmode(self):
        window_state = self.app.window_debug.state()
        self.assertEqual("withdrawn", window_state)

        self.app.button_debug.invoke()

        window_state = self.app.window_debug.state()
        self.assertEqual("normal", window_state)

    def test_button_proxy(self):
        button_state = self.app.button_proxy.state()[0]
        self.assertEqual("disabled", button_state)

        proxy_state = self.app.proxy.get()
        self.assertEqual(False, proxy_state)

        window_state = self.app.window_proxy.state()
        self.assertEqual("withdrawn", window_state)
        self.app.button_proxy.invoke()
        window_state = self.app.window_proxy.state()
        self.assertEqual("withdrawn", window_state)

        self.app.checkbutton_enable_proxy.invoke()
        proxy_state = self.app.proxy.get()
        self.assertEqual(True, proxy_state)

        button_state = self.app.button_proxy.cget('state')
        self.assertEqual('normal', str(button_state))

        self.app.button_proxy.invoke()
        window_state = self.app.window_proxy.state()
        self.assertEqual("normal", window_state)

    def test_button_cookies(self):
        window_state = self.app.window_cookies.state()
        self.assertEqual("withdrawn", window_state)

        self.app.button_cookies.invoke()

        window_state = self.app.window_cookies.state()
        self.assertEqual("normal", window_state)

    def test_button_download(self):
        self.app.text_input_download.set("http://google.com")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_info = mock_messagebox

        self.app.button_download.invoke()
        self.assertEqual(True, messagebox_shown[0])

        filename = get_init_dir() + '/google.com'
        os.remove(filename)

    def test_button_upload(self):
        filename = get_init_dir() + '/sometestname'
        with open(filename, 'w') as f:
            f.write("sometesttext")

        self.app.path_upload.set(filename)

        self.app.text_input_download.set("http://google.com/")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_info = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

        filename = get_init_dir() + '/sometestname'
        os.remove(filename)


class BadSituationsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def tearDown(self):
        self.app.destroy()

    def test_download_bad_folder(self):
        self.app.text_input_download.set("http://google.com")

        folder = get_init_dir() + "/somefolder/someonemoreunknownfolder"
        self.app.path_download.set(folder)

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_download.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_upload_bad_file(self):
        self.app.text_input_download.set("http://google.com")

        filename = get_init_dir() + "/someunknownfilekekerslol.exe"
        self.app.path_upload.set(filename)

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_download_empty_url(self):
        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_download.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_upload_empty_url(self):
        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_download_empty_path(self):
        self.app.path_download.set("")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_download.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_upload_empty_path(self):
        self.app.path_upload.set("")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_download_bad_speedlimit_negative(self):
        self.app.text_input_download.set("http://google.com")
        self.app.input_speedlimit.insert(0, '-1')

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_download.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_download_bad_speedlimit_letters(self):
        self.app.text_input_download.set("http://google.com")
        self.app.input_speedlimit.insert(0, 'test')

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_download.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_upload_bad_speedlimit_number(self):
        self.app.text_input_download.set("http://google.com")
        self.app.input_speedlimit.insert(0, '-1')

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_upload_bad_speedlimit_letter(self):
        self.app.text_input_download.set("http://google.com")
        self.app.input_speedlimit.insert(0, 'test')

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_download_empty_customuseragent(self):
        self.app.text_input_download.set("http://google.com")
        self.app.combobox_useragent.current(11)
        self.app.combobox_useragent.event_generate("<<ComboboxSelected>>")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_download.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_upload_empty_customuseragent(self):
        self.app.text_input_download.set("http://google.com")
        self.app.combobox_useragent.current(11)
        self.app.combobox_useragent.event_generate("<<ComboboxSelected>>")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_download_bad_proxy_only_hostname(self):
        self.app.text_input_download.set("http://google.com")
        self.app.checkbutton_enable_proxy.invoke()
        self.app.window_proxy.input_hostname.insert(tk.END, "testuser")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_download.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_download_bad_proxy_only_port(self):
        self.app.text_input_download.set("http://google.com")
        self.app.checkbutton_enable_proxy.invoke()
        self.app.window_proxy.input_port.insert(tk.END, "12345")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_download.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_download_bad_proxy_full_empty(self):
        self.app.text_input_download.set("http://google.com")
        self.app.checkbutton_enable_proxy.invoke()

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_upload_bad_proxy_only_hostname(self):
        self.app.text_input_download.set("http://google.com")
        self.app.checkbutton_enable_proxy.invoke()
        self.app.window_proxy.input_hostname.insert(tk.END, "testuser")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_upload_bad_proxy_only_port(self):
        self.app.text_input_download.set("http://google.com")
        self.app.checkbutton_enable_proxy.invoke()
        self.app.window_proxy.input_port.insert(tk.END, "12345")

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])

    def test_upload_bad_proxy_full_empty(self):
        self.app.text_input_download.set("http://google.com")
        self.app.checkbutton_enable_proxy.invoke()

        def mock_messagebox(_):
            messagebox_shown[0] = True

        messagebox_shown = [False]

        self.app.show_error = mock_messagebox

        self.app.button_upload.invoke()
        self.assertEqual(True, messagebox_shown[0])


class ButtonDebugTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def tearDown(self):
        self.app.destroy()

    def test_start_checkbutton_verbose(self):
        check_verbose = self.app.verbose.get()
        self.assertEqual(False, check_verbose)

        self.app.window_debug.checkbutton_verbose.invoke()

        check_verbose = self.app.verbose.get()
        self.assertEqual(True, check_verbose)

    def test_button_clear_logs(self):
        self.app.window_debug.text_logs.config(state=tk.NORMAL)
        self.app.window_debug.text_logs.insert(tk.END, "teststring")
        self.app.window_debug.text_logs.see(tk.END)
        self.app.window_debug.text_logs.config(state=tk.DISABLED)

        check_text = self.app.window_debug.text_logs.get("1.0", tk.END)
        self.assertEqual("teststring\n", check_text)

        self.app.window_debug.button_clear_logs.invoke()

        check_text = self.app.window_debug.text_logs.get("1.0", tk.END)
        self.assertEqual("\n", check_text)

    def test_button_export_logs(self):
        self.app.window_debug.text_logs.config(state=tk.NORMAL)
        self.app.window_debug.text_logs.insert(tk.END, "teststring")
        self.app.window_debug.text_logs.see(tk.END)
        self.app.window_debug.text_logs.config(state=tk.DISABLED)

        def mock_messagebox(_):
            pass

        self.app.show_info = mock_messagebox

        self.app.window_debug.button_export_debug.invoke()
        today = datetime.datetime.today()
        formatted_date = today.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"../logs/log_{formatted_date}.txt"

        check_text = self.app.window_debug.text_logs.get("1.0", tk.END)
        self.assertEqual("teststring\n", check_text)
        self.assertEqual(True, os.path.exists("../logs"))
        self.assertEqual(True, os.path.exists(filename))

        with open(filename, "r") as f:
            file_text = f.read()
            self.assertEqual(check_text[:-1], file_text)

        os.remove(filename)


class ComboboxApplicationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def tearDown(self):
        self.app.destroy()

    def test_combobox_useragent(self):
        useragent = self.app.combobox_useragent.get()
        self.assertEqual("cURL", useragent)

        self.app.combobox_useragent.current(11)
        useragent = self.app.combobox_useragent.get()
        self.assertEqual("Custom", useragent)

        self.app.combobox_useragent.event_generate("<<ComboboxSelected>>")

        state = self.app.input_customuseragent.cget("state")
        self.assertEqual("normal", str(state))

    def test_combobox_speedlimit(self):
        speedlimit = self.app.combobox_speedlimit.get()
        self.assertEqual("B/S", speedlimit)


class ComboboxProxyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def tearDown(self):
        self.app.destroy()

    def test_combobox_protocol(self):
        protocol = self.app.window_proxy.combobox_protocol.get()
        self.assertEqual("HTTP", protocol)


if __name__ == '__main__':
    unittest.main()
