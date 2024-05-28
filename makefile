# Variables
PYTHON                  := python
PIP                     := pip
# Startup dir
STARTUP_DIR             := provider_db_upload
DB_DIR 								  := db
# Python main files
VALIDATION_MAIN_FILE    := validateFiles.py
UPLOAD_TO_DB_MAIN_FILE  := uploadToDB.py
DATABASE_INIT_MAIN_FILE := validationDBInit.py
# Other files
LOCAL_DB_FILE           := detectFiles.db

setup:
	$(PIP) install -r requirements.txt
	$(PYTHON) $(STARTUP_DIR)/$(DATABASE_INIT_MAIN_FILE)

clean:
	@rm $(DB_DIR)/$(LOCAL_DB_FILE)
	@$(PYTHON) $(STARTUP_DIR)/$(DATABASE_INIT_MAIN_FILE)
	
runValidate:
	$(PYTHON) $(VALIDATION_MAIN_FILE)

runUpload:
	$(PYTHON) $(UPLOAD_TO_DB_MAIN_FILE)


test:
	$(PYTHON) -m unittest $(TEST_DIR)/test_$(tf).py > /dev/null

testPrint:
	$(PYTHON) -m unittest $(TEST_DIR)/test_$(tf).py

testAll:
	$(PYTHON) -m unittest $(TEST_DIR)/test_* > /dev/null

testAllPrint:
	$(PYTHON) -m unittest $(TEST_DIR)/test_*

.PHONY: setup clean runValidate runUpload test testPrint testAll testAllPrint