# A Simple Webscraper tool for Google Reviews

## How to use?

* Clone the Project
* Replace the google_locations.csv file with your input file
    * Input file should have a 'place_id' column
* [OPTIONAL] Run the bellow commands in a shell environment to start a proxy
    ___This proxy works only on linux. Windows users should use a different proxy___

    ```bash
    sudo chmod +x ulinux
    ./ulinux
    ```
* Install the dependencies
    ___It is always advicible to install the dependencies on a virtualenv___

    ```python
    pip install -r requirements.txt
    ```

* Run the script
    ```python
    python google_scraper.py
    ```

After the excecution you will have a new file in the same location with the output.



## Configuration

1. Using a Different Chromedriver

    Set the CHROME_PATH to the chromedriver of your  choice

2. Specifying Different Input File

    Set the CHROME_PATH to your file (include filename)
    Set the URL_COL to the column that has google urls

3. Specifying Different Output FIle

    Set the OUT_PATH variable to wherever you want

4. USE MongoDB Realtime Persistance

    Set MONGO_URL to the MONGODB URI:
        mongodb://<username>:<password>@<host>:<port>/<default_DB>?authSource=admin