from setuptools import setup, find_packages
import codecs
import os
# 
here = os.path.abspath(os.path.dirname(__file__))
# 
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'README.md'), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()\

from pathlib import Path
this_directory = Path(__file__).parent
#long_description = (this_directory / "README.md").read_text()

VERSION = '''0.20'''
DESCRIPTION = '''Big automation package for ADB'''

# Setting up
setup(
    name="adbkit",
    version=VERSION,
    license='MIT',
    url = 'https://github.com/hansalemaos/adbkit',
    author="Johannes Fischer",
    author_email="aulasparticularesdealemaosp@gmail.com",
    description=DESCRIPTION,
long_description = long_description,
long_description_content_type="text/markdown",
    #packages=['a_cv2_imshow_thread', 'a_cv2_shape_finder', 'a_cv_imwrite_imread_plus', 'a_pandas_ex_adb_execute_activities', 'a_pandas_ex_adb_settings_to_df', 'a_pandas_ex_adb_to_df', 'a_pandas_ex_apply_ignore_exceptions', 'a_pandas_ex_csv_plus', 'a_pandas_ex_image_tools', 'a_pandas_ex_logcat2df', 'a_pandas_ex_tesseract_multirow_regex_fuzz', 'adb_grep_search', 'adb_push_create', 'adb_unicode_keyboard', 'adbblitz', 'adbdevicechanger', 'adbescapes', 'androdf', 'bstconnect', 'check_if_nan', 'cv2imshow', 'flatten_everything', 'getevent_sendevent', 'kthread', 'numpy', 'opencv_python', 'pandas', 'Pillow', 'Pillow', 'psutil', 'pyperclip', 'rapidfuzz', 'regex', 'sendevent_getevent_keyboard', 'sendevent_touch', 'subprocess_print_and_capture', 'taskkill', 'tesseractmultiprocessing', 'touchtouch'],
    keywords=['adb', 'android', 'automation', 'shell', 'root'],
    classifiers=['Development Status :: 4 - Beta', 'Programming Language :: Python :: 3 :: Only', 'Programming Language :: Python :: 3.10', 'Topic :: Software Development :: Libraries :: Python Modules', 'Topic :: Utilities'],
    install_requires=['a_cv2_imshow_thread', 'a_cv2_shape_finder', 'a_cv_imwrite_imread_plus', 'a_pandas_ex_adb_execute_activities', 'a_pandas_ex_adb_settings_to_df', 'a_pandas_ex_adb_to_df', 'a_pandas_ex_apply_ignore_exceptions', 'a_pandas_ex_csv_plus', 'a_pandas_ex_image_tools', 'a_pandas_ex_logcat2df', 'a_pandas_ex_tesseract_multirow_regex_fuzz', 'adb_grep_search', 'adb_push_create', 'adb_unicode_keyboard', 'adbblitz', 'adbdevicechanger', 'adbescapes', 'androdf', 'bstconnect', 'check_if_nan', 'cv2imshow', 'flatten_everything', 'getevent_sendevent', 'kthread', 'numpy', 'opencv_python', 'pandas', 'Pillow', 'Pillow', 'psutil', 'pyperclip', 'rapidfuzz', 'regex', 'sendevent_getevent_keyboard', 'sendevent_touch', 'subprocess_print_and_capture', 'taskkill', 'tesseractmultiprocessing', 'touchtouch'],
    include_package_data=True
)
#python setup.py sdist bdist_wheel
#twine upload dist/*