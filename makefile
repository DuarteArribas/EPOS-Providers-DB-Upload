#variables
PYTHON                 := python
PIP                    := pip
VALIDATION_MAIN_FILE   := validateFiles.py
UPLOAD_TO_DB_MAIN_FILE := uploadToDB.py
##files
#appsIdQueue         := apps_id_queue
#rinexQueue          := rinex_queue
#idQueue             := idQueue
#regularUsersIdQueue := regularUsersIDQueue
#logs                := logs.log
#logs2               := logsServer.log
##directories
#testDir             := tests
#inDir               := in
#outDir              := out
#toDownloadDir       := to_download
#toUploadDir         := to_upload
#toUploadRegDir      := to_upload_regular
#resultsDir          := results
#resultsRegDir       := results_regular
#queuesDir           := queues
#logsDir             := logs
##paths
#toDownloadPath      := $(inDir)/$(toDownloadDir)
#toUploadPath        := $(inDir)/$(toUploadDir)
#toUploadRegPath     := $(inDir)/$(toUploadRegDir)
#resultsPath         := $(outDir)/$(resultsDir)
#resultsRegPath      := $(outDir)/$(resultsRegDir)
#appsIdQueuePath     := $(queuesDir)/$(appsIdQueue)
#rinexQueuePath      := $(queuesDir)/$(rinexQueue)
#idQueuePath         := $(queuesDir)/$(idQueue)
#regUsersQueuePath   := $(queuesDir)/$(regularUsersIdQueue)
#logsPath            := $(logsDir)/$(logs)
#logsPath2           := $(logsDir)/$(logs2)

runValidate:
	$(PYTHON) $(VALIDATION_MAIN_FILE)

runUpload:
	$(PYTHON) $(UPLOAD_TO_DB_MAIN_FILE)

setup:
	$(PIP) install -r requirements.txt
	@mkdir -p $(toDownloadPath)
	@mkdir -p $(toUploadPath)
	@mkdir -p $(toUploadRegPath)
	@mkdir -p $(resultsPath)
	@mkdir -p $(resultsRegPath)
	@mkdir -p $(queuesDir)
	@mkdir -p $(logsDir)
	@touch $(appsIdQueuePath)
	@touch $(rinexQueuePath)
	@touch $(idQueuePath)
	@touch $(regUsersQueuePath)
	@touch $(logsPath)

test:
	$(PYTHON) -m unittest $(testDir)/test_$(tf).py > /dev/null

testPrint:
	$(PYTHON) -m unittest $(testDir)/test_$(tf).py

testAll:
	$(PYTHON) -m unittest $(testDir)/test_* > /dev/null

testAllPrint:
	$(PYTHON) -m unittest $(testDir)/test_*

.PHONY: run setup test testPrint testAll testAllPrint clean clearLogs