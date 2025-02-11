from origin_processing.task_processor import get_instructions
from origin_processing.submission_processor import read_submission_file

from origin_processing.review_processor import (
    processor, 
)

import argparse
from pathlib import Path
import os
import pathlib

import psycopg2

import statistics

import spacy
from spacy.tokens import Span

BASE_DIR = Path(__file__).resolve().parent


def list_folders(directory, recursive=False, indent=""):
    dirs = []

    try:
        abs_directory = os.path.abspath(directory)

        items = os.listdir(abs_directory)

        folders = [item for item in items if os.path.isdir(os.path.join(abs_directory, item))]

        # Print the folders
        for folder in folders:
            # print(f"{indent}{folder}")
            dirs.append(folder)

            if recursive:
                subfolder_path = os.path.join(abs_directory, folder)
                list_folders(subfolder_path, recursive, indent + "  ")

    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found.")

    except PermissionError:
        print(f"Error: Permission denied to access '{directory}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

    return dirs


def find_files(directory, extensions, recursive=False) -> list[str]:
    found_files = []

    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    found_files.append(os.path.join(root, file))

            if not recursive:
                break

    except Exception as e:
        print(f"An error occurred while searching the directory: {e}")
    return found_files


def validate_task_pdf(pdf_path):
    get_file_name = lambda x: pathlib.Path(x).name
    file_name = get_file_name(pdf_path)

    match file_name:
        case '08-009-1_PKI and Man-in-the-Middle Attacks.pdf':
            return False
        case '10-023_Programming with User-defined Functions.pdf':
            return True
        case '08-011_XSS (Cross-Site Scripting) Vulnerability.pdf':
            return False
        case '10-038 Iteration.pdf':
            return True
        case '18-008-02 - Build Your Brand – Technical Portfolio.pdf':
            return False
        case '10-029_OOP – Classes.pdf':
            return True
        case '08-005_Cyber Security Tools – Linux.pdf':
            return True
        case '01-013 Pre-Assessment Cyber Security MCQ.pdf':
            return True
        case '08-014-1_Penetration Testing.pdf':
            return False
        case '12-018_SQL Injection.pdf':
            return False
        case '08-001_Cyber Crimes.pdf':
            return False
        case '08-017-01_A Toolbox for Ethical Hacking.pdf':
            return False
        case '10-036 Getting Started with Your Bootcamp.pdf':
            return False
        case '10-037 Data Types and Conditional Statements.pdf':
            return True
        case _:
            return False


def cr_pipeline(file_path):
        review_content = processor(file_path)

        review_title = review_content['title']
        review_text =  review_content['review_text']
        review_metadata = review_content['metadata']

        review_analysis = nlp(review_text)

        review_sentiment = [sent._.sentiment for sent in review_analysis.sents]

        # Calculate mean avg
        review_average_sentiment = sum(review_sentiment) / len(review_sentiment) if review_sentiment else 0
        
        review_id = insert_review(review_title, review_text, review_average_sentiment, review_metadata)

        return review_id


if __name__ == "__main__":
    dirs = list_folders('data')

    parser = argparse.ArgumentParser(description="Find PDF documents and Python scripts in a directory.")
    parser.add_argument("-d", "--directory", default=".", help="The directory to search in. Defaults to current directory.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Search recursively through subdirectories.")
    args = parser.parse_args()

    db_config = {
        'host': 'localhost',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'postgres'
    }

    get_file_name = lambda x: pathlib.Path(x).name

    # spaCy setup
    nlp = spacy.load("en_core_web_md")
    nlp.add_pipe("sentiment_review", last=True)

    extensions = ('.pdf', '.py', '.txt')

    files = []

    for student_dir in dirs:
        search_dir = f'data/{student_dir}'
        task_dirs = list_folders(search_dir)
        
        for task in task_dirs:
            task_dir = f'data/{student_dir}/{task}'
            task_files = find_files(task_dir, extensions)
            
            file_content = None
            solution_file_name = None

            for file_path in task_files:
                file_name = get_file_name(file_path)

                # Submission
                if file_name != 'review_text.txt' and file_name.endswith('.pdf') == False:
                    max_length = 15
                    
                    submission_text = read_submission_file(file_path)


                
                
                # # Submission pipeline
                # if validate_task_pdf(file_name):
                #     task_pdf = get_instructions(file_path)
                #     for content in task_pdf:
                #         print(content['content'] if content['section'] == 'Instructions' else None)
                    
                


            input()
                
                # Code review pipeline
                # if file_name == 'review_text.txt':
                #     cr_pipeline(file_path)
    
    print('All Done!')


'''
                if file_path.endswith('.pdf'):
                    # Uncomment and implement the logic as needed
                    # is_valid = validate_task_pdf(file_path)
                    # if is_valid:
                    #     structured_content = extract_pdf_content(file_path)
                    #     task_title = structured_content[0]['content']
                    #     for obj in structured_content:
                    #         if obj['section'] == 'Instructions':
                    #             task_instructions = obj['content']
                    pass

                elif file_path.endswith('.py'):
                    solution_file_name = get_file_name(file_path)
                    solution_file_content = stream_code_file(file_path)

                elif file_path.endswith('.txt'):
                    file_name = get_file_name(file_path)
                    
                    if file_name == 'review_text.txt':
                        review_content = stream_review(file_path)

                        student = None
                        task_name = None
                        course = None

                        student = review_content['review_details'][0]['student']
                        task_name = review_content['review_details'][0]['task_name']
                        course = review_content['review_details'][0]['course']

                        review_content =  review_content['review_content']
                        print(review_content)

                        review_analysis = nlp(review_content)
                        sentiments = [sent._.sentiment for sent in review_analysis.sents]
                        average_sentiment = sum(sentiments) / len(sentiments) \
                            if sentiments else 0
                        
                        print(average_sentiment)

                        # if solution_file_content and solution_file_name:
                        #     review_id = insert_review(f'{average_sentiment:.3f}', processed_review)
                        #     solution_id = insert_solution(review_id, solution_file_name, solution_file_content)
'''

    # for student_dir in dirs:
    #     search_dir = f'data/{student_dir}'
    #     task_dirs = list_folders(search_dir)
    #     tasks = [task for task in task_dirs]

    #     for task in tasks:
    #         search_dir = f'data\\{student_dir}\\{task}'
    #         task_files = find_files(search_dir, extensions)

    #         for file_path in task_files:
    #             if file_path.endswith('.pdf'):
    #                 pass
    #                 # is_valid = validate_task_pdf(file_path)

    #                 # if is_valid:
    #                 #     structured_content = extract_pdf_content(file_path)

    #                 #     task_title = structured_content[0]['content']

    #                 #     for obj in structured_content:
    #                 #         if obj['section'] == 'Instructions':
    #                 #             task_instructions = obj['content']

    #             elif file_path.endswith('.py'):
    #                 solution_file_name = get_file_name(file_path)
    #                 file_content = stream_code_file(file_path)
                
    #             elif file_path.endswith('.txt'):
    #                 file_name = get_file_name(file_path)
    #                 if file_name == 'review_text.txt':
    #                     original__review, process_review = stream_review(file_path)
    #                     processed_review = "\n".join(process_review)

    #                     review_analysis = nlp(processed_review)

    #                     sentiments = [sent._.sentiment for sent in review_analysis.sents]

    #                     average_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

    #         review_id = insert_review(f'{average_sentiment:.3f}', processed_review)

    #         if file_content:
    #             solution_id = insert_solution(review_id, solution_file_name)



