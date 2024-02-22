# Introduction
This page is intended to capture instructions to assist a data engineer set up a Spark development environment locally on their laptop. There are roughly three stages:

**1** install VS Code
**2** install Python
**3** install Java.

## Part 1 & 2 Steps
1. Install VS Code from https://code.visualstudio.com/Download
1. Check Python install
   1. Open terminal![1.png](/.attachments/1-2a0e3795-7e40-4f6f-b923-e662578ce1dd.png =200x)
   1. ```python --version```
   1. If not, install Python 3.8.10 or newer from https://www.python.org/downloads/windows/
   1. 3.8.10 download link is https://www.python.org/downloads/release/python-3810/
1. Set up VS Code for Python
   1. Add Python extension
   ![2.png](/.attachments/2-827aa0f3-6dd5-4aa4-a23d-8779463f1e27.png =250x)
   1. Add Azure extension
 ![3.png](/.attachments/3-1d3e9f7e-bd8b-4f38-a011-075445105cc4.png =250x)
   1. Optional - Add Thunder Client
  ![4.png](/.attachments/4-be877a63-44db-4836-9a0c-38680f0546af.png =250x)
1. At this point you should be able to create some python code. You should always use a python virtual environment. To create one, type this in a terminal:
    1. ``` python -m venv .venv```
    1. You should see a new folder created:
    ![5.png](/.attachments/5-9ff11572-237f-41ee-bc29-7ba0da0b7c84.png =200x)
    1. Tell VS Code to use this environment - select it from this menu
    ![6.png](/.attachments/6-21a8d1b2-4eaa-4deb-b1cd-2641639454ae.png =200x)
    1. Create a `requirements.txt` file and add a dependency. Say `azure-storage-blob==12.9.0` and then run `pip install -r requirements.txt`. This will install your libraries into you `.venv` virtual environment.

## Part 3 Steps
This is a little harder I think.
1. Check if you have Java installed. Type this in a VS Code terminal:
   `java -version`
1. If not you have to install it. I have this version. It's a little old but it seemed to show fewer errors/warning than newer versions:
 
   ```
   java version "1.8.0_311"
   Java(TM) SE Runtime Environment (build 1.8.0_311-b11)
   Java HotSpot(TM) 64-Bit Server VM (build 25.311-b11, mixed mode)
   ```
1. Downloading it requires you to create an Oracle account. To save you time, I've shared it here for you: [jdk-8u311-windows-x64.exe](https://seaspan-my.sharepoint.com/personal/sarbjit_sarkaria-az_seaspan_com/_layouts/15/guestaccess.aspx?guestaccesstoken=%2byuPtDOiOPfGLUPjfGm6oobkFzYl%2fwI1po%2bwPTZYN%2bA%3d&docid=2_06bc913cea4c94c26828198591af4e556&rev=1) 
FYI: The current latest version is Java 17. I also have Java 11 if you're interested.
1. Next step is to clone a git project.
   1. In a VS Code bash terminal:

      ```
       cd ~/source/repos
       git clone git@ssh.dev.azure.com:v3/seaspan-edw/DataOps/maretron-sparkapp
       ```
   2. The second step is expected to fail. This is because you need to authenticate to get access to the repo. The industry convention is to authenticate by uploading your _public ssh key_ to the repo.
      * To generate a key pair, type `ssh-keygen -t rsa` and send me the contents of `id_rsa.pub`. The file is typically generated in a folder called `.ssh`. I will upload them to the repo.
      * Now try the `git clone` command again. It should work.
      * At this point you are sharing code via `git`. VS Code supports version control using git both via the UI and via the terminal. Be careful what you check in and on what branch! If you're not familiar with `git` and how it works, we can do another knowledge sharing session on this.
1. Open the project folder in VS Code.
1. Edit the `.env` file so that it has the correct path to `HADOOP_HOME`. The version checked-in references a path specific to my laptop.
1. Add a new environment variable to your Windows machine and make sure that it points to the new project folder. (It should point to maretron-sparkapp not sql2delta as it shows in the illustration)
![7.png](/.attachments/7-c238a345-0836-4262-861e-2431553d3bd6.png =400x)
1. Update the `PATH` environment variable in Windows so that it has an entry for `%HADOOP_HOME%\bin`
![8.png](/.attachments/8-78366623-5029-4d45-87bd-03a4bfbc5997.png =500x)
1. (Optional?) I felt that I had to restart my Windows machine at this point. Though I'm not sure if that's necessary.
1. In a VS Code terminal create a virtual environment: `python -m venv .venv`
   * Activate it: `source .venv/Scripts/activate`
1. Install spark dependencies
   * `pip install -r requirements.txt`
1. In VS Code, run the file called `create_test_delta_tables_from_csv_files.py`.
   * If you get the following error in the logs:
   ```
    java.lang.UnsatisfiedLinkError: org.apache.hadoop.io.nativeio.NativeIO$Windows.access0(Ljava/lang/String;I)Z
   ```
   Then your something is wrong with your `HADOOP_HOME` environment variable. You may need to restart your machine.
   * If it works, you will see a new `output` folder created in the `storage` folder.
     ![9.png](/.attachments/9-7cec59b4-0136-4e53-9eb8-7f7eeb11ecd9.png =200x)
1. Congratulations - you're done! You now have a local Spark development environment installed.
1. Try running the unit tests.
   1. First set up the unittest framework. In VS Code, press CTRL-Shift-P then enter `Python: Configure Tests`
![10.png](/.attachments/10-ab2d772a-d978-47ea-8e57-30c6e885a3c0.png =350x)
   1. Select the `unittest` option.
   1. Tests filename pattern is `test_*.py`
   1. You should now see a flask icon appear
![11.png](/.attachments/11-bf63f4df-4b6c-46fd-a456-8b227e3d6bc8.png =150x)
   1. Select this and start the tests by pressing the ">>" button.