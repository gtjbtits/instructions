# How to run a Flask app on Internet Information Services (IIS)

Based on [this](https://github.com/JeevanSandhu/Documentation/blob/master/Flask%20API%20on%20IIS.md) guide. I've changed some steps and extended it a bit.

## Table of contents

* [Pre-requirements](#Pre-requirements)
* [Tested on](#tested_on)
* [Step by step guide](#step_by_step_guide)
    * [A. Enabling IIS](#enabling_iis)
    * [B. Installing Python and enabling WFastCGI](#python_and_wfastcgi)
    * [C. IIS Configuration](#iis_configuration)
    * [D. Test Flask app](#test)
* [Troubleshooting](#troubleshooting)

## Pre-requirements

* Your own Flask app. You also may take an example app from `assets/1/example_app`

## Tested on<a name="tested_on"></a>

* Windows Server 2016 and 2022 Standard with Desktop option
* Python 3.12.6

## Step by step guide<a name="step_by_step_guide"></a>

### A. Enabling IIS<a name="enabling_iis"></a>

1. Go to `Control Panel\All Control Panel Items\Programs and Features` in Explorer. Click on `Turn Windows features on or off` on the left bar
    1. (OR) Open `Server Manager` and click on `2 Add Roles and Features` on the `Quick start` tab:  
![Add Roles and Features Wizzard](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/1.png)  
3. Click `Next` 3 times until you reach `Select server roles` step. Minimal required options set is presented on picture below:  
![Select server roles](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/2.png)  
You don't need to change anything on `Features` tab, so just skip it by hitting `Next`. 

### B. Installing Python and enabling WFastCGI<a name="python_and_wfastcgi"></a>

1. Install Python 3.12 and add it to the `Path`. You can find Python MSI-disribute in `assets/1`
    * **IMPORTANT #1:** You'll need an administrative rights to install Python
    * **IMPORTANT #2:** Make sure you check `Add Python to environment variables`. You can run an installation .exe-file once again, pick a `Modify` option and change any checkboxes, if you've missed them for the first time
    * **TROUBLESHHOTING:** If you'll get an `0x80070659` error, try `Run as administrator`
    * **NOTE:** You can fild old versions of Python for Windows at [official Python FTP-server](https://www.python.org/ftp/python/)
2. Create directory and place there your Flask app with `requirements.txt`. You can get an example application from `assets/1/example_app`
3. Go to created app folder. Create virtual environment (venv) for your app and run `pip install -r requirements.txt`
    * **NOTE:** You can install app packages without venv. It's not recomended, but if you do so, all `Scripts` will be avalable for you in Path environment. So you can type just `wfastcgi-enable` instead of `.\<your_venv_folder>\Scripts\wfastcgi-enable`
4. Enable **wfastcgi**
    1. Run `cmd` as administrator
    2. Type `.\<your_venv_folder>\Scripts\wfastcgi-enable` to enable wfastcgi. Save the path that is given for use later:   
    ![Enable WFastCGI](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/3.png)  
    3. You'll get something like: `C:\sites\new_app\.venv\Scripts\python.exe|C:\sites\new_app\.venv\Lib\site-packages\wfastcgi.py`

### C. IIS Configuration<a name="iis_configuration"></a>

1. Open `Internet Information Services (IIS) Manager`
2. Add new site:  
![Adding a site](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/4.png)  
3. Choose desired `Port` binding and `Physical path`:  
![New site](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/5.png)  
    * **IMPORTANT:** Physical path must contain the full path of the previously created directory with Flask app
4. Add Python **Module Mapping** for the site
    1. Choose *Handler Mappings*:  
    ![Choose Handler Mappings](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/6.png)  
    2. Add new Module Mapper:
        * **IMPORTANT:** `Executable` must contains previously saved `wfastcgi-enable` output (C 4.2).
    ![Adding Module Mapper](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/7.png)  
    3. Disable default `Request restrictions...`:  
    ![Request restrctions. 1](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/15.png)  
    ![Request restrctions. 2](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/16.png)  
    4. Confirm mapper creation:  
    ![Click Yes](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/8.png)  
5. Adjust the **Application pool**
    1. Go to `Application pools` submenu and find application pool with the same name as your site (C 3), that was been automaticly created right after new site was created:  
    ![Application pool](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/9.png)  
    2. Check its `Basic settings`:  
    ![Basic settings](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/10.png)  
    3. When go to `Advanced setings` and change the `Identity` option to `LocalSystem`:  
    ![Advenced settings](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/11.png)  
        * **NOTE:** It's recomended to use `Application Pool Identity` instead, but it required additional permission settings. If you find the way how it can be done, feel free to complete this guide
6. Adjust `FastCGI Settings` on server level  
![FastCGI Settings](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/12.png)  
    1. Open `FastCGI Settings` and go to `Environment variables`. Click on tree dots near by *(Collection)*:  
    ![FastCGI Properties](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/13.png)  
    2. Create at least two nessesary environment variables:  
    ![FastCGI Properties](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/21.png)  
        * `PYTHON_PATH` must contain path to directory with your Flask app file. Eqvivalent to `Physical path` (C 3) (`C:\sites\new_app` by default)
        * `WSGI_HANDLER` must contain Flask app name in format: `<Flask app filename without extension>.<Flask app variable name>` (`app.app` for example_app):
        ```python
        # If filename is "myapp.py"
        flask = Flask(__name__) # Flask app variable name
        # Then WSGI_HANDLER=myapp.flask
        ```
        * **NOTE:** you can also add your own variables. If you created variable with name `MY_VARIABLE` it will be accessible in your app in following way:
        ```python
        import os
        my_variable = os.environ["MY_VARIABLE"]
        ```
7. Restart your IIS server in order to be sure that all cofigurations are applied:  
![Restart IIS Server](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/17.png)

### D. Test Flask app<a name="test"></a>

1. Open web-brouser and go to `http://localhost:<Binded port (C3)>/<your-app-rest-method>` (`http://localhost:5200/test` by default for example_app)
2. If all done right you'll see the `Ok` for example_app:  
![Congratulations](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/20.png)  

## Troubleshooting<a name="troubleshooting"></a>

1. 404 error page
    1. Web server tries to your URL as a file:  
    ![404 error](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/14.png)  
    **SOLUTION:** You forgott to disable `Request restrictions...` (C 4.3)
2. 500 error page
    1. 500.0 error. Used `Identity` (C 5.3) in the `Application pool` hasn't access to `Physical path` (C 3):  
    ![500.0 error](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/18.png)  
    **SOLUTION:** Be sure that the selected `Identity` or user has right access to folder with your Flask app. It also may be solved by choosing `LocalSystem` as a application pool identity
    2. 500 WSGI_HANDLER Python error with message: `AttributeError: module '<X>' has no attribute '<Y>'`:  
    ![500 WSGI_HANDLER error](https://raw.githubusercontent.com/gtjbtits/instructions/master/assets/1/pics/19.png)  
    **SOLUTION:** Check `WSGI_HANDLER` environment variable value (C 6.2)






