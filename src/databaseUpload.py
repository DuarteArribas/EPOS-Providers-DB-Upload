import psycopg2

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
          {solution_type},
          {ac_acronym},
          {creation_date},
          {software},
          {doi},
          {url},
          {ac_name},
          {version},
          {reference_frame},
          {processing_parameters_url},
          {sampling_period} 
        )
        """
      )
      self.cursor.commit()
    except Exception as err:
      print("Error: Could not connect to database: \n" + str(err),file=sys.stderr)
      self.cursor.rollback()