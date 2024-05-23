### <center>SciSpark: An Interactive Storytelling System for Young Children's Science Education with Large Language Model (LLM) and Retrieval-Augmented Generation (RAG)</center>

The codes are written for an interactive storytelling system that teaches scientific knowledge through interacting with children during book reading.

#### 1. File Structure

The **front-end** of the system is written in *html*, *css*, and *.js*. 

All the *html* pages can be found in the `./template/` folder.

All the *css* file can be found in the `./static/css/styles.css` file.

All the *.js* files can be found in the `./static/js/`folder.

All the books, images, audio files, and user data are stored in the `./static/files/` folder.

The files are named under each interface:

- **login page:** This interface asks the user to enter their username and password to login to our system. All the users' usernames and passwords are stored in the back-end file (`./Backend.py`).

- **library page:** This interface displays all the books pre-stored in our system, users can select one book and read it.

- **book detail page:** This interface supports users to read each page of a selected book. When the page has a matched scientific knowledge, the page displays the *concept word*, *scientific knowledge*, and a *chatbox*.

  - In the chatbox, there is a chatbot to interact with the child. The chatbot asks questions and provides responsive feedback according to the child's answers.

- **dashboard page:** This interface displays the user's learning records, such as learning progress of each book, the distribution of learned scientific knowledge, reading time, etc.

- **customize page:** This interface supports users to upload their own book. They can take a picture of each page, and modify the text recognized by our system, and see the distribution of matched scientific knowledge. For this function, there are three html files:

  - *customize.html:* This page allows user to view all the uploaded books, and click on an empty block to upload a new book.
  - *upload.html:* This page allows user to 1. upload the cover of a book, 2. upload each page of a book, and 3. view the distribution of matched scientific knowledge of the uploaded book.
  - *custbookdetail.html:* This page allows user to read their uploaded book just like the books in the library interface.

  

The **back-end** of the system is written in python using *Flask*.

The main back-end file is `./backend/Backend.py`, other files in this folder include:

- **NGSS_DCI.json:** All the Disciplinary Core Ideas in the Next Generation Science Standards (NGSS) between kindergarten level to second grade level. Stored in the format of dictionary.
- **NGSS_statements.json:** All the statements in the NGSS between kindergarten level to second grade level. Stored in the format of dictionary.
- **Similarity_dict.json:** This file stores all the concept words with their matched knowledge. When the system matches a new paragraph with scientific knowledge, it will first look for existing words in this file. If the concept words cannot be found in this file, it will generate new data and add it to this file.
- **Text_Process.py:** This file processes the story text by splitting each word in a paragraph and mark the property of each word (stop word or not).
- **GPT_process.py:** This file uses the OpenAI chat completion API and applies our prompts to ask GPT-4 to generate questions and feedbacks according to users' inputs.
- **Keyword_Matching.py:** This file uses the OpenAI chat completion API and applies our prompts to ask GPT-4 to generate a short sentence of explanation of a concept word.
- **Audio_Generation.py:** This file uses the OpenAI text to speech API to generate audio files from a given text, such as story texts, chatbot's questions and feedback.



#### 2. Quickstart

To run the codes for our system, you can create a virtual environment using anaconda, and install all the required packages in the `requirements.txt` file, using the following command line:

```shell
pip install -r requirements.txt
```

Then, open the back-end file:  `./backend/Backend.py` and running this file, you should be able to access the system via your local server.

