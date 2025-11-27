# import modules
import json
import time
from json import JSONDecodeError
from pathlib import Path

import openai
import pandas as pd
from openai import InvalidRequestError
from tqdm import tqdm

from .helpers import output_paths
from .prompts import load_prompt_text, substitute_desired_positions

# add a progress bar to pandas operations
tqdm.pandas(desc="CVs")


# define a class to extract CV information
class CVsInfoExtractor:
    # define a constructor that initializes the class with a DataFrame of CVs
    def __init__(self, cvs_df, openai_api_key, desired_positions, output_dir: str | Path | None = None):
        self.cvs_df = cvs_df

        # build prompt text from bundled resource
        base_prompt = load_prompt_text()
        self.prompt = substitute_desired_positions(base_prompt, desired_positions)

        self.output_csv_path, self.output_excel_path = output_paths(output_dir)

        # set the OpenAI API key
        openai.api_key = openai_api_key


    # define internal function to call GPT for CV info extraction
    def _call_gpt_for_cv_info_extraction(self, prompt, cv_content, model, temperature = 0):

        # create a dict of parameters for the ChatCompletion API
        completion_params = {
            'model': model,
            'messages': [{"role": "system", "content": prompt},
                        {"role": "user", "content": cv_content}],
            'temperature': temperature}

        # send a request to the ChatCompletion API and store the response
        response = openai.ChatCompletion.create(**completion_params)
        # if the response contains choices and at least one choice, extract the message content
        if 'choices' in response and len(response.choices) > 0:
            cleaned_response = response['choices'][0]['message']['content']
            try:
                # try to convert the message content to a JSON object
                json_response = json.loads(cleaned_response)
            except JSONDecodeError:
                # if the conversion fails, set the JSON response to None
                json_response = None  
        else:
            # if the response does not contain choices or no choice, set the JSON response to None
            json_response = None
            
        # return the JSON response
        return json_response
    
    
    # Defines internal function to normalize a JSON response from GPT
    def _normalize_gpt_json_response(self, CV_Filename, json_response):
        
        # Creates a DataFrame with one column "CV_Filename", the values of this column is from the "CV_Filename"
        CV_Filename_df = pd.DataFrame([CV_Filename], columns = ['CV_Filename'])

        # Creates a DataFrame with one column "All_Info_JSON", the values of this column is the JSON response
        df_CV_Info_Json = pd.DataFrame([[json_response]], columns = ['All_Info_JSON'])

        # Normalize the JSON response, flattening it into a table
        df_CV_Info_Json_normalized = pd.json_normalize(json_response)

        # Concatenates the three DataFrame along the columns
        df = pd.concat([CV_Filename_df, df_CV_Info_Json_normalized, df_CV_Info_Json], axis=1)
        
        # Returns the final DataFrame
        return df


    # Defines internal function to write the DataFrame into a CSV file
    def _write_response_to_file(self, df):
        # Append if file exists; otherwise include headers
        append = self.output_csv_path.exists()
        df.to_csv(self.output_csv_path, mode="a" if append else "w", index=False, header=not append)


    # Define the internal function _gpt_pipeline
    def _gpt_pipeline(self, row, model = 'gpt-3.5-turbo'):

        # Retrieve the CV Filename and Content from the given row
        CV_Filename = row['CV_Filename']
        CV_Content = row['CV_Content']

        # Sleep for 5 seconds to delay the next operation
        time.sleep(5)
        
        try:
            # Print status message indicating GPT is being called for CV info extraction
            print('Calling GPT For CV Info Extraction...')

            # Call the GPT model for CV information extraction
            json_response = self._call_gpt_for_cv_info_extraction(prompt=self.prompt, cv_content=CV_Content, model=model)

            # Print status message indicating normalization of GPT response
            print('Normalizing GPT Response...')

            # Normalize the GPT JSON response
            df = self._normalize_gpt_json_response(CV_Filename, json_response)

            # Print status message indicating that the results are being appended to the CSV file
            print('Appending Results To The CSV File...')

            # Write the normalized response to a file
            self._write_response_to_file(df)
            
            # Print a line for clarity in the output
            print('----------------------------------------------')

            # Return the GPT JSON response
            return json_response

        # Catch an exception when the tokens don't fit in the chosen GPT model
        except InvalidRequestError as e:
            # Print the error that occurred
            print('An Error Occurred:', str(e))

            # Print status message indicating that gpt-4 is being called instead
            print("Tokens don't fit gpt-3.5-turbo, calling gpt-4...")

            # Retry the pipeline with the gpt-4 model
            return self._gpt_pipeline(row, model = 'gpt-4')


    # Define the internal function _write_final_results_to_excel
    def _write_final_results_to_excel(self):
        # Load the CSV file into a pandas DataFrame
        df_to_excel = pd.read_csv(self.output_csv_path)

        # Write the DataFrame to an Excel file
        df_to_excel.to_excel(self.output_excel_path)

        # Return the DataFrame
        return df_to_excel


    # Define the main function extract_cv_info
    def extract_cv_info(self):
        # Print a status message indicating the start of the ResumeGPT Pipeline
        print('---- Excecuting ResumeGPT Pipeline ----')
        print('----------------------------------------------')

        # Apply the _gpt_pipeline function to each row in cvs_df DataFrame
        self.cvs_df['CV_Info_Json'] = self.cvs_df.progress_apply(self._gpt_pipeline, axis=1)

        # Print a status message indicating the completion of the extraction
        print('Extraction Completed!')

        # Print a status message indicating that results are being saved to Excel
        print('Saving Results to Excel...')

        # Write the final results to an Excel file
        final_df = self._write_final_results_to_excel()

        # Return the final DataFrame
        return final_df
