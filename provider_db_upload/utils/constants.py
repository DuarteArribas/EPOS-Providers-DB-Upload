# Routine Messages
ROUTINE_MSG = {
  "VALIDATING_FILES"    : "Validating files...",
  "VALIDATING_PROVIDER" : "Validating {file_length} files from provider {provider}...",
  "VALIDATING_SNX"      : "Validating the snx file {file}...",
  "VALIDATING_TS"       : "Validating the ts file {file}...",
  "VALIDATING_VEL"      : "Validating the vel file {file}..."
}
# Success Messages
SUCC_MSG = { 
  "DB_CREATE" : "Database created successfully!"
}
# Error Messages
ERROR_MSG = {
  "CONFIG_READ" : "Could not read config file. Exiting...",
  "DB_EXISTS"   : "Database already exists. Did nothing..."
}


dbConnectionError = "Error: Could not connect to the database: '{errMsg}'."
dbUploadError     = "Could not upload file '{file}' to the database (problem in '{uploadType}'): '{errMsg}'."
dbUploadAllError  = "Could not upload all '{uploadType}' to the database: '{errMsg}'."
dbBulkUploadError = "Could not bulk insert files to the database."
getTSFiles        = "Get TS files."
filesFound        = "Files found: '{files}'."
filesNotFound     = "No files found!"
saveFiles         = "Saving information to temporary files."
uploadTSOpt       = "Optimized TS insertion."
uploadSolutionOpt = "Optimized solution insertion."
tmpFileDelete     = "Deleting temporary files."
uploadTS          = "TS Insertion."
uploadSolution    = "Solution insertion."
uploadSuccess     = "Successfully uploaded '{file}' to the database."
uploadBulkSuccess = "Successfully bulk uploaded all files to the database."
saveSuccess       = "Successfully saved all ts information to temporary files."