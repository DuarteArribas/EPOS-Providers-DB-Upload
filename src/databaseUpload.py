import psycopg2
import sys

class TSDatabaseUpload:
  """Upload TS solutions to the database."""
  
  # == Methods ==
  def __init__(self,conn,cursor):
    self.conn   = conn
    self.cursor = cursor
    
  def uploadSolution(
    self,
    solution_type,
    ac_acronym,
    creation_date,
    software,
    doi,
    url,
    ac_name,
    version,
    reference_frame,
    processing_parameters_url,
    sampling_period
  ):
    self.cursor.execute("BEGIN TRANSACTION")
    try:
      self.cursor.execute(
        f"""
        INSERT INTO solution(
          solution_type,
          ac_acronym,
          creation_date,
          software,
          doi,
          url,
          ac_name,
          version,
          reference_frame,
          processing_parameters_url,
          sampling_period
        )
        VALUES(
          '{solution_type}',
          '{ac_acronym}',
          '{creation_date}',
          '{software}',
          '{doi}',
          '{url}',
          '{ac_name}',
          '{version}',
          '{reference_frame}',
          '{processing_parameters_url}',
          '{sampling_period}'
        )
        """
      )
      self.cursor.execute("COMMIT TRANSACTION")
    except Exception as err:
      print("Error: Could not connect to database: \n" + str(err),file=sys.stderr)
      self.cursor.execute("ROLLBACK TRANSACTION")
  
  def uploadSolutionOptimized(
    self,
    solutionFile
  ):
    self.cursor.execute("BEGIN TRANSACTION")
    try:
      with open(solutionFile,"r") as csvFile:
        self.cursor.copy_expert(
          f"""
          COPY solution(
            solution_type,
            ac_acronym,
            creation_date,
            software,
            doi,
            url,
            ac_name,
            version,
            reference_frame,
            processing_parameters_url,
            sampling_period
          )
          FROM STDIN
          WITH (FORMAT CSV,HEADER TRUE);
          """,
          csvFile
        )
      self.cursor.execute("COMMIT TRANSACTION")
    except Exception as err:
      print("Error: Could not connect to database: \n" + str(err),file=sys.stderr)
      self.cursor.execute("ROLLBACK TRANSACTION")