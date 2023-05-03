#variables
PYTHON                  := python3
PIP                     := pip3
#python main files
VALIDATION_MAIN_FILE    := validateFiles.py
UPLOAD_TO_DB_MAIN_FILE  := uploadToDB.py
DATABASE_INIT_MAIN_FILE := validationDBInit.py
#directories
TEST_DIR                := tests

runValidate:
	$(PYTHON) $(VALIDATION_MAIN_FILE)

runUpload:
	$(PYTHON) $(UPLOAD_TO_DB_MAIN_FILE)

setup:
	$(PIP) install -r requirements.txt
	$(PYTHON) $(DATABASE_INIT_MAIN_FILE)

clean:
	@rm db/detectFiles.db
	@$(PYTHON) $(DATABASE_INIT_MAIN_FILE)

test:
	$(PYTHON) -m unittest $(TEST_DIR)/test_$(tf).py > /dev/null

testPrint:
	$(PYTHON) -m unittest $(TEST_DIR)/test_$(tf).py

testAll:
	$(PYTHON) -m unittest $(TEST_DIR)/test_* > /dev/null

testAllPrint:
	$(PYTHON) -m unittest $(TEST_DIR)/test_*

.PHONY: runValidate runUpload setup clean test testPrint testAll testAllPrint